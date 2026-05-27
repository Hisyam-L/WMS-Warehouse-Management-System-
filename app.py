import os
from flask import Flask, render_template
from supabase import create_client, Client
from dotenv import load_dotenv

# Membaca file .env untuk mengambil API Key Supabase
load_dotenv()

# Konfigurasi Flask agar membaca HTML dari folder 'views' dan CSS/JS dari 'views/assets'
base_dir = os.path.abspath(os.path.dirname(__file__))
views_dir = os.path.join(base_dir, 'views')
assets_dir = os.path.join(views_dir, 'assets')

app = Flask(__name__,
            template_folder=views_dir,
            static_folder=assets_dir,
            static_url_path='/assets')

# Inisialisasi Koneksi Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# Rute Dashboard Kepala Gudang (Udah ada sebelumnya)
@app.route('/kepala_gudang/dashboard')
def home():
    return render_template('kepala_gudang/dashboard.html')

# TAMBAH INI: Rute untuk Instruksi
@app.route('/kepala_gudang/instruksi')
def instruksi():
    return render_template('kepala_gudang/intruksi.html')

# TAMBAH INI: Rute untuk Chatting
@app.route('/kepala_gudang/chatting')
def chatting():
    return render_template('kepala_gudang/chatting.html')

# TAMBAH INI: Rute untuk Tambah Akun
@app.route('/kepala_gudang/tambahAkun')
def tambah_akun():
    return render_template('kepala_gudang/tambahAkun.html')

# (Rute petugas-monitoring yang tadi juga biarin aja di sini)
@app.route('/petugas-monitoring')
def petugas_monitoring():
    return render_template('petugas_monitoring/dashboad.html')


if __name__ == '__main__':
    app.run(debug=True)