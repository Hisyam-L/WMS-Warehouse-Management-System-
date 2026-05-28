import os
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Import helper lu
from utils.helper import format_tanggal_indo

# Setting koneksi Supabase (Cukup di file ini aja!)
base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
env_path = os.path.join(base_dir, '.env')
load_dotenv(env_path)

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def get_stok_summary():
    stok_summary = {}
    try:
        response = supabase.table('stok').select('jumlah, kondisi, kaca(kategori(kategori))').execute()
        for item in response.data:
            if not item.get('kaca') or not item['kaca'].get('kategori'):
                continue
            nama_kategori = item['kaca']['kategori']['kategori']
            kondisi = item['kondisi'] if item['kondisi'] else "Baik"

            if nama_kategori not in stok_summary:
                stok_summary[nama_kategori] = {"Baik": 0, "Rusak": 0}
            if kondisi not in stok_summary[nama_kategori]:
                stok_summary[nama_kategori][kondisi] = 0
            stok_summary[nama_kategori][kondisi] += item['jumlah']
    except Exception as e:
        print(f"Error stok: {e}")

    return stok_summary

def get_semua_transaksi():
    transactions_list = []
    transaction_id = 1

    try:
        # Kaca Masuk
        masuk_resp = supabase.table('kaca_masuk').select('jumlah, tanggal, kaca(ukuran, ketebalan, kategori(kategori))').execute()
        for item in masuk_resp.data:
            tgl, wkt = format_tanggal_indo(item.get('tanggal'))
            transactions_list.append({
                "id": transaction_id, "tanggal": tgl, "waktu": wkt,
                "jenis": item['kaca']['kategori']['kategori'],
                "ukuran": item['kaca']['ukuran'], "ketebalan": item['kaca']['ketebalan'],
                "status": "Masuk", "jumlah": item['jumlah']
            })
            transaction_id += 1

        # Kaca Keluar
        keluar_resp = supabase.table('detail_kaca_keluar').select('jumlah, kaca(ukuran, ketebalan, kategori(kategori))').execute()
        for item in keluar_resp.data:
            tgl, wkt = format_tanggal_indo(datetime.now().isoformat())
            transactions_list.append({
                "id": transaction_id, "tanggal": tgl, "waktu": wkt,
                "jenis": item['kaca']['kategori']['kategori'],
                "ukuran": item['kaca']['ukuran'], "ketebalan": item['kaca']['ketebalan'],
                "status": "Keluar", "jumlah": item['jumlah']
            })
            transaction_id += 1

    except Exception as e:
        print(f"Error transaksi: {e}")

    transactions_list.reverse()
    return transactions_list