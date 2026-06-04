import json
from flask import Blueprint, render_template, request, session, flash, redirect, url_for, jsonify
from services.supabase_services import supabase

petugas_monitoring_bp = Blueprint('petugas_monitoring', __name__, url_prefix='/petugas_monitoring')

@petugas_monitoring_bp.before_request
def cek_sesi():
    if 'user_id' not in session or session.get('role') != 'petugas_monitoring':
        flash("Akses ditolak! Silakan login sebagai Petugas Monitoring.", "danger")
        return redirect(url_for('auth.login'))

# ==========================================
# 1. DASHBOARD MONITORING STOK
# ==========================================
@petugas_monitoring_bp.route('/dashboard')
def dashboard():
    try:
        res_stok = supabase.table('stok').select('*, kaca(*, kategori(*))').execute()
        raw_stok = res_stok.data if res_stok.data else []
    except Exception as e:
        print("Error fetch stok (Dashboard):", e)
        raw_stok = []

    return render_template('petugas_monitoring/dashboard.html', raw_stok=raw_stok)

# ==========================================
# 2. INSTRUKSI BELI
# ==========================================
@petugas_monitoring_bp.route('/instruksi', methods=['GET', 'POST'])
def instruksi():
    if request.method == 'POST':
        id_kaca = request.form.get('id_kaca')
        jumlah = request.form.get('jumlah')
        id_user = session.get('user_id')

        if not id_kaca or not jumlah:
            flash("Kaca dan jumlah wajib diisi!", "danger")
            return redirect(url_for('petugas_monitoring.instruksi'))

        try:
            res_instruksi = supabase.table('instruksi_beli').insert({
                'id_user': id_user,
                'status': 'Menunggu'
            }).execute()
            id_instruksi = res_instruksi.data[0]['id_instruksi_beli']

            supabase.table('detail_instruksi').insert({
                'id_instruksi_beli': id_instruksi,
                'id_kaca': id_kaca,
                'jumlah': int(jumlah)
            }).execute()

            flash("Instruksi beli kaca berhasil dikirim ke Pencatatan!", "success")
        except Exception as e:
            flash(f"Gagal mengirim instruksi: {str(e)}", "danger")

        return redirect(url_for('petugas_monitoring.instruksi'))

    try:
        res_kaca = supabase.table('kaca').select('*, kategori(*)').execute()
        list_kaca = res_kaca.data if res_kaca.data else []
    except Exception as e:
        list_kaca = []

    return render_template('petugas_monitoring/instruksi.html', list_kaca=list_kaca)

# ==========================================
# 3. LAPORAN KONDISI KACA (RUSAK)
# ==========================================
@petugas_monitoring_bp.route('/kondisi_kaca', methods=['GET', 'POST'])
def kondisi_kaca():
    if request.method == 'POST':
        id_kaca = request.form.get('id_kaca')
        catatan = request.form.get('catatan')
        id_user = session.get('user_id')
        jumlah_rusak = int(request.form.get('jumlah_rusak', 0))
        gambar_base64 = request.form.get('gambar_base64', '')

        if not id_kaca or not catatan:
            flash("Mohon pastikan Kategori, Ukuran, dan Ketebalan sudah terpilih!", "danger")
            return redirect(url_for('petugas_monitoring.kondisi_kaca'))

        try:
            supabase.table('laporan_kerusakan').insert({
                'id_kaca': id_kaca,
                'id_user': id_user,
                'catatan': catatan,
                'gambar': gambar_base64
            }).execute()

            if jumlah_rusak > 0:
                stok_rusak = supabase.table('stok').select('*').eq('id_kaca', id_kaca).eq('kondisi', 'Rusak').execute()
                if stok_rusak.data:
                    baru_rusak = stok_rusak.data[0]['jumlah'] + jumlah_rusak
                    supabase.table('stok').update({'jumlah': baru_rusak}).eq('id_stok', stok_rusak.data[0]['id_stok']).execute()
                else:
                    supabase.table('stok').insert({'id_kaca': id_kaca, 'jumlah': jumlah_rusak, 'kondisi': 'Rusak'}).execute()

                stok_baik = supabase.table('stok').select('*').eq('id_kaca', id_kaca).eq('kondisi', 'Baik').execute()
                if stok_baik.data:
                    baru_baik = max(0, stok_baik.data[0]['jumlah'] - jumlah_rusak)
                    supabase.table('stok').update({'jumlah': baru_baik}).eq('id_stok', stok_baik.data[0]['id_stok']).execute()

            flash("Laporan kerusakan dan foto berhasil dicatat ke database!", "success")
        except Exception as e:
            flash(f"Gagal melapor: {str(e)}", "danger")

        return redirect(url_for('petugas_monitoring.kondisi_kaca'))

    try:
        res_kaca = supabase.table('kaca').select('*, kategori(*)').execute()
        list_kaca = res_kaca.data if res_kaca.data else []
    except Exception as e:
        list_kaca = []

    return render_template('petugas_monitoring/kondisiKaca.html', list_kaca=list_kaca)

# ==========================================
# 4. CHATTING (UI & API)
# ==========================================
@petugas_monitoring_bp.route('/chatting')
def chatting():
    my_id = session.get('user_id')
    my_perusahaan = session.get('perusahaan') # Ambil nama perusahaan kita dari sesi login

    try:
        # FILTER PENTING: Hanya tarik user yang perusahaannya SAMA dan bukan kita sendiri
        res_user = supabase.table('users').select('id_user, username, role') \
            .eq('perusahaan', my_perusahaan) \
            .neq('id_user', my_id).execute()

        daftar_user = res_user.data if res_user.data else []
    except Exception as e:
        print("Error fetch user:", e)
        daftar_user = []

    return render_template('petugas_monitoring/chatting.html', daftar_user=daftar_user)

@petugas_monitoring_bp.route('/api/pesan', methods=['GET', 'POST'])
def api_pesan():
    my_id = session.get('user_id')

    if request.method == 'GET':
        lawan_id = request.args.get('lawan_id')
        if not lawan_id:
            return jsonify({'pesan': [], 'my_id': my_id})

        try:
            # Mengambil histori chat antara User A dan User B
            query = f"and(id_pengirim.eq.{my_id},id_penerima.eq.{lawan_id}),and(id_pengirim.eq.{lawan_id},id_penerima.eq.{my_id})"
            res = supabase.table('pesan').select('*').or_(query).order('waktu', desc=False).execute()
            return jsonify({'pesan': res.data, 'my_id': my_id})
        except Exception as e:
            print("Error get pesan:", e)
            return jsonify({'pesan': [], 'my_id': my_id})

    if request.method == 'POST':
        data = request.json
        id_penerima = data.get('id_penerima')
        isi = data.get('isi')

        if id_penerima and isi:
            try:
                supabase.table('pesan').insert({
                    'id_pengirim': my_id,
                    'id_penerima': id_penerima,
                    'isi': isi
                }).execute()
                return jsonify({'status': 'success'})
            except Exception as e:
                return jsonify({'status': 'error', 'msg': str(e)}), 500

        return jsonify({'status': 'error', 'msg': 'Data tidak lengkap'}), 400