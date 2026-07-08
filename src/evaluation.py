"""
evaluation.py

Membandingkan performa Greedy Best First Search dan A* Search
"""

import time

from src.algorithms import SearchAlgorithms


class Evaluator:

    @staticmethod
    def calculate_total_distance(graph, path):
        """
        Menghitung total jarak dari sebuah path.
        """
        if path is None:
            return float("inf")

        total = 0

        for i in range(len(path) - 1):
            total += graph.get_edge_cost(path[i], path[i + 1])

        return round(total, 2)

    @staticmethod
    def compare(graph, start, goal):

        # =====================
        # Greedy
        # =====================
        greedy_start = time.perf_counter()

        greedy_path = SearchAlgorithms.greedy_best_first_search(
            graph,
            start,
            goal
        )

        greedy_time = time.perf_counter() - greedy_start

        greedy_distance = Evaluator.calculate_total_distance(
            graph,
            greedy_path
        )

        # =====================
        # A*
        # =====================
        astar_start = time.perf_counter()

        astar_path = SearchAlgorithms.a_star(
            graph,
            start,
            goal
        )

        astar_time = time.perf_counter() - astar_start

        astar_distance = Evaluator.calculate_total_distance(
            graph,
            astar_path
        )

        return {
            "Greedy": {
                "path": greedy_path,
                "distance": greedy_distance,
                "time": round(greedy_time * 1000, 3)
            },
            "A*": {
                "path": astar_path,
                "distance": astar_distance,
                "time": round(astar_time * 1000, 3)
            }
        }