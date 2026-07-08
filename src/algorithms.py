"""
algorithms.py

Implementasi:
1. Greedy Best First Search
2. A* Search
"""

import heapq

from src.heuristic import euclidean


class SearchAlgorithms:

    @staticmethod
    def reconstruct_path(came_from, current):
        """
        Membangun kembali jalur dari goal ke start.
        """
        path = [current]

        while current in came_from:
            current = came_from[current]
            path.append(current)

        path.reverse()
        return path

    @staticmethod
    def greedy_best_first_search(graph, start, goal):

        open_list = []

        heapq.heappush(open_list, (0, start))

        visited = set()

        came_from = {}

        while open_list:

            _, current = heapq.heappop(open_list)

            if current == goal:
                return SearchAlgorithms.reconstruct_path(
                    came_from,
                    current
                )

            if current in visited:
                continue

            visited.add(current)

            for neighbor, _ in graph.get_neighbors(current):

                if neighbor not in visited:

                    priority = euclidean(
                        graph,
                        neighbor,
                        goal
                    )

                    came_from[neighbor] = current

                    heapq.heappush(
                        open_list,
                        (priority, neighbor)
                    )

        return None

    @staticmethod
    def a_star(graph, start, goal):

        open_list = []

        heapq.heappush(open_list, (0, start))

        came_from = {}

        g_score = {
            node: float("inf")
            for node in graph.get_nodes()
        }

        g_score[start] = 0

        while open_list:

            _, current = heapq.heappop(open_list)

            if current == goal:
                return SearchAlgorithms.reconstruct_path(
                    came_from,
                    current
                )

            for neighbor, cost in graph.get_neighbors(current):

                tentative_g = (
                    g_score[current] + cost
                )

                if tentative_g < g_score[neighbor]:

                    came_from[neighbor] = current

                    g_score[neighbor] = tentative_g

                    f_score = (
                        tentative_g
                        + euclidean(
                            graph,
                            neighbor,
                            goal
                        )
                    )

                    heapq.heappush(
                        open_list,
                        (f_score, neighbor)
                    )

        return None