import itertools
import time
import os
import random


class Block:
    def __init__(self, block_type, block_coords):
        """Initializes the Block class variables.

        **Parameters**
        block_type: *string*
            The type of  block  this block is.
        block_coords: *list*
            Coordinates of the block.
        **Returns"
        None
        """
        self.block_type = block_type

        # Coordinates of block centers in expanded grid
        block_cx = 2*block_coords[0] - 1
        block_cy = 2*block_coords[1] - 1

        # What we really want are the block edge centers which are where the
        # lasers will intersect
        self.tec = (block_cx, block_cy - 1)
        self.bec = (block_cx, block_cy + 1)
        self.lec = (block_cx - 1, block_cy)
        self.rec = (block_cx + 1, block_cy)

    def refract(self, l_x, l_y, d_x, d_y, edge, lasers):
        """Adds new laser coordinates when passing through a refract block.

        **Parameters**
        l_x: *int*
            Current laser x coordinates
        l_y: *int*
            The coefficient of the second term of the polynomial.
        d_x: *int*
            The coefficient of the third term of the polynomial.
        d_y: *int*
            The coefficient of the third term of the polynomial.
        edge: **
            Where the lasers will intersect with block
        lasers: *list*
            List of all current/previous laser coordinates
        **Returns"
        l_x: *int*
            New laser x coordinatese
        l_y: *int*
            New laser y coordinates
        d_x: *int*
            Change in x as a result of block.
        d_y: *int*
            Change in y as a result of block.
        lasers: *list*
            List of all current/previous laser coordinates
        """

        # Pass through operation (New laser source)
        lasers.append(tuple([l_x + d_x, l_y + d_y, d_x, d_y]))

        # Reflect operation
        l_x, l_y, d_x, d_y = self.reflect(l_x, l_y, d_x, d_y, edge)

        return l_x, l_y, d_x, d_y, lasers

    def reflect(self, l_x, l_y, d_x, d_y, edge):
        """Adds new laser coordinates when contacting a reflect block.

        **Parameters**
        l_x: *int*
            Current laser x coordinates
        l_y: *int*
            The coefficient of the second term of the polynomial.
        d_x: *int*
            The coefficient of the third term of the polynomial.
        d_y: *int*
            The coefficient of the third term of the polynomial.
        edge: **
            Where the lasers will intersect with block
        **Returns"
        l_x: *int*
            New laser x coordinatese
        l_y: *int*
            New laser y coordinates
        d_x: *int*
            Change in x as a result of block.
        d_y: *int*
            Change in y as a result of block.
        """

        # Top edge :     i) d_x = 1, d_y = 1   --> d_x = 1, d_y = -1
        #               ii) d_x = -1, d_y = 1  --> d_x = -1, d_y = -1

        # Bottom edge :  i) d_x = 1, d_y = -1  --> d_x = 1, d_y = 1
        #               ii) d_x = -1, d_y = -1 --> d_x = -1, d_y = 1

        # Left edge :    i) d_x = 1, d_y = -1  --> d_x = -1, d_y = -1
        #               ii) d_x = 1, d_y = 1   --> d_x = -1, d_y = 1

        # Right edge :   i) d_x = -1, d_y = -1 --> d_x = 1, d_y = -1
        #               ii) d_x = -1, d_y = 1  --> d_x = 1, d_y = 1

        # Reflection of top or bottom edge negate the y direction
        if edge == 'top' or edge == 'bottom':
            d_y = -(d_y)

        # Reflection of left or right edge negate the x direction
        if edge == 'left' or edge == 'right':
            d_x = -(d_x)

        l_x, l_y = l_x + d_x, l_y + d_y

        return l_x, l_y, d_x, d_y

    def opaque(self, l_x, l_y, d_x, d_y):
        """Returns coordinates of laser interesecting with opaque block.

        **Parameters**
        l_x: *int*
            New laser x coordinatese
        l_y: *int*
            New laser y coordinates
        d_x: *int*
            Change in x as a result of block.
        d_y: *int*
            Change in y as a result of block.
        **Returns"
        l_x: *int*
            New laser x coordinatese
        l_y: *int*
            New laser y coordinates
        d_x: *int*
            Change in x as a result of block.
        d_y: *int*
            Change in y as a result of block.
        """
        # We will terminate the ray path in the loop
        pass
        return l_x, l_y, d_x, d_y


class Board():
    def __init__(self):
        """Initializes parameters of the Board Class.

        **Parameters**
        None
        **Returns"
        None
        """

        # Empty board that will be initialized with values read from .bff file
        self.num_reflect = 0
        self.num_refract = 0
        self.num_opaque = 0
        self.num_rows = 0
        self.num_cols = 0
        self.layout = None
        self.solution = None
        self.list_of_block_types = None
        self.lasers = None
        self.sinks = None

    def check_within_bounds(self, l_x, l_y):
        """QChecks if given coordinates are in bounds of grid.

        **Parameters**
        l_x: *int*
            X coordinates of laser end.
        l_y: *int*
            Y coordinate of laser end.
        **Returns"
        *bool*
            True if within bounds, False if not.
        """

        # Check if laser coords is on boundary
        if (l_x < 0 or l_x > self.num_rows*2
           or l_y < 0 or l_y > self.num_cols*2):
            return False
        else:
            return True

    def check_sink_intersection(self, l_x, l_y, sinks, sink_intersections):
        """Checks if the  laser is intersecting a goal point (AKA  "Sink)

        **Parameters**
        l_x: *int*
            X coordinate of laser end.
        l_y: *int*
            Y coordinate of laser end
        sinks: *list*
            List of coordinates of sinks.
        sink_intersections: *list*
            List of booleans for each sink, True if sink is intersected, False
            if not.
        **Returns"
        sink_intersections: *list*
            List of booleans for each sink, True if sink is intersected, False
            if not.
        """

        # If any of the lasers intersect the sinks keep a track
        if (l_x, l_y) in sinks:
            i = sinks.index((l_x, l_y))
            sink_intersections[i] = True

        return sink_intersections
