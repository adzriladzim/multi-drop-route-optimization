"""
heuristic.py
Berisi fungsi heuristic Euclidean untuk algoritma A*
"""

import math


def euclidean(graph, current_node, goal_node):
    """
    Menghitung heuristic Euclidean antara current_node dan goal_node

    Parameter
    ---------
    graph : Graph
        Object graph yang menyimpan koordinat node
    current_node : str
        Node saat ini
    goal_node : str
        Node tujuan

    Return
    ------
    float
        Estimasi jarak Euclidean
    """

    x1, y1 = graph.get_position(current_node)
    x2, y2 = graph.get_position(goal_node)

    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)