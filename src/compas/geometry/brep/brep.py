from compas.geometry import Geometry
from compas.plugins import pluggable
from compas.plugins import PluginNotInstalledError


LINEAR_DEFLECTION = 1e-3


@pluggable(category="factories")
def new_brep(*args, **kwargs):
    raise PluginNotInstalledError()


@pluggable(category="factories")
def from_brep(*args, **kwargs):
    raise PluginNotInstalledError()


@pluggable(category="factories")
def from_mesh(*args, **kwargs):
    raise PluginNotInstalledError()


@pluggable(category="factories")
def from_box(*args, **kwargs):
    raise PluginNotInstalledError()


@pluggable(category="factories")
def from_cylinder(*args, **kwargs):
    raise PluginNotInstalledError()


@pluggable(category="factories")
def from_sphere(*args, **kwargs):
    raise PluginNotInstalledError()


@pluggable(category="factories")
def from_cone(*args, **kwargs):
    raise PluginNotInstalledError()


@pluggable(category="factories")
def from_surface(*args, **kwargs):
    raise PluginNotInstalledError()


@pluggable(category="factories")
def from_torus(*args, **kwargs):
    raise PluginNotInstalledError()


@pluggable(category="factories")
def from_sweep(*args, **kwargs):
    raise PluginNotInstalledError()


@pluggable(category="factories")
def from_step_file(*args, **kwargs):
    raise PluginNotInstalledError()


@pluggable(category="factories")
def from_polygons(*args, **kwargs):
    raise PluginNotInstalledError()


@pluggable(category="factories")
def from_curves(*args, **kwargs):
    raise PluginNotInstalledError()


class BrepType:
    """
    Possible types of a Brep
    """

    COMPOUND = 0
    COMPSOLID = 1
    SHELL = 2
    FACE = 3
    WIRE = 4
    EDGE = 5
    VERTEX = 6
    SHAPE = 7


class BrepOrientation:
    """
    Possible orientations of a Brep
    """

    FORWARD = 0
    REVERSED = 1
    INTERNAL = 2
    EXTERNAL = 3


class Brep(Geometry):
    """Contains the topological and geometrical information of a Brep shape.

    This class serves as an interface for a Brep and allows instantiating a Brep object depending on the available Backend.
    Note: this is not a full implementation of Brep and rather relies on COMPAS's plugin system for actual implementation.

    Attributes
    ----------
    vertices : list[:class:`~compas_rhino.geometry.BrepVertex`], read-only
        The vertices of the Brep.
    edges : list[:class:`~compas_rhino.geometry.BrepEdge`], read-only
        The edges of the Brep.
    loops : list[:class:`~compas_rhino.geometry.BrepLoop`], read-only
        The loops of the Brep.
    faces : list[:class:`~compas_rhino.geometry.BrepFace`], read-only
        The faces of the Brep.
    frame : :class:`~compas.geometry.Frame`, read-only
        The local coordinate system of the Brep.
    area : float, read-only
        The surface area of the Brep.
    volume : float, read-only
        The volume of the regions contained by the Brep.

    Other Attributes
    ----------------
    type : :class:`~compas.geometry.BrepType`, read-only
        The type of Brep shape.
    orientation : :class:`~compas.geometry.BrepOrientation`, read-obly
        Orientation of the shape.

    """

    def __new__(cls, *args, **kwargs):
        return new_brep(cls, *args, **kwargs)

    def __init__(self, name=None):
        super(Brep, self).__init__(name=name)

    def __str__(self):
        lines = [
            "Brep",
            "-----",
            "Vertices: {}".format(len(self.vertices)),
            "Edges: {}".format(len(self.edges)),
            "Loops: {}".format(len(self.loops)),
            "Faces: {}".format(len(self.faces)),
            "Frame: {}".format(self.frame),
            "Area: {}".format(self.area),
            "Volume: {}".format(self.volume),
        ]
        return "\n".join(lines)

    # ==============================================================================
    # Data
    # ==============================================================================

    @property
    def DATASCHEMA(self):
        import schema
        return schema.Schema({
            "faces": list,
        })

    @property
    def JSONSCHEMANAME(self):
        return 'brep'

    @property
    def data(self):
        faces = []
        for face in self.faces:
            faces.append(face.data)
        return {"faces": faces}

    @data.setter
    def data(self):
        raise NotImplementedError

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def orientation(self):
        """
        Returns the current orientation of this Brep.

        Returns
        -------
        :class:`~compas.geometry.BrepOrientation`
        """
        raise NotImplementedError

    @property
    def type(self):
        """
        Returns the type of this Brep.

        Returns
        -------
        :class:`~compas.geometry.BrepType`
        """
        raise NotImplementedError

    @property
    def is_shell(self):
        """
        Returns True if the geometry of this Brep is a shell.

        Returns
        -------
        bool
        """
        raise NotImplementedError

    @property
    def is_solid(self):
        """
        Returns True if the geometry of this Brep is a solid.

        Returns
        -------
        bool
        """
        raise NotImplementedError

    @property
    def is_compound(self):
        """
        Returns True if the geometry of this Brep is a compound.

        Returns
        -------
        bool
        """
        raise NotImplementedError

    @property
    def is_compoundsolid(self):
        """
        Returns True if the geometry of this Brep is a compound solid.

        Returns
        -------
        bool
        """
        raise NotImplementedError

    @property
    def is_orientable(self):
        """
        Returns True if the geometry of this Brep is orientable.

        Returns
        -------
        bool
        """
        raise NotImplementedError

    @property
    def is_closed(self):
        """
        Returns True if the geometry of this Brep is closed.

        Returns
        -------
        bool
        """
        raise NotImplementedError

    @property
    def is_infinite(self):
        """
        Returns True if the geometry of this Brep is infinte.

        Returns
        -------
        bool
        """
        raise NotImplementedError

    @property
    def is_convex(self):
        """
        Returns True if the geometry of this Brep is convex.

        Returns
        -------
        bool
        """
        raise NotImplementedError

    @property
    def is_manifold(self):
        """
        Returns True if the geometry of this Brep is a manifold.

        Returns
        -------
        bool
        """
        raise NotImplementedError

    @property
    def is_surface(self):
        """
        Returns True if the geometry of this Brep is a surface.

        Returns
        -------
        bool
        """
        raise NotImplementedError

    # ==============================================================================
    # Geometric Components
    # ==============================================================================

    @property
    def points(self):
        """
        Returns the points which underly this brap's vertices.

        Returns
        -------
        List[:class:`~compas.geometry.Point`]
        """
        raise NotImplementedError

    @property
    def curves(self):
        """
        Returns the curves which underly this breb's edges.

        Returns
        -------
        List[:class:`compas.geometry.Curve`]
        """
        raise NotImplementedError

    @property
    def surfaces(self):
        """
        Returns the surfaces which underly this brep's faces.

        Returns
        -------
        List[:class:`~compas.geometry.NurbsSurface`]
        """
        raise NotImplementedError

    # ==============================================================================
    # Topological Components
    # ==============================================================================

    @property
    def vertices(self):
        """
        Return the vertices of this brep.

        Returns
        -------
        List[:class:`compas.geometry.BrepVertex`]
        """
        raise NotImplementedError

    @property
    def edges(self):
        """
        Return the edges of this brep.

        Returns
        -------
        List[:class:`compas.geometry.BrepEdge`]
        """
        raise NotImplementedError

    @property
    def loops(self):
        """
        Return the loops of this brep.

        Returns
        -------
        List[:class:`compas.geometry.BrepLoop`]
        """
        raise NotImplementedError

    @property
    def faces(self):
        """
        Return the faces of this brep.

        Returns
        -------
        List[:class:`compas.geometry.BrepFace]
        """
        raise NotImplementedError

    @property
    def shells(self):
        """
        Returns the shells of this brep, if any.
        TODO: do we have a type for this? is this just a list of faces?
        Returns
        -------
        """
        raise NotImplementedError

    @property
    def solids(self):
        """
        Returns the solids of this brep.
        TODO: do we have a type for this?
        Returns
        -------
        """
        raise NotImplementedError

    # ==============================================================================
    # Geometric Properties
    # ==============================================================================

    @property
    def frame(self):
        """
        Returns the Frame of this Brep.

        Returns
        -------
        :class:`~compas.geometry.Frame`
        """
        raise NotImplementedError

    @property
    def area(self):
        """
        Returns the calculated area of this brep.

        Returns
        -------
        float
        """
        raise NotImplementedError

    @property
    def volume(self):
        """
        Returns the calculated volume of this brep.

        Returns
        -------
        float
        """
        raise NotImplementedError

    @property
    def centroid(self):
        """
        TODO: is this just a frame?
        Returns
        -------

        """
        raise NotImplementedError

    # ==============================================================================
    # Constructors
    # ==============================================================================

    @classmethod
    def from_brep(cls, brep):
        return from_brep(brep)

    @classmethod
    def from_step_file(cls, filename):
        return from_step_file(filename)

    @classmethod
    def from_polygons(cls, polygons):
        return from_polygons(polygons)

    @classmethod
    def from_curves(cls, curves):
        return from_curves(curves)

    @classmethod
    def from_box(cls, box):
        return from_box(box)

    @classmethod
    def from_sphere(cls, sphere):
        return from_sphere(sphere)

    @classmethod
    def from_cylinder(cls, cylinder):
        return from_cylinder(cylinder)

    @classmethod
    def from_cone(cls, cone):
        return from_cone(cone)

    @classmethod
    def from_torus(cls, torus):
        return from_torus(torus)

    @classmethod
    def from_mesh(cls, mesh):
        return from_mesh(mesh)

    @classmethod
    def from_brepfaces(cls, faces):
        raise NotImplementedError

    @classmethod
    def from_extrusion(cls, curve, vector):
        raise NotImplementedError

    @classmethod
    def from_sweep(cls, profile, path):
        raise NotImplementedError

    # create pipe
    # create patch
    # create offset

    # ==============================================================================
    # Boolean Constructors
    # ==============================================================================

    @classmethod
    def from_boolean_difference(cls, A, B):
        raise NotImplementedError

    @classmethod
    def from_boolean_intersection(cls, A, B):
        raise NotImplementedError

    @classmethod
    def from_boolean_union(cls, A, B):
        raise NotImplementedError

    # ==============================================================================
    # Converters
    # ==============================================================================

    def to_json(self, filepath):
        raise NotImplementedError

    def to_step(self, filepath):
        raise NotImplementedError

    def to_tesselation(self, linear_deflection=LINEAR_DEFLECTION):
        raise NotImplementedError

    def to_meshes(self, u=16, v=16):
        raise NotImplementedError

    def to_viewmesh(self, precision):
        """
        Convert this Brep to a view mesh
        Parameters
        ----------
        precision:
            float

        Returns
        -------

        """
        raise NotImplementedError

    # ==============================================================================
    # Relationships
    # ==============================================================================

    def vertex_neighbors(self, vertex):
        raise NotImplementedError

    def vertex_edges(self, vertex):
        raise NotImplementedError

    def vertex_faces(self, vertex):
        raise NotImplementedError

    # ==============================================================================
    # Other Methods
    # ==============================================================================

    # flip
    # join
    # join edges
    # join naked edges
    # merge coplanar faces
    # remove fins
    # remove holes
    # repair
    # rotate
    # scale
    # trim
    # rotate
    # translate
    # unjoin edges

    def trim(self, trimming_plane, tolerance):
        """Trim this Brep using the given trimming plane

        Parameters
        ----------
        trimming_plane: defines the trimming plane
            :class:`~compas.geometry.Frame

        tolerance: the tolerance to use when trimming
            float
        """
        raise NotImplementedError

    def is_valid(self):
        """
        Returns True if this brep is a vaild brep.

        Returns
        -------
        bool
        """
        raise NotImplementedError

    def make_solid(self):
        """TODO: What should this do?"""
        raise NotImplementedError

    def sew(self):
        """TODO: What should this do?"""
        raise NotImplementedError

    def fix(self):
        """TODO: What should this do?"""
        raise NotImplementedError

    def cull_unused_vertices(self):
        """Remove all unused vertices.

        Returns
        -------
        None

        """
        NotImplementedError

    def cull_unused_edges(self):
        """Remove all unused edges.

        Returns
        -------
        None

        """
        NotImplementedError

    def cull_unused_loops(self):
        """Remove all unused loops.

        Returns
        -------
        None

        """
        NotImplementedError

    def cull_unused_faces(self):
        """Remove all unused faces.

        Returns
        -------
        None

        """
        NotImplementedError

    def contours(self, planes):
        """TODO: What should this do?"""
        raise NotImplementedError

    def slice(self, plane):
        raise NotImplementedError

    def split(self, other):
        raise NotImplementedError

    def overlap(self, other, deflection=LINEAR_DEFLECTION, tolerance=0.0):
        raise NotImplementedError
