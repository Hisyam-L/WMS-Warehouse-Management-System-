import json
from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from utils.helper import generate_invite_token
from services.supabase_services import AuthService
from services.supabase_services import get_stok_summary, get_semua_transaksi

kepala_gudang_bp = Blueprint('kepala_gudang', __name__, url_prefix='/kepala_gudang')

# SATPAM ROUTE: Mencegah nyelonong masuk kalau belum login / role salah
@kepala_gudang_bp.before_request
def cek_sesi():
    # Kalau belum login atau role-nya bukan kepala gudang, tendang ke login!
    if 'user_id' not in session or session.get('role') != 'kepala_gudang':
        flash("Akses ditolak! Silakan login sebagai Kepala Gudang.", "danger")
        return redirect(url_for('auth.login'))
# =========================================================================

@kepala_gudang_bp.route('/dashboard')
def dashboard():
    stok_data = get_stok_summary()
    transaksi_data = get_semua_transaksi()
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

@kepala_gudang_bp.route('/invite', methods=['POST'])
def undang_petugas():
    # Nggak perlu if session lagi di sini, udah di-handle sama satpam di atas
    role_tujuan = request.form.get('role_tujuan')
    perusahaan = session.get('perusahaan')

    token = generate_invite_token(perusahaan, role_tujuan)
    link_undangan = url_for('auth.daftar_petugas', token=token, _external=True)

    flash(f"Link undangan untuk {role_tujuan} berhasil dibuat: {link_undangan}", "success")
    return redirect(url_for('kepala_gudang.tambah_akun'))

@kepala_gudang_bp.route('/verifikasi/<id_user>/<keputusan>', methods=['GET'])
def melakukan_verifikasi(id_user, keputusan):
    # Nggak perlu if session lagi di sini
    AuthService.terima_atau_tolak_petugas(id_user, keputusan)
    flash(f"Akun petugas telah berhasil di-{keputusan}.", "success")
    return redirect(url_for('kepala_gudang.dashboard'))