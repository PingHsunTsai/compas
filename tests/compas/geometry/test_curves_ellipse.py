import pytest
import json
import compas

from compas.tolerance import TOL
from compas.geometry import Frame
from compas.geometry import Ellipse
from compas.geometry import Plane


def test_ellipse_create():
    ellipse = Ellipse(major=1.0, minor=0.5)

    assert TOL.is_close(ellipse.major, 1.0)
    assert TOL.is_close(ellipse.minor, 0.5)
    assert TOL.is_close(ellipse.area, 1.5707963267948966)
    assert TOL.is_close(ellipse.semifocal, 0.8660254037844386)
    assert TOL.is_close(ellipse.eccentricity, 0.8660254037844386)
    assert TOL.is_close(ellipse.focal, 1.7320508075688772)

    assert ellipse.is_closed
    assert ellipse.is_periodic

    assert ellipse.frame == Frame.worldXY()

    assert TOL.is_allclose(ellipse.point_at(0.0), [1.0, 0.0, 0.0])
    assert TOL.is_allclose(ellipse.point_at(0.25), [0.0, 0.5, 0.0])
    assert TOL.is_allclose(ellipse.point_at(0.5), [-1.0, 0.0, 0.0])
    assert TOL.is_allclose(ellipse.point_at(0.75), [0.0, -0.5, 0.0])
    assert TOL.is_allclose(ellipse.point_at(1.0), [1.0, 0.0, 0.0])

    assert TOL.is_allclose(ellipse.point_at(0.0), ellipse.point_at(0.0, world=False))
    assert TOL.is_allclose(ellipse.point_at(0.25), ellipse.point_at(0.25, world=False))
    assert TOL.is_allclose(ellipse.point_at(0.5), ellipse.point_at(0.5, world=False))
    assert TOL.is_allclose(ellipse.point_at(0.75), ellipse.point_at(0.75, world=False))
    assert TOL.is_allclose(ellipse.point_at(1.0), ellipse.point_at(1.0, world=False))


def test_ellipse_create_with_frame():
    ellipse = Ellipse(major=1.0, minor=0.5, frame=Frame.worldZX())

    assert TOL.is_close(ellipse.major, 1.0)
    assert TOL.is_close(ellipse.minor, 0.5)
    assert TOL.is_close(ellipse.area, 1.5707963267948966)
    assert TOL.is_close(ellipse.semifocal, 0.8660254037844386)
    assert TOL.is_close(ellipse.eccentricity, 0.8660254037844386)
    assert TOL.is_close(ellipse.focal, 1.7320508075688772)

    assert ellipse.is_closed
    assert ellipse.is_periodic

    assert ellipse.frame == Frame.worldZX()

    assert TOL.is_allclose(ellipse.point_at(0.0), [0.0, 0.0, 1.0])
    assert TOL.is_allclose(ellipse.point_at(0.25), [0.5, 0.0, 0.0])
    assert TOL.is_allclose(ellipse.point_at(0.5), [0.0, 0.0, -1.0])
    assert TOL.is_allclose(ellipse.point_at(0.75), [-0.5, 0.0, 0.0])
    assert TOL.is_allclose(ellipse.point_at(1.0), [0.0, 0.0, 1.0])

    assert TOL.is_allclose(ellipse.point_at(0.0, world=False), [1.0, 0.0, 0.0])
    assert TOL.is_allclose(ellipse.point_at(0.25, world=False), [0.0, 0.5, 0.0])
    assert TOL.is_allclose(ellipse.point_at(0.5, world=False), [-1.0, 0.0, 0.0])
    assert TOL.is_allclose(ellipse.point_at(0.75, world=False), [0.0, -0.5, 0.0])
    assert TOL.is_allclose(ellipse.point_at(1.0, world=False), [1.0, 0.0, 0.0])

    assert TOL.is_allclose(
        ellipse.point_at(0.0),
        ellipse.point_at(0.0, world=False).transformed(ellipse.transformation),
    )
    assert TOL.is_allclose(
        ellipse.point_at(0.25),
        ellipse.point_at(0.25, world=False).transformed(ellipse.transformation),
    )
    assert TOL.is_allclose(
        ellipse.point_at(0.50),
        ellipse.point_at(0.50, world=False).transformed(ellipse.transformation),
    )
    assert TOL.is_allclose(
        ellipse.point_at(0.75),
        ellipse.point_at(0.75, world=False).transformed(ellipse.transformation),
    )
    assert TOL.is_allclose(
        ellipse.point_at(1.00),
        ellipse.point_at(1.00, world=False).transformed(ellipse.transformation),
    )


# =============================================================================
# Data
# =============================================================================


def test_ellipse_data():
    ellipse = Ellipse(major=1.0, minor=0.5)
    other = Ellipse.__from_data__(json.loads(json.dumps(ellipse.__data__)))

    assert ellipse.major == other.major
    assert ellipse.minor == other.minor
    assert ellipse.frame.point == other.frame.point
    assert TOL.is_allclose(ellipse.frame.xaxis, other.frame.xaxis)
    assert TOL.is_allclose(ellipse.frame.yaxis, other.frame.yaxis)

    if not compas.IPY:
        assert Ellipse.validate_data(ellipse.__data__)
        assert Ellipse.validate_data(other.__data__)


# =============================================================================
# Constructors
# =============================================================================


def test_ellipse_create_from_point_major_minor():
    ellipse = Ellipse.from_point_major_minor([1.0, 2.0, 3.0], 1.0, 0.5)

    assert TOL.is_close(ellipse.major, 1.0)
    assert TOL.is_close(ellipse.minor, 0.5)
    assert TOL.is_close(ellipse.area, 1.5707963267948966)
    assert TOL.is_close(ellipse.semifocal, 0.8660254037844386)
    assert TOL.is_close(ellipse.eccentricity, 0.8660254037844386)
    assert TOL.is_close(ellipse.focal, 1.7320508075688772)

    assert ellipse.is_closed
    assert ellipse.is_periodic

    assert TOL.is_allclose(ellipse.frame.point, [1, 2, 3])
    assert TOL.is_allclose(ellipse.frame.xaxis, Frame.worldXY().xaxis)
    assert TOL.is_allclose(ellipse.frame.yaxis, Frame.worldXY().yaxis)
    assert TOL.is_allclose(ellipse.frame.zaxis, Frame.worldXY().zaxis)


def test_ellipse_create_from_plane_major_minor():
    plane = Plane([1.0, 2.0, 3.0], [0.0, 0.0, 1.0])
    frame = Frame.from_plane(plane)
    ellipse = Ellipse.from_plane_major_minor(plane, 1.0, 0.5)

    assert TOL.is_close(ellipse.major, 1.0)
    assert TOL.is_close(ellipse.minor, 0.5)
    assert TOL.is_close(ellipse.area, 1.5707963267948966)
    assert TOL.is_close(ellipse.semifocal, 0.8660254037844386)
    assert TOL.is_close(ellipse.eccentricity, 0.8660254037844386)
    assert TOL.is_close(ellipse.focal, 1.7320508075688772)

    assert ellipse.is_closed
    assert ellipse.is_periodic

    assert TOL.is_allclose(ellipse.frame.point, frame.point)
    assert TOL.is_allclose(ellipse.frame.xaxis, frame.xaxis)
    assert TOL.is_allclose(ellipse.frame.yaxis, frame.yaxis)
    assert TOL.is_allclose(ellipse.frame.zaxis, frame.zaxis)


# =============================================================================
# Properties and Geometry
# =============================================================================


def test_ellipse_major():
    ellipse = Ellipse(major=1.0, minor=0.5)

    assert TOL.is_close(ellipse.major, 1.0)

    ellipse._major = None
    with pytest.raises(ValueError):
        ellipse.major

    with pytest.raises(ValueError):
        ellipse.major = -1.0


def test_ellipse_minor():
    ellipse = Ellipse(major=1.0, minor=0.5)

    assert TOL.is_close(ellipse.minor, 0.5)

    ellipse._minor = None
    with pytest.raises(ValueError):
        ellipse.minor

    with pytest.raises(ValueError):
        ellipse.minor = -1.0


# =============================================================================
# Accessors
# =============================================================================

# =============================================================================
# Comparison
# =============================================================================

# =============================================================================
# Other Methods
# =============================================================================
