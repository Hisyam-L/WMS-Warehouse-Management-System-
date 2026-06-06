import os
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

from utils.helper import format_tanggal_indo

# Setting koneksi Supabase
base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(base_dir, ".env"))

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# 1. Tambah parameter perusahaan dan filter eq('perusahaan', perusahaan)
def get_stok_summary(perusahaan):
    stok_summary = {}
    try:
        response = (
            supabase.table("stok")
            .select("jumlah, kondisi, kaca(kategori(kategori))")
            .eq("perusahaan", perusahaan)
            .execute()
        )
        for item in response.data:
            if not item.get("kaca") or not item["kaca"].get("kategori"):
                continue
            nama_kategori = item["kaca"]["kategori"]["kategori"]
            kondisi = item["kondisi"] if item["kondisi"] else "Baik"

            if nama_kategori not in stok_summary:
                stok_summary[nama_kategori] = {"Baik": 0, "Rusak": 0}
            if kondisi not in stok_summary[nama_kategori]:
                stok_summary[nama_kategori][kondisi] = 0
            stok_summary[nama_kategori][kondisi] += item["jumlah"]
    except Exception as e:
        print(f"Error stok: {e}")

    return stok_summary


# 2. Tambah parameter perusahaan dan filter pada kaca_masuk serta kaca_keluar
def get_semua_transaksi(perusahaan):
    transactions_list = []
    transaction_id = 1

    try:
        # Kaca Masuk - Filter berdasarkan perusahaan
        masuk_resp = (
            supabase.table("kaca_masuk")
            .select("jumlah, tanggal, kaca(ukuran, ketebalan, kategori(kategori))")
            .eq("perusahaan", perusahaan)
            .execute()
        )
        for item in masuk_resp.data:
            tgl, wkt = format_tanggal_indo(item.get("tanggal"))
            transactions_list.append(
                {
                    "id": transaction_id,
                    "tanggal": tgl,
                    "waktu": wkt,
                    "jenis": item["kaca"]["kategori"]["kategori"],
                    "ukuran": item["kaca"]["ukuran"],
                    "ketebalan": item["kaca"]["ketebalan"],
                    "status": "Masuk",
                    "jumlah": item["jumlah"],
                }
            )
            transaction_id += 1

        # Kaca Keluar - Join dengan kaca_keluar untuk filter berdasarkan perusahaannya
        keluar_resp = (
            supabase.table("detail_kaca_keluar")
            .select(
                "jumlah, kaca(ukuran, ketebalan, kategori(kategori)), kaca_keluar!inner(perusahaan)"
            )
            .eq("kaca_keluar.perusahaan", perusahaan)
            .execute()
        )
        for item in keluar_resp.data:
            tgl, wkt = format_tanggal_indo(datetime.now().isoformat())
            transactions_list.append(
                {
                    "id": transaction_id,
                    "tanggal": tgl,
                    "waktu": wkt,
                    "jenis": item["kaca"]["kategori"]["kategori"],
                    "ukuran": item["kaca"]["ukuran"],
                    "ketebalan": item["kaca"]["ketebalan"],
                    "status": "Keluar",
                    "jumlah": item["jumlah"],
                }
            )
            transaction_id += 1

    except Exception as e:
        print(f"Error transaksi: {e}")

    transactions_list.reverse()
    return transactions_list


# 3. Tambah parameter perusahaan dan filter eq('perusahaan', perusahaan)
def get_stok_detail(perusahaan):
    stok_list = []
    try:
        # Ambil id_kaca, jumlah, kondisi beserta data detail kacanya
        response = (
            supabase.table("stok")
            .select(
                "id_kaca, jumlah, kondisi, kaca(ukuran, ketebalan, kategori(kategori))"
            )
            .eq("perusahaan", perusahaan)
            .execute()
        )
        for item in response.data:
            if not item.get("kaca") or not item["kaca"].get("kategori"):
                continue
            stok_list.append(
                {
                    "id_kaca": item["id_kaca"],
                    "kategori": item["kaca"]["kategori"]["kategori"],
                    "ukuran": item["kaca"]["ukuran"],
                    "ketebalan": item["kaca"]["ketebalan"],
                    "kondisi": item["kondisi"] if item["kondisi"] else "Baik",
                    "jumlah": item["jumlah"],
                }
            )
    except Exception as e:
        print(f"Error fetch stok detail: {e}")
    return stok_list


# Bagian AuthService biarin aja persis kayak gini
class AuthService:
    @staticmethod
    def register_kepala_gudang(username, email, password, perusahaan):
        hashed_password = generate_password_hash(password)
        data = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "perusahaan": perusahaan,
            "role": "kepala_gudang",
            "status": "aktif",
        }
        return supabase.table("users").insert(data).execute()

    @staticmethod
    def register_petugas_pending(username, email, password, perusahaan, role):
        hashed_password = generate_password_hash(password)
        data = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "perusahaan": perusahaan,
            "role": role,
            "status": "pending",
        }
        return supabase.table("users").insert(data).execute()

    @staticmethod
    def login_user(email, password):
        response = supabase.table("users").select("*").eq("email", email).execute()
        if not response.data:
            return {"success": False, "message": "Email tidak terdaftar."}

        user = response.data[0]

        if user["status"] == "pending":
            return {"success": False, "message": "Akun Anda belum diverifikasi."}
        if user["status"] == "ditolak":
            return {"success": False, "message": "Pendaftaran Anda ditolak."}

        if check_password_hash(user["password"], password):
            return {"success": True, "user": user}

        return {"success": False, "message": "Password salah."}

    @staticmethod
    def terima_atau_tolak_petugas(id_user, keputusan):
        status_baru = "aktif" if keputusan == "terima" else "ditolak"
        return (
            supabase.table("users")
            .update({"status": status_baru})
            .eq("id_user", id_user)
            .execute()
        )
