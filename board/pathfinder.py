from queue import PriorityQueue

from board.board import Board
from types import FunctionType as function


class UnreachableDestination(Exception):
    pass


def get_shortest_path(board: Board, source_tile_id, dest_tile_id,  walkable_tile_function: function) -> (list, int):
    """
    Uses the A* algorithm to find the shortest path between the source tile and
    the destination tile. This method is designed to be fast

    Args:
        board: The board in which the path finding will be performed
        source_tile_id: The identifier of the tile from which the path finding is started
        dest_tile_id: The identifier of the tile to which the path finding ends
        walkable_tile_function:
            A function that take a tile in parameter and that returns True if the given tile can be walked on.
            By default, only the "walkability" of the tile is tested, which means that a deadly tile is considered in
            the path finding.

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
        # TODO: Handle every other types of identifiers

    frontier = PriorityQueue()
    frontier.put(source_tile_id, 0)
    came_from = {}
    cost_so_far = {source_tile_id: 0}
    came_from[source_tile_id] = None

    while not frontier.empty():
        current = frontier.get()

        if current == dest_tile_id:
            break
        for next_tile_id in board.getTileById(current).neighbours:
            new_cost = cost_so_far[current] + 1  # Cost just one more because all the cost in the graph == 1
            next_tile = board.getTileById(next_tile_id)
            if next_tile.walkable and (walkable_tile_function is None or walkable_tile_function(next_tile)) \
                    and (next_tile_id not in cost_so_far or new_cost < cost_so_far[next_tile_id]):
                cost_so_far[next_tile_id] = new_cost
                priority = new_cost + heuristic(dest_tile_id, next_tile_id)
                frontier.put(next_tile_id, priority)
                came_from[next_tile_id] = current
    return reconstruct_path(came_from, source_tile_id, dest_tile_id)


def get_shortest_paths(board: Board, source_tile_id, max_dist: int, walkable_tile_function: function) -> (dict, list):
    """
    Uses Dijkstra's algorithm to find all the paths available from the given source tile to any other tile
    within the given maximum distance.

    Args:
        board: The board in which the algorithm will search the shortest paths
        source_tile_id: The identifier of the tile from which the path finding is started
        max_dist: The maximum distance allowed between the source and the destination tile (< 0 => no max distance)
        walkable_tile_function:
            A function that take a tile in parameter and that returns True if the given tile can be walked on.
            By default, only the "walkability" of the tile is tested, which means that a deadly tile is considered in
            the path finding.

    Returns:
        A tuple containing:
            - A dict containing, for a key being a tile identifier, the previous tile
            - The cost to reach that destination tile
    """

    frontier = PriorityQueue()
    frontier.put(source_tile_id, 0)
    came_from = {}
    cost_so_far = {source_tile_id: 0}
    came_from[source_tile_id] = None

    while not frontier.empty():
        current = frontier.get()

        for next_tile_id in board.getTileById(current).neighbours:
            new_cost = cost_so_far[current] + 1
            next_tile = board.getTileById(next_tile_id)
            if max_dist < 0 or new_cost <= max_dist:
                if next_tile.walkable and (walkable_tile_function is None or walkable_tile_function(next_tile)) \
                        and (next_tile_id not in cost_so_far or new_cost < cost_so_far[next_tile_id]):
                    cost_so_far[next_tile_id] = new_cost
                    priority = new_cost
                    frontier.put(next_tile_id, priority)
                    came_from[next_tile_id] = current

    return came_from, cost_so_far


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
