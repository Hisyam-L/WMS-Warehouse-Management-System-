import os
from flask import Blueprint, render_template, request, session, flash, redirect, url_for, jsonify
from services.supabase_services import supabase

petugas_pencatatan_bp = Blueprint('petugas_pencatatan', __name__, url_prefix='/petugas_pencatatan')

@petugas_pencatatan_bp.before_request
def cek_sesi():
    if 'user_id' not in session or session.get('role') != 'petugas_pencatatan':
        flash("Akses ditolak! Silakan login sebagai Petugas Pencatatan.", "danger")
        return redirect(url_for('auth.login'))

# ==========================================
# 1. LAPOR BARANG MASUK
# ==========================================
@petugas_pencatatan_bp.route('/lapor_masuk', methods=['GET', 'POST'])
def lapor_masuk():
    my_perusahaan = session.get('perusahaan')

    if request.method == 'POST':
        id_kaca = request.form.get('id_kaca')
        jumlah = int(request.form.get('jumlah', 0))
        kat_man = request.form.get('kategori_manual')
        uk_man = request.form.get('ukuran_manual')
        teb_man = request.form.get('ketebalan_manual')
        gambar_url = request.form.get('gambar_url', '').strip()

        try:
            # Jika Kaca Baru / Manual
            if not id_kaca or id_kaca.strip() == "":
                res_kat = supabase.table('kategori').select('id_kategori').eq('kategori', kat_man).execute()
                id_kategori = res_kat.data[0]['id_kategori'] if res_kat.data else supabase.table('kategori').insert({'kategori': kat_man}).execute().data[0]['id_kategori']

                kaca_data_insert = {'id_kategori': id_kategori, 'ukuran': uk_man, 'ketebalan': teb_man}
                if gambar_url:
                    kaca_data_insert['gambar'] = gambar_url
                id_kaca = supabase.table('kaca').insert(kaca_data_insert).execute().data[0]['id_kaca']
            else:
                # Update gambar kaca jika ada URL baru
                if gambar_url:
                    supabase.table('kaca').update({'gambar': gambar_url}).eq('id_kaca', id_kaca).execute()

            # Catat ke kaca_masuk
            supabase.table('kaca_masuk').insert({'id_kaca': id_kaca, 'jumlah': jumlah, 'perusahaan': my_perusahaan}).execute()

            # Tambah Stok
            cek_stok = supabase.table('stok').select('*').eq('id_kaca', id_kaca).eq('perusahaan', my_perusahaan).eq('kondisi', 'Baik').execute()
            if cek_stok.data:
                stok_baru = cek_stok.data[0]['jumlah'] + jumlah
                supabase.table('stok').update({'jumlah': stok_baru}).eq('id_stok', cek_stok.data[0]['id_stok']).execute()
            else:
                supabase.table('stok').insert({'id_kaca': id_kaca, 'jumlah': jumlah, 'kondisi': 'Baik', 'perusahaan': my_perusahaan}).execute()

            flash("Barang masuk berhasil dicatat dan stok bertambah!", "success")
        except Exception as e:
            flash(f"Error: {e}", "danger")

        return redirect(url_for('petugas_pencatatan.lapor_masuk'))

    res_kaca = supabase.table('kaca').select('*, kategori(*)').execute()
    list_kaca = res_kaca.data if res_kaca.data else []
    return render_template('petugas_pencatatan/laporMasuk.html', list_kaca=list_kaca)

# ==========================================
# 2. INFO BARANG DIBELI (Dari Petugas Monitoring)
# ==========================================
@petugas_pencatatan_bp.route('/info_dibeli', methods=['GET', 'POST'])
def info_dibeli():
    my_perusahaan = session.get('perusahaan')

    # JIKA TOMBOL "TANDAI SUDAH DIBELI" DITEKAN
    if request.method == 'POST':
        id_instruksi = request.form.get('id_instruksi')
        try:
            res_detail = supabase.table('detail_instruksi').select('id_kaca, jumlah').eq('id_instruksi_beli', id_instruksi).execute()
            list_detail = res_detail.data if res_detail.data else []

            if list_detail:
                for item in list_detail:
                    id_kaca = item['id_kaca']
                    jumlah = int(item['jumlah'])

                    supabase.table('kaca_masuk').insert({
                        'id_kaca': id_kaca,
                        'jumlah': jumlah,
                        'perusahaan': my_perusahaan
                    }).execute()

                    cek_stok = supabase.table('stok').select('*').eq('id_kaca', id_kaca).eq('perusahaan', my_perusahaan).eq('kondisi', 'Baik').execute()

                    if cek_stok.data:
                        stok_baru = cek_stok.data[0]['jumlah'] + jumlah
                        supabase.table('stok').update({'jumlah': stok_baru}).eq('id_stok', cek_stok.data[0]['id_stok']).execute()
                    else:
                        supabase.table('stok').insert({
                            'id_kaca': id_kaca,
                            'jumlah': jumlah,
                            'kondisi': 'Baik',
                            'perusahaan': my_perusahaan
                        }).execute()

            # Status kita pastiin ubah ke kapital 'Selesai' (walau di HTML udh kebal filter)
            supabase.table('instruksi_beli').update({'status': 'Selesai'}).eq('id_instruksi_beli', id_instruksi).execute()

            flash("Barang masuk berhasil dicatat otomatis dan stok gudang telah bertambah!", "success")
        except Exception as e:
            flash(f"Gagal memproses pencatatan otomatis: {e}", "danger")

        return redirect(url_for('petugas_pencatatan.info_dibeli'))

    # AMBIL DATA UNTUK DITAMPILKAN DI HALAMAN (GET)
    try:
        res = supabase.table('instruksi_beli').select('*, detail_instruksi(*, kaca(*, kategori(*))), users(username)').eq('perusahaan', my_perusahaan).order('tanggal', desc=True).execute()
        instruksi_data = res.data if res.data else []
    except Exception as e:
        print(f"============== ERROR DATABASE INFO DIBELI: {e} ==============")
        flash("Gagal menarik data dari Database. Cek terminal untuk detail error!", "danger")
        instruksi_data = []

    return render_template('petugas_pencatatan/infoDibeli.html', instruksi_data=instruksi_data)

# ==========================================
# 3. LAPOR BARANG KELUAR (Instruksi dari Kepala Gudang)
# ==========================================
@petugas_pencatatan_bp.route('/lapor_keluar', methods=['GET', 'POST'])
def lapor_keluar():
    my_perusahaan = session.get('perusahaan')

    # Jika pencet tombol "Selesai"
    if request.method == 'POST':
        id_kaca_keluar = request.form.get('id_kaca_keluar')
        try:
            # Ubah status jadi Terkirim
            supabase.table('kaca_keluar').update({'status_pengiriman': 'Terkirim'}).eq('id_kaca_keluar', id_kaca_keluar).execute()
            flash("Barang berhasil ditandai sebagai Terkirim!", "success")
        except Exception as e:
            flash(f"Gagal memproses: {e}", "danger")
        return redirect(url_for('petugas_pencatatan.lapor_keluar'))

    try:
        # Tampilkan yang masih Pending saja
        res = supabase.table('kaca_keluar').select('*, detail_kaca_keluar(*, kaca(*, kategori(*)))').eq('perusahaan', my_perusahaan).eq('status_pengiriman', 'Pending').execute()
        keluar_data = res.data if res.data else []
    except Exception as e:
        keluar_data = []

    return render_template('petugas_pencatatan/laporKeluar.html', keluar_data=keluar_data)
# ==========================================
# 4. CHATTING (UI & API)
# ==========================================
@petugas_pencatatan_bp.route('/chatting')
def chatting():
    my_id = session.get('user_id')
    my_perusahaan = session.get('perusahaan')
    try:
        # Ambil daftar kontak (satu perusahaan, kecuali diri sendiri)
        res_user = supabase.table('users').select('id_user, username, role').eq('perusahaan', my_perusahaan).neq('id_user', my_id).execute()
        daftar_user = res_user.data if res_user.data else []
    except Exception as e:
        daftar_user = []
    return render_template('petugas_pencatatan/chatting.html', daftar_user=daftar_user)

@petugas_pencatatan_bp.route('/api/pesan', methods=['GET'])
def get_pesan():
    my_id = session.get('user_id')
    lawan_id = request.args.get('lawan_id')

    if not lawan_id:
        return jsonify({"pesan": [], "my_id": my_id})

    # Logika OR Supabase persis kayak Kepala Gudang
    query = f"and(id_pengirim.eq.{my_id},id_penerima.eq.{lawan_id}),and(id_pengirim.eq.{lawan_id},id_penerima.eq.{my_id})"
    resp = supabase.table('pesan').select('*').or_(query).order('waktu').execute()

    return jsonify({"pesan": resp.data, "my_id": my_id})

@petugas_pencatatan_bp.route('/api/pesan', methods=['POST'])
def kirim_pesan():
    my_id = session.get('user_id')
    data = request.json
    id_penerima = data.get('id_penerima')
    isi = data.get('isi')

    if not id_penerima or not isi:
        return jsonify({"status": "error", "message": "Data tidak lengkap"}), 400

    supabase.table('pesan').insert({
        'id_pengirim': my_id,
        'id_penerima': id_penerima,
        'isi': isi
    }).execute()

    return jsonify({"status": "success"})

# ==========================================
# 5. UPLOAD GAMBAR (bypass RLS via server)
# ==========================================
@petugas_pencatatan_bp.route('/api/upload_gambar', methods=['POST'])
def upload_gambar():
    if 'file' not in request.files:
        return jsonify({"error": "Tidak ada file yang dikirim"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nama file kosong"}), 400

    try:
        import random, string, time
        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
        filename = f"kaca_{int(time.time())}_{''.join(random.choices(string.ascii_lowercase, k=6))}.{ext}"
        file_bytes = file.read()
        content_type = file.content_type or f'image/{ext}'

        supabase.storage.from_('kaca-images').upload(
            path=filename,
            file=file_bytes,
            file_options={"content-type": content_type, "upsert": "true"}
        )

        supabase_url = os.environ.get('SUPABASE_URL', '')
        public_url = f"{supabase_url}/storage/v1/object/public/kaca-images/{filename}"
        return jsonify({"url": public_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500