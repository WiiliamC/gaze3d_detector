import inspect

import pytest


def test_get_edges_accepts_cx_cy():
    from pye3d.cpp.pupil_detection_3d import get_edges

    sig = inspect.signature(get_edges)
    params = list(sig.parameters.keys())
    assert "cx" in params, "get_edges should accept cx parameter"
    assert "cy" in params, "get_edges should accept cy parameter"


def test_search_on_sphere_accepts_cx_cy():
    from pye3d.cpp.pupil_detection_3d import search_on_sphere

    sig = inspect.signature(search_on_sphere)
    params = list(sig.parameters.keys())
    assert "cx" in params, "search_on_sphere should accept cx parameter"
    assert "cy" in params, "search_on_sphere should accept cy parameter"
