# B1 dedicated-process contract

Status: binding for the B1 experimental profile. This is the narrow BLK-05
resolution; it does not claim that the historical loader is process-safe.

`pocket4_proto.load_pocket()` creates a dynamic `pocket20` module and
`pocket4_proto.install()` installs wrappers on its classes while mutating
module-global Pocket 4 state. Rebuilding those accepted wrappers is outside
this sprint and would risk changing B0 behavior.

The boundary is therefore:

1. A parent, orchestration, baseline, or experiment-control process must not
   import `b1.runtime`, `pocket4_proto`, or `pocket20`.
2. It invokes a declared entrypoint through `b1.process_runner.run_worker`.
   The declared worker entrypoints are `b1.run` and `b1.g1`.
3. The child process exclusively owns `load_pocket()`, `install()`, Pocket
   classes, Pocket module globals, simulator RNGs, and one B1 job.
4. Only serialized request, trace, result, and evidence values cross the
   process boundary. A module object, class, Match, Player, RNG, callback, or
   mutable simulator object must never cross it.
5. A worker must not run an accepted B0 comparison after enabling B1. B0
   comparisons run in their own fresh processes, matching the accepted T1
   capture procedure.
6. The child terminates after its job. A B1-only matrix may reuse one child
   only when each episode already reconstructs all declared match state and
   its replay test proves exact determinism; it still may not host B0.

Direct construction of `PhysicalExecutionPort` is an internal worker
operation. Tests that exercise the port directly must themselves run inside a
disposable test process; they are not precedent for application code.

The canonical 427-blob B0 inventory in
`b1/baseline/B0_2abe497_GIT_BLOBS.json` is checked before evidence is accepted.
Untracked files are outside the frozen tree; a missing or changed committed
blob fails the guard.
