from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from utils.helper import verify_invite_token
from services.supabase_services import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Udah bersih, nggak butuh bawa-bawa variabel supabase lagi
        hasil = AuthService.login_user(email, password)

        if hasil["success"]:
            user = hasil["user"]
            session['user_id'] = user["id_user"]
            session['username'] = user["username"]
            session['role'] = user["role"]
            session['perusahaan'] = user["perusahaan"]

            if user['role'] == 'kepala_gudang':
                return redirect(url_for('kepala_gudang.dashboard'))
            elif user['role'] == 'petugas_pencatatan':
                return redirect(url_for('petugas_pencatatan.dashboard'))
            elif user['role'] == 'petugas_monitoring':
                return redirect(url_for('petugas_monitoring.dashboard'))
        else:
            flash(hasil["message"], "danger")

    return render_template('auth/login.html')

@auth_bp.route('/daftar-kepala', methods=['GET', 'POST'])
def daftar_kepala():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        perusahaan = request.form.get('perusahaan')

        try:
            AuthService.register_kepala_gudang(username, email, password, perusahaan)
            flash("Akun Kepala Gudang berhasil dibuat! Silakan login.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            print(f"ERROR SAAT DAFTAR KEPALA GUDANG: {str(e)}")
            flash("Registrasi gagal. Cek terminal VS Code untuk detailnya.", "danger")

    return render_template('auth/daftar.html', role_konteks="kepala_gudang")

@auth_bp.route('/daftar-petugas', methods=['GET', 'POST'])
def daftar_petugas():
    token = request.args.get('token')
    if not token:
        return "Akses dilarang: Token tidak ditemukan.", 403

    token_data = verify_invite_token(token)
    if not token_data:
        return "Link undangan tidak valid atau sudah kedaluwarsa (24 jam).", 403

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            AuthService.register_petugas_pending(
                username, email, password,
                token_data['perusahaan'], token_data['role']
            )
            flash("Pendaftaran berhasil! Silakan tunggu verifikasi akun dari Kepala Gudang.", "info")
            return redirect(url_for('auth.login'))
        except Exception as e:
            print(f"ERROR SAAT DAFTAR PETUGAS: {str(e)}")
            flash("Registrasi gagal. Cek terminal VS Code untuk detailnya.", "danger")

    return render_template('auth/daftar.html',
                           role_konteks=token_data["role"],
                           perusahaan=token_data["perusahaan"])

@auth_bp.route('/logout')
def logout():
    session.clear() # Ini yang bikin cookie lu bersih dan gak stuck!
    flash("Anda telah berhasil logout.", "success")
    return redirect(url_for('auth.login'))