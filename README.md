# Multi-Drop Route Optimization

Optimasi rute pengiriman barang multi-drop menggunakan algoritma kecerdasan buatan pencarian rute terbaik (**A\*** dan **Greedy Best First Search**). Proyek ini menyediakan aplikasi visualisasi interaktif berbasis Streamlit dan REST API berbasis FastAPI.

---

## Project Overview

Proyek ini bertujuan untuk menyelesaikan tantangan rute pengiriman multi-drop (Traveling Salesperson Problem / TSP) di mana kendaraan pengiriman harus mengunjungi semua titik drop pengiriman barang dari Depot asal, mencari urutan kunjungan yang paling hemat jarak, dan akhirnya kembali ke Depot. 

Optimasi urutan kunjungan multi-drop diimplementasikan menggunakan strategi *Nearest Neighbor* berbasis heuristik, di mana pencarian rute titik-ke-titik dilakukan dengan menggunakan algoritma **A\*** (optimal & admissible) dan **Greedy Best First Search**.

---

## Features

- **Peta Lokasi & Visualisasi Rute**: Menampilkan visualisasi titik depot (segitiga merah) dan drop points (lingkaran biru) beserta garis rute, arah panah, dan urutan nomor kunjungan.
- **Dua Mode Rute**:
  - *Point-to-Point (Single-Drop)*: Pencarian rute langsung dari satu titik ke titik lainnya.
  - *Multi-Drop Optimization*: Mengoptimalkan urutan kunjungan untuk mendatangi semua titik drop dari depot dan kembali ke depot.
- **Analisis & Perbandingan Algoritma**: Membandingkan rute, total jarak, dan waktu eksekusi secara side-by-side antara algoritma A* dan Greedy Best First Search.
- **REST API (FastAPI)**: Menyediakan API endpoint untuk melakukan pencarian rute yang dapat diintegrasikan dengan aplikasi lain.
- **Dataset Fleksibel**: Dapat menggunakan dataset bawaan (simulasi) maupun mengunggah file CSV buatan sendiri secara langsung dari UI.

---

## Folder Structure

```text
multi-drop-route-optimization/
│
├── data/
│   ├── raw/
│   │   └── locations.csv          # Dataset lokasi contoh
│   └── generate_dataset.py        # Pembuat data lokasi sintetis
│
├── src/
│   ├── algorithms.py              # Implementasi Core AI (A* & Greedy BFS)
│   ├── api.py                     # Implementasi REST API FastAPI
│   ├── evaluation.py              # Evaluator & pembanding algoritma
│   ├── graph.py                   # Struktur data Graph & DeliveryGraph
│   ├── heuristic.py               # Fungsi heuristik Euclidean
│   ├── route_service.py           # Logika optimasi & rute multi-drop
│   ├── testing.py                 # Script uji coba internal
│   ├── utils.py                   # Fungsi pembantu tambahan
│   └── visualization.py           # Fungsi plot & visualisasi matplotlib
│
├── app.py                         # File utama aplikasi Streamlit
├── requirements.txt               # Daftar dependensi library
├── test_algorithms.py             # Unit test algoritma
├── test_evaluation.py             # Unit test pembanding/evaluasi
├── test_graph.py                  # Unit test struktur Graph
├── test_heuristic.py              # Unit test fungsi heuristik
└── README.md                      # Dokumentasi proyek
```

---

## Installation

1. Pastikan Anda telah menginstal Python 3.10 ke atas pada komputer Anda.
2. Clone repository ini ke sistem lokal Anda.
3. Instal semua dependensi library yang dibutuhkan dengan menjalankan perintah berikut di terminal:

```bash
pip install streamlit fastapi uvicorn networkx matplotlib pandas requests
```

---

## Running Streamlit

Jalankan perintah berikut pada terminal di folder root proyek untuk memulai aplikasi dashboard Streamlit:

```bash
streamlit run app.py
```

Aplikasi akan otomatis terbuka di browser Anda pada alamat `http://localhost:8501`.

---

## Running API

Untuk menjalankan REST API server menggunakan Uvicorn:

```bash
uvicorn src.api:app --reload
```

Server API akan berjalan pada alamat `http://127.0.0.1:8000`.

---

## API Documentation

FastAPI menyediakan dokumentasi interaktif otomatis (Swagger UI) yang dapat diakses melalui browser pada:

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

### Endpoint: `POST /route`

Mencari rute pengiriman berdasarkan titik awal, titik akhir, mode, dan pilihan algoritma.

#### Request Body
```json
{
  "start": "Gudang",
  "destination": "Gudang",
  "algorithm": "astar",
  "mode": "multi"
}
```

- `start`: Nama lokasi asal (misalnya `"Gudang"`, `"Depot"`, atau ID numerik).
- `destination`: Nama lokasi akhir (misalnya `"Gudang"` atau ID numerik).
- `algorithm`: Pilihan algoritma (`"astar"` atau `"greedy"`).
- `mode`: Mode rute (`"single"` untuk point-to-point, `"multi"` untuk mengunjungi semua titik drop).

#### Response Body (HTTP 200 OK)
```json
{
  "route": [
    "Depot",
    "Drop-7",
    "Drop-5",
    "Drop-2",
    "Drop-4",
    "Drop-1",
    "Drop-8",
    "Drop-6",
    "Drop-3",
    "Depot"
  ],
  "distance": 264.55,
  "execution_time": 0.001072
}
```

#### Validation Error (HTTP 400 Bad Request)
Jika lokasi tidak ditemukan dalam graph:
```json
{
  "error": "Destination node not found."
}
```

---

## Screenshots

*( screenshots dapat ditambahkan di folder assets setelah melakukan simulasi )*

---

## Authors
- **Adzril Adzim Hendrynov**
- **Adikto Hutabalian**
- **Muhammad Reski**
