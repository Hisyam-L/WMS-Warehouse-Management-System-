import json
from flask import Blueprint, render_template, redirect, url_for, session, flash, request, jsonify
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

# INI RUTE YANG HILANG DAN BIKIN ERROR 404
@kepala_gudang_bp.route('/buat_instruksi', methods=['POST'])
def buat_instruksi():
    id_kaca = request.form.get('id_kaca')
    jumlah = int(request.form.get('jumlah'))
    user_id = session.get('user_id')

    # 1. Insert ke tabel instruksi_beli
    resp = supabase.table('instruksi_beli').insert({
        'id_user': user_id,
        'status': 'Pending'
    }).execute()
    id_instruksi = resp.data[0]['id_instruksi_beli']

    # 2. Insert ke detail_instruksi
    supabase.table('detail_instruksi').insert({
        'id_kaca': id_kaca,
        'id_instruksi_beli': id_instruksi,
        'jumlah': jumlah
    }).execute()

    # 3. LOGIKA POTONG STOK OTOMATIS
    stok_resp = supabase.table('stok').select('jumlah').eq('id_kaca', id_kaca).execute()

    if stok_resp.data:
        stok_sekarang = stok_resp.data[0]['jumlah']
        stok_baru = stok_sekarang - jumlah

        # Cegah kalau pesanan melebihi stok yang ada
        if stok_baru < 0:
            flash("Stok tidak mencukupi untuk instruksi ini!", "danger")
        else:
            supabase.table('stok').update({'jumlah': stok_baru}).eq('id_kaca', id_kaca).execute()
            flash("Instruksi berhasil dibuat!", "success")

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
    my_id = session.get('user_id')
    my_perusahaan = session.get('perusahaan') # 1. Ambil nama perusahaan user yang lagi login

    # 2. Filter .eq('perusahaan', my_perusahaan) biar nggak nyampur sama perusahaan lain
    users_resp = supabase.table('users').select('id_user, username, role') \
        .eq('perusahaan', my_perusahaan) \
        .neq('id_user', my_id) \
        .execute()

    daftar_user = users_resp.data if users_resp.data else []

    return render_template('kepala_gudang/chatting.html', daftar_user=daftar_user)

@kepala_gudang_bp.route('/api/pesan', methods=['GET'])
def get_pesan():
    my_id = session.get('user_id')
    lawan_id = request.args.get('lawan_id')

    if not lawan_id:
        return jsonify({"pesan": [], "my_id": my_id})

    # Logika OR Supabase: (pengirim=Saya DAN penerima=Dia) ATAU (pengirim=Dia DAN penerima=Saya)
    query = f"and(id_pengirim.eq.{my_id},id_penerima.eq.{lawan_id}),and(id_pengirim.eq.{lawan_id},id_penerima.eq.{my_id})"
    resp = supabase.table('pesan').select('*').or_(query).order('waktu').execute()

    return jsonify({"pesan": resp.data, "my_id": my_id})

@kepala_gudang_bp.route('/api/pesan', methods=['POST'])
def kirim_pesan():
    my_id = session.get('user_id')
    data = request.json
    lawan_id = data.get('id_penerima')
    isi = data.get('isi')

    if not lawan_id or not isi:
        return jsonify({"error": "Data tidak valid"}), 400

    # Insert data ke tabel pesan sesuai skema
    supabase.table('pesan').insert({
        'id_pengirim': my_id,
        'id_penerima': lawan_id,
        'isi': isi
    }).execute()

    return jsonify({"status": "sukses"})