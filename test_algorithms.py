from src.graph import Graph
from src.algorithms import SearchAlgorithms

graph = Graph()

graph.add_node("Warehouse", 2, 2)
graph.add_node("A", 5, 4)
graph.add_node("B", 6, 8)
graph.add_node("C", 9, 6)
graph.add_node("Goal", 11, 9)

graph.add_edge("Warehouse", "A")
graph.add_edge("Warehouse", "B")
graph.add_edge("A", "C")
graph.add_edge("B", "C")
graph.add_edge("C", "Goal")

print("===== GREEDY =====")
print(SearchAlgorithms.greedy_best_first_search(graph, "Warehouse", "Goal"))

print("\n===== A STAR =====")
print(SearchAlgorithms.a_star(graph, "Warehouse", "Goal"))