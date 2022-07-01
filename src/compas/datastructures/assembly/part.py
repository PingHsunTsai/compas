from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import copy
import abc
from collections import deque

from compas.geometry import Frame
from compas.geometry import Polyhedron
from compas.geometry import Transformation
from compas.geometry import boolean_union_mesh_mesh
from compas.geometry import boolean_difference_mesh_mesh
from compas.geometry import boolean_intersection_mesh_mesh
from compas.datastructures import Mesh
from compas.data import Data
from compas.plugins import pluggable

from ..datastructure import Datastructure
from .exceptions import FeatureError

# TODO: not to do
try:
    from compas_rhino.conversions import xform_to_rhino, frame_to_rhino
except ImportError:
    pass


# TODO what's the category?
# TODO move to geotmetry.__init__py
@pluggable(category="trim")
def trim_brep_with_plane(brep, cutting_plane, precision):
    raise NotImplementedError


class Feature(Data):
    """
    Abstract class. Holds all the information needed to perform a certain operation using a shape on a specific part.
    When applying the feature to the geometry of the part, stores the pre-change geometry in order
    to allow restoring the state of the part before the operation. a la Command.
    """

    ALLOWED_OPERATIONS = {}

    def __init__(self, geometry, operation):
        """

        Parameters
        ----------
        shape : :class:`~compas.geometry._shape.Shape`
                The shape of this feature
        operation : :callable: e.g. boolean_op_mesh_mesh(A, B)
        """
        super(Feature, self).__init__()

        if operation not in self.ALLOWED_OPERATIONS:
            raise ValueError("Operation {} unknown. Expected one of {}".format(operation, list(self.ALLOWED_OPERATIONS.keys())))

        self.operation = self.ALLOWED_OPERATIONS[operation]
        self.feature_geometry = geometry
        self.part = None
        self.previous_geometry = None

    @property
    def DATASCHEMA(self):
        import schema

        return schema.Schema(
            {
                "feature_geometry": PartGeometry,
                "operation": str,
            }
        )

    @property
    def JSONSCHEMANAME(self):
        return "feature"

    @property
    def data(self):
        return {"feature_geometry": self.feature_geometry, "operation": self.get_operation_name_by_value(self.operation)}

    @data.setter
    def data(self, value):
        self.feature_geometry = value["feature_geometry"]
        self.operation = self.ALLOWED_OPERATIONS[value["operation"]]

    def apply(self, part):
        """
        Applies this feature to the current geometry of part and replaces it with the resulting geometry.

        Parameters
        ----------
        part : :class: `~compas.datastructures.assembly.part.Part`
                The part on which this feature should be applied
        """
        self._store_previous_geometry(part)
        self._apply_feature()

    @abc.abstractmethod
    def _apply_feature(self):
        """
        Preforms the required geometry type specific operation required to apply this feature to self.part
        and set its new geometry.
        Called by Feature().apply()
        """
        raise NotImplementedError

    def _store_previous_geometry(self, part):
        self.part = part
        self.previous_geometry = copy.deepcopy(self.part._part_geometry)

    def restore(self):
        """
        Restores the part's geometry to the one before the application of this feature.
        Raises a FeatureError if no part has been associated with this feature.

        """
        if not self.part:
            raise FeatureError("This feature is not associated with any Part!")
        self.part._part_geometry = self.previous_geometry

    @classmethod
    def get_operation_name_by_value(cls, value):
        """
        Gets the the operation name of the given operation function

        Parameters
        ----------
        value: :callback: one of the pluggable operation calls from Part.ALLOWED_OPERATIONS

        Returns
        -------
        :str: the operation name which corresponds to the given operation function

        """
        try:
            return {v: k for k, v in cls.ALLOWED_OPERATIONS.items()}[value]
        except KeyError:
            raise ValueError("Expected one of the following operations {} got instead {}".format([v.__name__ for _, v in cls.ALLOWED_OPERATIONS.items()], value))


class MeshFeature(Feature):
    """
    Represents a Mesh/Shape feature of a Part. Can be applied to Part whose geometry is described by a MeshGeometry.
    """

    ALLOWED_OPERATIONS = {"union": boolean_union_mesh_mesh, "difference": boolean_difference_mesh_mesh, "intersection": boolean_intersection_mesh_mesh}

    def __init__(self, geometry, operation):
        super(MeshFeature, self).__init__(geometry, operation)

    def _apply_feature(self):
        part_mesh = self.part._part_geometry.to_vertices_and_faces(triangulated=True)
        feature_mesh = self.feature_geometry.to_vertices_and_faces(triangulated=True)
        result = self.operation(part_mesh, feature_mesh)
        self.part._part_geometry = MeshGeometry(Polyhedron(*result))


class BrepFeature(Feature):
    """
    Represents a Brep feature of a Part. Can be applied to Part whose geometry is described by a BrepGeometry.
    """

    ALLOWED_OPERATIONS = {"trim": trim_brep_with_plane}  # TODO: map to pluggable trim operation function

    def __init__(self, cutting_plane, operation):
        super(BrepFeature, self).__init__(cutting_plane, operation)

    def _apply_feature(self):
        cutting_plane = self.feature_geometry.geometry
        rhino_plane = frame_to_rhino(cutting_plane)
        rhino_plane.Flip()  # why?
        breps = self.operation(self.part.geometry, rhino_plane, 1e-6)
        result = BrepGeometry(self._pick_resulting_brep(breps))
        self.part._part_geometry = result.transformed(Transformation.from_frame_to_frame(self.part.frame, Frame.worldXY()))

    @staticmethod
    def _pick_resulting_brep(brep_list):
        if not brep_list:
            raise AssertionError("Expected at least one Brep in result. Got zero or None.")
        return brep_list[0]


class PartGeometry(Data):
    """
    Interface for a Part's geometry.
    Abstracts the concrete type of geometry e.g. Brep/Mesh
    """

    def __init__(self):
        super(PartGeometry, self).__init__()

    @abc.abstractproperty
    def FEATURE_CLASS(self):
        """
        Class attribute. Holds the concrete type of Feature which is supported by this type of PartGeometry.

        Returns
        -------
        Type[:class:`~compas.datastructures.assembly.part.Feature`]
        """
        raise NotImplementedError

    @abc.abstractmethod
    def transformed(self, transformation):
        """
        Returns a copy of this geometry, transformed according to the given transformation.
        Parameters
        ----------
        transformation :class:`~compas.geometry.Transformation`
        The transformation object to apply to the copy of this geometry.

        Returns
        -------
        :class:`~compas.datastructures.assembly.part.PartGeometry`
        The transformed geometry

        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_drawable(self):
        """
        Returns a representation of this geometry which can be drawn by an Artist.

        Returns
        -------
        :class:`~compas.data.Data`
        An instance of an object which represents this geometry and can be drawn by one of the currently supported Artists.

        >>> from compas.artists import Artist
        >>> shape = Box()
        >>> geometry = MeshGeometry(shape)
        >>> a = Artist(geometry.get_drawable()).draw()
        """
        raise NotImplementedError


class MeshGeometry(PartGeometry):
    """
    Mesh/Shape based Part geometry
    """

    FEATURE_CLASS = MeshFeature

    def __init__(self, geometry):
        super(MeshGeometry, self).__init__()
        self.geometry = geometry

    def transformed(self, transformation):
        transformed_copy = copy.deepcopy(self)
        transformed_copy.geometry.transform(transformation)
        return transformed_copy

    def to_vertices_and_faces(self, triangulated=False):
        return self.geometry.to_vertices_and_faces(triangulated)

    def get_drawable(self):
        """
        Returns
        -------

        """
        return self.geometry

    @property
    def data(self):
        return {"geometry": self.geometry}

    @data.setter
    def data(self, value):
        self.geometry = value["geometry"]


class BrepGeometry(PartGeometry):
    """
    Brap based Part geometry.
    """

    FEATURE_CLASS = BrepFeature

    def __init__(self, brep):
        super(BrepGeometry, self).__init__()
        self.geometry = brep

    @property
    def data(self):
        return {"geometry": self.geometry}

    @data.setter
    def data(self, value):
        self.geometry = value["geometry"]

    def transformed(self, transformation):
        transformed_copy = copy.deepcopy(self)
        transformed_copy.geometry.Transform(xform_to_rhino(transformation))
        return transformed_copy

    def get_drawable(self):
        return self.geometry


class Part(Datastructure):
    """A data structure for representing assembly parts.

    Parameters
    ----------
    name : str, optional
        The name of the part.
        The name will be stored in :attr:`Part.attributes`.
    frame : :class:`~compas.geometry.Frame`, optional
        The local coordinate system of the part.
    shape : :class:`~compas.geometry.Shape`, optional
        The base shape of the part geometry.
    features : sequence[tuple[:class:`~compas.geometry.Shape`, str]], optional
        The features to be added to the base shape of the part geometry.

    Attributes
    ----------
    attributes : dict[str, Any]
        General data structure attributes that will be included in the data dict and serialization.
    key : int or str
        The identifier of the part in the connectivity graph of the parent assembly.
    frame : :class:`~compas.geometry.Frame`
        The local coordinate system of the part.
    shape : :class:`~compas.geometry.Shape`
        The base shape of the part geometry.
    features : list[tuple[:class:`~compas.geometry.Shape`, str]]
        The features added to the base shape of the part geometry.
    transformations : Deque[:class:`~compas.geometry.Transformation`]
        The stack of transformations applied to the part geometry.
        The most recent transformation is on the left of the stack.
        All transformations are with respect to the local coordinate system.
    geometry : :class:`~compas.geometry.Polyhedron`, read-only
        A copy of the part's geometry, including applied features, transformed to part.frame.

    Class Attributes
    ----------------
    operations : dict[str, callable]
        Available operations for combining features with a base shape.

    """

    def __init__(self, name=None, frame=None, geometry=None, features=None, **kwargs):
        super(Part, self).__init__()
        self.attributes = {"name": name or "Part"}
        self.attributes.update(kwargs)
        self.key = None
        self.frame = frame or Frame.worldXY()
        self.features = features or []
        self.transformations = deque()  # TODO: why is it necessary to queue all transformations?

        self._original_shape = geometry or MeshGeometry(geometry=Polyhedron([], []))  # always in Frame.worldXY
        self._part_geometry = copy.deepcopy(self._original_shape)  # always in Frame.worldXY, w/ features applied

    @property
    def DATASCHEMA(self):
        import schema

        return schema.Schema(
            {
                "attributes": dict,
                "key": int,
                "frame": Frame,
                "geometry": PartGeometry,
                "features": list,
                "transformations": list,
            }
        )

    @property
    def JSONSCHEMANAME(self):
        return "part"

    @property
    def data(self):
        data = {
            "attributes": self.attributes,
            "key": self.key,
            "frame": self.frame,
            "shape": self._original_shape,
            "features": [f.data for f in self.features],
            "transformations": [T.data for T in self.transformations],
        }
        return data

    @data.setter
    def data(self, data):
        self.attributes.update(data["attributes"] or {})
        self.key = data["key"]
        self.frame = data["frame"]
        self._original_shape = data["shape"]
        self.features = [self.add_feature(shape, operation) for shape, operation in data["features"]]
        self.transformations = deque([Transformation.from_data(T) for T in data["transformations"]])

    @property
    def name(self):
        return self.attributes.get("name") or self.__class__.__name__

    @name.setter
    def name(self, value):
        self.attributes["name"] = value

    @property
    def shape(self):
        return getattr(self._original_shape, "shape", None)

    @property
    def geometry(self):
        """
        Returns a transformed copy of the part's geometry with features applied, if any.

        The returned type can be drawn with an Artist.
        Returns
        -------

        """
        transformed_geometry = self._part_geometry.transformed(Transformation.from_frame_to_frame(Frame.worldXY(), self.frame))
        return transformed_geometry.get_drawable()

    def __str__(self):
        tpl = "<Part with shape {} and features {}>"
        return tpl.format(self.shape, self.features)

    def transform(self, T):
        """Transform the part with respect to the local cooordinate system.

        Parameters
        ----------
        T : :class:`~compas.geometry.Transformation`

        Returns
        -------
        None

        """
        self.transformations.appendleft(T)
        self.shape.transform(T)
        for feature in self.features:
            feature.transform(T)

    def clear_features(self, features_to_clear=None):
        if not features_to_clear:
            self._restore_original_geometry()
            self.features = []
        else:
            earliest_feature_index = self._restore_earliest_feature_in_list(features_to_clear)
            self.features = [f for f in self.features if f not in features_to_clear]
            self._replay_features(from_index=earliest_feature_index)

    def _restore_earliest_feature_in_list(self, features_to_restore):
        for index, feature in enumerate(self.features):
            if feature in features_to_restore:
                feature.restore()
                return index

        raise AssertionError("Part does not contain the requested feature!")

    def add_feature(self, geometry, operation):
        """Add a feature to the shape of the part and the operation through which it should be integrated.

        Parameters
        ----------
        shape : :class:`~compas.geometry.Shape`
            The shape of the feature.
        operation : Literal['union', 'difference', 'intersection']
            The boolean operation through which the feature should be integrated in the base shape.

        Returns
        -------
        :class: `~compas.datastructures.assembly.part.Feature`
        Returns the instance of the created feature to allow the creator to
        keep track of the features it has created (and "own" them)

        """
        class_ = geometry.FEATURE_CLASS

        # unload_modules can make it difficult comparying types by identity
        if class_.__name__ != self._part_geometry.FEATURE_CLASS.__name__:
            raise TypeError("Cannot mix Brep geometry with mesh operations or vice versa.")

        feature = class_(geometry, operation)
        self.features.append(feature)
        feature.apply(self)
        return feature

    def replay_all_features(self):
        if not self.features:
            raise AssertionError("No features to replay!")
        self._replay_features(from_index=0)

    def _replay_features(self, from_index):
        for feature in self.features[from_index:]:
            feature.apply(part=self)

    def _restore_original_geometry(self):
        self._part_geometry = copy.deepcopy(self._original_shape)

    # def apply_transformations(self):
    #     """Apply all transformations to the part shape."""
    #     X = Transformation.from_frame(self.frame)
    #     transformations = self.transformations[:]
    #     transformations.append(X)
    #     T = reduce(multiply_matrices, transformations)
    #     self.shape.transform(T)

    def to_mesh(self, cls=None):
        """Convert the part geometry to a mesh.

        Parameters
        ----------
        cls : :class:`~compas.datastructures.Mesh`, optional
            The type of mesh to be used for the conversion.

        Returns
        -------
        :class:`~compas.datastructures.Mesh`
            The resulting mesh.

        """
        cls = cls or Mesh
        return cls.from_shape(self.geometry)
