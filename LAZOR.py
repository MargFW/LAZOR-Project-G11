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

    def check_block_intersection(self, l_x, l_y, list_of_blocks):
        """Check_block_intersection checks if the laser touches the block.

        **Parameters**
        l_x: *int*
            X coordinate of laser end
        l_y *int*
            Y coordinate of laser end.
        list_of_blocks: *list*
            List of all blocks on grids' sides
        **Returns"
        intersected_blocks[0]: *_main_.Block*
            Block that has been intersected with laser
        intersected_block_edges[0]: *string*
            Edge that has been intersected with laser.
        two_block_intersection: *bool*
            True if blocks are intersected, False if not.
        """

        # If laser intersects any of the block edges note the the edge/type
        intersected_block_edges = []
        intersected_blocks = []
        for block in list_of_blocks:
            list_of_block_edge_centers = [block.tec,
                                          block.bec,
                                          block.lec,
                                          block.rec]
            if (l_x, l_y) in list_of_block_edge_centers:
                index = list_of_block_edge_centers.index((l_x, l_y))
                if index == 0:
                    intersected_block_edges.append('top')
                elif index == 1:
                    intersected_block_edges.append('bottom')
                elif index == 2:
                    intersected_block_edges.append('left')
                else:
                    intersected_block_edges.append('right')
                intersected_blocks.append(block)

        if len(intersected_blocks) > 1:
            two_block_intersection = True
            return None, None, two_block_intersection
        elif len(intersected_blocks) == 1:
            two_block_intersection = False
            return intersected_blocks[0], intersected_block_edges[0],\
                two_block_intersection
        else:
            two_block_intersection = False
            return None, None, False

    def generate_board_permutations(self, shuffle, shuffle_seed):
        """generate_board_permutations gives the amount of possible different
           configurations of the board.

        **Parameters**
        shuffle: *bool*
            Allows permuations to be shuffled.
        shuffle_seed: *int*
            Used to initialize a random number generator.
        **Returns"
        board_permutations: *list*
            Number of board permuations
        list_of_fixed_blocks: *list*
            List of blocks that are fixed.
        """

        # Get list of all open positions
        open_board_positions = []
        list_of_fixed_blocks = []
        for i, row in enumerate(self.layout):
            for j, col in enumerate(row):

                # Get the open cooridnates which we will use to generate
                # permutation pairs and assign to blocks
                if col == 'o':
                    # Store coords in format specified (x, y) == (col, row)
                    open_board_positions.append((j+1, i+1))

                # Get the coordinates of the fixed reflector block
                if col == 'A':
                    list_of_fixed_blocks.append(Block('reflect', (j+1, i+1)))

                # Get the coordinates of the fixed opaque block
                if col == 'B':
                    list_of_fixed_blocks.append(Block('opaque', (j+1, i+1)))

                # Get the cooridnates of the fixed refractor block
                if col == 'C':
                    list_of_fixed_blocks.append(Block('refract', (j+1, i+1)))

        print(f' --> Open board positions : {open_board_positions}')

        # Get all available block positions
        self.list_of_block_types = (['refract']*self.num_refract
                                    + ['reflect']*self.num_reflect
                                    + ['opaque']*self.num_opaque)
        print(f' --> Available blocks : {self.list_of_block_types}')

        # Get all possible open block configurations for number of blocks
        start = time.process_time()
        board_permutations =\
            list(itertools.permutations(open_board_positions,
                                        len(self.list_of_block_types)))
        if shuffle:
            random.Random(shuffle_seed).shuffle(board_permutations)
        print(f' --> Total number of board permutations : \
              {len(board_permutations)}')
        print(f' --> Time elapsed to generate board positions :\
              {time.process_time() - start}')

        return board_permutations, list_of_fixed_blocks

    def solve_board(self,
                    board_permutations,
                    list_of_fixed_blocks, di, debug_mode=False):
        """solve_board solves the layout and creates a solution

        **Parameters**
        board_permutations: *list*
            List of possibel arrangements of board
        list_of_fixed_blocks: *list*
            List of fixed blocks on board.
        di: *int*
            Every di iterations, we check runtime an current iteration.
        debug_mode: *bool*
            Set to False, meaning the funciton is not in debug mode. (Made for
            testing)
        **Returns"
        None
        """

        # Iterate through each possible board configuration.
        store_times = []
        for iteration, board_permutation in enumerate(board_permutations):

            if debug_mode:
                print(board_permutation)
                print(board.list_of_block_types)

            # Add the fixed blocks to the list
            list_of_blocks = [Block(block_type, board_permutation[i])
                              for i, block_type in
                              enumerate(self.list_of_block_types)]\
                + list_of_fixed_blocks

            # Start clock to check computation time/ board permutation
            start = time.process_time()

            # Reset for next board permutation
            sink_intersections = [False]*len(self.sinks)
            # Make it into a list so we can append new lasers
            lasers = list(self.lasers)

            for laser in lasers:

                # Convert laser to a list
                laser = list(laser)
                if debug_mode:
                    print(f'All lasers : {lasers}')

                # A very crude way to handle infinity loops created by blocks
                iter_counter = 0

                while True:

                    # Apply step by either a block operation or by adding step
                    # in direction of laser
                    block, edge, two_block_intersection \
                        = self.check_block_intersection(laser[0],
                                                        laser[1],
                                                        list_of_blocks)

                    if two_block_intersection:
                        break

                    if block:
                        # Check if laser is pointing towards or away from block
                        if edge == 'right' and laser[2] == -1:
                            towards_edge = True
                        elif edge == 'left' and laser[2] == 1:
                            towards_edge = True
                        elif edge == 'top' and laser[3] == 1:
                            towards_edge = True
                        elif edge == 'bottom' and laser[3] == -1:
                            towards_edge = True
                        else:
                            towards_edge = False

                        if block.block_type == 'refract':
                            if towards_edge:
                                laser[0], laser[1], laser[2], laser[3], \
                                    lasers = block.refract(laser[0],
                                                           laser[1],
                                                           laser[2],
                                                           laser[3],
                                                           edge,
                                                           lasers)
                            else:
                                laser[0], \
                                    laser[1] = laser[0] + laser[2], \
                                    laser[1] + laser[3]
                        elif block.block_type == 'reflect':
                            if towards_edge:
                                laser[0], laser[1], laser[2], \
                                    laser[3] = block.reflect(laser[0],
                                                             laser[1],
                                                             laser[2],
                                                             laser[3], edge)
                            else:
                                laser[0], laser[1] = laser[0] + laser[2], \
                                    laser[1] + laser[3]
                        else:
                            if towards_edge:
                                laser[0], laser[1], laser[2], laser[3] =\
                                    block.opaque(laser[0], laser[1], laser[2],
                                                 laser[3])
                                # After applying step check for sink
                                # intersection and break loop
                                sink_intersections = \
                                    self.\
                                    check_sink_intersection(laser[0],
                                                            laser[1],
                                                            self.sinks,
                                                            sink_intersections)
                                break
                            else:
                                laser[0], \
                                    laser[1] = laser[0] + laser[2],\
                                    laser[1] + laser[3]
                    else:
                        laser[0],\
                            laser[1] = laser[0] + laser[2], laser[1] + laser[3]

                    if debug_mode:
                        print(f'Laser step :\
                              {[laser[0], laser[1], laser[2], laser[3]]}')

                    # After applying step check if laser is still within bounds
                    # else go to next laser in stack
                    if self.check_within_bounds(laser[0], laser[1]) is False:
                        break

                    # After applying step check for sink intersection
                    sink_intersections = \
                        self.check_sink_intersection(laser[0],
                                                     laser[1],
                                                     self.sinks,
                                                     sink_intersections)

                    # If with given lasers all sinks are intersected no need to
                    # check for other lasers
                    if all(sink_intersections) is True:
                        break

                    iter_counter += 1

                    if iter_counter == 50:
                        # In an infinity loop created by blocks
                        break

            store_times.append(time.process_time() - start)

            if debug_mode:
                print(f'Iteration : {iteration}')

            if iteration % di == 0:
                print(f' --> Current iteration {iteration}')
                print(f' --> Avg time per board computation : \
                      {sum(store_times)/len(store_times)}')
                store_times = []

            # Check if all sinks have been intersected
            if all(sink_intersections) is True:
                print(f' --> Iteration number {iteration}')
                print(' --> All sinks intersected')
                print(f' --> Board solution : Place \
                      {self.list_of_block_types} @ {board_permutation}')
                print(f' --> % search space explored : \
                      {round(iteration/len(board_permutations)*100,3)}')
                self.solution = board_permutation
                break
            else:
                lasers = []
                continue


def read_bff(filename, board):
    """read_bff reads the input bff.

    **Parameters**
    filename: *string*
        The name of the bff file and input level.
    board: *_main_.Board*
        A blank board to put the input layout onto.
    **Returns"
    None
    """

    with open(filename, 'r') as file:

        # Get all the lines in the file
        lines = file.readlines()

    line_num = 0
    # Iterate until you reach end of lines
    while True:

        # Strip the '\n' from end of line
        line = lines[line_num].strip("\n")

        # Blank line do nothing
        if line == '':
            line_num += 1
            continue

        # Start reading the board
        elif line == 'GRID START':
            board_layout = []
            while True:
                line_num += 1
                line_entry = lines[line_num].strip('\n')
                if line_entry == 'GRID STOP':
                    line_num += 1
                    board.num_cols = len(board_layout)
                    board.num_rows = len(board_layout[0])
                    board.layout = board_layout
                    break
                # Using list comprehension to get board positions as a list
                board_row = [pos for pos in line_entry.split(' ') if pos]
                board_layout.append(board_row)
            continue

        # Get the number reflectors
        elif line.split(' ')[0] == 'A':
            line_num += 1
            board.num_reflect = int(line.split(' ')[1])
            continue

        # Get the number of opqaue blocks
        elif line.split(' ')[0] == 'B':
            line_num += 1
            board.num_opaque = int(line.split(' ')[1])
            continue

        # Get the number of refractor blocks
        elif line.split(' ')[0] == 'C':
            line_num += 1
            board.num_refract = int(line.split(' ')[1])
            continue

        # Get number of laser sources and their coordinates
        elif line.split(' ')[0] == 'L':
            num_lasers = 0
            laser_coords = []
            while True:
                laser_line = lines[line_num].strip('\n')
                if laser_line == '':
                    line_num += 1
                    continue
                elif laser_line.split(' ')[0] == 'L':
                    num_lasers += 1
                    line_num += 1
                    coords = tuple([int(coord) for coord in
                                    laser_line.split(' ')[1:]])
                    laser_coords.append(coords)
                else:
                    board.lasers = tuple(laser_coords)
                    break
            continue

        # Get number of sinks and their coordinates
        elif line.split(' ')[0] == 'P':
            num_sinks = 0
            sink_coords = []
            while (line_num) < len(lines):
                sink_line = lines[line_num].strip('\n')
                if sink_line == '':
                    line_num += 1
                    continue
                else:
                    num_sinks += 1
                    line_num += 1
                    coords = tuple([int(coord)
                                    for coord in sink_line.split(' ')[1:]])
                    sink_coords.append(coords)
            board.sinks = tuple(sink_coords)
            break

        # For any other line
        else:
            line_num += 1
            continue


if __name__ == '__main__':

    # First Initialize an empty board
    board = Board()
    filename = 'bffs/mad_1.bff'
    boardname = 'mad_1'
    shuffle = True
    shuffle_seed = 1001

    # Read the bff
    read_bff(filename, board)

    board_permutations, list_of_fixed_blocks = \
        board.generate_board_permutations(shuffle, shuffle_seed)
    board.solve_board(board_permutations,
                      list_of_fixed_blocks,
                      int(len(board_permutations)*0.1),
                      False)

    # If solution is obtained write it to a directory
    if board.solution is not None:
        if os.path.exists('solutions'):
            os.mkdir('solutions/'+boardname)
            with open('solutions/'+boardname+'/'+boardname+'.txt', 'w') \
                 as file:
                file.write(f' --> Board solution : \
                           Place {board.list_of_block_types} \
                               @ {board.solution}')
        else:
            # Make directory solutions
            os.mkdir('solutions')
            os.mkdir('solutions/'+boardname)
            with open('solutions/'+boardname+'/'+boardname+'.txt', 'w') \
                 as file:
                file.write(f' --> Board solution : \
                           Place {board.list_of_block_types} \
                               @ {board.solution}')
    else:
        print(' --> No solution obtained')
