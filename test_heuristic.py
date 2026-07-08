from src.graph import Graph
from src.heuristic import euclidean

graph = Graph()

graph.add_node("Warehouse", 2, 3)
graph.add_node("A", 5, 7)
graph.add_node("Goal", 10, 10)

print("===== HEURISTIC TEST =====")
print("Warehouse -> Goal =", euclidean(graph, "Warehouse", "Goal"))
print("A -> Goal =", euclidean(graph, "A", "Goal"))