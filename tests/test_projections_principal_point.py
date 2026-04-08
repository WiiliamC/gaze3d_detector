import numpy as np
import pytest


def test_project_sphere_with_custom_principal_point():
    from pye3d.geometry.primitives import Sphere
    from pye3d.geometry.projections import project_sphere_into_image_plane

    sphere = Sphere(center=[0, 0, 40], radius=12)
    focal_length = 561.5
    width, height = 400, 400
    cx, cy = 195.0, 205.0

    ellipse = project_sphere_into_image_plane(
        sphere, focal_length, transform=True, width=width, height=height, cx=cx, cy=cy
    )

    expected_center_x = (0 / 40 * focal_length) + cx
    expected_center_y = (0 / 40 * focal_length) + cy
    assert ellipse.center[0] == expected_center_x
    assert ellipse.center[1] == expected_center_y


def test_project_sphere_default_principal_point():
    from pye3d.geometry.primitives import Sphere
    from pye3d.geometry.projections import project_sphere_into_image_plane

    sphere = Sphere(center=[0, 0, 40], radius=12)
    focal_length = 561.5
    width, height = 400, 400

    ellipse = project_sphere_into_image_plane(
        sphere, focal_length, transform=True, width=width, height=height
    )

    expected_center_x = 0 / 40 * focal_length + width / 2
    expected_center_y = 0 / 40 * focal_length + height / 2
    assert ellipse.center[0] == expected_center_x
    assert ellipse.center[1] == expected_center_y


def test_project_circle_with_custom_principal_point():
    from pye3d.geometry.primitives import Circle
    from pye3d.geometry.projections import project_circle_into_image_plane

    circle = Circle(center=[0, 0, 40], normal=[0, 0, 1], radius=5)
    focal_length = 561.5
    width, height = 400, 400
    cx, cy = 195.0, 205.0

    ellipse = project_circle_into_image_plane(
        circle, focal_length, transform=True, width=width, height=height, cx=cx, cy=cy
    )

    assert ellipse is not False
    assert abs(ellipse.center[0] - cx) < 1.0
    assert abs(ellipse.center[1] - cy) < 1.0


def test_unproject_edges_with_custom_principal_point():
    from pye3d.geometry.projections import unproject_edges_to_sphere

    edges = np.array([[200.0, 200.0]])
    focal_length = 561.5
    sphere_center = np.array([0, 0, 40])
    sphere_radius = 12
    width, height = 400, 400
    cx, cy = 195.0, 205.0

    edges_on_sphere, idxs = unproject_edges_to_sphere(
        edges,
        focal_length,
        sphere_center,
        sphere_radius,
        width=width,
        height=height,
        cx=cx,
        cy=cy,
    )

    assert len(idxs) > 0
