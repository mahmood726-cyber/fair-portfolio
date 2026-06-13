"""Import-smoke + pure-function tests for fair-portfolio (Bucket-B no-tests remediation).

The import-smoke guards against dependency drift / syntax breakage (the same
class of bug that crashed a sibling shipped engine on numpy 2.x).
"""
import importlib.util
import os
import sys

import pytest

_SCRIPT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'scripts', 'build_fair_portfolio.py')


def _load():
    sys.path.insert(0, os.path.dirname(_SCRIPT))
    spec = importlib.util.spec_from_file_location("buildmod_fair_portfolio", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    # Some build modules reassign sys.stdout to io.TextIOWrapper(sys.stdout.buffer)
    # at import; under pytest capture sys.stdout has no .buffer. Lend the real
    # stdout (which has a buffer) during import, then restore pytest's capture.
    saved_out, saved_err = sys.stdout, sys.stderr
    if not hasattr(sys.stdout, "buffer"):
        sys.stdout = sys.__stdout__
    if not hasattr(sys.stderr, "buffer"):
        sys.stderr = sys.__stderr__
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.stdout, sys.stderr = saved_out, saved_err
    return mod


def test_script_exists():
    assert os.path.isfile(_SCRIPT), _SCRIPT


def test_module_imports():
    # import-smoke: any dep/syntax/import error fails here
    assert _load() is not None


def test_has_public_callable():
    mod = _load()
    publics = [n for n in dir(mod) if callable(getattr(mod, n)) and not n.startswith("_")]
    assert publics, "module exposes no public callable"


def test_empty_portfolio_raises():
    """build_payload must raise ValueError rather than crash with StatisticsError/ZeroDivisionError."""
    mod = _load()
    empty_source = {"overview": {"sourcePath": "test"}, "portfolio": []}
    with pytest.raises(ValueError, match="no projects"):
        mod.build_payload(empty_source)


def test_classify_band_boundaries():
    mod = _load()
    assert mod.classify_band(80) == "strong"
    assert mod.classify_band(79) == "emerging"
    assert mod.classify_band(60) == "emerging"
    assert mod.classify_band(59) == "partial"
    assert mod.classify_band(40) == "partial"
    assert mod.classify_band(39) == "weak"
    assert mod.classify_band(0) == "weak"


def test_score_project_total_in_range():
    """score_project total must be 0..100; components must each be 0..25."""
    mod = _load()
    project = {
        "id": "test-001",
        "name": "TestProject",
        "path": r"C:\Projects\TestProject",
        "tierShortName": "T1",
        "tierName": "Tier 1",
        "status": "active",
        "statusLabel": "Active",
        "statusExplicit": True,
        "type": "HTML app",
        "detail": "A test project with tests, v1.0.",
        "row": {"Status": "Active", "Paper Status": "", "Last Touch": ""},
    }
    result = mod.score_project(project)
    total = result["scores"]["total"]
    assert 0 <= total <= 100, f"total out of range: {total}"
    for comp in ("findable", "accessible", "interoperable", "reusable"):
        v = result["scores"][comp]
        assert 0 <= v <= 25, f"{comp} out of range: {v}"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
