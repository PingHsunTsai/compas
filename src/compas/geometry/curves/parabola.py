from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import Vector
from compas.geometry import Point
from compas.geometry import Frame
from .line import Line
from .conic import Conic


class Parabola(Conic):
    """
    A parabola is defined by a plane and a major and minor axis.
    The origin of the coordinate frame is the center of the parabola.

    The parabola in this implementation is based on the equation ``y = a * x**2``.
    Therefore it will have the y axis of the coordinate frame as its axis of symmetry.

    Parameters
    ----------
    frame : :class:`compas.geometry.Frame`
        The coordinate frame of the parabola.
    major : float
        The major of the parabola.

    Attributes
    ----------
    frame : :class:`compas.geometry.Frame`
        The coordinate frame of the hyperbola.
    focal : float
        The distance between the two focus points.
    center : :class:`compas.geometry.Point`, read-only
        The center of the parabola.
    normal : :class:`compas.geometry.Vector`, read-only
        The normal of the parabola.
    plane : :class:`compas.geometry.Plane`, read-only
        The plane of the parabola.
    latus : :class:`compas.geometry.Point`, read-only
        The latus rectum of the parabola.
    eccentricity : float, read-only
        The eccentricity of a parabola is between 0 and 1.
    focus : :class:`compas.geometry.Point`, read-only
        The focus of the parabola.
    directix : :class:`compas.geometry.Line`, read-only
        The directix is the line perpendicular to the y axis of the parabola
        at a distance ``d = + major / eccentricity`` from the center of the parabola.
        The second directix intersects the positive x axis.
    domain : tuple[float, float], read-only
        The parameter domain: 0, 2pi
    is_closed : bool, read-only
        An parabola is closed (True).
    is_periodic : bool, read-only
        An parabola is periodic (True).

    """

    def __init__(self, frame=None, focal=1.0, **kwargs):
        super(Parabola, self).__init__(frame=frame, **kwargs)
        self._focal = None
        self.focal = focal

    def __repr__(self):
        return "Parabola({0!r}, {1!r})".format(self.frame, self.focal)

    def __len__(self):
        return 2

    def __getitem__(self, key):
        if key == 0:
            return self.frame
        elif key == 1:
            return self.focal
        else:
            raise KeyError

    def __setitem__(self, key, value):
        if key == 0:
            self.frame = value
        elif key == 1:
            self.focal = value
        else:
            raise KeyError

    def __iter__(self):
        return iter([self.frame, self.focal])

    # ==========================================================================
    # Data
    # ==========================================================================

    @property
    def data(self):
        return {"frame": self.frame, "focal": self.focal}

    @data.setter
    def data(self, data):
        self.frame = data["frame"]
        self.focal = data["focal"]

    # ==========================================================================
    # properties
    # ==========================================================================

    @property
    def focal(self):
        if self._focal is None:
            raise ValueError("The focal length of the parabola is not set.")
        return self._focal

    @focal.setter
    def focal(self, focal):
        self._focal = focal

    @property
    def a(self):
        return 1 / (4 * self.focal)

    @a.setter
    def a(self, a):
        self.focal = 1 / (4 * a)

    @property
    def eccentricity(self):
        return 1

    @property
    def latus(self):
        return 2 * self.focal

    @property
    def focus(self):
        return self.point + self.yaxis * self.focal

    @property
    def vertex(self):
        return self.point

    @property
    def directix(self):
        point = self.point + self.yaxis * -self.focal
        return Line(point, point + self.xaxis)

    # ==========================================================================
    # Constructors
    # ==========================================================================

    # ==========================================================================
    # Methods
    # ==========================================================================

    def point_at(self, t):
        """
        Point at the parameter.

        Parameters
        ----------
        t : float

        Returns
        -------
        :class:`compas_future.geometry.Point`

        """
        x = t
        y = self.a * x**2
        z = 0
        point = Point(x, y, z)
        # point.transform(self.transformation)
        return point

    def tangent_at(self, t):
        """
        Tangent vector at the parameter.

        Parameters
        ----------
        t : float
            The line parameter.

        Returns
        -------
        :class:`compas_future.geometry.Vector`

        """
        x0 = t
        y0 = self.a * t**2
        x = 2 * t
        y = 2 * self.a * x0 * x - y0
        tangent = Vector(x - x0, y - y0, 0)
        tangent.unitize()
        tangent.transform(self.transformation)
        return tangent

    def normal_at(self, t):
        """
        Normal at a specific normalized parameter.

        Parameters
        ----------
        t : float
            The line parameter.

        Returns
        -------
        :class:`compas_future.geometry.Vector`

        """
        x0 = t
        y0 = self.a * t**2
        x = 2 * t
        y = 2 * self.a * x0 * x - y0
        normal = Vector(y0 - y, x - x0, 0)
        normal.unitize()
        normal.transform(self.transformation)
        return normal

    def frame_at(self, t):
        """
        Frame at the parameter.

        Parameters
        ----------
        t : float
            The line parameter.

        Returns
        -------
        :class:`compas_future.geometry.Frame`

        """
        point = self.point_at(t)
        xaxis = self.tangent_at(t)
        yaxis = self.frame.zaxis.cross(xaxis)
        return Frame(point, xaxis, yaxis)