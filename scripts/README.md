# Cara mengubah profil

Semua gambar di `assets/` dibuat oleh `build.py`, kecuali `snake-*.svg`
yang diperbarui otomatis setiap hari oleh workflow `.github/workflows/snake.yml`.

1. Edit bagian **DATA** di `scripts/build.py` (peran, tagline, proyek, toolkit, footer).
2. Bangun ulang aset:

   ```bash
   pip install fonttools brotli
   python3 scripts/build.py
   ```

3. Teks di luar gambar (Tentang Aku, link proyek, badge) ada di `README.md`.
4. Naikkan angka `?v=` di `README.md` (mis. `?v=4` → `?v=5`) supaya GitHub tidak memakai
   gambar lama dari cache, lalu commit & push ke `main`.

Generator akan berhenti dengan pesan error kalau ada teks yang terlalu panjang
untuk kartunya, jadi tinggal pendekkan teksnya lalu jalankan ulang.
