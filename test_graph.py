from src.graph import Graph

graph = Graph()

graph.add_node("Warehouse", 2, 3)
graph.add_node("A", 5, 7)
graph.add_node("B", 8, 2)

graph.add_edge("Warehouse", "A")
graph.add_edge("Warehouse", "B")

print("===== NODE =====")
print(graph.get_nodes())

print()

print("===== NEIGHBORS =====")
print(graph.get_neighbors("Warehouse"))

print()

print("===== DISTANCE =====")
print(graph.euclidean_distance("Warehouse", "A"))