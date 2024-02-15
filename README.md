# maze_builder

A maze builder algorithm made in python. I did it based on [this](https://stackoverflow.com/questions/29739751/implementing-a-randomly-generated-maze-using-prims-algorithm/29758926#29758926) stackoverflow post. 

The main logic is in the dig method in the class Maze. Once provided with a list of `frontiers` to explore, the algorithm will dig a maze, walking 2 steps into a random valid direction.

Assumptions:

- A frontier is a cell chosen to explore for its neighbours, digging from it until there are no move moves available.
- The algorithm does not intersect an existing tunnel. It shall continue digging avoiding passage areas.

It works as follows:

1 - Pick a random cell from `frontiers` list to explore (call it `current_cell`)

2 - Check current_cell's valid neighbors. This way, two situations can happen:
    
### Case A : `current_cell` do not have a valid neighbor

3 - remove `current_cell` it from `frontiers` list.

4 - Repeat from 1 until there are no more cells in `frontiers` to explore.

### Case B : `current_cell` has valid neighbors

3 - current_cell has valid neighbors, so random pick one and call it `new_cell`.

4 - Mark the new_cell (which is 2 steps away from current cell)

5 - Mark the cell between current_cell and new_cell, creating a passage.

6 - Add new_cell to `frontiers` list (so it shall be explored again in the future).
Repeat from 1 until there are no more frontiers to explore.

## Notes

- The algorithm logic avoids creating open rooms.  
- Cells are marked as a passage before adding them to frontiers list.
- So each time a new frontier is selected to explore the maze, there is no need to paint it again.
- This assures that when looking for a new neighbor, the rejected neighbor cells does not reappears in the frontiers list.
- It is a simple way to avoid adding the same cell to the frontiers list multiple times.
- It also avoids adding cells that are already part of the maze.


