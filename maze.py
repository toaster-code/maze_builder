""" A maze builder algorithm.

Based on https://stackoverflow.com/questions/29739751/implementing-a-randomly-generated-maze-using-prims-algorithm/29758926#29758926

The main logic is in the dig method in the class Maze.
Once provided with a list of `fronts` to explore, the algorithm will dig a maze in 2 steps movement (avoiding creating open rooms).

Assumptions:
- A frontier is a cell chosen to explore for its neighbours, digging from it until there are no move moves available.
- The algorithm does not intersect an existing tunnel. It shall continue digging avoiding passage areas.

It works as follows:

1 - Pick a random cell from `front` list to explore (call it `current_cell`)
2 - Check current_cell's valid neighbors. This way, two situations can happen:
    A - current_cell has no valid neighbors
    B - current_cell has valid neighbors
Case A:
3 - current_cell has no valid neighbors, so remove it from `frontiers` list.
4 - Repeat from 1 until there are no more frontiers to explore.

Case B:
3 - current_cell has valid neighbors, so random pick one and call it `new_cell`.
4 - Mark the new_cell (which is 2 steps away from current cell)
5 - Mark the cell between current_cell and new_cell, creating a passage.
6 - Add new_cell to the `frontiers` list (so it shall be explored again in the future).
Repeat from 1 until there are no more frontiers to explore.

Notes: Cells are marked as a passage before adding them to frontiers list.
So each time a new frontier is selected to explore the maze, there is no need to paint it again.
This assures that when looking for a new neighbor, the rejected neighbor cells does not reappears in the frontiers list.
It is a simple way to avoid adding the same cell to the frontiers list multiple times.
It also avoids adding cells that are already part of the maze.
"""
import sys
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D, lineMarkers
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, Normalize
import random
from enum import Enum, auto
rng = random.Random()
# rng.seed(55)

# Set the minimum required Python version
MINIMUM_PYTHON_VERSION = (3, 8)
if sys.version_info < MINIMUM_PYTHON_VERSION:
    raise SystemExit(f"This script requires Python {'.'.join([str(i) for i in MINIMUM_PYTHON_VERSION])} or higher.")


class Cell(Enum):
    PASSAGE = auto()
    WALL = auto()
    HARDWALL = auto()
    START = auto()
    END = auto()
    VISITED = auto()
    WORMHOLE_A = auto()
    WORMHOLE_B = auto()
    WORMHOLE_C = auto()
    WORMHOLE_D = auto()
    WORMHOLE_E = auto()
    WORMHOLE_F = auto()

class Wormhole(Enum):
    A = Cell.WORMHOLE_A
    B = Cell.WORMHOLE_B
    C = Cell.WORMHOLE_C
    D = Cell.WORMHOLE_D
    E = Cell.WORMHOLE_E
    F = Cell.WORMHOLE_F

class Maze:
    def __init__(self, width, height, verbose=False, debug_plot=False):
        self.width = width
        self.height = height
        self._grid = self._generate_empty_grid()
        self.verbose = verbose # Set to True to print the dig process
        self.debug_plot = debug_plot # Set to True to plot the maze dig process

    def reset(self):
        """Reset the maze grid."""
        self._grid = self._generate_empty_grid()

    def _generate_empty_grid(self):
        """Generate an empty grid."""
        return [[Cell.WALL for _ in range(self.width)] for _ in range(self.height)]

    def set_cells(self, cells:list, ctype:Cell):
        """Set a cell (or a list of cells) in the maze grid."""
        if len(cells) != 0:
            if self.verbose:
                print(f"Setting {ctype.name} cells: {cells}")
            for x, y in cells:
                self._grid[y][x] = ctype

    def set_range(self, xiyixfyf:tuple, ctype:Cell):
        """Set a range of the maze grid."""
        if len(xiyixfyf) == 4 and xiyixfyf[0] < xiyixfyf[2] and xiyixfyf[1] < xiyixfyf[3]:
            if self.verbose:
                print(f"Setting range {ctype.name} cells: {xiyixfyf}")
            for x in range(xiyixfyf[0], xiyixfyf[2]):
                for y in range(xiyixfyf[1], xiyixfyf[3]):
                    self._grid[y][x] = ctype
        else:
            raise ValueError("Invalid range")

    def is_legal(self, x, y):
        """ Check if the coordinates are within the maze.
        A cell is legal when within 1 cell from the border.
        """
        return (0 < x < self.width - 1) and (0 < y < self.height - 1)

    def is_diggable(self, x, y):
        return self._grid[y][x] in (Cell.WALL,) and (self._grid[y][x] != Cell.HARDWALL)

    def filter_neighbors(self, x, y):
        """Get the valid neighbor cells to the x, y coordinates.

        Valid neighbors are 2 cells away, whithin valid maze area, and are marked as wall.
        Note: This 2 cells away check allows exploring walls. It does not Interconnect tunnels.
        So the maze has only one solution to the end.
        """
        validator = filter(
            lambda xy: self.is_legal(*xy) and self.is_diggable(*xy),
            [(x - 2, y), (x + 2, y), (x, y - 2), (x, y + 2)]
        )
        return list(validator)

    def neighbor(self, x, y):
        return [(x - 2, y), (x + 2, y), (x, y - 2), (x, y + 2)]

    def get_random_cell(self):
        """Get a random cell within the maze.
        This cell depends on the size of the maze, and should be pair.
        """
        return rng.randint(0, (self.width - 1)//2)*2, rng.randint(0, (self.height - 1)//2)*2

    def create_passage(self, p1, p2):
        """ Mark the destination and the cell between p1, p2. They should be spaced by 2 cells.
        It does not mark the current cell.
        """
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        if (dx == 2 and dy == 0) or (dx == -2 and dy == 0) or (dx == 0 and dy == 2) or (dx == 0 and dy == -2):
            x = p1[0] + dx // 2
            y = p1[1] + dy // 2
            self._grid[y][x] = Cell.PASSAGE # Mark the cell between p1, p2 as passage
            self._grid[p2[1]][p2[0]] = Cell.PASSAGE # Mark the destination cell as passage
        else:
            raise ValueError("Invalid path")

    def _draw_border(self):
        """Draw a border around the maze with hardwall."""
        for y in range(self.height):
            self._grid[y][0] = Cell.HARDWALL
            self._grid[y][self.width-1] = Cell.HARDWALL
        for x in range(1,self.width-1):
            self._grid[0][x] = Cell.HARDWALL
            self._grid[self.height-1][x] = Cell.HARDWALL

    def _dig(self, frontiers:list):
        """
        Dig the maze.

        Once provided with a list of fronts to explore. This function will dig the maze.
        A frontier is a new cell to explore for its neighbours.

        The algorithm works as follows:
        1 - Pick a random cell from `front` list to explore (call it `current_cell`)
        2 - Check current_cell's valid neighbors. Two situations can happen:
        2.A - current_cell has no valid neighbors:
            Remove current_cell from `frontiers` list.
        2.B - current_cell has valid neighbors:
            2.B.1 - Random pick one of the neighbors (new_cell).
            2.B.2 - Mark the new_cell and the passage between current_cell and new_cell (creating a passage)
            2.B.3 - Add new_cell to the `frontiers` list
        Repeat until there are no more frontiers to explore.

        Notes: This code assumes that cells are marked as passage before adding them to frontiers list.
        This assures that when looking for a new neighbor, the rejected neighbor cells are not in the frontiers list.
        This is a simple way to avoid adding the same cell to the frontiers list multiple times. It also avoids
        adding cells that are already part of the maze to the frontiers list.
        """
        if not frontiers:
            raise ValueError("No frontiers to explore. Set a start cell to explore the maze.")

        while frontiers: # No frontier cells left to connect to the maze
            picked_index = rng.randint(0, len(frontiers) - 1) # Pick a random frontier cell to explore
            current_cell = frontiers[picked_index] # Get the coordinates of the picked frontier cell
            neighbors = self.filter_neighbors(*current_cell) # Get valid neighbors of the picked frontier cell
            if not neighbors: # If there are no valid neighbors
                frontiers.pop(picked_index) # Remove it from the frontier list
            else:
                new_cell = neighbors[rng.randint(0, len(neighbors) - 1)] # Pick a random neighbor
                xn, yn = new_cell
                if 0 <= xn <= self.width-1 and 0 <= yn <= self.height-1: # check if new_cell coordinates are within the maze
                    self.create_passage(current_cell, new_cell) # Dig a passage between the current cell and the neighbor
                    frontiers += [new_cell] # Add new_cell to the frontier list
                    if self.debug_plot:
                        plt.imshow(self._grid, cmap='gray_r', origin='lower')
                    if self.verbose:
                        print(f"current_cell: {current_cell}; new_cell: {new_cell}; frontiers no: {len(frontiers)}")

    def image(self):
        """Plot the maze."""
        maze_data = self.to_int()
        maze_types = list(set([i for i in self._grid for i in i]))

        # Get the default color cycle
        # default_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

        # Take the first 10 colors from the default color cycle
        custom_colors = {
            Cell.PASSAGE.value :   'white',
            Cell.WALL.value :      'black',
            Cell.HARDWALL.value :  'red',
            Cell.START.value :     'green',
            Cell.END.value :       'blue',
            Cell.VISITED.value :   'yellow',
            Cell.WORMHOLE_A.value :'purple',
            Cell.WORMHOLE_B.value :'cyan',
            Cell.WORMHOLE_C.value :'magenta',
            Cell.WORMHOLE_D.value :'orange',
            Cell.WORMHOLE_E.value :'brown',
            Cell.WORMHOLE_F.value :'pink',
        }

        # Create a normalization function based on the custom values
        norm = Normalize(vmin=min(custom_colors.keys()), vmax=max(custom_colors.keys()))

        # Apply the normalization to your data
        normalized_data = norm(maze_data)

        # Create a custom colormap
        # cmap = LinearSegmentedColormap.from_list('custom_colormap', custom_colors[], N=10)
        cmap = plt.cm.colors.ListedColormap(list(custom_colors.values()))
        # cmap = plt.get_cmap('tab10', num_maze_items)
        plt.figure(figsize=(6, 6))
        plt.imshow(maze_data,
                   origin='lower',
                   cmap=cmap,
                   interpolation='none',
                   vmin=min(custom_colors.keys()),
                   vmax=max(custom_colors.keys())
                   )
        # Create legend based on the Cell enumeration
        legend_elements = [Line2D([0],
                                  [0],
                                  marker="s",
                                  color='none',
                                  markerfacecolor=custom_colors[cell.value],
                                  label=str(cell.name)) for cell in maze_types]

        plt.legend(handles=legend_elements,
                   title='Cell Types',
                   loc='upper left',
                   borderaxespad=0.,
                   bbox_to_anchor=(1.01, 1.0))
        plt.grid(which="major", linestyle=":", linewidth=.4, color='black')
        plt.xticks([i+.5 for i in range(self.width)])
        plt.yticks([i+.5 for i in range(self.height)])
        # hide the ticks
        plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
        plt.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)
        plt.show()

    def to_int(self):
        """Convert the maze to a list of integers."""
        return [[int(cell.value) for cell in row] for row in self._grid]

    def __str__(self):
        return "\n".join(["".join([str(cell.value) for cell in row]) for row in self._grid])

    def build(self, frontiers):
        """Build the maze.

        Frontiers contains the diggin starting points.
        """
        self._dig(frontiers)


def generate_maze(dim,
                  verbose=False,
                  frontiers=[],
                  hardwall_border=True,
                  pre_paint={"start":[],
                             "passage":[],
                             "wall":[],
                             "hardwall":[],
                             "wormhole_a":[],
                             "wormhole_b":[],
                             "wormhole_c":[],
                             "wormhole_d":[],
                             "wormhole_e":[],
                             "wormhole_f":[]},
                  pos_paint={"start":[],
                             "end":[],
                             "passage":[],
                             "wall":[],
                             "hardwall":[],
                             "wormhole_a":[],
                             "wormhole_b":[],
                             "wormhole_c":[],
                             "wormhole_d":[],
                             "wormhole_e":[],
                             "wormhole_f":[]}):
    # Create a new maze instance
    maze = Maze(width=dim[0], height=dim[1], verbose=verbose)

    # Pre-paint cells:
    if len(frontiers)==0: # if no frontiers are provided, use a random cell
        frontiers = [maze.get_random_cell()]

    if pre_paint.get("start", []):
        if maze.verbose:
            print("Pre-painting start cells")
        maze.set_cells(pre_paint.get("start_cells", []), Cell.START)

    if pre_paint.get("end", []):
        if maze.verbose:
            print("Pre-painting end cells")
        maze.set_cells(pre_paint.get("end", []), Cell.END)

    if pre_paint.get("passage", []):
        if maze.verbose:
            print("Pre-painting passage cells")
        maze.set_cells(pre_paint.get("passage", []), Cell.PASSAGE)

    if pre_paint.get("wall", []):
        if maze.verbose:
            print("Pre-painting wall cells")
        maze.set_cells(pre_paint.get("wall", []), Cell.WALL)

    if pre_paint.get("hardwall", []):
        if maze.verbose:
            print("Pre-painting hardwall cells")
        maze.set_cells(pre_paint.get("hardwall", []), Cell.HARDWALL)

    if pre_paint.get("wormhole_a", []):
        if maze.verbose:
            print("Pre-painting wormhole A cells")
        maze.set_cells(pre_paint.get("wormhole_a", []), Cell.WORMHOLE_A)

    if pre_paint.get("wormhole_b", []):
        if maze.verbose:
            print("Pre-painting wormhole B cells")
        maze.set_cells(pre_paint.get("wormhole_b", []), Cell.WORMHOLE_B)

    if pre_paint.get("wormhole_c", []):
        if maze.verbose:
            print("Pre-painting wormhole C cells")
        maze.set_cells(pre_paint.get("wormhole_c", []), Cell.WORMHOLE_C)

    if pre_paint.get("wormhole_d", []):
        if maze.verbose:
            print("Pre-painting wormhole D cells")
        maze.set_cells(pre_paint.get("wormhole_d", []), Cell.WORMHOLE_D)

    if pre_paint.get("wormhole_e", []):
        if maze.verbose:
            print("Pre-painting wormhole E cells")
        maze.set_cells(pre_paint.get("wormhole_e", []), Cell.WORMHOLE_E)

    if pre_paint.get("wormhole_f", []):
        if maze.verbose:
            print("Pre-painting wormhole F cells")
        maze.set_cells(pre_paint.get("wormhole_f", []), Cell.WORMHOLE_F)

    # Add a border around the maze
    if hardwall_border:
        maze._draw_border()

    # Dig the maze
    maze.build(frontiers)

    # Post-paint cells:
    if pos_paint.get("start", []):
        if maze.verbose:
            print("Post-painting start cells")
        maze.set_cells(pos_paint.get("start", []), Cell.START)

    if pos_paint.get("end", []):
        if maze.verbose:
            print("Post-painting end cells")
        maze.set_cells(pos_paint.get("end", []), Cell.END)

    if pos_paint.get("passage", []):
        if maze.verbose:
            print("Post-painting passage cells")
        maze.set_cells(pos_paint.get("passage", []), Cell.PASSAGE)

    if pos_paint.get("wall", []):
        if maze.verbose:
            print("Post-painting wall cells")
        maze.set_cells(pos_paint.get("wall", []), Cell.WALL)

    if pos_paint.get("hardwall", []):
        if maze.verbose:
            print("Post-painting hardwall cells")
        maze.set_cells(pos_paint.get("hardwall", []), Cell.HARDWALL)

    if pos_paint.get("wormhole_a", []):
        if maze.verbose:
            print("Post-painting wormhole A cells")
        maze.set_cells(pos_paint.get("wormhole_a", []), Cell.WORMHOLE_A)

    if pos_paint.get("wormhole_b", []):
        if maze.verbose:
            print("Post-painting wormhole B cells")
        maze.set_cells(pos_paint.get("wormhole_b", []), Cell.WORMHOLE_B)

    if pos_paint.get("wormhole_c", []):
        if maze.verbose:
            print("Post-painting wormhole C cells")
        maze.set_cells(pos_paint.get("wormhole_c", []), Cell.WORMHOLE_C)

    if pos_paint.get("wormhole_d", []):
        if maze.verbose:
            print("Post-painting wormhole D cells")
        maze.set_cells(pos_paint.get("wormhole_d", []), Cell.WORMHOLE_D)

    if pos_paint.get("wormhole_e", []):
        if maze.verbose:
            print("Post-painting wormhole E cells")
        maze.set_cells(pos_paint.get("wormhole_e", []), Cell.WORMHOLE_E)

    if pos_paint.get("wormhole_f", []):
        if maze.verbose:
            print("Post-painting wormhole F cells")
        maze.set_cells(pos_paint.get("wormhole_f", []), Cell.WORMHOLE_F)

    return maze

def create_points(xi, yi, xf, yf):
    """Create a list of points from xi, yi to xf, yf."""
    return [(x, y) for x in range(xi, xf) for y in range(yi, yf)]

if __name__ == "__main__":
    width, height = 47, 41
    pre_paint={
        "hardwall":create_points(0, 0, width, 1) + create_points(0, 0, 1, height) + create_points(0, height-1, width, height) + create_points(width-1, 0, width, height),
        }
    pos_paint={
        "start":[(0,1)],
        "end":[(width-1, 1)],
        "wormhole_a":[(5,2)],
        "wormhole_b":[(39,1)],
        "wormhole_c":[(29,12)],
        "wormhole_d":[(1,9)],
        "wormhole_e":[(15,8)],
        "wormhole_f":[(23,3)]}

    maze = generate_maze(dim=(width, height),
                         frontiers=[(0, 1)],
                         verbose=False,
                         hardwall_border=True,
                         pre_paint=pre_paint,
                         pos_paint=pos_paint)
    maze.image()

