import json
from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from utils.helper import generate_invite_token
from services.supabase_services import AuthService, supabase
from services.supabase_services import get_stok_detail, get_semua_transaksi

kepala_gudang_bp = Blueprint('kepala_gudang', __name__, url_prefix='/kepala_gudang')

@kepala_gudang_bp.before_request
def cek_sesi():
    if 'user_id' not in session or session.get('role') != 'kepala_gudang':
        flash("Akses ditolak! Silakan login sebagai Kepala Gudang.", "danger")
        return redirect(url_for('auth.login'))

@kepala_gudang_bp.route('/dashboard')
def dashboard():
    stok_data = get_stok_detail()
    transaksi_data = get_semua_transaksi()
    return render_template('kepala_gudang/dashboard.html',
                           stok_json=json.dumps(stok_data),
                           transactions_json=json.dumps(transaksi_data))

@kepala_gudang_bp.route('/instruksi')
def instruksi():
    kaca_data = get_stok_detail()
    return render_template('kepala_gudang/intruksi.html', kaca_json=json.dumps(kaca_data), kaca_data=kaca_data)

@kepala_gudang_bp.route('/buat_instruksi', methods=['POST'])
def buat_instruksi():
    id_kaca = request.form.get('id_kaca')
    jumlah = int(request.form.get('jumlah'))
    user_id = session.get('user_id')

    # 1. Insert ke instruksi_beli
    resp = supabase.table('instruksi_beli').insert({'id_user': user_id, 'status': 'Pending'}).execute()
    id_instruksi = resp.data[0]['id_instruksi_beli']

    # 2. Insert ke detail_instruksi
    supabase.table('detail_instruksi').insert({'id_kaca': id_kaca, 'id_instruksi_beli': id_instruksi, 'jumlah': jumlah}).execute()

    flash("Instruksi pesanan kaca berhasil dikirim ke Petugas Pencatatan!", "success")
    return redirect(url_for('kepala_gudang.instruksi'))

@kepala_gudang_bp.route('/tambahAkun')
def tambah_akun():
    # Ambil user yang statusnya masih 'pending' di perusahaan ini
    resp = supabase.table('users').select('*').eq('perusahaan', session.get('perusahaan')).eq('status', 'pending').execute()
    return render_template('kepala_gudang/tambahAkun.html', pending_users=resp.data)

@kepala_gudang_bp.route('/invite_api', methods=['POST'])
def invite_api():
    # API khusus untuk Generate URL Enkripsi ke WhatsApp
    role_tujuan = request.form.get('role_tujuan')
    token = generate_invite_token(session.get('perusahaan'), role_tujuan)
    link = url_for('auth.daftar_petugas', token=token, _external=True)
    return {"link": link}

@kepala_gudang_bp.route('/verifikasi/<id_user>/<keputusan>', methods=['GET'])
def melakukan_verifikasi(id_user, keputusan):
    AuthService.terima_atau_tolak_petugas(id_user, keputusan)
    flash(f"Akun petugas telah di-{keputusan}.", "success")
    return redirect(url_for('kepala_gudang.tambah_akun'))

@kepala_gudang_bp.route('/chatting')
def chatting():
    # Ambil daftar karyawan (Petugas) di satu perusahaan
    users = supabase.table('users').select('id_user, username, role').eq('perusahaan', session.get('perusahaan')).neq('id_user', session['user_id']).execute()
    return render_template('kepala_gudang/chatting.html', users=users.data)

@kepala_gudang_bp.route('/api/pesan', methods=['GET', 'POST'])
def handle_pesan():
    if request.method == 'POST':
        data = request.json
        supabase.table('pesan').insert({
            'id_pengirim': session['user_id'], 'id_penerima': data['id_penerima'], 'isi': data['isi']
        }).execute()
        return {"success": True}
    else:
        # GET pesan
        lawan_id = request.args.get('lawan_id')
        my_id = session['user_id']
        query = f"and(id_pengirim.eq.{my_id},id_penerima.eq.{lawan_id}),and(id_pengirim.eq.{lawan_id},id_penerima.eq.{my_id})"
        resp = supabase.table('pesan').select('*').or_(query).order('waktu').execute()
        return {"pesan": resp.data, "my_id": my_id}