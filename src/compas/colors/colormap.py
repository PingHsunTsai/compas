from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from compas.utilities import linspace

from .color import Color
from .mpl_colormap import _magma_data
from .mpl_colormap import _inferno_data
from .mpl_colormap import _plasma_data
from .mpl_colormap import _viridis_data

mpl = {
    'magma': _magma_data,
    'inferno': _inferno_data,
    'plasma': _plasma_data,
    'viridis': _viridis_data
}


class ColorMap(object):
    """Class providing a map for colors of a specific color palette.

    Parameters
    ----------
    colors : sequence[tuple[float, float, float]]
        A sequence of colors forming the map.

    Attributes
    ----------
    colors : list[:class:`compas.colors.Color`]
        The colors of the map.

    Examples
    --------
    >>> cmap = ColorMap.from_palette('bamako')
    >>> for i in range(100):
    ...     color = cmap[random.random()]
    ...

    >>> cmap = ColorMap.from_mpl('viridis')
    >>> n = 100
    >>> for i in range(n):
    ...     color = cmap.get(i, 0, n - 1)
    ...

    >>> cmap = ColorMap.from_color(Color.red(), rangetype='light')
    >>> cmap.plot()

    """

    def __init__(self, colors):
        self._colors = None
        self.colors = colors

    # --------------------------------------------------------------------------
    # properties
    # --------------------------------------------------------------------------

    @property
    def colors(self):
        return self._colors

    @colors.setter
    def colors(self, colors):
        self._colors = [Color(r, g, b) for r, g, b in colors]

    # --------------------------------------------------------------------------
    # customization
    # --------------------------------------------------------------------------

    def __getitem__(self, key):
        if key > 1.0 or key < 0.0:
            raise KeyError('The key value must be in the range 0-1.')
        # this currently just computes the closest index to the key
        # more accurate would be to compute an interpolation
        # but perhaps that is not necessary
        index = int(key * (len(self.colors) - 1))
        return self.colors[index]

    # --------------------------------------------------------------------------
    # constructors
    # --------------------------------------------------------------------------

    @classmethod
    def from_palette(cls, name):
        """Construct a color map from a named palette.

        Parameters
        ----------
        name : str
            The name of the palette.

        Returns
        -------
        :class:`compas.colors.ColorMap`

        Raises
        ------
        FileNotFoundError
            If the file containing the colors of the palette doesn't exist.

        Notes
        -----
        The colormaps use the colors of the palettes available here https://www.fabiocrameri.ch/colourmaps/
        and the python package https://pypi.org/project/cmcrameri/.
        See `compas/colors/cmcrameri/LICENSE` for more info.

        """
        here = os.path.dirname(__file__)
        path = os.path.join(here, 'cmcrameri', '{}.txt'.format(name))
        colors = []
        with open(path, 'r') as f:
            for line in f:
                if line:
                    parts = line.split()
                    if len(parts) == 3:
                        r = float(parts[0])
                        g = float(parts[1])
                        b = float(parts[2])
                        colors.append((r, g, b))
        cmap = cls(colors)
        return cmap

    @classmethod
    def from_mpl(cls, name):
        """Construct a color map from matplotlib.

        Parameters
        ----------
        name : {'magma', 'inferno', 'plasma', 'viridis'}
            The name of the mpl colormap.

        Returns
        -------
        :class:`compas.colors.ColorMap`

        Raises
        ------
        KeyError
            If the color is not available.

        Notes
        -----
        The palettes available through this function are from https://github.com/BIDS/colormap,
        but with the dependency on `matplotlib` removed to ensure compatibility with RhinoGH.
        See `compas/colors/mpl_colormap.py` for more info and license information.

        """
        colors = [Color(r, g, b) for r, g, b in mpl[name]]
        return cls(colors)

    @classmethod
    def from_color(cls, color, rangetype='full'):
        """Construct a color map from a single color by varying luminance.

        Parameters
        ----------
        color : :class:`compas.colors.Color`
            The base color.
        rangetype : {'full', 'light', 'dark'}, optional
            If ``'full'``, use the full luminance range (0.0 - 1.0).
            If ``'light'``, use only the "light" part of the luminance range (0.5 - 1.0).
            If ``'dark'``, use only the "dark" part of the luminance range (0.0 - 0.5).

        Returns
        -------
        :class:`compas.colors.Color`

        """
        n = 256
        h, _, s = color.hls

        if rangetype == 'full':
            step = 1.0 / (n - 1)
            colors = [Color.from_hls(h, 0.0 + i * step, s) for i in range(n)]
            return cls(colors)

        if rangetype == 'light':
            step = 0.5 / (n - 1)
            colors = [Color.from_hls(h, 0.5 + i * step, s) for i in range(n)]
            return cls(colors)

        if rangetype == 'dark':
            step = 0.5 / (n - 1)
            colors = [Color.from_hls(h, 0.0 + i * step, s) for i in range(n)]
            return cls(colors)

        raise ValueError("`rangetype` should be one of 'full', 'light', 'dark'.")

    @classmethod
    def from_two_colors(cls, color1, color2):
        dr = (color2[0] - color1[0]) / 255
        dg = (color2[1] - color1[1]) / 255
        db = (color2[2] - color1[2]) / 255
        colors = []
        for i in linspace(0, 255, 256):
            r = color1[0] + i * dr
            g = color1[1] + i * dg
            b = color1[2] + i * db
            color = Color(r, g, b)
            colors.append(color)
        return cls(colors)

    # --------------------------------------------------------------------------
    # methods
    # --------------------------------------------------------------------------

    def get(self, value, minval=0.0, maxval=1.0):
        """Returns the color in the map corresponding to the given value.

        Parameters
        ----------
        value : float
            The data value for which a color should be computed.
        minval : float, optional
            The minimum value of the data range.
        maxval : float, optional
            The maximum value of the data range.

        Returns
        -------
        :class:`compas.colors.Color`

        Notes
        -----
        This is the same as :meth:`__getitem__` but with additional options.

        """
        key = (value - minval) / (maxval - minval)
        return self[key]

    def plot(self):
        """Visualize the current map with the plotter.

        Returns
        -------
        None

        """
        from compas_plotters.plotter import Plotter
        from compas.geometry import Pointcloud
        from compas.geometry import Plane, Circle, Polygon
        plotter = Plotter()
        w = 8
        h = 5
        n = len(self.colors)
        d = 8 / n
        cloud = Pointcloud.from_bounds(w, h, 0, n)
        white = Color.white()
        for i, color in enumerate(self.colors):
            c = Circle(Plane(cloud[i], [0, 0, 1]), 0.1)
            p = Polygon([[i * d, -2, 0], [(i + 1) * d, -2, 0], [(i + 1) * d, -1, 0], [i * d, -1, 0]])
            plotter.add(c, facecolor=color, edgecolor=white, linewidth=0.5)
            plotter.add(p, facecolor=color, edgecolor=color)
        plotter.zoom_extents()
        plotter.show()


mpl_magma = ColorMap.from_mpl('magma')
mpl_inferno = ColorMap.from_mpl('inferno')
mpl_plasma = ColorMap.from_mpl('plasma')
mpl_viridis = ColorMap.from_mpl('viridis')
