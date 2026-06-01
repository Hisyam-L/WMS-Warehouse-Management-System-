from flask import Blueprint, render_template, request, session, flash, redirect, url_for, jsonify
from services.supabase_services import supabase

petugas_pencatatan_bp = Blueprint('petugas_pencatatan', __name__, url_prefix='/petugas_pencatatan')

@petugas_pencatatan_bp.before_request
def cek_sesi():
    """Proteksi halaman khusus untuk role petugas_pencatatan"""
    if 'user_id' not in session or session.get('role') != 'petugas_pencatatan':
        flash("Akses ditolak! Silakan login terlebih dahulu.", "danger")
        return redirect(url_for('auth.login'))

@petugas_pencatatan_bp.route('/dashboard')
def dashboard():
    """Redirect utama dashboard ke pencatatan kaca masuk"""
    return redirect(url_for('petugas_pencatatan.kaca_masuk'))


# ==========================================
# 1. PENCATATAN KACA MASUK
# ==========================================
@petugas_pencatatan_bp.route('/kaca-masuk', methods=['GET', 'POST'])
def kaca_masuk():
    if request.method == 'POST':
        id_kaca = request.form.get('id_kaca')
        jumlah = request.form.get('jumlah')

        if not id_kaca or not jumlah:
            flash("Semua field harus diisi!", "danger")
            return redirect(url_for('petugas_pencatatan.kaca_masuk'))

        jumlah = int(jumlah)

        try:
            # Catat transaksi di tabel kaca_masuk
            supabase.table('kaca_masuk').insert({
                'id_kaca': id_kaca,
                'jumlah': jumlah
            }).execute()

            # Update atau Tambah Stok Utama
            cek_stok = supabase.table('stok').select('*').eq('id_kaca', id_kaca).execute()

            if cek_stok.data:
                stok_baru = cek_stok.data[0]['jumlah'] + jumlah
                supabase.table('stok').update({'jumlah': stok_baru}).eq('id_kaca', id_kaca).execute()
            else:
                supabase.table('stok').insert({
                    'id_kaca': id_kaca,
                    'jumlah': jumlah,
                    'kondisi': 'Baik'
                }).execute()

            flash("Data kaca masuk berhasil dicatat dan stok diperbarui!", "success")
        except Exception as e:
            flash(f"Gagal mencatat data: {str(e)}", "danger")

        return redirect(url_for('petugas_pencatatan.kaca_masuk'))

    # Ambil list master data kaca untuk drop-down pilihan di form
    res_kaca = supabase.table('kaca').select('id_kaca, ketebalan, ukuran, kategori(kategori)').execute()
    list_kaca = res_kaca.data if res_kaca.data else []

    return render_template('petugas_pencatatan/kacaMasuk.html', list_kaca=list_kaca)


# ==========================================
# 2. PENCATATAN KACA KELUAR
# ==========================================
@petugas_pencatatan_bp.route('/lapor-keluar', methods=['GET', 'POST'])
def lapor_keluar():
    if request.method == 'POST':
        nama_pembeli = request.form.get('nama_pembeli')
        no_hp = request.form.get('no_hp')
        alamat = request.form.get('alamat')
        id_kaca = request.form.get('id_kaca')
        jumlah = request.form.get('jumlah')
        status_pembayaran = request.form.get('status_pembayaran', 'Belum Dibayar')

        if not nama_pembeli or not id_kaca or not jumlah:
            flash("Data utama laporan keluar tidak boleh kosong!", "danger")
            return redirect(url_for('petugas_pencatatan.lapor_keluar'))

        jumlah = int(jumlah)

        try:
            # Cek ketersediaan stok sebelum dikurangi
            cek_stok = supabase.table('stok').select('*').eq('id_kaca', id_kaca).execute()
            stok_sekarang = cek_stok.data[0]['jumlah'] if cek_stok.data else 0

            if stok_sekarang < jumlah:
                flash(f"Stok tidak cukup! Sisa stok saat ini hanya {stok_sekarang} buah.", "danger")
                return redirect(url_for('petugas_pencatatan.lapor_keluar'))

            # Insert ke tabel induk kaca_keluar (Default status pengiriman dari kepala: Menunggu Dikirim)
            res_keluar = supabase.table('kaca_keluar').insert({
                'nama_pembeli': nama_pembeli,
                'no_hp': no_hp,
                'alamat': alamat,
                'status_pembayaran': status_pembayaran,
                'status_pengiriman': 'Menunggu Dikirim'
            }).execute()

            id_kaca_keluar = res_keluar.data[0]['id_kaca_keluar']

            # Insert ke tabel detail_kaca_keluar
            supabase.table('detail_kaca_keluar').insert({
                'id_kaca': id_kaca,
                'id_kaca_keluar': id_kaca_keluar,
                'jumlah': jumlah,
                'kondisi': 'Baik'
            }).execute()

            # Potong jumlah stok di gudang
            stok_akhir = stok_sekarang - jumlah
            supabase.table('stok').update({'jumlah': stok_akhir}).eq('id_kaca', id_kaca).execute()

            flash("Laporan pengeluaran kaca berhasil dibuat!", "success")
            return redirect(url_for('petugas_pencatatan.proses_keluar'))
        except Exception as e:
            flash(f"Gagal memproses pengeluaran: {str(e)}", "danger")
            return redirect(url_for('petugas_pencatatan.lapor_keluar'))

    res_kaca = supabase.table('kaca').select('id_kaca, ketebalan, ukuran, kategori(kategori)').execute()
    list_kaca = res_kaca.data if res_kaca.data else []
    return render_template('petugas_pencatatan/laporCatatKeluar.html', list_kaca=list_kaca)


# ==========================================
# 3. PROSES KACA KELUAR & INSTRUKSI KIRIM KEPALA
# ==========================================
@petugas_pencatatan_bp.route('/proses-keluar', methods=['GET', 'POST'])
def proses_keluar():
    """Halaman memantau status pesanan kirim dan menyelesaikan tugas kirim dari kepala"""
    if request.method == 'POST':
        id_kaca_keluar = request.form.get('id_kaca_keluar')
        try:
            # Petugas Pencatatan menandai instruksi pengiriman barang dari Kepala Gudang telah SELESAI dikirim
            supabase.table('kaca_keluar').update({
                'status_pengiriman': 'Selesai Dikirim'
            }).eq('id_kaca_keluar', id_kaca_keluar).execute()

            flash("Status pengiriman berhasil diperbarui menjadi Selesai!", "success")
        except Exception as e:
            flash(f"Gagal memperbarui status: {str(e)}", "danger")
        return redirect(url_for('petugas_pencatatan.proses_keluar'))

    # Ambil seluruh list kaca keluar beserta relasi detail itemnya
    res_proses = supabase.table('kaca_keluar').select('*, detail_kaca_keluar(*, kaca(*, kategori(*)))').execute()
    data_keluar = res_proses.data if res_proses.data else []
    return render_template('petugas_pencatatan/prosesKacaKeluar.html', data_keluar=data_keluar)


@petugas_pencatatan_bp.route('/akan-keluar')
def akan_keluar():
    """Daftar antrean barang yang akan keluar/dijadwalkan"""
    res_akan_keluar = supabase.table('kaca_keluar').select('*, detail_kaca_keluar(*, kaca(*))').eq('status_pengiriman', 'Menunggu Dikirim').execute()
    list_akan_keluar = res_akan_keluar.data if res_akan_keluar.data else []
    return render_template('petugas_pencatatan/akanKeluar.html', list_akan_keluar=list_akan_keluar)


# ==========================================
# 4. INSTRUKSI BELI DARI PETUGAS MONITORING
# ==========================================
@petugas_pencatatan_bp.route('/akan-atau-sudah-dibeli', methods=['GET', 'POST'])
def akan_atau_sudah_dibeli():
    if request.method == 'POST':
        id_instruksi_beli = request.form.get('id_instruksi_beli')
        status_opsi = request.form.get('status', 'Sudah Dibeli') # Aksi penandaan barang belanja

        try:
            # 1. Update status di tabel instruksi_beli induk
            supabase.table('instruksi_beli').update({
                'status': status_opsi
            }).eq('id_instruksi_beli', id_instruksi_beli).execute()

            # 2. Sinkronisasi atau buat data record pelaporan di tabel pembelian
            cek_beli = supabase.table('pembelian').select('*').eq('id_instruksi_beli', id_instruksi_beli).execute()
            if cek_beli.data:
                supabase.table('pembelian').update({'status': 'Selesai'}).eq('id_instruksi_beli', id_instruksi_beli).execute()
            else:
                supabase.table('pembelian').insert({
                    'id_instruksi_beli': id_instruksi_beli,
                    'status': 'Selesai'
                }).execute()

            flash("Instruksi pembelian berhasil diperbarui statusnya!", "success")
        except Exception as e:
            flash(f"Gagal memperbarui status instruksi beli: {str(e)}", "danger")
        return redirect(url_for('petugas_pencatatan.akan_atau_sudah_dibeli'))

    # Ambil instruksi beli dari user monitoring beserta detail barang kacanya
    res_instruksi = supabase.table('instruksi_beli').select('*, users(username), detail_instruksi(*, kaca(*, kategori(*)))').execute()
    data_instruksi = res_instruksi.data if res_instruksi.data else []

    return render_template('petugas_pencatatan/akanAtauSudahDibeli.html', instruksi=data_instruksi)


# ==========================================
# 5. INTEGRASI DISKUSI CHATTING (KEPALA & MONITORING)
# ==========================================
@petugas_pencatatan_bp.route('/chatting')
def chatting():
    """Menu utama room list chattings"""
    return render_template('petugas_pencatatan/chatting.html')


@petugas_pencatatan_bp.route('/chat/kepala-gudang')
def chat_kepala():
    """Halaman chat personal ke Kepala Gudang"""
    my_perusahaan = session.get('perusahaan')
    # Cari user kepala gudang di perusahaan yang sama
    res_user = supabase.table('users').select('id_user, username, role').eq('perusahaan', my_perusahaan).eq('role', 'kepala_gudang').execute()
    target_user = res_user.data[0] if res_user.data else None
    return render_template('petugas_pencatatan/kepalaGudang.html', target=target_user)


@petugas_pencatatan_bp.route('/chat/petugas-monitoring')
def chat_monitoring():
    """Halaman chat personal ke Petugas Monitoring"""
    my_perusahaan = session.get('perusahaan')
    # Cari user petugas monitoring di perusahaan yang sama
    res_user = supabase.table('users').select('id_user, username, role').eq('perusahaan', my_perusahaan).eq('role', 'petugas_monitoring').execute()
    target_user = res_user.data[0] if res_user.data else None
    return render_template('petugas_pencatatan/petugasMonitoring.html', target=target_user)


# ==========================================
# API ENDPOINT CHAT (REALTIME ASYNC / FETCH AJAX)
# ==========================================
@petugas_pencatatan_bp.route('/api/pesan', methods=['GET', 'POST'])
def api_pesan():
    my_id = session.get('user_id')

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        id_penerima = data.get('lawan_id') or data.get('id_penerima')
        isi = data.get('isi')

        if not id_penerima or not isi:
            return jsonify({"success": False, "message": "Penerima atau isi pesan kosong"}), 400

        try:
            supabase.table('pesan').insert({
                'id_pengirim': my_id,
                'id_penerima': id_penerima,
                'isi': isi
            }).execute()
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    # Method GET: Ambil history percakapan antara saya dan target lawan chat
    lawan_id = request.args.get('lawan_id')
    if not lawan_id:
        return jsonify({"pesan": [], "my_id": my_id})

    try:
        query_filter = f"and(id_pengirim.eq.{my_id},id_penerima.eq.{lawan_id}),and(id_pengirim.eq.{lawan_id},id_penerima.eq.{my_id})"
        resp = supabase.table('pesan').select('*').or_(query_filter).order('waktu', ascending=True).execute()
        return jsonify({"pesan": resp.data, "my_id": my_id})
    except Exception as e:
        return jsonify({"pesan": [], "error": str(e), "my_id": my_id})