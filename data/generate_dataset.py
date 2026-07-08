"""
generate_dataset.py
--------------------
Membuat dataset SINTETIS untuk kasus "Optimasi Rute Pengiriman Barang Multi-Drop".

Kenapa data sintetis?
- Koordinat bisa kita kontrol penuh -> mudah dibuktikan heuristik Euclidean
  bersifat ADMISSIBLE (tidak pernah overestimate jarak asli) dan CONSISTENT
  (h(n) <= cost(n, n') + h(n')), karena garis lurus (Euclidean) adalah jarak
  terpendek yang mungkin di ruang 2D bebas arah.
- Reproducible (pakai random seed) sehingga anggota tim lain (Core AI) bisa
  memakai graph & dataset yang PERSIS SAMA untuk testing algoritma mereka.

Output:
- data/raw/locations.csv  -> tabel titik (id, nama, x, y, tipe)
- data/raw/locations.json -> versi JSON (gampang di-load Streamlit teman kamu)

Jalankan:
    python generate_dataset.py --n_drops 8 --seed 42
"""

import argparse
import json
import csv
import random
import os


def generate_locations(n_drops: int = 8, seed: int = 42,
                        area_size: float = 100.0):
    """
    Membuat 1 depot + n_drops titik pengiriman dengan koordinat acak.

    Parameters
    ----------
    n_drops : int
        Jumlah titik pengiriman (5-10 sesuai kesepakatan kelompok).
    seed : int
        Random seed, supaya dataset SELALU SAMA setiap di-generate ulang
        (penting untuk keperluan pembuktian & testing bersama tim).
    area_size : float
        Ukuran area simulasi (koordinat 0..area_size), analoginya "kota"
        dalam satuan km atau grid unit.

    Returns
    -------
    list[dict] : daftar lokasi, index 0 selalu depot.
    """
    rng = random.Random(seed)
    locations = []

    # Depot selalu ditaruh di tengah area, biar simulasi rute lebih realistis
    depot = {
        "id": 0,
        "name": "Depot",
        "type": "depot",
        "x": round(area_size / 2, 2),
        "y": round(area_size / 2, 2),
        "demand": 0,
    }
    locations.append(depot)

    for i in range(1, n_drops + 1):
        loc = {
            "id": i,
            "name": f"Drop-{i}",
            "type": "drop_point",
            "x": round(rng.uniform(0, area_size), 2),
            "y": round(rng.uniform(0, area_size), 2),
            # demand = jumlah paket yang harus diantar di titik ini
            "demand": rng.randint(1, 5),
        }
        locations.append(loc)

    return locations


def save_csv(locations, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "type", "x", "y", "demand"])
        writer.writeheader()
        writer.writerows(locations)


def save_json(locations, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(locations, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="Generate dataset sintetis multi-drop delivery")
    parser.add_argument("--n_drops", type=int, default=8, help="Jumlah titik pengiriman (5-10)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--area_size", type=float, default=100.0, help="Ukuran area (unit)")
    default_outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")
    parser.add_argument("--outdir", type=str, default=default_outdir,
                         help="Folder output (default: data/raw/, sesuai struktur repo)")
    args = parser.parse_args()

    if not (5 <= args.n_drops <= 10):
        print(f"[WARNING] n_drops={args.n_drops} di luar kesepakatan tim (5-10). Tetap dilanjutkan.")

    locations = generate_locations(args.n_drops, args.seed, args.area_size)

    csv_path = os.path.join(args.outdir, "locations.csv")
    json_path = os.path.join(args.outdir, "locations.json")
    save_csv(locations, csv_path)
    save_json(locations, json_path)

    print(f"[OK] {len(locations)} lokasi (1 depot + {args.n_drops} drop points) dibuat.")
    print(f"[OK] Disimpan ke:\n  - {csv_path}\n  - {json_path}")


if __name__ == "__main__":
    main()