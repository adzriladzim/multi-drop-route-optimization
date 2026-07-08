import streamlit as st
import tempfile
import os
import pandas as pd
import matplotlib.pyplot as plt

from src.graph import build_graph_from_csv
from src.route_service import search_route, search_multi_drop_route
from src.evaluation import Evaluator
from src.visualization import plot_route, plot_route_comparison, plot_locations

# Set page configuration
st.set_page_config(
    page_title="Multi-Drop Delivery Route Optimizer",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling using CSS
st.markdown("""
    <style>
    /* Custom background & card design */
    .reportview-container {
        background: #f8f9fa;
    }
    .metric-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #1E88E5;
        margin-bottom: 20px;
    }
    .metric-title {
        font-size: 14px;
        color: #757575;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    .metric-value {
        font-size: 28px;
        color: #1E88E5;
        font-weight: 700;
        margin-top: 5px;
    }
    .path-step {
        display: inline-block;
        background-color: #E3F2FD;
        color: #0D47A1;
        padding: 6px 12px;
        border-radius: 20px;
        margin: 4px;
        font-weight: 600;
        font-size: 14px;
        border: 1px solid #BBDEFB;
    }
    .path-arrow {
        color: #90CAF9;
        font-weight: bold;
        margin: 0 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Main Title & Description
st.title("🚚 Multi-Drop Route Optimization")
st.markdown(r"""
Aplikasi ini membantu mengoptimalkan rute pengiriman barang *multi-drop* dari Depot ke berbagai lokasi tujuan menggunakan algoritma kecerdasan buatan pencarian rute terbaik (**A\*** dan **Greedy Best First Search**).
""")

# Sidebar settings
st.sidebar.header("⚙️ Konfigurasi Data")

# Dataset Input Selection
data_option = st.sidebar.radio(
    "Pilih Sumber Dataset",
    ("Gunakan Contoh Dataset", "Upload CSV Lokasi")
)

graph = None
sample_path = "data/raw/locations.csv"

if data_option == "Gunakan Contoh Dataset":
    if os.path.exists(sample_path):
        try:
            graph = build_graph_from_csv(sample_path)
            st.sidebar.success("Berhasil memuat contoh dataset.")
        except Exception as e:
            st.sidebar.error(f"Gagal memuat contoh dataset: {e}")
    else:
        st.sidebar.error("Contoh dataset tidak ditemukan di `data/raw/locations.csv`.")
else:
    uploaded_file = st.sidebar.file_uploader("Upload CSV Lokasi", type=["csv"])
    if uploaded_file is not None:
        # Save temp file to parse it
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_path = temp_file.name
        
        try:
            graph = build_graph_from_csv(temp_path)
            st.sidebar.success("Berhasil memuat dataset CSV yang diupload.")
        except Exception as e:
            st.sidebar.error(f"Format CSV tidak valid: {e}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    else:
        st.sidebar.info("Silakan unggah file CSV berisi lokasi.")

# Execute main UI if graph is loaded successfully
if graph is not None:
    # Get nodes mapping
    name_to_id = {f"{loc.name} ({loc.type})": loc.id for loc in graph.locations.values()}
    node_options = list(name_to_id.keys())
    
    st.sidebar.subheader("📍 Konfigurasi Rute")
    
    start_node = st.sidebar.selectbox(
        "Start Node (Titik Awal)",
        options=node_options,
        index=0
    )
    
    destination_node = st.sidebar.selectbox(
        "Destination Node (Titik Akhir)",
        options=node_options,
        index=len(node_options) - 1 if len(node_options) > 1 else 0
    )
    
    route_mode = st.sidebar.radio(
        "Mode Rute",
        ("Point-to-Point (Single-Drop)", "Multi-Drop Optimization (Visit All)")
    )
    
    algorithm = st.sidebar.radio(
        "Pilihan Algorithm",
        ("A*", "Greedy Best First Search")
    )
    
    find_route_btn = st.sidebar.button("Find Best Route", type="primary")
    
    # Extract IDs
    start_id = name_to_id[start_node]
    dest_id = name_to_id[destination_node]
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🗺️ Peta Lokasi & Rute", "📊 Perbandingan Algoritma", "📋 Data Lokasi"])
    
    with tab1:
        if find_route_btn:
            with st.spinner("Mencari rute optimal..."):
                try:
                    if route_mode == "Multi-Drop Optimization (Visit All)":
                        result = search_multi_drop_route(graph, start_id, dest_id, algorithm)
                        title_prefix = "Rute Multi-Drop"
                    else:
                        result = search_route(graph, start_id, dest_id, algorithm)
                        title_prefix = "Rute Point-to-Point"
                        
                    path = result["path"]
                    distance = result["distance"]
                    
                    if path is None or len(path) == 0:
                        st.error("Rute tidak ditemukan.")
                    else:
                        # Display Results
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            st.markdown(f"""
                                <div class="metric-card">
                                    <div class="metric-title">Jarak Total ({algorithm})</div>
                                    <div class="metric-value">{distance:.2f} unit</div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            st.subheader("Urutan Rute Pengiriman")
                            # Map path IDs back to names
                            id_to_name = {loc.id: loc.name for loc in graph.locations.values()}
                            
                            st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
                            for i, node_id in enumerate(path):
                                st.markdown(f'<span class="path-step">{id_to_name[node_id]}</span>', unsafe_allow_html=True)
                                if i < len(path) - 1:
                                    st.markdown('<span class="path-arrow">➔</span>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            st.info("Keterangan angka pada rute menunjukkan urutan kunjungan lokasi.")
                            
                        with col2:
                            st.subheader("Visualisasi Rute")
                            fig = plot_route(graph, path, title=f"{title_prefix} ({algorithm})", color="green" if algorithm == "A*" else "darkorange")
                            st.pyplot(fig)
                            
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat mencari rute: {e}")
        else:
            # Show original location map before route is optimized
            st.subheader("Peta Distribusi Lokasi Depot & Drop Points")
            fig = plot_locations(graph)
            st.pyplot(fig)
            st.info("Klik tombol **Find Best Route** di sidebar untuk mengoptimalkan rute.")

    with tab2:
        st.subheader("Analisis Perbandingan Performa Algoritma")
        st.markdown(r"""
        Di bawah ini adalah perbandingan side-by-side antara algoritma **A\*** (yang admissible & menghasilkan rute optimal secara jarak) dengan **Greedy Best First Search** (yang lebih memprioritaskan estimasi heuristik ke tujuan).
        """)
        
        if st.button("Jalankan Perbandingan"):
            with st.spinner("Menghitung perbandingan performa..."):
                try:
                    import time
                    from src.route_service import optimize_multi_drop_route
                    
                    if route_mode == "Multi-Drop Optimization (Visit All)":
                        t0 = time.perf_counter()
                        res_astar = optimize_multi_drop_route(graph, start_id, dest_id, algorithm="astar")
                        time_astar = (time.perf_counter() - t0) * 1000
                        
                        t0 = time.perf_counter()
                        res_greedy = optimize_multi_drop_route(graph, start_id, dest_id, algorithm="greedy")
                        time_greedy = (time.perf_counter() - t0) * 1000
                        
                        comp_results = {
                            "A*": {
                                "path": res_astar["path"],
                                "distance": res_astar["distance"],
                                "time": round(time_astar, 3)
                            },
                            "Greedy": {
                                "path": res_greedy["path"],
                                "distance": res_greedy["distance"],
                                "time": round(time_greedy, 3)
                            }
                        }
                    else:
                        comp_results = Evaluator.compare(graph, start_id, dest_id)
                    
                    c1, c2 = st.columns(2)
                    
                    with c1:
                        st.markdown(f"""
                            <div class="metric-card" style="border-left-color: #2E7D32;">
                                <div class="metric-title">A* Search</div>
                                <div class="metric-value">{comp_results['A*']['distance']:.2f} unit</div>
                                <div style="font-size:12px;color:gray;margin-top:5px;">
                                    Waktu eksekusi: {comp_results['A*']['time']:.3f} ms<br>
                                    Langkah: {len(comp_results['A*']['path']) if comp_results['A*']['path'] else 0} nodes
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                    with c2:
                        st.markdown(f"""
                            <div class="metric-card" style="border-left-color: #EF6C00;">
                                <div class="metric-title">Greedy Best First Search</div>
                                <div class="metric-value">{comp_results['Greedy']['distance']:.2f} unit</div>
                                <div style="font-size:12px;color:gray;margin-top:5px;">
                                    Waktu eksekusi: {comp_results['Greedy']['time']:.3f} ms<br>
                                    Langkah: {len(comp_results['Greedy']['path']) if comp_results['Greedy']['path'] else 0} nodes
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.subheader("Perbandingan Visual Rute")
                    fig_comp = plot_route_comparison(
                        graph, 
                        comp_results['A*']['path'], 
                        comp_results['Greedy']['path'],
                        label_a=f"A* Search (Jarak: {comp_results['A*']['distance']:.2f})",
                        label_b=f"Greedy Best-First (Jarak: {comp_results['Greedy']['distance']:.2f})"
                    )
                    st.pyplot(fig_comp)
                    
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat membandingkan rute: {e}")
        else:
            st.info("Klik tombol di atas untuk menjalankan simulasi perbandingan performa.")
            
    with tab3:
        st.subheader("Daftar Detail Lokasi dalam Dataset")
        locations_data = []
        for loc in graph.locations.values():
            locations_data.append({
                "ID": loc.id,
                "Nama Lokasi": loc.name,
                "Tipe": loc.type,
                "Koordinat X": loc.x,
                "Koordinat Y": loc.y,
                "Demand (Paket)": loc.demand
            })
        df = pd.DataFrame(locations_data)
        st.dataframe(df, use_container_width=True)

else:
    st.warning("Silakan pilih/unggah data lokasi terlebih dahulu pada sidebar untuk memulai analisis.")
