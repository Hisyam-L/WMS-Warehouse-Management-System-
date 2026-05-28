import json
from flask import Blueprint, render_template

# IMPORT FUNGSI DARI FOLDER SERVICES LU
from services.supabase_services import get_stok_summary, get_semua_transaksi

kepala_gudang_bp = Blueprint('kepala_gudang', __name__, url_prefix='/kepala_gudang')

@kepala_gudang_bp.route('/dashboard')
def dashboard():
    # Panggil fungsi yang udah lu buatin di service
    stok_data = get_stok_summary()
    transaksi_data = get_semua_transaksi()

    # Kirim datanya ke front-end HTML
    return render_template('kepala_gudang/dashboard.html',
                           stok_summary=stok_data,
                           transactions_json=json.dumps(transaksi_data))

@kepala_gudang_bp.route('/instruksi')
def instruksi():
    return render_template('kepala_gudang/intruksi.html')

@kepala_gudang_bp.route('/chatting')
def chatting():
    return render_template('kepala_gudang/chatting.html')

@kepala_gudang_bp.route('/tambahAkun')
def tambah_akun():
    return render_template('kepala_gudang/tambahAkun.html')