import os
from flask import Flask, render_template, redirect, url_for

# Import blueprint lu di sini
from routes.kepala_gudang import kepala_gudang_bp
from routes.auth import auth_bp
from routes.petugas_pencatatan import petugas_pencatatan_bp
from routes.petugas_monitoring import petugas_monitoring_bp

base_dir = os.path.abspath(os.path.dirname(__file__))
views_dir = os.path.join(base_dir, 'views')
assets_dir = os.path.join(views_dir, 'assets')

app = Flask(__name__,
            template_folder=views_dir,
            static_folder=assets_dir,
            static_url_path='/assets')

# INI WAJIB BUAT SESSION/COOKIE
app.config['SECRET_KEY'] = 'kunci-rahasia-wms-kaca-2026'

# REGISTER SEMUA BLUEPRINT
app.register_blueprint(kepala_gudang_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(petugas_pencatatan_bp)
app.register_blueprint(petugas_monitoring_bp) 

@app.route('/')
def index():
    # Kalau buka web pertama kali, langsung tendang ke halaman login
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)