from datetime import datetime
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def format_tanggal_indo(iso_string):
    """
    Fungsi untuk mengubah string waktu ISO dari database Supabase
    menjadi format tanggal dan waktu lokal (Bahasa Indonesia).
    Contoh output: ('1 April 2026', '10:00')
    """
    # Jika data kosong, berikan nilai fallback (default)
    if not iso_string:
        return "1 April 2026", "10:00"

    try:
        # Menghapus offset zona waktu (misal: +00:00 atau Z) agar bisa diproses
        iso_string = iso_string.split('+')[0].replace('Z', '')
        dt = datetime.fromisoformat(iso_string)

        # Daftar nama bulan dalam Bahasa Indonesia
        bulan_indo = [
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ]

        # Format Tanggal: "DD NamaBulan YYYY"
        tanggal = f"{dt.day} {bulan_indo[dt.month - 1]} {dt.year}"

        # Format Waktu: "HH:MM"
        waktu = dt.strftime("%H:%M")

        return tanggal, waktu

    except Exception as e:
        print(f"Error format tanggal: {e}")
        return "1 April 2026", "10:00"

def generate_invite_token(perusahaan, role):
    """Membuat token terenkripsi berisi info perusahaan dan role"""
    # Mengambil SECRET_KEY dari konfigurasi Flask lu
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    payload = {'perusahaan': perusahaan, 'role': role}
    # Enkripsi data menjadi string token
    return serializer.dumps(payload, salt='undangan-petugas-wms')

def verify_invite_token(token, expiration=86400):
    """Memvalidasi token (Kedaluwarsa default: 24 jam / 86400 detik)"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        data = serializer.loads(token, salt='undangan-petugas-wms', max_age=expiration)
        return data
    except Exception:
        return None