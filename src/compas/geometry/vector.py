from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas import PRECISION

from compas.geometry import length_vector
from compas.geometry import cross_vectors
from compas.geometry import subtract_vectors
from compas.geometry import dot_vectors
from compas.geometry import angle_vectors
from compas.geometry import angle_vectors_signed
from compas.geometry import angles_vectors
from compas.geometry import transform_vectors
from compas.geometry import Geometry


class Vector(Geometry):
    """A vector is defined by XYZ components and a homogenisation factor.

    Parameters
    ----------
    x : float
        The X component of the vector.
    y : float
        The Y component of the vector.
    z : float
        The Z component of the vector.

    Attributes
    ----------
    x : float
        The X coordinate of the point.
    y : float
        The Y coordinate of the point.
    z : float
        The Z coordinate of the point.
    length : float, read-only
        The length of this vector.

    Examples
    --------
    >>> u = Vector(1, 0, 0)
    >>> v = Vector(0, 1, 0)
    >>> u
    Vector(1.000, 0.000, 0.000)
    >>> v
    Vector(0.000, 1.000, 0.000)
    >>> u.x
    1.0
    >>> u[0]
    1.0
    >>> u.length
    1.0
    >>> u + v
    Vector(1.000, 1.000, 0.000)
    >>> u + [0.0, 1.0, 0.0]
    Vector(1.000, 1.000, 0.000)
    >>> u * 2
    Vector(2.000, 0.000, 0.000)
    >>> u.dot(v)
    0.0
    >>> u.cross(v)
    Vector(0.000, 0.000, 1.000)

    """

    JSONSCHEMA = {
        "type": "array",
        "minItems": 3,
        "maxItems": 3,
        "items": {"type": "number"},
    }

    __slots__ = ["_x", "_y", "_z"]

    def __init__(self, x, y, z=0.0, **kwargs):
        super(Vector, self).__init__(**kwargs)
        self._x = 0.0
        self._y = 0.0
        self._z = 0.0
        self.x = x
        self.y = y
        self.z = z

    # ==========================================================================
    # data
    # ==========================================================================

    @property
    def data(self):
        """dict : The data dictionary that represents the vector."""
        return list(self)

    @data.setter
    def data(self, data):
        self.x = data[0]
        self.y = data[1]
        self.z = data[2]

    @classmethod
    def from_data(cls, data):
        """Construct a vector from a data dict.

        Parameters
        ----------
        data : dict
            The data dictionary.

        Returns
        -------
        :class:`~compas.geometry.Vector`
            The vector constructed from the provided data.

        Examples
        --------
        >>> Vector.from_data([0.0, 0.0, 1.0])
        Vector(0.000, 0.000, 1.000)
        """
        return cls(*data)

    # ==========================================================================
    # properties
    # ==========================================================================

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        self._x = float(x)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        self._y = float(y)

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, z):
        self._z = float(z)

    @property
    def length(self):
        return length_vector(self)

    # ==========================================================================
    # customization
    # ==========================================================================

    def __repr__(self):
        return "Vector({0:.{3}f}, {1:.{3}f}, {2:.{3}f})".format(self.x, self.y, self.z, PRECISION[:1])

    def __len__(self):
        return 3

    def __getitem__(self, key):
        if isinstance(key, slice):
            return [self[i] for i in range(*key.indices(len(self)))]
        i = key % 3
        if i == 0:
            return self.x
        if i == 1:
            return self.y
        if i == 2:
            return self.z
        raise KeyError

    def __setitem__(self, key, value):
        i = key % 3
        if i == 0:
            self.x = value
            return
        if i == 1:
            self.y = value
            return
        if i == 2:
            self.z = value
            return
        raise KeyError

    def __iter__(self):
        return iter([self.x, self.y, self.z])

    def __eq__(self, other):
        """Is this vector equal to the other vector?

        Two vectors are considered equal if their XYZ components are identical.

        Parameters
        ----------
        other : [float, float, float] | :class:`~compas.geometry.Vector`
            The vector to compare.

        Returns
        -------
        bool
            True if the vectors are equal.
            False otherwise.

        """
        return self.x == other[0] and self.y == other[1] and self.z == other[2]

    def __add__(self, other):
        """Return a vector that is the the sum of this vector and another vector.

        Parameters
        ----------
        other : [float, float, float] | :class:`~compas.geometry.Vector`
            The vector to add.

        Returns
        -------
        :class:`~compas.geometry.Vector`
            The resulting vector.

        """
        return Vector(self.x + other[0], self.y + other[1], self.z + other[2])

    def __sub__(self, other):
        """Return a vector that is the the difference between this vector and another vector.

        Parameters
        ----------
        other : [float, float, float] | :class:`~compas.geometry.Vector`
            The vector to subtract.

        Returns
        -------
        :class:`~compas.geometry.Vector`
            The resulting new vector.

        """
        return Vector(self.x - other[0], self.y - other[1], self.z - other[2])

    def __mul__(self, n):
        """Return a vector that is the scaled version of this vector.

        Parameters
        ----------
        n : float
            The scaling factor.

        Returns
        -------
        :class:`~compas.geometry.Vector`
            The resulting new vector.

        """
        return Vector(self.x * n, self.y * n, self.z * n)

    def __truediv__(self, n):
        """Return a vector that is the scaled version of this vector.

        Parameters
        ----------
        n : float
            The scaling factor.

        Returns
        -------
        :class:`~compas.geometry.Vector`
            The resulting new vector.

        """
        return Vector(self.x / n, self.y / n, self.z / n)

    def __pow__(self, n):
        """Create a vector from the components of the current vector raised
        to the given power.

        Parameters
        ----------
        n : float
            The power.

        Returns
        -------
        :class:`~compas.geometry.Vector`
            A new point with raised coordinates.

        """
        return Vector(self.x**n, self.y**n, self.z**n)

    def __neg__(self):
        return self.scaled(-1.0)

    def __iadd__(self, other):
        """Add the components of the other vector to this vector.

        Parameters
        ----------
        other : [float, float, float] | :class:`~compas.geometry.Vector`
            The vector to add.

        Returns
        -------
        None

        """
        self.x += other[0]
        self.y += other[1]
        self.z += other[2]
        return self

    def __isub__(self, other):
        """Subtract the components of the other vector from this vector.

        Parameters
        ----------
        other : [float, float, float] | :class:`~compas.geometry.Vector`
            The vector to subtract.

        Returns
        -------
        None

        """
        self.x -= other[0]
        self.y -= other[1]
        self.z -= other[2]
        return self

    def __imul__(self, n):
        """Multiply the components of this vector by the given factor.

        Parameters
        ----------
        n : float
            The multiplication factor.

        Returns
        -------
        None

        """
        self.x *= n
        self.y *= n
        self.z *= n
        return self

    def __itruediv__(self, n):
        """Divide the components of this vector by the given factor.

        Parameters
        ----------
        n : float
            The multiplication factor.

        Returns
        -------
        None

        """
        self.x /= n
        self.y /= n
        self.z /= n
        return self

    def __ipow__(self, n):
        """Raise the components of this vector to the given power.

        Parameters
        ----------
        n : float
            The power.

        Returns
        -------
        None

        """
        self.x **= n
        self.y **= n
        self.z **= n
        return self

    # ==========================================================================
    # constructors
    # ==========================================================================

    @classmethod
    def Xaxis(cls):
        """Construct a unit vector along the X axis.

        Returns
        -------
        :class:`~compas.geometry.Vector`
            A vector with components ``x = 1.0, y = 0.0, z = 0.0``.

        Examples
        --------
        >>> Vector.Xaxis()
        Vector(1.000, 0.000, 0.000)

        """
        return cls(1.0, 0.0, 0.0)

    @classmethod
    def Yaxis(cls):
        """Construct a unit vector along the Y axis.

        Returns
        -------
        :class:`~compas.geometry.Vector`
            A vector with components ``x = 0.0, y = 1.0, z = 0.0``.

        Examples
        --------
        >>> Vector.Yaxis()
        Vector(0.000, 1.000, 0.000)

        """
        return cls(0.0, 1.0, 0.0)

    @classmethod
    def Zaxis(cls):
        """Construct a unit vector along the Z axis.

        Returns
        -------
        :class:`~compas.geometry.Vector`
            A vector with components ``x = 0.0, y = 0.0, z = 1.0``.

        Examples
        --------
        >>> Vector.Zaxis()
        Vector(0.000, 0.000, 1.000)

        """
        return cls(0.0, 0.0, 1.0)

    @classmethod
    def from_start_end(cls, start, end):
        """Construct a vector from start and end points.

        Parameters
        ----------
        start : [float, float, float] | :class:`~compas.geometry.Point`
            The start point.
        end : [float, float, float] | :class:`~compas.geometry.Point`
            The end point.

        Returns
        -------
        :class:`~compas.geometry.Vector`
            The vector from start to end.

        Examples
        --------
        >>> Vector.from_start_end([1.0, 0.0, 0.0], [1.0, 1.0, 0.0])
        Vector(0.000, 1.000, 0.000)

        """
        v = subtract_vectors(end, start)
        return cls(*v)

    # ==========================================================================
    # static
    # ==========================================================================

    @staticmethod
    def transform_collection(collection, X):
        """Transform a collection of vector objects.

        Parameters
        ----------
        collection : list[[float, float, float] | :class:`~compas.geometry.Vector`]
            The collection of vectors.

        Returns
        -------
        None

        Examples
        --------
        >>> from compas.geometry import Rotation
        >>> R = Rotation.from_axis_and_angle(Vector.Zaxis(), math.radians(90))
        >>> u = Vector(1.0, 0.0, 0.0)
        >>> vectors = [u]
        >>> Vector.transform_collection(vectors, R)
        >>> v = vectors[0]
        >>> v
        Vector(0.000, 1.000, 0.000)
        >>> u is v
        True

        """
        data = transform_vectors(collection, X)
        for vector, xyz in zip(collection, data):
            vector.x = xyz[0]
            vector.y = xyz[1]
            vector.z = xyz[2]

    @staticmethod
    def transformed_collection(collection, X):
        """Create a collection of transformed vectors.

        Parameters
        ----------
        collection : list[[float, float, float] | :class:`~compas.geometry.Vector`]
            The collection of vectors.

        Returns
        -------
        list[:class:`~compas.geometry.Vector`]
            The transformed vectors.

        Examples
        --------
        >>> from compas.geometry import Rotation
        >>> R = Rotation.from_axis_and_angle(Vector.Zaxis(), math.radians(90))
        >>> u = Vector(1.0, 0.0, 0.0)
        >>> vectors = [u]
        >>> vectors = Vector.transformed_collection(vectors, R)
        >>> v = vectors[0]
        >>> v
        Vector(0.000, 1.000, 0.000)
        >>> u is v
        False

        """
        vectors = [vector.copy() for vector in collection]
        Vector.transform_collection(vectors, X)
        return vectors

    @staticmethod
    def length_vectors(vectors):
        """Compute the length of multiple vectors.

        Parameters
        ----------
        vectors : list[[float, float, float] | :class:`~compas.geometry.Vector`]
            A list of vectors.

        Returns
        -------
        list[float]
            A list of lengths.

        Examples
        --------
        >>> Vector.length_vectors([[1.0, 0.0, 0.0], [2.0, 0.0, 0.0]])
        [1.0, 2.0]

        """
        return [length_vector(vector) for vector in vectors]

    @staticmethod
    def sum_vectors(vectors):
        """Compute the sum of multiple vectors.

        Parameters
        ----------
        vectors : list[[float, float, float] | :class:`~compas.geometry.Vector`]
            A list of vectors.

        Returns
        -------
        :class:`~compas.geometry.Vector`
            A vector that is the sum of the vectors.

        Examples
        --------
        >>> Vector.sum_vectors([[1.0, 0.0, 0.0], [2.0, 0.0, 0.0]])
        Vector(3.000, 0.000, 0.000)

        """
        return Vector(*[sum(axis) for axis in zip(*vectors)])

    @staticmethod
    def dot_vectors(left, right):
        """Compute the dot product of two lists of vectors.

        Parameters
        ----------
        left : list[[float, float, float] | :class:`~compas.geometry.Vector`]
            A list of vectors.
        right : list[[float, float, float] | :class:`~compas.geometry.Vector`]
            A list of vectors.

        Returns
        -------
        list[float]
            A list of dot products.

        Examples
        --------
        >>> Vector.dot_vectors([[1.0, 0.0, 0.0], [2.0, 0.0, 0.0]], [[1.0, 0.0, 0.0], [2.0, 0.0, 0.0]])
        [1.0, 4.0]

        """
        return [Vector.dot(u, v) for u, v in zip(left, right)]

    @staticmethod
    def cross_vectors(left, right):
        """Compute the cross product of two lists of vectors.

        Parameters
        ----------
        left : list[[float, float, float] | :class:`~compas.geometry.Vector`]
            A list of vectors.
        right : list[[float, float, float] | :class:`~compas.geometry.Vector`]
            A list of vectors.

        Returns
        -------
        list[:class:`~compas.geometry.Vector`]
            A list of cross products.

        Examples
        --------
        >>> Vector.cross_vectors([[1.0, 0.0, 0.0], [2.0, 0.0, 0.0]], [[0.0, 1.0, 0.0], [0.0, 0.0, 2.0]])
        [Vector(0.000, 0.000, 1.000), Vector(0.000, -4.000, 0.000)]

        """
        # cross_vectors(u,v) from src\compas\geometry\_core\_algebra.py
        return [Vector(*cross_vectors(u, v)) for u, v in zip(left, right)]

    @staticmethod
    def angles_vectors(left, right):
        """Compute both angles between corresponding pairs of two lists of vectors.

        Parameters
        ----------
        left : list[[float, float, float] | :class:`~compas.geometry.Vector`]
            A list of vectors.
        right : list[[float, float, float] | :class:`~compas.geometry.Vector`]
            A list of vectors.

        Returns
        -------
        list[float]
            A list of angle pairs.

        Examples
        --------
        >>> Vector.angles_vectors([[1.0, 0.0, 0.0], [2.0, 0.0, 0.0]], [[0.0, 1.0, 0.0], [0.0, 0.0, 2.0]])
        [(1.5707963267948966, 4.71238898038469), (1.5707963267948966, 4.71238898038469)]

        """
        return [angles_vectors(u, v) for u, v in zip(left, right)]

    @staticmethod
    def angle_vectors(left, right):
        """Compute the smallest angle between corresponding pairs of two lists of vectors.

        Parameters
        ----------
        left : list[[float, float, float] | :class:`~compas.geometry.Vector`]
            A list of vectors.
        right : list[[float, float, float] | :class:`~compas.geometry.Vector`]
            A list of vectors.

        Returns
        -------
        list[float]
            A list of angles.

        Examples
        --------
        >>> Vector.angle_vectors([[1.0, 0.0, 0.0], [2.0, 0.0, 0.0]], [[0.0, 1.0, 0.0], [0.0, 0.0, 2.0]])
        [1.5707963267948966, 1.5707963267948966]

        """
        return [angle_vectors(u, v) for u, v in zip(left, right)]

    # ==========================================================================
    # helpers
    # ==========================================================================

    def copy(self):
        """Make a copy of this vector.

        Returns
        -------
        :class:`~compas.geometry.Vector`
            The copy.

        Examples
        --------
        >>> u = Vector(0.0, 0.0, 0.0)
        >>> v = u.copy()
        >>> u == v
        True
        >>> u is v
        False

        """
        cls = type(self)
        return cls(self.x, self.y, self.z)

    # ==========================================================================
    # methods
    # ==========================================================================

    def unitize(self):
        """Scale this vector to unit length.

        Returns
        -------
        None

        Examples
        --------
        >>> u = Vector(1.0, 2.0, 3.0)
        >>> u.unitize()
        >>> u.length
        1.0

        """
        length = self.length
        self.x = self.x / length
        self.y = self.y / length
        self.z = self.z / length

    def unitized(self):
        """Returns a unitized copy of this vector.

        Returns
        -------
        :class:`~compas.geometry.Vector`
            A unitized copy of the vector.

        Examples
        --------
        >>> u = Vector(1.0, 2.0, 3.0)
        >>> v = u.unitized()
        >>> u.length == 1.0
        False
        >>> v.length == 1.0
        True

        """
        v = self.copy()
        v.unitize()
        return v

    def invert(self):
        """Invert the direction of this vector

        Returns
        -------
        None

        Notes
        -----
        a negation of a vector is similar to inverting a vector

        Examples
        --------
        >>> u = Vector(1.0, 0.0, 0.0)
        >>> v = u.copy()
        >>> u.invert()
        >>> u == v
        False
        >>> u.invert()
        >>> u == v
        True
        >>> v == --v
        True

        """
        self.scale(-1.0)

    def inverted(self):
        """Returns a inverted copy of this vector

        Returns
        -------
        :class:`~compas.geometry.Vector`

        Examples
        --------
        >>> u = Vector(1.0, 0.0, 0.0)
        >>> v = u.inverted()
        >>> w = u + v
        >>> w.length
        0.0

        """
        return self.scaled(-1.0)

    def scale(self, n):
        """Scale this vector by a factor n.

        Parameters
        ----------
        n : float
            The scaling factor.

        Returns
        -------
        None

        Examples
        --------
        >>> u = Vector(1.0, 0.0, 0.0)
        >>> u.scale(3.0)
        >>> u.length
        3.0

        """
        self.x *= n
        self.y *= n
        self.z *= n

    def scaled(self, n):
        """Returns a scaled copy of this vector.

        Parameters
        ----------
        n : float
            The scaling factor.

        Returns
        -------
        :class:`~compas.geometry.Vector`
            A scaled copy of the vector.

        Examples
        --------
        >>> u = Vector(1.0, 0.0, 0.0)
        >>> v = u.scaled(3.0)
        >>> u.length
        1.0
        >>> v.length
        3.0

        """
        v = self.copy()
        v.scale(n)
        return v

    def dot(self, other):
        """The dot product of this vector and another vector.

        Parameters
        ----------
        other : [float, float, float] | :class:`~compas.geometry.Vector`
            The other vector.

        Returns
        -------
        float
            The dot product.

        Examples
        --------
        >>> u = Vector(1.0, 0.0, 0.0)
        >>> v = Vector(0.0, 1.0, 0.0)
        >>> u.dot(v)
        0.0

        """
        return dot_vectors(self, other)

    def cross(self, other):
        """The cross product of this vector and another vector.

        Parameters
        ----------
        other : [float, float, float] | :class:`~compas.geometry.Vector`
            The other vector.

        Returns
        -------
        :class:`~compas.geometry.Vector`
            The cross product.

        Examples
        --------
        >>> u = Vector(1.0, 0.0, 0.0)
        >>> v = Vector(0.0, 1.0, 0.0)
        >>> u.cross(v)
        Vector(0.000, 0.000, 1.000)

        """
        return Vector(*cross_vectors(self, other))

    def angle(self, other):
        """Compute the smallest angle between this vector and another vector.

        Parameters
        ----------
        other : [float, float, float] | :class:`~compas.geometry.Vector`
            The other vector.

        Returns
        -------
        float
            The smallest angle between the two vectors.

        Examples
        --------
        >>> u = Vector(1.0, 0.0, 0.0)
        >>> v = Vector(0.0, 1.0, 0.0)
        >>> u.angle(v) == 0.5 * math.pi
        True

        """
        return angle_vectors(self, other)

    def angle_signed(self, other, normal):
        """Compute the signed angle between this vector and another vector.

        Parameters
        ----------
        other : [float, float, float] | :class:`~compas.geometry.Vector`
            The other vector.
        normal : [float, float, float] | :class:`~compas.geometry.Vector`
            The plane's normal spanned by this and the other vector.

        Returns
        -------
        float
            The signed angle between the two vectors.

        Examples
        --------
        >>> u = Vector(1.0, 0.0, 0.0)
        >>> v = Vector(0.0, 1.0, 0.0)
        >>> u.angle_signed(v, Vector(0.0, 0.0, 1.0)) == 0.5 * math.pi
        True
        >>> u.angle_signed(v, Vector(0.0, 0.0, -1.0)) == -0.5 * math.pi
        True

        """
        return angle_vectors_signed(self, other, normal)

    def angles(self, other):
        """Compute both angles between this vector and another vector.

        Parameters
        ----------
        other : [float, float, float] | :class:`~compas.geometry.Vector`
            The other vector.

        Returns
        -------
        tuple[float, float]
            The angles between the two vectors, with the smallest angle first.

        Examples
        --------
        >>> u = Vector(1.0, 0.0, 0.0)
        >>> v = Vector(0.0, 1.0, 0.0)
        >>> u.angles(v)[0] == 0.5 * math.pi
        True

        """
        return angles_vectors(self, other)

    def transform(self, T):
        """Transform this vector.

        Parameters
        ----------
        T : :class:`~compas.geometry.Transformation` | list[list[float]]
            The transformation.

        Returns
        -------
        None

        Examples
        --------
        >>> from compas.geometry import Rotation
        >>> u = Vector(1.0, 0.0, 0.0)
        >>> R = Rotation.from_axis_and_angle([0.0, 0.0, 1.0], math.radians(90))
        >>> u.transform(R)
        >>> u
        Vector(0.000, 1.000, 0.000)

        """
        point = transform_vectors([self], T)[0]
        self.x = point[0]
        self.y = point[1]
        self.z = point[2]

    def transformed(self, T):
        """Return a transformed copy of this vector.

        Parameters
        ----------
        T : :class:`~compas.geometry.Transformation` | list[list[float]]
            The transformation.

        Returns
        -------
        :class:`~compas.geometry.Vector`
            The transformed copy.

        Examples
        --------
        >>> from compas.geometry import Rotation
        >>> u = Vector(1.0, 0.0, 0.0)
        >>> R = Rotation.from_axis_and_angle([0.0, 0.0, 1.0], math.radians(90))
        >>> v = u.transformed(R)
        >>> v
        Vector(0.000, 1.000, 0.000)

        """
        vector = self.copy()
        vector.transform(T)
        return vector