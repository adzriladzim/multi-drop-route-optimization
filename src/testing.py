"""
testing.py

Pengujian sederhana untuk Graph, Greedy, dan A* Search.
"""

from src.graph import Graph
from src.algorithms import SearchAlgorithms
from src.evaluation import Evaluator


def build_sample_graph():
    """
    Membuat graph contoh untuk pengujian.
    """

    graph = Graph()

    # Tambahkan node (x, y)
    graph.add_node("Warehouse", 2, 2)
    graph.add_node("A", 5, 4)
    graph.add_node("B", 6, 8)
    graph.add_node("C", 9, 6)
    graph.add_node("Goal", 11, 9)

    # Tambahkan edge
    graph.add_edge("Warehouse", "A")
    graph.add_edge("Warehouse", "B")
    graph.add_edge("A", "C")
    graph.add_edge("B", "C")
    graph.add_edge("C", "Goal")

    return graph


def test_greedy():
    graph = build_sample_graph()

    path = SearchAlgorithms.greedy_best_first_search(
        graph,
        "Warehouse",
        "Goal"
    )

    print("===== TEST GREEDY =====")
    print(path)
    print()


def test_astar():
    graph = build_sample_graph()

    path = SearchAlgorithms.a_star(
        graph,
        "Warehouse",
        "Goal"
    )

    print("===== TEST A* =====")
    print(path)
    print()


def test_evaluation():
    graph = build_sample_graph()

    result = Evaluator.compare(
        graph,
        "Warehouse",
        "Goal"
    )

    print("===== EVALUATION =====")
    print(result)
    print()


def test_same_start_goal():
    graph = build_sample_graph()

    path = SearchAlgorithms.a_star(
        graph,
        "Warehouse",
        "Warehouse"
    )

    print("===== START = GOAL =====")
    print(path)
    print()


def test_invalid_node():
    graph = build_sample_graph()

    try:

        path = SearchAlgorithms.a_star(
            graph,
            "Warehouse",
            "Z"
        )

        print(path)

    except Exception as e:

        print("===== INVALID NODE =====")
        print(e)
        print()


def main():

    test_greedy()

    test_astar()

    test_evaluation()

    test_same_start_goal()

    test_invalid_node()


if __name__ == "__main__":
    main()