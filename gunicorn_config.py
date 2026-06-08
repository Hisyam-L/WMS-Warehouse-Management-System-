# gunicorn_config.py
bind = "0.0.0.0:10000"  # Port default Render adalah 10000
workers = 2             # Jumlah worker (sesuaikan dengan RAM, 2 sudah cukup untuk app ringan)
timeout = 120           # Timeout biar koneksi database gak gampang putus