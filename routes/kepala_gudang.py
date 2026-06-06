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
    my_perusahaan = session.get('perusahaan') # Ambil perusahaan dari session

    stok_data = get_stok_detail(my_perusahaan) # Lempar ke fungsi
    transaksi_data = get_semua_transaksi(my_perusahaan) # Lempar ke fungsi

    return render_template('kepala_gudang/dashboard.html',
                           stok_json=json.dumps(stok_data),
                           transactions_json=json.dumps(transaksi_data))

@kepala_gudang_bp.route('/instruksi')
def instruksi():
    my_perusahaan = session.get('perusahaan') # Ambil perusahaan
    kaca_data = get_stok_detail(my_perusahaan) # Filter stok kaca buat modal instruksi
    return render_template('kepala_gudang/intruksi.html', kaca_json=json.dumps(kaca_data), kaca_data=kaca_data)

@kepala_gudang_bp.route('/buat_instruksi', methods=['POST'])
def buat_instruksi():
    my_perusahaan = session.get('perusahaan') # Ambil perusahaan buat disimpen ke tabel

    id_kaca = request.form.get('id_kaca')
    jumlah = int(request.form.get('jumlah'))
    nama_pembeli = request.form.get('nama_pembeli')
    status_pembayaran = request.form.get('status_pembayaran')
    no_hp_pembeli = request.form.get('no_hp_pembeli')
    alamat = request.form.get('alamat')

    # 1. Insert ke tabel kaca_keluar (wajib masukin 'perusahaan' ke DB)
    resp = supabase.table('kaca_keluar').insert({
        'perusahaan': my_perusahaan,      # <--- BIKIN DATA INI GAK BOCOR KE PERUSAHAAN LAIN
        'nama_pembeli': nama_pembeli,
        'no_hp': no_hp_pembeli,
        'alamat': alamat,
        'status_pembayaran': status_pembayaran,
        'status_pengiriman': 'Pending'
    }).execute()

    id_kaca_keluar = resp.data[0]['id_kaca_keluar']

    # 2. Insert ke detail_kaca_keluar
    supabase.table('detail_kaca_keluar').insert({
        'id_kaca': id_kaca,
        'id_kaca_keluar': id_kaca_keluar,
        'jumlah': jumlah
    }).execute()

    # 3. LOGIKA POTONG STOK OTOMATIS (Aman, ini udah per row ID Kacanya langsung)
    stok_resp = supabase.table('stok').select('jumlah').eq('id_kaca', id_kaca).execute()

    if stok_resp.data:
        stok_sekarang = stok_resp.data[0]['jumlah']
        stok_baru = stok_sekarang - jumlah

        if stok_baru < 0:
            flash("Stok tidak mencukupi untuk instruksi pesanan ini!", "danger")
        else:
            supabase.table('stok').update({'jumlah': stok_baru}).eq('id_kaca', id_kaca).execute()
            flash("Instruksi pesanan berhasil dibuat!", "success")

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