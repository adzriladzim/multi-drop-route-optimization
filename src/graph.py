"""
graph.py
--------
Representasi graph untuk kasus "Optimasi Rute Pengiriman Barang Multi-Drop".

Peran modul ini dalam pipeline tim:
    dataset (kamu) -> GRAPH (kamu) -> algorithms.py A*/Greedy (Core AI)
                                    -> visualization.py (kamu)
                                    -> Streamlit app (Teman 2)

Graph di sini adalah GRAPH LENGKAP (fully-connected / complete graph):
setiap titik terhubung ke setiap titik lain, karena pergerakan pengiriman
diasumsikan BEBAS ARAH (garis lurus / Euclidean), bukan grid jalan seperti
gudang (Manhattan). Ini sesuai fokus Topik 2: "pergerakan bebas arah".

Bobot edge (jarak antar titik) dihitung dengan Euclidean distance, dan
fungsi heuristic_euclidean() di bawah SENGAJA disamakan rumusnya dengan
bobot edge asli. Ini penting untuk pembuktian:

    ADMISSIBLE : h(n) <= jarak_asli(n, tujuan)  untuk semua n
                 Karena h(n) dihitung dengan rumus Euclidean yang SAMA
                 PERSIS dengan jarak asli (bukan estimasi kasar), maka
                 h(n) == jarak asli (tidak pernah overestimate). QED.

    CONSISTENT : h(n) <= cost(n, n') + h(n') untuk setiap tetangga n'
                 Ini otomatis terpenuhi karena Euclidean distance memenuhi
                 TRIANGLE INEQUALITY: jarak(A,C) <= jarak(A,B) + jarak(B,C).
                 (Bukti/plot triangle inequality ada di notebook analisis.)
"""

import csv
import json
import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import networkx as nx


@dataclass
class Location:
    id: int
    name: str
    type: str
    x: float
    y: float
    demand: int = 0


def load_locations_csv(path: str) -> List[Location]:
    locations = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            locations.append(Location(
                id=int(row["id"]),
                name=row["name"],
                type=row["type"],
                x=float(row["x"]),
                y=float(row["y"]),
                demand=int(row["demand"]),
            ))
    return locations


def load_locations_json(path: str) -> List[Location]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [Location(**item) for item in data]


def euclidean_distance(a: Location, b: Location) -> float:
    """Jarak garis lurus antar dua titik. Dipakai sebagai BOBOT EDGE asli."""
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)


def heuristic_euclidean(a: Location, b: Location) -> float:
    """
    Fungsi heuristik h(n) untuk A* Search.

    Rumusnya identik dengan euclidean_distance() -> ini yang membuat
    heuristik ini admissible & consistent (lihat docstring modul).
    Fungsi ini dipisah namanya (bukan cuma alias) supaya jelas secara
    KONSEPTUAL: satu dipakai sebagai "cost aktual graph", satu lagi
    dipakai sebagai "estimasi" oleh algoritma A* di algorithms.py.
    """
    return euclidean_distance(a, b)


class Graph:
    """
    Representasi graph umum untuk pengujian algoritma pencarian rute.
    Mendukung koordinat node (x, y) dan penambahan edge manual.
    """

    def __init__(self):
        self.nodes = {}       # name -> (x, y)
        self.edges = {}       # name -> list of (neighbor, weight)
        self.locations = {}   # name -> Location object (untuk kompatibilitas)

    def add_node(self, name, x, y, demand=0, type="drop_point", label=None):
        self.nodes[name] = (x, y)
        if name not in self.edges:
            self.edges[name] = []
        # Untuk kompatibilitas dengan DeliveryGraph.locations
        self.locations[name] = Location(
            id=name,
            name=str(label if label is not None else name),
            type=type,
            x=float(x),
            y=float(y),
            demand=demand
        )

    def add_edge(self, node_a, node_b, weight=None):
        if node_a not in self.nodes or node_b not in self.nodes:
            raise ValueError("Kedua node harus ditambahkan terlebih dahulu.")
        if weight is None:
            weight = self.euclidean_distance(node_a, node_b)
        
        # Simpan adjacency list
        # Update jika edge sudah ada, jika tidak tambahkan
        self.edges[node_a] = [e for e in self.edges[node_a] if e[0] != node_b] + [(node_b, weight)]
        self.edges[node_b] = [e for e in self.edges[node_b] if e[0] != node_a] + [(node_a, weight)]

    def get_nodes(self) -> List:
        return list(self.nodes.keys())

    def get_neighbors(self, node) -> List[Tuple]:
        return self.edges.get(node, [])

    def get_position(self, node) -> Tuple[float, float]:
        if node not in self.nodes:
            raise KeyError(f"Node {node} tidak ditemukan.")
        return self.nodes[node]

    def get_edge_cost(self, node_a, node_b) -> float:
        for neighbor, weight in self.edges.get(node_a, []):
            if neighbor == node_b:
                return weight
        return float("inf")

    def euclidean_distance(self, node_a, node_b) -> float:
        x1, y1 = self.get_position(node_a)
        x2, y2 = self.get_position(node_b)
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


class DeliveryGraph(Graph):
    """
    Wrapper di atas networkx.Graph yang merepresentasikan jaringan
    depot + titik pengiriman sebagai complete graph berbobot Euclidean.
    """

    def __init__(self, locations: List[Location]):
        super().__init__()
        # Load locations ke Graph parent
        for loc in locations:
            self.add_node(loc.id, loc.x, loc.y, demand=loc.demand, type=loc.type, label=loc.name)
        
        # Build complete graph (tetangga untuk semua node)
        ids = self.get_nodes()
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                w = self.euclidean_distance(ids[i], ids[j])
                self.add_edge(ids[i], ids[j], w)

        self.depot_id = next(loc.id for loc in locations if loc.type == "depot")
        self.graph = nx.Graph()
        self._build()

    def _build(self):
        for loc in self.locations.values():
            self.graph.add_node(loc.id, **loc.__dict__)

        ids = list(self.locations.keys())
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                w = self.euclidean_distance(ids[i], ids[j])
                self.graph.add_edge(ids[i], ids[j], weight=w)

    # ---- API yang enak dipakai algorithms.py (A* / Greedy) ----

    def neighbors(self, node_id: int) -> List[int]:
        return list(self.graph.neighbors(node_id))

    def cost(self, node_a: int, node_b: int) -> float:
        """g(n): biaya aktual antar dua node bertetangga."""
        return self.graph[node_a][node_b]["weight"]

    def heuristic(self, node_a: int, node_b: int) -> float:
        """h(n): estimasi jarak node_a ke node_b (goal), untuk A*/Greedy."""
        return heuristic_euclidean(self.locations[node_a], self.locations[node_b])

    def all_node_ids(self) -> List[int]:
        return list(self.locations.keys())

    def drop_point_ids(self) -> List[int]:
        return [loc.id for loc in self.locations.values() if loc.type == "drop_point"]

    def distance_matrix(self) -> Tuple[List[int], List[List[float]]]:
        """Mengembalikan (daftar_id, matrix jarak NxN) - berguna utk EDA & heatmap."""
        ids = self.all_node_ids()
        n = len(ids)
        matrix = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i != j:
                    matrix[i][j] = self.cost(ids[i], ids[j])
        return ids, matrix

    def path_length(self, path: List[int]) -> float:
        """Total jarak sebuah rute (urutan node id), termasuk kembali ke depot bila
        node terakhir path bukan depot dan mau dihitung round-trip -> panggil manual."""
        return sum(self.cost(path[i], path[i + 1]) for i in range(len(path) - 1))

    def verify_triangle_inequality(self, sample_size: int = None) -> bool:
        """
        Membuktikan (secara empiris, untuk semua/simpel triple titik) bahwa
        heuristik Euclidean CONSISTENT: h(a,c) <= cost(a,b) + h(b,c).
        Dipakai di notebook analisis sebagai bukti pendukung.
        """
        ids = self.all_node_ids()
        triples = [(a, b, c) for a in ids for b in ids for c in ids if len({a, b, c}) == 3]
        if sample_size:
            triples = triples[:sample_size]
        for a, b, c in triples:
            h_ac = self.heuristic(a, c)
            cost_ab_plus_h_bc = self.cost(a, b) + self.heuristic(b, c)
            if h_ac > cost_ab_plus_h_bc + 1e-9:  # toleransi floating point
                return False
        return True


def build_graph_from_csv(path: str) -> DeliveryGraph:
    """Shortcut: langsung load CSV -> DeliveryGraph."""
    return DeliveryGraph(load_locations_csv(path))


if __name__ == "__main__":
    # Contoh pemakaian / smoke test
    g = build_graph_from_csv("../data/raw/locations.csv")
    print(f"Jumlah node: {len(g.all_node_ids())}")
    print(f"Depot id: {g.depot_id}")
    print(f"Drop points: {g.drop_point_ids()}")
    print(f"Contoh cost(0,1): {g.cost(0, 1):.2f}")
    print(f"Contoh heuristic(0,1): {g.heuristic(0, 1):.2f}")
    print(f"Triangle inequality (consistency) terbukti: {g.verify_triangle_inequality()}")