import time
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Union

from src.graph import build_graph_from_csv
from src.route_service import search_route

from fastapi.responses import JSONResponse

app = FastAPI(
    title="Multi-Drop Delivery Route Optimization API",
    description="REST API to optimize delivery routes using A* and Greedy Best First Search.",
    version="1.0.0"
)

# Load graph once at startup
GRAPH_PATH = "data/raw/locations.csv"
try:
    graph = build_graph_from_csv(GRAPH_PATH)
except Exception as e:
    # Fallback to an empty graph or dummy if file does not exist yet (useful during setup/testing)
    from src.graph import Graph
    graph = Graph()


class RouteRequest(BaseModel):
    start: Union[str, int] = Field(..., example="Gudang")
    destination: Union[str, int] = Field(..., example="Drop-1")
    algorithm: str = Field(..., example="astar")
    mode: str = Field("single", example="single")


class RouteResponse(BaseModel):
    route: List[Union[str, int]]
    distance: float
    execution_time: float


def find_node_id(node_name_or_id):
    """
    Look up a node ID by exact ID, name, or translation.
    """
    nodes = graph.get_nodes()
    
    # 1. Direct ID match (string or int)
    if node_name_or_id in nodes:
        return node_name_or_id
    
    try:
        val = int(node_name_or_id)
        if val in nodes:
            return val
    except ValueError:
        pass

    # 2. Check location names case-insensitively
    for node_id, loc in graph.locations.items():
        if loc.name.lower() == str(node_name_or_id).lower():
            return node_id

    # 3. Handle standard translations (Gudang -> Depot)
    translations = {
        "gudang": ["depot", "warehouse"],
        "depot": ["gudang", "warehouse"],
        "warehouse": ["gudang", "depot"]
    }
    
    target_lower = str(node_name_or_id).lower()
    for trans_key, trans_list in translations.items():
        if target_lower == trans_key:
            for item in trans_list:
                for node_id, loc in graph.locations.items():
                    if loc.name.lower() == item:
                        return node_id
                        
    return None


@app.post("/route", response_model=RouteResponse, status_code=status.HTTP_200_OK)
def get_optimized_route(request: RouteRequest):
    # 1. Validate start node
    start_id = find_node_id(request.start)
    if start_id is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Start node not found."}
        )

    # 2. Validate destination node
    dest_id = find_node_id(request.destination)
    if dest_id is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Destination node not found."}
        )

    # Validate algorithm
    algo = request.algorithm.lower()
    if algo not in ["astar", "greedy", "a*", "greedy best first search"]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"Algorithm '{request.algorithm}' is not supported. Use 'astar' or 'greedy'."}
        )

    # Map algorithm names to what search_route expects
    algo_map = {
        "astar": "A*",
        "a*": "A*",
        "greedy": "Greedy Best First Search",
        "greedy best first search": "Greedy Best First Search"
    }
    selected_algo = algo_map[algo]

    # 3. Calculate route & execution time
    start_time = time.perf_counter()
    try:
        if request.mode.lower() in ["multi", "multidrop", "multi-drop"]:
            from src.route_service import search_multi_drop_route
            result = search_multi_drop_route(graph, start_id, dest_id, selected_algo)
        else:
            result = search_route(graph, start_id, dest_id, selected_algo)
            
        path = result["path"]
        distance = result["distance"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": f"Route search failed: {str(e)}"}
        )
    end_time = time.perf_counter()
    execution_time = end_time - start_time

    if path is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "No route found between the start and destination."}
        )

    # Map path IDs back to location names for the response
    route_names = [graph.locations[node_id].name for node_id in path]

    return RouteResponse(
        route=route_names,
        distance=distance,
        execution_time=round(execution_time, 6)
    )
