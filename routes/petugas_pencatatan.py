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

petugas_pencatatan_bp = Blueprint(
    "petugas_pencatatan", __name__, url_prefix="/petugas_pencatatan"
)


@petugas_pencatatan_bp.before_request
def cek_sesi():
    if "user_id" not in session or session.get("role") != "petugas_pencatatan":
        flash("Akses ditolak! Silakan login sebagai Petugas Pencatatan.", "danger")
        return redirect(url_for("auth.login"))


@petugas_pencatatan_bp.route("/dashboard")
def dashboard():
    return redirect(url_for("petugas_pencatatan.kaca_masuk"))


# ==========================================
# 1. KACA MASUK (DARI INSTRUKSI MONITORING)
# ==========================================
@petugas_pencatatan_bp.route("/kaca_masuk", methods=["GET"])
def kaca_masuk():
    # Tarik instruksi beli yang statusnya 'Menunggu'
    try:
        res = (
            supabase.table("instruksi_beli")
            .select("*, users(username), detail_instruksi(*, kaca(*, kategori(*)))")
            .eq("status", "Menunggu")
            .order("tanggal", desc=True)
            .execute()
        )
        instruksi_list = res.data if res.data else []
    except Exception as e:
        print("Error fetch instruksi:", e)
        instruksi_list = []

    return render_template(
        "petugas_pencatatan/kacaMasuk.html", instruksi_list=instruksi_list
    )


@petugas_pencatatan_bp.route("/proses_masuk/<id_instruksi>", methods=["POST"])
def proses_masuk(id_instruksi):
    try:
        res_detail = (
            supabase.table("detail_instruksi")
            .select("*")
            .eq("id_instruksi_beli", id_instruksi)
            .execute()
        )

        if res_detail.data:
            for detail in res_detail.data:
                id_kaca = detail["id_kaca"]
                jumlah = detail["jumlah"]

                # Catat ke history kaca_masuk
                supabase.table("kaca_masuk").insert(
                    {"id_kaca": id_kaca, "jumlah": jumlah}
                ).execute()

                # Tambah stok "Baik"
                stok_baik = (
                    supabase.table("stok")
                    .select("*")
                    .eq("id_kaca", id_kaca)
                    .eq("kondisi", "Baik")
                    .execute()
                )
                if stok_baik.data:
                    baru_baik = stok_baik.data[0]["jumlah"] + jumlah
                    supabase.table("stok").update({"jumlah": baru_baik}).eq(
                        "id_stok", stok_baik.data[0]["id_stok"]
                    ).execute()
                else:
                    supabase.table("stok").insert(
                        {"id_kaca": id_kaca, "jumlah": jumlah, "kondisi": "Baik"}
                    ).execute()

        # Update status instruksi
        supabase.table("instruksi_beli").update({"status": "Selesai"}).eq(
            "id_instruksi_beli", id_instruksi
        ).execute()
        flash("Barang masuk berhasil dicatat dan stok gudang ditambahkan!", "success")
    except Exception as e:
        flash(f"Gagal memproses barang masuk: {str(e)}", "danger")

    return redirect(url_for("petugas_pencatatan.kaca_masuk"))


# ==========================================
# 2. KACA KELUAR (DARI PESANAN KEPALA GUDANG)
# ==========================================
@petugas_pencatatan_bp.route("/kaca_keluar", methods=["GET"])
def kaca_keluar():
    try:
        # Mengambil semua pesanan dari kepala gudang
        res = (
            supabase.table("kaca_keluar")
            .select("*, detail_kaca_keluar(*, kaca(*, kategori(*)))")
            .execute()
        )

        semua_pesanan = res.data if res.data else []
        # Filter manual di python untuk pesanan yang belum selesai
        pesanan_list = [
            p for p in semua_pesanan if p.get("status_pengiriman") != "Selesai"
        ]
    except Exception as e:
        print("Error fetch pesanan:", e)
        pesanan_list = []

    return render_template(
        "petugas_pencatatan/kacaKeluar.html", pesanan_list=pesanan_list
    )


@petugas_pencatatan_bp.route("/proses_keluar/<id_keluar>", methods=["POST"])
def proses_keluar(id_keluar):
    try:
        res_detail = (
            supabase.table("detail_kaca_keluar")
            .select("*")
            .eq("id_kaca_keluar", id_keluar)
            .execute()
        )

        if res_detail.data:
            for detail in res_detail.data:
                id_kaca = detail["id_kaca"]
                jumlah = detail["jumlah"]

                # Kurangi stok "Baik"
                stok_baik = (
                    supabase.table("stok")
                    .select("*")
                    .eq("id_kaca", id_kaca)
                    .eq("kondisi", "Baik")
                    .execute()
                )
                if stok_baik.data:
                    stok_sekarang = stok_baik.data[0]["jumlah"]
                    if stok_sekarang < jumlah:
                        flash(
                            f"Gagal: Stok Kaca tidak cukup untuk memproses pengiriman ini!",
                            "danger",
                        )
                        return redirect(url_for("petugas_pencatatan.kaca_keluar"))

                    baru_baik = stok_sekarang - jumlah
                    supabase.table("stok").update({"jumlah": baru_baik}).eq(
                        "id_stok", stok_baik.data[0]["id_stok"]
                    ).execute()
                else:
                    flash("Gagal: Stok kaca tidak ditemukan di gudang!", "danger")
                    return redirect(url_for("petugas_pencatatan.kaca_keluar"))

        # Update status pesanan jadi Selesai
        supabase.table("kaca_keluar").update({"status_pengiriman": "Selesai"}).eq(
            "id_kaca_keluar", id_keluar
        ).execute()
        flash(
            "Pengiriman barang keluar berhasil diproses dan stok dikurangi!", "success"
        )
    except Exception as e:
        flash(f"Gagal memproses barang keluar: {str(e)}", "danger")

    return redirect(url_for("petugas_pencatatan.kaca_keluar"))


# ==========================================
# 3. CHATTING (UI & API)
# ==========================================
@petugas_pencatatan_bp.route("/chatting")
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
        daftar_user = []

    return render_template("petugas_pencatatan/chatting.html", daftar_user=daftar_user)


@petugas_pencatatan_bp.route("/api/pesan", methods=["GET", "POST"])
def api_pesan():
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
        except:
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
