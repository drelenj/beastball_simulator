import tempfile
from pathlib import Path

from .check_replay import default_output as replay_output
from .reproduce_blocker import default_output as blocker_output


def test_check_tools_default_to_temp_not_committed_evidence():
    root=Path(tempfile.gettempdir()).resolve()
    for path in (replay_output(),blocker_output()):
        assert path.resolve().parent==root
        assert 'evidence' not in path.parts
