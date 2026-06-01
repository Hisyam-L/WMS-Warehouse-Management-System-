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
    # Tarik data stok dari database
    res_stok = supabase.table('stok').select('jumlah, kondisi, kaca(kategori(kategori))').execute()

    stok_dict = {}
    if res_stok.data:
        for item in res_stok.data:
            if not item.get('kaca') or not item['kaca'].get('kategori'):
                continue

            kategori = item['kaca']['kategori']['kategori']
            kondisi = item.get('kondisi', 'Baik').lower()
            jumlah = item.get('jumlah', 0)

            if kategori not in stok_dict:
                stok_dict[kategori] = {'stock': 0, 'rusak': 0}

            if kondisi == 'rusak':
                stok_dict[kategori]['rusak'] += jumlah
            else:
                stok_dict[kategori]['stock'] += jumlah

    # Kirim data ke frontend (ubah dictionary python ke JSON string)
    return render_template('petugas_monitoring/dashboard.html', stok_data=json.dumps(stok_dict))


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
            # Bikin master instruksinya
            res_instruksi = supabase.table('instruksi_beli').insert({
                'id_user': id_user,
                'status': 'Menunggu'
            }).execute()

            id_instruksi = res_instruksi.data[0]['id_instruksi_beli']

            # Bikin detail kacanya
            supabase.table('detail_instruksi').insert({
                'id_instruksi_beli': id_instruksi,
                'id_kaca': id_kaca,
                'jumlah': int(jumlah)
            }).execute()

            flash("Instruksi beli kaca berhasil dikirim ke Pencatatan!", "success")
        except Exception as e:
            flash(f"Gagal mengirim instruksi: {str(e)}", "danger")

        return redirect(url_for('petugas_monitoring.instruksi'))

    res_kaca = supabase.table('kaca').select('id_kaca, ketebalan, ukuran, kategori(kategori)').execute()
    list_kaca = res_kaca.data if res_kaca.data else []
    return render_template('petugas_monitoring/intruksi.html', list_kaca=list_kaca)


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

        if not id_kaca or not catatan:
            flash("Semua field wajib diisi!", "danger")
            return redirect(url_for('petugas_monitoring.kondisi_kaca'))

        try:
            # Catat laporannya
            supabase.table('laporan_kerusakan').insert({
                'id_kaca': id_kaca,
                'id_user': id_user,
                'catatan': catatan
            }).execute()

            # (Opsional) Langsung update tambah stok 'Rusak' dan kurangi stok 'Baik'
            if jumlah_rusak > 0:
                # 1. Tambah data rusak
                stok_rusak = supabase.table('stok').select('*').eq('id_kaca', id_kaca).eq('kondisi', 'Rusak').execute()
                if stok_rusak.data:
                    baru_rusak = stok_rusak.data[0]['jumlah'] + jumlah_rusak
                    supabase.table('stok').update({'jumlah': baru_rusak}).eq('id_stok', stok_rusak.data[0]['id_stok']).execute()
                else:
                    supabase.table('stok').insert({'id_kaca': id_kaca, 'jumlah': jumlah_rusak, 'kondisi': 'Rusak'}).execute()

                # 2. Kurangi stok baik
                stok_baik = supabase.table('stok').select('*').eq('id_kaca', id_kaca).eq('kondisi', 'Baik').execute()
                if stok_baik.data:
                    baru_baik = max(0, stok_baik.data[0]['jumlah'] - jumlah_rusak)
                    supabase.table('stok').update({'jumlah': baru_baik}).eq('id_stok', stok_baik.data[0]['id_stok']).execute()

            flash("Laporan kerusakan berhasil dicatat!", "success")
        except Exception as e:
            flash(f"Gagal melapor: {str(e)}", "danger")

        return redirect(url_for('petugas_monitoring.kondisi_kaca'))

    res_kaca = supabase.table('kaca').select('id_kaca, ketebalan, ukuran, kategori(kategori)').execute()
    list_kaca = res_kaca.data if res_kaca.data else []
    return render_template('petugas_monitoring/kondisiKaca.html', list_kaca=list_kaca)


# ==========================================
# 4. CHATTING
# ==========================================
@petugas_monitoring_bp.route('/chatting')
def chatting():
    return render_template('petugas_monitoring/chatting.html')

# Rute ini lu sesuaikan dengan nama file HTML chat-nya yang bener (kalo ada)
@petugas_monitoring_bp.route('/chat/kepala')
def chat_kepala():
    return render_template('petugas_monitoring/kepalaGudang.html')

@petugas_monitoring_bp.route('/chat/pencatatan')
def chat_pencatatan():
    return render_template('petugas_monitoring/petugasPencatatan.html')