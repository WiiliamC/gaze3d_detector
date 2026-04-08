import numpy as np
import pytest


def test_camera_model_default_principal_point():
    from pye3d.camera import CameraModel

    camera = CameraModel(focal_length=561.5, resolution=(400, 400))
    assert camera.cx is None
    assert camera.cy is None
    assert camera.cx_computed == 200.0
    assert camera.cy_computed == 200.0


def test_camera_model_custom_principal_point():
    from pye3d.camera import CameraModel

    camera = CameraModel(focal_length=561.5, resolution=(400, 400), cx=195.0, cy=205.0)
    assert camera.cx == 195.0
    assert camera.cy == 205.0


def test_camera_model_explicit_none_principal_point():
    from pye3d.camera import CameraModel

    camera = CameraModel(focal_length=561.5, resolution=(400, 400), cx=None, cy=None)
    assert camera.cx is None
    assert camera.cy is None
