"""
File containing methods that can be used to find shortest paths inside a board.
"""

from queue import PriorityQueue
from typing import Callable, Tuple, Dict, List, Optional, Any

from .board import Tile, TileIdentifier

__author__ = 'Anthony Rouneau'


Cost = int


class UnreachableDestination(Exception):
    """
    Exception raised when the destination tile is not found in the exploration, and thus unreachable
    """
    pass


# -------------------- PUBLIC METHODS -------------------- #

def get_shortest_path(source_tile_id, dest_tile_id, get_tile_by_id_func: Callable[[Any, TileIdentifier], Tile],
                      get_tile_neighbours_func: Callable[[Any, Tile], List[TileIdentifier]],
                      walkable_tile_func: Callable[[Any, Tile], bool]) -> List[TileIdentifier]:
    """
    Uses the A* algorithm to find the shortest path between the source tile and
    the destination tile. This method is designed to be fast

    Args:
        source_tile_id: The identifier of the tile from which the path finding is started
        dest_tile_id: The identifier of the tile to which the path finding ends
        get_tile_by_id_func: function allowing to get the tile located at the given ID
        get_tile_neighbours_func: function allowing to get the IDs of the given tile's neighbours.
        walkable_tile_func:
            A function that take a tile in parameter and that returns True if the given tile can be walked on.

    Returns:
        The shortest path (list of tile_ids) to travel to reach the destination tile from the source tile.
        The cost of this path is equal to the length of this list.
        Returns None if the destination is unreachable
    """

    def heuristic(a: TileIdentifier, b: TileIdentifier):
        if type(a) == type(b) == tuple:
            (x1, y1) = a
            (x2, y2) = b
            return abs(x1 - x2) + abs(y1 - y2)

    came_from, _ = __find_path(dest_tile_id, source_tile_id, get_tile_by_id_func, get_tile_neighbours_func,
                               walkable_tile_func, heuristic, -1)
    return reconstruct_path(came_from, source_tile_id, dest_tile_id)


def get_shortest_paths(source_tile_id: TileIdentifier, max_dist: int,
                       get_tile_by_id_func: Callable[[Any, TileIdentifier], Tile],
                       get_tile_neighbours_func:  Callable[[Any, Tile], List[Tuple]],
                       walkable_tile_function: Callable[[Any, Tile], bool]) \
                                        -> Tuple[Dict[TileIdentifier, TileIdentifier], Dict[TileIdentifier, Cost]]:
    """
    Uses Dijkstra's algorithm to find all the paths available from the given source tile to any other tile
    within the given maximum distance.

    Args:
        source_tile_id: The identifier of the tile from which the path finding is started
        max_dist: The maximum distance allowed between the source and the destination tile (< 0 => no max distance)
        get_tile_by_id_func: function allowing to get the tile located at the given ID
        get_tile_neighbours_func: function allowing to get the IDs of the given tile's neighbours.
        walkable_tile_function:
            A function that take a tile in parameter and that returns True if the given tile can be walked on.

    Returns:
        A tuple containing

        - A dict containing, for a key being a tile identifier, the previous tile in the path to reach that destination
        - The cost to reach that destination tile
    """
    return __find_path(None, source_tile_id, get_tile_by_id_func, get_tile_neighbours_func, walkable_tile_function,
                       None, max_dist)


def reconstruct_path(came_from: Dict[TileIdentifier, TileIdentifier], source_tile_id: TileIdentifier,
                     dest_tile_id: TileIdentifier) -> List[TileIdentifier]:
    """
    Reconstruct the path given the came_from dict, a source tile and a destination tile

    Args:
        came_from:
            Dict containing tiles as key, and giving the previous tile to reach the key tile in the
            shortest path as value
        source_tile_id: The identifier of the source tile
        dest_tile_id: The identifier of the destination tile

    Returns:
        A List containing the identifiers of the tiles in the path, beginning with the source tile and finishing
        with the destination tile

    Raises:
        UnreachableDestination: If the destination is not in the came_from dict, or the path contains unknown tile ids
    """
    try:
        current = came_from[dest_tile_id]
        path = [dest_tile_id]
        while current != source_tile_id:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path
    except KeyError:
        raise UnreachableDestination("The tile " + str(dest_tile_id) +
                                     " is unreachable from the tile " + str(source_tile_id))


# -------------------- PRIVATE METHODS -------------------- #

def __find_path(dest_tile_id: Optional[TileIdentifier], source_tile_id: TileIdentifier,
                get_tile_by_id_func: Callable[[Any, TileIdentifier], Tile],
                get_tile_neighbours_func:  Callable[[Any, Tile], List[TileIdentifier]],
                walkable_tile_function: Callable[[Any, Tile], bool],
                heuristic: Optional[Callable[[TileIdentifier, TileIdentifier], int]], max_dist: int)\
                                -> Tuple[Dict[TileIdentifier, TileIdentifier], Dict[TileIdentifier, Cost]]:
    """
    Args:
        dest_tile_id: The identifier of the destination of the path (can be None if there is no specific destination).
        source_tile_id: The identifier of the tile from which the path will begin.
        get_tile_by_id_func: A callable that, given a tile identifier returns a Tile
        get_tile_neighbours_func: A callable that takes a tile and returns its neighbours
        walkable_tile_function: A callable that returns True if the given tile is walkable, and False otherwise.
        heuristic: A callable that, given two tiles identifier, returns the estimated distance between them.
        max_dist: The maximum distance that can separate the source tile from the farthest destination in the path.

    Returns:
        A tuple containing

        - A dictionary that links a destination with the tile that came before in the path.
        - A dictionary that links a destination with the cost to reach it.

    """
    frontier = PriorityQueue()
    frontier.put(source_tile_id, 0)
    came_from = {}
    cost_so_far = {source_tile_id: 0}
    came_from[source_tile_id] = None
    while not frontier.empty():
        current = frontier.get()

        if dest_tile_id is not None and current == dest_tile_id:
            break
        for next_tile_id in get_tile_neighbours_func(get_tile_by_id_func(current)):
            new_cost = cost_so_far[current] + 1  # Cost just one more because all the cost in the graph == 1
            next_tile = get_tile_by_id_func(next_tile_id)
            if next_tile.walkable and (walkable_tile_function is None or walkable_tile_function(next_tile)) \
                    and (next_tile_id not in cost_so_far or new_cost < cost_so_far[next_tile_id]):
                cost_so_far[next_tile_id] = new_cost
                priority = new_cost
                if heuristic is not None:
                    priority += heuristic(dest_tile_id, next_tile_id)
                if max_dist < 0 or new_cost < max_dist:
                    frontier.put(next_tile_id, priority)
                came_from[next_tile_id] = current
    return came_from, cost_so_far
