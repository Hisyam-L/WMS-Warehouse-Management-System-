from flask import Blueprint, render_template, request, session, flash, redirect, url_for, jsonify
from services.supabase_services import supabase

petugas_pencatatan_bp = Blueprint('petugas_pencatatan', __name__, url_prefix='/petugas_pencatatan')

@petugas_pencatatan_bp.before_request
def cek_sesi():
    if 'user_id' not in session or session.get('role') != 'petugas_pencatatan':
        flash("Akses ditolak! Silakan login sebagai Petugas Pencatatan.", "danger")
        return redirect(url_for('auth.login'))

@petugas_pencatatan_bp.route('/dashboard')
def dashboard():
    return redirect(url_for('petugas_pencatatan.kaca_masuk'))

# --- FITUR KACA MASUK ---
@petugas_pencatatan_bp.route('/kaca-masuk', methods=['GET', 'POST'])
def kaca_masuk():
    if request.method == 'POST':
        id_kaca = request.form.get('id_kaca')
        jumlah = int(request.form.get('jumlah', 0))

        if id_kaca and jumlah > 0:
            # 1. Catat di tabel kaca_masuk
            supabase.table('kaca_masuk').insert({'id_kaca': id_kaca, 'jumlah': jumlah}).execute()

            # 2. Update atau tambah stok
            stok_ada = supabase.table('stok').select('*').eq('id_kaca', id_kaca).execute()
            if stok_ada.data:
                stok_baru = stok_ada.data[0]['jumlah'] + jumlah
                supabase.table('stok').update({'jumlah': stok_baru}).eq('id_kaca', id_kaca).execute()
            else:
                supabase.table('stok').insert({'id_kaca': id_kaca, 'jumlah': jumlah, 'kondisi': 'Baik'}).execute()

            flash("Kaca masuk berhasil dicatat!", "success")
            return redirect(url_for('petugas_pencatatan.kaca_masuk'))

    # Ambil list kaca untuk dropdown form
    list_kaca = supabase.table('kaca').select('id_kaca, ketebalan, ukuran, kategori(kategori)').execute()
    return render_template('petugas_pencatatan/kacaMasuk.html', list_kaca=list_kaca.data)

# --- FITUR KACA KELUAR ---
@petugas_pencatatan_bp.route('/lapor-keluar', methods=['GET', 'POST'])
def lapor_keluar():
    if request.method == 'POST':
        nama_pembeli = request.form.get('nama_pembeli')
        no_hp = request.form.get('no_hp')
        alamat = request.form.get('alamat')
        id_kaca = request.form.get('id_kaca')
        jumlah = int(request.form.get('jumlah', 0))

        if nama_pembeli and id_kaca and jumlah > 0:
            # 1. Bikin record di kaca_keluar
            kaca_keluar_resp = supabase.table('kaca_keluar').insert({
                'nama_pembeli': nama_pembeli,
                'no_hp': no_hp,
                'alamat': alamat,
                'status_pembayaran': request.form.get('status_pembayaran', 'Belum Dibayar'),
                'status_pengiriman': 'Menunggu Dikirim'
            }).execute()

            id_keluar = kaca_keluar_resp.data[0]['id_kaca_keluar']

            # 2. Bikin detail_kaca_keluar
            supabase.table('detail_kaca_keluar').insert({
                'id_kaca': id_kaca,
                'id_kaca_keluar': id_keluar,
                'jumlah': jumlah,
                'kondisi': 'Baik'
            }).execute()

            # 3. Kurangi stok
            stok_ada = supabase.table('stok').select('*').eq('id_kaca', id_kaca).execute()
            if stok_ada.data:
                stok_baru = max(0, stok_ada.data[0]['jumlah'] - jumlah)
                supabase.table('stok').update({'jumlah': stok_baru}).eq('id_kaca', id_kaca).execute()

            flash("Kaca keluar berhasil diproses!", "success")
            return redirect(url_for('petugas_pencatatan.proses_keluar'))

    list_kaca = supabase.table('kaca').select('id_kaca, ketebalan, ukuran').execute()
    return render_template('petugas_pencatatan/laporCatatKeluar.html', list_kaca=list_kaca.data)

@petugas_pencatatan_bp.route('/proses-keluar')
def proses_keluar():
    # Ambil list kaca yang mau keluar untuk dipantau
    data_keluar = supabase.table('kaca_keluar').select('*, detail_kaca_keluar(*)').execute()
    return render_template('petugas_pencatatan/prosesKacaKeluar.html', data_keluar=data_keluar.data)

@petugas_pencatatan_bp.route('/akan-keluar')
def akan_keluar():
    return render_template('petugas_pencatatan/akanKeluar.html')

# --- FITUR INSTRUKSI BELI DARI MONITORING ---
@petugas_pencatatan_bp.route('/akan-atau-sudah-dibeli', methods=['GET', 'POST'])
def akan_atau_sudah_dibeli():
    if request.method == 'POST':
        id_instruksi = request.form.get('id_instruksi')
        # Ganti status di instruksi_beli dan pembelian jadi selesai/sudah dibeli
        supabase.table('instruksi_beli').update({'status': 'Sudah Dibeli'}).eq('id_instruksi_beli', id_instruksi).execute()

        cek_pembelian = supabase.table('pembelian').select('*').eq('id_instruksi_beli', id_instruksi).execute()
        if cek_pembelian.data:
            supabase.table('pembelian').update({'status': 'Selesai'}).eq('id_instruksi_beli', id_instruksi).execute()
        else:
            supabase.table('pembelian').insert({'id_instruksi_beli': id_instruksi, 'status': 'Selesai'}).execute()

        flash("Barang sudah ditandai sebagai dibeli!", "success")
        return redirect(url_for('petugas_pencatatan.akan_atau_sudah_dibeli'))

    # Ambil data instruksi_beli
    instruksi = supabase.table('instruksi_beli').select('*, detail_instruksi(*, kaca(*))').execute()
    return render_template('petugas_pencatatan/akanAtauSudahDibeli.html', instruksi=instruksi.data)

# --- FITUR CHATTING ---
@petugas_pencatatan_bp.route('/chatting')
def chatting():
    return render_template('petugas_pencatatan/chatting.html')

@petugas_pencatatan_bp.route('/chat/kepala-gudang')
def chat_kepala():
    return render_template('petugas_pencatatan/kepalaGudang.html')

@petugas_pencatatan_bp.route('/chat/petugas-monitoring')
def chat_monitoring():
    return render_template('petugas_pencatatan/petugasMonitoring.html')

@petugas_pencatatan_bp.route('/api/pesan', methods=['GET', 'POST'])
def api_pesan():
    my_id = session.get('user_id')

    if request.method == 'POST':
        lawan_id = request.json.get('lawan_id')
        isi = request.json.get('isi')
        if not isi or not lawan_id:
            return jsonify({"error": "Data ga lengkap"}), 400

        supabase.table('pesan').insert({'id_pengirim': my_id, 'id_penerima': lawan_id, 'isi': isi}).execute()
        return jsonify({"success": True})

    lawan_id = request.args.get('lawan_id')
    if not lawan_id:
        return jsonify({"pesan": [], "my_id": my_id})

    query = f"and(id_pengirim.eq.{my_id},id_penerima.eq.{lawan_id}),and(id_pengirim.eq.{lawan_id},id_penerima.eq.{my_id})"
    resp = supabase.table('pesan').select('*').or_(query).order('waktu').execute()
    return jsonify({"pesan": resp.data, "my_id": my_id})