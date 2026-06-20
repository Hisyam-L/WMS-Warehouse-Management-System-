import os
import json
from flask import (
    Blueprint,
    render_template,
    request,
    session,
    flash,
    redirect,
    url_for,
    jsonify,
)
from services.supabase_services import supabase

petugas_monitoring_bp = Blueprint(
    "petugas_monitoring", __name__, url_prefix="/petugas_monitoring"
)


@petugas_monitoring_bp.before_request
def cek_sesi():
    if "user_id" not in session or session.get("role") != "petugas_monitoring":
        flash("Akses ditolak! Silakan login sebagai Petugas Monitoring.", "danger")
        return redirect(url_for("auth.login"))


# ==========================================
# 1. DASHBOARD MONITORING STOK
# ==========================================
@petugas_monitoring_bp.route("/dashboard")
def dashboard():
    my_perusahaan = session.get("perusahaan")  # PENTING BIAR GAK BOCOR
    try:
        # FILTER PERUSAHAAN DITAMBAHKAN DI SINI
        res_stok = (
            supabase.table("stok")
            .select("*, kaca(*, kategori(*))")
            .eq("perusahaan", my_perusahaan)
            .execute()
        )
        raw_stok = res_stok.data if res_stok.data else []
    except Exception as e:
        print("Error fetch stok (Dashboard):", e)
        raw_stok = []

    return render_template("petugas_monitoring/dashboard.html", raw_stok=raw_stok)


# ==========================================
# 2. INSTRUKSI BELI (UDAH SUPORT INPUT MANUAL)
# ==========================================
@petugas_monitoring_bp.route("/instruksi", methods=["GET", "POST"])
def instruksi():
    my_perusahaan = session.get("perusahaan")

    if request.method == "POST":
        id_kaca = request.form.get("id_kaca")
        jumlah = request.form.get("jumlah")
        id_user = session.get("user_id")

        # Nangkep inputan kalau user ngetik manual
        kategori_manual = request.form.get("kategori")
        ukuran_manual = request.form.get("ukuran")
        ketebalan_manual = request.form.get("ketebalan")

        if not jumlah:
            flash("Jumlah wajib diisi!", "danger")
            return redirect(url_for("petugas_monitoring.instruksi"))

        try:
            # KALAU DIKETIK MANUAL (id_kaca KOSONG)
            if not id_kaca or id_kaca.strip() == "":
                # 1. Cek atau Insert Kategori
                res_kat = (
                    supabase.table("kategori")
                    .select("id_kategori")
                    .eq("kategori", kategori_manual)
                    .execute()
                )
                if res_kat.data:
                    id_kategori = res_kat.data[0]["id_kategori"]
                else:
                    kat_baru = (
                        supabase.table("kategori")
                        .insert({"kategori": kategori_manual})
                        .execute()
                    )
                    id_kategori = kat_baru.data[0]["id_kategori"]

                # 2. Insert Kaca Baru
                kaca_baru = (
                    supabase.table("kaca")
                    .insert(
                        {
                            "id_kategori": id_kategori,
                            "ukuran": ukuran_manual,
                            "ketebalan": ketebalan_manual,
                        }
                    )
                    .execute()
                )
                id_kaca = kaca_baru.data[0]["id_kaca"]

            # INSERT INSTRUKSI BELI DENGAN PERUSAHAAN
            res_instruksi = (
                supabase.table("instruksi_beli")
                .insert(
                    {
                        "id_user": id_user,
                        "status": "Menunggu",
                        "perusahaan": my_perusahaan,
                    }
                )
                .execute()
            )
            id_instruksi = res_instruksi.data[0]["id_instruksi_beli"]

            # INSERT DETAIL INSTRUKSI
            supabase.table("detail_instruksi").insert(
                {
                    "id_instruksi_beli": id_instruksi,
                    "id_kaca": id_kaca,
                    "jumlah": int(jumlah),
                }
            ).execute()

            flash("Instruksi beli kaca berhasil dikirim ke Pencatatan!", "success")
        except Exception as e:
            flash(f"Gagal mengirim instruksi: {str(e)}", "danger")

        return redirect(url_for("petugas_monitoring.instruksi"))

    try:
        res_kaca = supabase.table("kaca").select("*, kategori(*)").execute()
        list_kaca = res_kaca.data if res_kaca.data else []
    except Exception as e:
        list_kaca = []

    return render_template("petugas_monitoring/instruksi.html", list_kaca=list_kaca)


# ==========================================
# 3. LAPORAN KONDISI KACA (RUSAK)
# ==========================================
@petugas_monitoring_bp.route("/kondisi_kaca", methods=["GET", "POST"])
def kondisi_kaca():
    my_perusahaan = session.get("perusahaan")

    if request.method == "POST":
        id_kaca = request.form.get("id_kaca")
        catatan = request.form.get("catatan")
        id_user = session.get("user_id")
        jumlah_rusak = int(request.form.get("jumlah_rusak", 0))
        gambar_url = request.form.get("gambar_url", "").strip()

        if not id_kaca or not catatan:
            flash(
                "Mohon pastikan Kategori, Ukuran, dan Ketebalan sudah terpilih!",
                "danger",
            )
            return redirect(url_for("petugas_monitoring.kondisi_kaca"))

        try:
            # Validasi backend: jumlah rusak tidak boleh melebihi stok baik
            if jumlah_rusak > 0:
                stok_baik_cek = (
                    supabase.table("stok")
                    .select("jumlah")
                    .eq("id_kaca", id_kaca)
                    .eq("kondisi", "Baik")
                    .eq("perusahaan", my_perusahaan)
                    .execute()
                )

                stok_tersedia = (
                    stok_baik_cek.data[0]["jumlah"] if stok_baik_cek.data else 0
                )
                if jumlah_rusak > stok_tersedia:
                    flash(
                        f"Jumlah rusak ({jumlah_rusak}) melebihi stok baik tersedia ({stok_tersedia} pcs)!",
                        "danger",
                    )
                    return redirect(url_for("petugas_monitoring.kondisi_kaca"))

            # Catat laporan kerusakan dengan URL gambar dari Supabase Storage
            laporan_data = {
                "id_kaca": id_kaca,
                "id_user": id_user,
                "catatan": catatan,
                "gambar": gambar_url if gambar_url else None,
            }
            supabase.table("laporan_kerusakan").insert(laporan_data).execute()

            if jumlah_rusak > 0:
                # Update atau insert stok RUSAK
                stok_rusak = (
                    supabase.table("stok")
                    .select("*")
                    .eq("id_kaca", id_kaca)
                    .eq("kondisi", "Rusak")
                    .eq("perusahaan", my_perusahaan)
                    .execute()
                )

                if stok_rusak.data:
                    baru_rusak = stok_rusak.data[0]["jumlah"] + jumlah_rusak
                    supabase.table("stok").update({"jumlah": baru_rusak}).eq(
                        "id_stok", stok_rusak.data[0]["id_stok"]
                    ).execute()
                else:
                    supabase.table("stok").insert(
                        {
                            "id_kaca": id_kaca,
                            "jumlah": jumlah_rusak,
                            "kondisi": "Rusak",
                            "perusahaan": my_perusahaan,
                        }
                    ).execute()

                # Kurangi stok BAIK
                stok_baik = (
                    supabase.table("stok")
                    .select("*")
                    .eq("id_kaca", id_kaca)
                    .eq("kondisi", "Baik")
                    .eq("perusahaan", my_perusahaan)
                    .execute()
                )

                if stok_baik.data:
                    baru_baik = max(0, stok_baik.data[0]["jumlah"] - jumlah_rusak)
                    supabase.table("stok").update({"jumlah": baru_baik}).eq(
                        "id_stok", stok_baik.data[0]["id_stok"]
                    ).execute()

            flash("Laporan kerusakan dan foto berhasil dicatat ke database!", "success")
        except Exception as e:
            flash(f"Gagal melapor: {str(e)}", "danger")

        return redirect(url_for("petugas_monitoring.kondisi_kaca"))

    # GET — hanya tampilkan kaca yang ada di stok BAIK perusahaan ini
    try:
        res_stok = (
            supabase.table("stok")
            .select("id_kaca, jumlah, kaca(*, kategori(*))")
            .eq("perusahaan", my_perusahaan)
            .eq("kondisi", "Baik")
            .execute()
        )

        seen = set()
        list_kaca = []
        for item in res_stok.data or []:
            kaca = item.get("kaca")
            if kaca and kaca["id_kaca"] not in seen:
                seen.add(kaca["id_kaca"])
                kaca["stok_baik"] = item.get("jumlah", 0)  # disisipkan untuk JS
                list_kaca.append(kaca)

    except Exception as e:
        print("Error fetch kaca (kondisi_kaca):", e)
        list_kaca = []

    return render_template("petugas_monitoring/kondisiKaca.html", list_kaca=list_kaca)


# ==========================================
# 4. CHATTING (UI & API)
# ==========================================
@petugas_monitoring_bp.route("/chatting")
def chatting():
    my_id = session.get("user_id")
    my_perusahaan = session.get("perusahaan")

    try:
        res_user = (
            supabase.table("users")
            .select("id_user, username, role")
            .eq("perusahaan", my_perusahaan)
            .neq("id_user", my_id)
            .execute()
        )
        daftar_user = res_user.data if res_user.data else []
    except Exception as e:
        print("Error fetch user:", e)
        daftar_user = []

    return render_template("petugas_monitoring/chatting.html", daftar_user=daftar_user)


@petugas_monitoring_bp.route("/api/pesan", methods=["GET", "POST"])
def api_pesan():
    # BIARKAN SAMA SEPERTI KODE LU, GAK ADA MASALAH DI SINI
    my_id = session.get("user_id")

    if request.method == "GET":
        lawan_id = request.args.get("lawan_id")
        if not lawan_id:
            return jsonify({"pesan": [], "my_id": my_id})

        try:
            query = f"and(id_pengirim.eq.{my_id},id_penerima.eq.{lawan_id}),and(id_pengirim.eq.{lawan_id},id_penerima.eq.{my_id})"
            res = (
                supabase.table("pesan")
                .select("*")
                .or_(query)
                .order("waktu", desc=False)
                .execute()
            )
            return jsonify({"pesan": res.data, "my_id": my_id})
        except Exception as e:
            return jsonify({"pesan": [], "my_id": my_id})

    if request.method == "POST":
        data = request.json
        id_penerima = data.get("id_penerima")
        isi = data.get("isi")

        if id_penerima and isi:
            try:
                supabase.table("pesan").insert(
                    {"id_pengirim": my_id, "id_penerima": id_penerima, "isi": isi}
                ).execute()
                return jsonify({"status": "success"})
            except Exception as e:
                return jsonify({"status": "error", "msg": str(e)}), 500

        return jsonify({"status": "error", "msg": "Data tidak lengkap"}), 400


# ==========================================
# 5. UPLOAD GAMBAR (bypass RLS via server)
# ==========================================
@petugas_monitoring_bp.route('/api/upload_gambar', methods=['POST'])
def upload_gambar():
    if 'file' not in request.files:
        return jsonify({"error": "Tidak ada file yang dikirim"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nama file kosong"}), 400

    try:
        import random, string, time
        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
        filename = f"laporan_{int(time.time())}_{''.join(random.choices(string.ascii_lowercase, k=6))}.{ext}"
        file_bytes = file.read()
        content_type = file.content_type or f'image/{ext}'

        supabase.storage.from_('laporan-images').upload(
            path=filename,
            file=file_bytes,
            file_options={"content-type": content_type, "upsert": "true"}
        )

        supabase_url = os.environ.get('SUPABASE_URL', '')
        public_url = f"{supabase_url}/storage/v1/object/public/laporan-images/{filename}"
        return jsonify({"url": public_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
