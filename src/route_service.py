from src.algorithms import SearchAlgorithms
from src.evaluation import Evaluator


def optimize_route(graph, start, goal, algorithm="astar"):
    """
    Menjalankan algoritma pencarian rute.
    """

    if algorithm == "astar":
        path = SearchAlgorithms.a_star(graph, start, goal)

    elif algorithm == "greedy":
        path = SearchAlgorithms.greedy_best_first_search(
            graph,
            start,
            goal
        )

    else:
        raise ValueError("Algoritma tidak dikenali.")

    distance = Evaluator.calculate_total_distance(graph, path)

    return {
        "path": path,
        "distance": distance
    }