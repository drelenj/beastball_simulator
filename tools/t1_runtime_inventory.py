"""T1 runtime inventory (read-only instrumentation, behaviour unchanged).
mode 'pristine': load the core only.  mode 'installed': load + pocket4_proto.install() + one short B0 game (seed 1).
For every class in the embedded core modules, record each attribute's identity: defining file + qualname + sha256 of its code object.
In 'installed' mode also record every os.environ.get / os.environ[] read (key, default, value) during import, install and the game.
usage: python3 tools/t1_runtime_inventory.py pristine|installed <out.json>"""
import os, sys, json, hashlib, types, inspect
mode, out = sys.argv[1], sys.argv[2]; sys.argv = ['x']; sys.path.insert(0, os.getcwd())
reads = {}
class Env(type(os.environ)): pass
_get = os.environ.get
def logged_get(k, d=None):
    v = _get(k, d); reads.setdefault(k, dict(default=d, value=v, set=k in os.environ)); return v
os.environ.get = logged_get
def code_id(f):
    f = getattr(f, '__func__', f)
    c = getattr(f, '__code__', None)
    if c is None: return None
    h = hashlib.sha256(code_bytes(c)).hexdigest()[:16]
    return dict(file=c.co_filename, line=c.co_firstlineno, qualname=getattr(f, '__qualname__', '?'), code=h, chain=chain(f))
def code_bytes(c):
    # nested code objects hashed recursively (repr() of a code object embeds a memory address, which differs per process)
    parts = [c.co_code, repr(c.co_names).encode(), c.co_filename.encode()]
    for k in c.co_consts: parts.append(code_bytes(k) if isinstance(k, types.CodeType) else repr(k).encode())
    return b'|'.join(parts)
def chain(f, depth=0, seen=None):
    # follow closure cells to the functions a wrapper calls (the wrapped originals), outermost first
    seen = seen or set(); out = []
    for cell in (getattr(f, '__closure__', None) or ()):
        try: v = cell.cell_contents
        except ValueError: continue
        v = getattr(v, '__func__', v)
        if isinstance(v, types.FunctionType) and id(v) not in seen and depth < 12:
            seen.add(id(v)); c = v.__code__
            out.append(dict(file=c.co_filename.split('/')[-1], line=c.co_firstlineno, qualname=v.__qualname__, inner=chain(v, depth + 1, seen)))
    return out
import pocket4_proto as X
P = X.load_pocket()
if mode == 'installed':
    P = X.install(P); over, ex, names = X.make_rosters(seed=1); X.run(P, over, ex, names, seed=1, short=True)
inv = {}
for modname in sorted(k for k in sys.modules if k.startswith('_beastball_pocket.')):
    mod = sys.modules[modname]
    for cname, cls in sorted(vars(mod).items()):
        if not isinstance(cls, type) or cls.__module__ != modname: continue
        for an, av in sorted(vars(cls).items()):
            ci = code_id(av)
            if ci: inv[f'{modname.split(".")[-1]}.{cname}.{an}'] = ci
    for an, av in sorted(vars(mod).items()):
        if isinstance(av, types.FunctionType) and av.__module__ == modname: inv[f'{modname.split(".")[-1]}.<module>.{an}'] = code_id(av)
json.dump(dict(mode=mode, core_file=getattr(P, '__file__', None), attrs=inv, env_reads=reads if mode == 'installed' else None), open(out, 'w'), indent=1, default=str)
print(mode, len(inv), 'attrs', len(reads), 'env reads')
