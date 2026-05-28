# File: app.py
import os
from flask import Flask, render_template
from routes.kepala_gudang import kepala_gudang_bp

base_dir = os.path.abspath(os.path.dirname(__file__))
views_dir = os.path.join(base_dir, 'views')
assets_dir = os.path.join(views_dir, 'assets')

app = Flask(__name__,
            template_folder=views_dir,
            static_folder=assets_dir,
            static_url_path='/assets')

# REGISTER BLUEPRINT KEPALA GUDANG
app.register_blueprint(kepala_gudang_bp)

@app.route('/')
def index():
    return render_template('pilih_role.html')

if __name__ == '__main__':
    app.run(debug=True)