"""
visualization.py
-----------------
Fungsi-fungsi visualisasi untuk kasus "Optimasi Rute Pengiriman Barang Multi-Drop".

Dipakai oleh:
- notebook analisis (EDA kamu)
- Streamlit app (Teman 2) -> tinggal panggil fungsi-fungsi ini dan
  return fig-nya ke st.pyplot(fig)

Semua fungsi mengembalikan objek `matplotlib.figure.Figure`, BUKAN langsung
plt.show(), supaya fleksibel dipakai di notebook maupun Streamlit.
"""

from typing import List, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from graph import DeliveryGraph


def plot_locations(g: DeliveryGraph, title: str = "Peta Depot & Titik Pengiriman"):
    """Scatter plot semua titik: depot (segitiga merah) + drop points (biru)."""
    fig, ax = plt.subplots(figsize=(7, 6))

    for loc in g.locations.values():
        if loc.type == "depot":
            ax.scatter(loc.x, loc.y, c="red", marker="^", s=200, zorder=3, label="Depot")
        else:
            ax.scatter(loc.x, loc.y, c="steelblue", s=120, zorder=3)
            ax.annotate(f"demand={loc.demand}", (loc.x, loc.y),
                        textcoords="offset points", xytext=(6, -10), fontsize=7, color="gray")
        ax.annotate(loc.name, (loc.x, loc.y), textcoords="offset points",
                    xytext=(6, 6), fontsize=9)

    ax.set_title(title)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid(True, linestyle="--", alpha=0.4)

    handles = [mpatches.Patch(color="red", label="Depot"),
               mpatches.Patch(color="steelblue", label="Drop point")]
    ax.legend(handles=handles, loc="best")
    fig.tight_layout()
    return fig


def plot_full_graph(g: DeliveryGraph, title: str = "Graph Lengkap (Complete Graph)",
                     show_weights: bool = False):
    """
    Menampilkan SEMUA edge (complete graph) antar titik dengan transparansi rendah,
    untuk menunjukkan bahwa pergerakan bebas arah (bukan grid jalan).
    """
    fig, ax = plt.subplots(figsize=(7, 6))
    ids = g.all_node_ids()

    # gambar semua edge dulu (tipis, transparan) baru node di atasnya
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = g.locations[ids[i]], g.locations[ids[j]]
            ax.plot([a.x, b.x], [a.y, b.y], color="lightgray", linewidth=0.7, zorder=1)
            if show_weights:
                mx, my = (a.x + b.x) / 2, (a.y + b.y) / 2
                ax.annotate(f"{g.cost(a.id, b.id):.1f}", (mx, my), fontsize=6, color="gray")

    for loc in g.locations.values():
        color = "red" if loc.type == "depot" else "steelblue"
        marker = "^" if loc.type == "depot" else "o"
        size = 200 if loc.type == "depot" else 120
        ax.scatter(loc.x, loc.y, c=color, marker=marker, s=size, zorder=3)
        ax.annotate(loc.name, (loc.x, loc.y), textcoords="offset points",
                    xytext=(6, 6), fontsize=9)

    ax.set_title(title)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    fig.tight_layout()
    return fig


def plot_route(g: DeliveryGraph, path: List[int], title: str = "Rute Pengiriman",
               color: str = "green", ax: Optional[plt.Axes] = None):
    """
    Menggambar satu rute (urutan node id) di atas peta titik.
    `path` contoh: [0, 3, 1, 5, 0]  (mulai & selesai di depot)
    """
    own_fig = ax is None
    if own_fig:
        fig, ax = plt.subplots(figsize=(7, 6))
    else:
        fig = ax.figure

    # titik-titik dasar
    for loc in g.locations.values():
        c = "red" if loc.type == "depot" else "lightsteelblue"
        m = "^" if loc.type == "depot" else "o"
        s = 180 if loc.type == "depot" else 100
        ax.scatter(loc.x, loc.y, c=c, marker=m, s=s, zorder=3)
        ax.annotate(loc.name, (loc.x, loc.y), textcoords="offset points",
                    xytext=(6, 6), fontsize=8)

    # garis rute + panah arah + nomor urutan kunjungan
    for idx in range(len(path) - 1):
        a, b = g.locations[path[idx]], g.locations[path[idx + 1]]
        ax.annotate("", xy=(b.x, b.y), xytext=(a.x, a.y),
                    arrowprops=dict(arrowstyle="->", color=color, lw=2, alpha=0.85),
                    zorder=2)
    for order, node_id in enumerate(path):
        loc = g.locations[node_id]
        ax.annotate(str(order), (loc.x, loc.y), textcoords="offset points",
                    xytext=(-10, -12), fontsize=8, color=color, fontweight="bold")

    total_dist = g.path_length(path)
    ax.set_title(f"{title}  |  Total jarak = {total_dist:.2f}")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    if own_fig:
        fig.tight_layout()
    return fig


def plot_route_comparison(g: DeliveryGraph, path_a: List[int], path_b: List[int],
                           label_a: str = "A* Search", label_b: str = "Greedy Best-First"):
    """
    Side-by-side comparison dua rute (misalnya hasil A* vs Greedy dari
    algorithms.py Core AI) -> langsung dipakai di notebook / Streamlit
    untuk bagian evaluasi.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    plot_route(g, path_a, title=label_a, color="green", ax=axes[0])
    plot_route(g, path_b, title=label_b, color="darkorange", ax=axes[1])
    fig.tight_layout()
    return fig


def plot_distance_heatmap(g: DeliveryGraph, title: str = "Heatmap Matriks Jarak Euclidean"):
    """Heatmap matriks jarak antar semua titik -> untuk notebook EDA."""
    ids, matrix = g.distance_matrix()
    labels = [g.locations[i].name for i in ids]

    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(matrix, cmap="viridis")
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_title(title)
    fig.colorbar(im, ax=ax, label="Jarak (unit)")
    fig.tight_layout()
    return fig


if __name__ == "__main__":
    from graph import build_graph_from_csv

    g = build_graph_from_csv("../data/raw/locations.csv")

    fig1 = plot_locations(g)
    fig1.savefig("../assets/01_locations.png", dpi=120)

    fig2 = plot_full_graph(g)
    fig2.savefig("../assets/02_full_graph.png", dpi=120)

    dummy_route = [g.depot_id] + g.drop_point_ids() + [g.depot_id]
    fig3 = plot_route(g, dummy_route, title="Contoh Rute (urutan asli, belum dioptimasi)")
    fig3.savefig("../assets/03_route_example.png", dpi=120)

    fig4 = plot_distance_heatmap(g)
    fig4.savefig("../assets/04_heatmap.png", dpi=120)

    print("[OK] 4 contoh visualisasi disimpan ke folder assets/")