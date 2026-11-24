"""Trusted local snapshots of an offline Native match.

Rulebook review preserves the field state and adjudication counters. Drill
snapshots extend that boundary to the entire match graph, including observation
queues, the driver clocks, commitments, transport, RNGs and the trace prefix.
Static wiring belongs to the fresh Native build, including its private modules.
"""
from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from types import ModuleType
import gzip
import pickle

from native.port import digest
from native.rulebook.port import RulebookPort
from native.run import MatchDriver

SCHEMA = 'oracle-snapshot/1'


class RecordingHash:
    """Write-ahead trace data for exact resumes. Used only by the offline harness."""

    def __init__(self, prefix=b''):
        self.data = bytearray(prefix)
        self.hash = sha256(prefix)

    def update(self, data):
        self.hash.update(data)
        self.data.extend(data)

    def copy(self):
        return self.hash.copy()

    def hexdigest(self):
        return self.hash.hexdigest()


@dataclass(frozen=True)
class Build:
    seed: int
    config: object
    rosters: dict
    policies: dict | None = None
    plumbing: bool = True

    def create(self, *, record=True):
        port = RulebookPort(self.seed, self.config, self.policies, self.plumbing, self.rosters)
        if record:
            prefix = port.behavior_digest.encode() + digest(
                {team: policy.as_dict() for team, policy in port.policies.items()}).encode()
            assert sha256(prefix).hexdigest() == port.trace.hexdigest()
            port.trace = RecordingHash(prefix)
        return MatchDriver(port)


def roots(driver):
    port = driver.port
    values = {'driver': driver, 'port': port, 'match': port.m, 'engine': port.m.e}
    values.update(('policy/' + team, policy) for team, policy in port.m.pol.items())
    for name in ('rb317', 'rb318'):
        if hasattr(port, name):
            values[name] = getattr(port, name)
    return values


def is_wiring(value):
    return callable(value) or isinstance(value, ModuleType)


class EventSuffix:
    """Retain the live log window at its original absolute indices."""

    def __init__(self, log, start):
        self.start = start
        self.rows = log[start:]

    def __len__(self):
        return self.start + len(self.rows)

    def __iter__(self):
        return iter(self.rows)

    def _offset(self, start):
        if start is None:
            return None
        index = start if start >= 0 else len(self) + start
        if index < self.start:
            raise IndexError('event index predates the retained window')
        return index - self.start

    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.rows[slice(self._offset(key.start), self._offset(key.stop), key.step)]
        return self.rows[self._offset(key)]

    def __delitem__(self, key):
        del self.rows[slice(self._offset(key.start), self._offset(key.stop), key.step)]

    def append(self, row):
        self.rows.append(row)


def compact_histories(graph, port):
    """Rollouts start new result histories while retaining active witnesses."""
    engine, match = port.m.e, port.m
    indices = [max(0, len(engine.log) - 8), engine.native_seen, match.last_log_seen]
    if engine.review_snapshot:
        indices.append(engine.review_snapshot[2])
    if getattr(engine, 'rb310_hold', None):
        indices.append(engine.rb310_hold['log_index'])
    graph['engine']['log'] = EventSuffix(engine.log, min(indices))
    for name in ('command_log', 'release_log', 'outcomes', 'intents', 'prism_commits'):
        if name in graph['port']:
            graph['port'][name] = []
    graph['match']['trace'] = []


class GraphWriter(pickle.Pickler):
    def __init__(self, file, bound):
        super().__init__(file, protocol=5)
        self.bound = {id(obj): name for name, obj in bound.items()}

    def persistent_id(self, value):
        key = self.bound.get(id(value))
        return key


class GraphReader(pickle.Unpickler):
    def __init__(self, file, bound, namespace, fresh_namespace):
        super().__init__(file)
        self.bound = bound
        self.namespace = namespace
        self.fresh_namespace = fresh_namespace

    def persistent_load(self, token):
        return self.bound[token]

    def find_class(self, module, name):
        if module.startswith(self.namespace + '.'):
            module = self.fresh_namespace + module[len(self.namespace):]
        return super().find_class(module, name)


@dataclass(frozen=True)
class Snapshot:
    schema: str
    build: Build
    namespace: str
    payload: bytes
    prefix: bytes
    prefix_hash: str
    compact: bool = False

    def save(self, path):
        Path(path).write_bytes(gzip.compress(pickle.dumps(self, protocol=5), mtime=0))

    @classmethod
    def load(cls, path):
        """Read a snapshot created by this engine from a trusted local source."""
        snapshot = pickle.loads(gzip.decompress(Path(path).read_bytes()))
        if not isinstance(snapshot, cls) or snapshot.schema != SCHEMA:
            raise ValueError('unsupported snapshot format')
        return snapshot


def capture(build, driver, *, prepared=None, compact=False):
    port = driver.port
    if not isinstance(port.trace, RecordingHash) or port.config != build.config:
        raise ValueError('capture needs a recording driver from the same build')
    bound = roots(driver)
    graph = {key: {name: value for name, value in vars(obj).items()
                   if not is_wiring(value) and (key, name) != ('port', 'trace')}
             for key, obj in bound.items()}
    if compact:
        compact_histories(graph, port)
    stream = BytesIO()
    GraphWriter(stream, bound).dump((graph, prepared))
    return Snapshot(SCHEMA, build, port.CO.__name__, stream.getvalue(),
                    b'' if compact else bytes(port.trace.data), port.trace.hexdigest(), compact)


def restore(snapshot, driver=None, *, record=True):
    if snapshot.schema != SCHEMA:
        raise ValueError('unsupported snapshot format')
    driver = driver or snapshot.build.create(record=False)
    if driver.port.config != snapshot.build.config:
        raise ValueError('snapshot config does not match the target driver')
    bound = roots(driver)
    wiring = {key: {name: value for name, value in vars(obj).items() if is_wiring(value)}
              for key, obj in bound.items()}
    graph, prepared = GraphReader(BytesIO(snapshot.payload), bound, snapshot.namespace,
                                  driver.port.CO.__name__).load()
    for key, state in graph.items():
        vars(bound[key]).clear()
        vars(bound[key]).update(wiring[key], **state)
    prefix = (b'oracle-branch/1/' + bytes.fromhex(snapshot.prefix_hash)
              if snapshot.compact else snapshot.prefix)
    trace = RecordingHash(prefix) if record else sha256(prefix)
    if not snapshot.compact and trace.hexdigest() != snapshot.prefix_hash:
        raise ValueError('snapshot trace prefix differs from its fingerprint')
    driver.port.trace = trace
    return driver, prepared
