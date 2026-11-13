from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
import json
import pytest
from . import cognition as C
from . import communication as M
from .matchport import MatchPort, run_match

TEAMS = {'A0':'A','A1':'A','A2':'A','B0':'B'}

def envelope(cid='cause/0', payload=b'\x00\x10', recipients=('A1',), sender='A0', now=0):
    return M.MessageEnvelope(sender,recipients,'synthetic',payload,cid,now)


def replay(reverse=False):
    t = M.TeamTransport(17,TEAMS,M.DeliveryModel(enabled=True,noise=.5,loss=.2))
    batch = [envelope(f'cause/{i}') for i in range(10)]
    t.send_batch(reversed(batch) if reverse else batch,0)
    return t.intake('A1',1000), t.audit


def test_M2_2_delay_loss_noise_and_view_only_intake():
    cfg = M.DeliveryModel(enabled=True,delay_min_ms=100,delay_max_ms=100,noise=1.)
    t = M.TeamTransport(1,TEAMS,cfg)
    t.send_batch([envelope()],0)
    assert t.intake('A1',99) == ()
    received = t.intake('A1',100)
    assert len(received) == 1
    d = received[0]
    assert d.envelope.payload != b'\x00\x10'
    assert d.envelope.causal_id == 'cause/0'
    assert d.due_ms == d.delivered_ms == 100
    lossy = M.TeamTransport(1,TEAMS,replace(cfg,loss=1.))
    lossy.send_batch([envelope()],0)
    assert lossy.intake('A1',100) == ()
    p = MatchPort(1,'g1',communication_model=cfg)
    p.capture(1000)
    p.communication.send_batch([envelope(now=1000)],1000)
    # Future messages cannot be pulled into an earlier view.
    p.capture(2000)
    v,b = p.deliver('A1',2100)
    assert b.messages == v.messages and len(b.messages) == 1
    assert v.messages[0].envelope.payload != envelope().payload
    before = C.decide(v,b)
    p.communication._pending.clear()
    p.m.s.ball.x = -99999
    p.m.s.players['A0'].x = 99999
    assert C.decide(v,b) == before
    v2,b2 = C.view_from_json(json.loads(json.dumps(C.view_to_json(v,b))))
    assert C.decide(v2,b2) == before
    assert v2.messages == v.messages


def test_poison_before_view_delivery_and_empty_registry_do_not_change_decisions():
    ports = [MatchPort(1,'g1',communication_model=M.DeliveryModel(enabled=True)) for _ in range(2)]
    for p in ports:
        for now in range(1000,2100,100):
            p.capture(now)
        p.communication.send_batch([envelope(now=1000)],1000)
    ports[1].m.s.ball.x = -99999
    ports[1].m.s.players['A0'].x = 99999
    ports[1].m.s.owner = 'B'
    # Poison unobservable future communication. It cannot be delivered early.
    ports[1].communication.send_batch([envelope('future',now=2200)],2200)
    va,ba = ports[0].deliver('A1',2100)
    vb,bb = ports[1].deliver('A1',2100)
    assert va == vb and ba == bb
    assert C.decide(va,ba) == C.decide(vb,bb)
    assert not M.plan_hooks(va,ba)[0].active


def test_M2_3_serial_parallel_and_causal_ids():
    serial = [replay(False),replay(True)]
    with ProcessPoolExecutor(2) as pool:
        parallel = list(pool.map(replay,[False,True]))
    assert serial[0] == serial[1] == parallel[0] == parallel[1]
    t = M.TeamTransport(1,TEAMS,M.DeliveryModel(enabled=True))
    with pytest.raises(ValueError):
        t.send_batch([envelope(),envelope()],0)
    assert t._pending == []
    t.send_batch([envelope()],0)
    with pytest.raises(ValueError):
        t.send_batch([envelope(now=1)],1)


def test_M2_4_bandwidth_ordering_capacity_and_team_routing():
    e = envelope()
    cfg = M.DeliveryModel(enabled=True,delay_min_ms=0,delay_max_ms=0,
                          bandwidth_bytes=e.wire_bytes,queue_capacity=1)
    t = M.TeamTransport(1,TEAMS,cfg)
    rows = t.send_batch([envelope('cause/1'),e],0)
    assert [r[2] for r in rows] == ['queued','bandwidth']
    assert t.intake('A1',0)[0].envelope.causal_id == e.causal_id
    t = M.TeamTransport(1,TEAMS,replace(cfg,bandwidth_bytes=99999))
    assert [r[2] for r in t.send_batch([e,envelope('cause/1')],0)] == ['queued','queue_capacity']
    t = M.TeamTransport(1,TEAMS,replace(cfg,bandwidth_bytes=99999,queue_capacity=10,intake_capacity=1))
    t.send_batch([envelope('cause/2'),e,envelope('cause/1')],0)
    assert t.intake('A1',0)[0].envelope.causal_id == 'cause/0'
    assert sum(r[2] == 'intake_capacity' for r in t.audit) == 2
    assert t.intake('A1',1) == ()
    t = M.TeamTransport(1,TEAMS,replace(cfg,bandwidth_bytes=99999,messages_per_window=1))
    assert t.send_batch([e,envelope('cause/1')],0)[1][2] == 'bandwidth'
    with pytest.raises(ValueError):
        t.send_batch([],0)
    with pytest.raises(ValueError):
        t.send_batch([envelope(recipients=('B0',),now=1)],1)
    # Window rollover restores capacity; multicast charges every recipient.
    t.send_batch([envelope('new',now=1000)],1000)
    t = M.TeamTransport(1,TEAMS,cfg)
    assert t.send_batch([envelope(recipients=('A1','A2'))],0)[0][2] == 'bandwidth'


def test_M2_5_messages_cannot_change_action_kind_target_receiver_or_aim():
    r,p = run_match(1,'g1',2000,False)
    for pid in p.active_ids():
        v,b = p.deliver(pid,p.m.s.now)
        for role in ('field','keeper','archer'):
            for holds in (False,True):
                for pending in (False,True):
                    variant = replace(v,role=role,holds_ball=holds,arrows_loaded=5,
                                      pending_command_id='synthetic/command' if pending else None,
                                      pending_kind='pass' if pending else None)
                    d = M.Delivery(envelope(recipients=(pid,),payload=b'{"kind":"synthetic","target":"B0"}'),
                                   pid,0,v.delivered_ms)
                    with_messages = replace(variant,messages=(d,))
                    belief = replace(b,messages=M.receive_messages(with_messages))
                    assert C.decide(variant,b) == C.decide(with_messages,belief)
                    activation, gate = M.plan_hooks(with_messages,belief)
                    assert not activation.active and activation.stage_id is None and gate.bypass


def test_M2_1_null_does_not_iterate_send_or_touch_rng_and_matches_short_replay():
    t = M.TeamTransport(1,TEAMS)
    def forbidden():
        raise AssertionError('null mode consumed send input')
        yield
    assert t.send_batch(forbidden(),0) == t.intake('A1',0) == ()
    assert t.audit == [] and t._pending == []
    a = run_match(1,'g1',9000,False)[0]
    b = run_match(1,'g1',9000,False,communication_model=M.DeliveryModel())[0]
    assert (a['trace_hash'],a['state_hash']) == (b['trace_hash'],b['state_hash'])


def test_bad_models_and_envelopes_rejected():
    for kwargs in ({'loss':2.},{'noise':-1.},{'delay_min_ms':400},{'queue_capacity':0}):
        with pytest.raises(ValueError):
            M.DeliveryModel(**kwargs)
    with pytest.raises(ValueError):
        envelope(recipients=('A1','A1'))
