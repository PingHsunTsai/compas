from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import Rhino

from compas.geometry import Frame

from compas_rhino.geometry._geometry import BaseRhinoGeometry


__all__ = ['RhinoCircle']


class RhinoCircle(BaseRhinoGeometry):
    """Wrapper for a Rhino circle objects.

    Attributes
    ----------
    point (read-only) : :class:`Rhino.Geometry.Point3d`
        Base point of the plane.
    normal (read-only) : :class:`Rhino.Geometry.Vector3d`
        The normal vector of the plane.
    xaxis (read-only) : :class:`Rhino.Geometry.Vector3d`
        The X axis of the plane.
    yaxis (read-only) : :class:`Rhino.Geometry.Vector3d`
        The Y axis of the plane.

    Notes
    -----
    In Rhino, a plane and a frame are equivalent.
    Therefore, the COMPAS conversion function of this class returns a frame object instead of a plane.

    """

    def __init__(self):
        super(RhinoCircle, self).__init__()

    @property
    def plane(self):
        return self.geometry.Plane

    @property
    def radius(self):
        return self.geometry.Radius

    @property
    def center(self):
        return self.geometry.Center

    @property
    def normal(self):
        return self.geometry.Normal

    @classmethod
    def from_geometry(cls, geometry):
        """Construct a circle wrapper from an existing geometry object.

        Parameters
        ----------
        geometry : :class:`Rhino.Geometry.Circle` or :class:`compas.geometry.Circle` or tuple of plane and radius
            The geometry object defining a circle.

        Returns
        -------
        :class:`RhinoCircle`
            The Rhino circle wrapper.
        """
        if not isinstance(geometry, Rhino.Geometry.Circle):
            plane, radius = geometry
            point, normal = plane
            point = Rhino.Geometry.Point3d(point[0], point[1], point[2])
            normal = Rhino.Geometry.Vector3d(normal[0], normal[1], normal[2])
            plane = Rhino.Geometry.Plane(point, normal)
            geometry = Rhino.Geometry.Circle(plane, radius)

        circle = cls()
        circle.geometry = geometry
        return circle

    @classmethod
    def from_selection(cls):
        raise NotImplementedError

    def to_compas(self):
        """Convert to a COMPAS geometry object.

        Returns
        -------
        :class:`Circle`
            A COMPAS circle.
        """
        return Circle(self.point, self.xaxis, self.yaxis)
