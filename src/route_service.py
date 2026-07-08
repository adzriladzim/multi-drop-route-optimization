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


def search_route(graph, start, destination, algorithm):
    """
    Wrapper untuk mencari rute terbaik berdasarkan pilihan algoritma dari UI.
    """
    algo_map = {
        "A*": "astar",
        "Greedy Best First Search": "greedy",
        "astar": "astar",
        "greedy": "greedy"
    }
    
    selected_algo = algo_map.get(algorithm)
    if not selected_algo:
        raise ValueError(f"Algoritma '{algorithm}' tidak didukung.")
        
    return optimize_route(graph, start, destination, algorithm=selected_algo)


def optimize_multi_drop_route(graph, start, destination, algorithm="astar"):
    """
    Mengoptimalkan rute pengiriman multi-drop dengan mengunjungi seluruh titik pengiriman (drop points).
    Menggunakan strategi greedy (nearest neighbor) dan menggunakan algoritma pencarian point-to-point (A* atau Greedy)
    untuk menghitung rute antar titik drop.
    """
    if hasattr(graph, 'drop_point_ids'):
        drop_points = set(graph.drop_point_ids())
    else:
        drop_points = set(graph.get_nodes()) - {start, destination}
    
    unvisited = set(drop_points) - {start}
    
    current = start
    overall_path = [start]
    
    while unvisited:
        nearest_node = None
        min_dist = float("inf")
        best_subpath = None
        
        for candidate in unvisited:
            if algorithm == "astar":
                path = SearchAlgorithms.a_star(graph, current, candidate)
            else:
                path = SearchAlgorithms.greedy_best_first_search(graph, current, candidate)
                
            if path:
                dist = Evaluator.calculate_total_distance(graph, path)
                if dist < min_dist:
                    min_dist = dist
                    nearest_node = candidate
                    best_subpath = path
                    
        if nearest_node is None or best_subpath is None:
            break
            
        overall_path.extend(best_subpath[1:])
        unvisited.remove(nearest_node)
        current = nearest_node
        
    # Terakhir, kembali dari titik kunjungan terakhir ke destination (Depot)
    if algorithm == "astar":
        final_path = SearchAlgorithms.a_star(graph, current, destination)
    else:
        final_path = SearchAlgorithms.greedy_best_first_search(graph, current, destination)
        
    if final_path:
        overall_path.extend(final_path[1:])
        
    total_distance = Evaluator.calculate_total_distance(graph, overall_path)
    
    return {
        "path": overall_path,
        "distance": total_distance
    }


def search_multi_drop_route(graph, start, destination, algorithm):
    """
    Wrapper untuk mencari rute multi-drop optimal berdasarkan pilihan algoritma dari UI.
    """
    algo_map = {
        "A*": "astar",
        "Greedy Best First Search": "greedy",
        "astar": "astar",
        "greedy": "greedy"
    }
    
    selected_algo = algo_map.get(algorithm)
    if not selected_algo:
        raise ValueError(f"Algoritma '{algorithm}' tidak didukung.")
        
    return optimize_multi_drop_route(graph, start, destination, algorithm=selected_algo)
