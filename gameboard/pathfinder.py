from queue import PriorityQueue

from gameboard.board import Board
from types import FunctionType as function


class UnreachableDestination(Exception):
    pass


def get_shortest_path(source_tile_id, dest_tile_id, get_tile_by_id_func: function, get_tile_neighbours_func: function,
                      walkable_tile_func: function) -> (list, int):
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

    def heuristic(a, b):
        if type(a) == type(b) == tuple:
            (x1, y1) = a
            (x2, y2) = b
            return abs(x1 - x2) + abs(y1 - y2)

    came_from, _ = __find_path(dest_tile_id, source_tile_id, get_tile_by_id_func, get_tile_neighbours_func,
                               walkable_tile_func, heuristic, -1)
    return reconstruct_path(came_from, source_tile_id, dest_tile_id)


def get_shortest_paths(source_tile_id, max_dist: int, get_tile_by_id_func: function, get_tile_neighbours_func: function,
                       walkable_tile_function: function) -> (dict, list):
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
        A tuple containing:
            - A dict containing, for a key being a tile identifier, the previous tile
            - The cost to reach that destination tile
    """
    return __find_path(None, source_tile_id, get_tile_by_id_func, get_tile_neighbours_func, walkable_tile_function,
                       None, max_dist)


def reconstruct_path(came_from, source_tile_id, dest_tile_id):
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


def __find_path(dest_tile_id, source_tile_id, get_tile_by_id_func: function, get_tile_neighbours_func: function,
                walkable_tile_function: function, heuristic, max_dist):
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
