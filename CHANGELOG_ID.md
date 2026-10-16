# Changelog
## 3.3.0 (2026-10-15)
- Menggunakan 15 potongan ekspresi dari spritesheet karakter yang diunggah; ekspresi berganti menurut mood, status mendengar/berpikir/berbicara, dan animasi ringan.
- Menambahkan modul Keuangan lokal SQLite: pencatatan income/spending dengan taksonomi produktif/konsumtif, aset, langganan, anggaran, tujuan, ringkasan kesehatan, rekomendasi, dan ekspor CSV.
- Menambahkan Pasar Saham: indeks IHSG dan watchlist `.JK` melalui Yahoo Finance, berita Google News RSS, indikator tren/volatilitas sederhana, serta label ketidakpastian. Pembaruan berkala opsional 15 menit saat aplikasi terbuka.
- Memperluas prompt konsultan keuangan, kategori bisnis, serta jalur deep-long dan timeout yang sesuai.
- Menambahkan playbook 60 teknik optimasi token dengan pemisahan praktik aktif, pengaman, dan eksperimen.
- Menambahkan catatan privasi modul keuangan/pasar dan workflow GitHub Actions untuk membangun EXE Windows.
- Menambah tes otomatis untuk transaksi, dashboard, kategori, aset/langganan, ticker, sinyal sintetis, dan spritesheet.
- Batas penting: sinyal saham adalah heuristik informasional, bukan rekomendasi pasti; update perlu internet; EXE harus dibangun pada Windows atau workflow runner Windows.

## 3.2.0 (2026-10-14)
- Pecah kode: `clara_core.py` (logika), `clara_avatar.py` (karakter), `clara_buddy.py` (GUI); tambah `test_core.py` (41 tes).
- GUI baru + karakter baru berdasarkan gambar referensi; animasi di thread latar dengan cache frame.
- Hemat token: router lokal, cache jawaban, routing model, kompresi memori, batas output, detail gambar adaptif, planner 2 tahap, live layar hemat, meter & batas biaya harian.
- Mode Otonom; aksi baru (open_file/open_folder/write_file/copy_text/focus_window/right_click).
- Perbaikan: skala koordinat klik; TTS di thread sendiri (COM); `tool_choice` web tidak lagi "required"; pembuatan jendela/dialog dari thread kerja lewat antrean UI.
- Kunci API opsional tersimpan terenkripsi (DPAPI).
- EXE 3.1 dihapus; bangun ulang dengan BUILD_EXE.bat.
