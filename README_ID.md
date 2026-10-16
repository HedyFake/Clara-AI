# Clara Desktop Buddy v3.3.0 — asisten desktop Windows, keuangan, dan pasar saham

## Mulai cepat
1. Pasang Python **3.11 atau 3.12 (64-bit)** dari python.org (centang *tcl/tk* dan *Add to PATH*).
2. Klik **START_CLARA.bat**. Pertama kali ia memasang dependensi otomatis ke folder `.venv` (butuh internet), lalu membuka Clara.
3. Buka menu **Hemat & Pengaturan**, tempel API key OpenAI (opsional: *Ingat key* menyimpannya terenkripsi dengan Windows DPAPI).
4. Mau jadi satu file EXE? Jalankan **BUILD_EXE.bat** (di Windows). EXE lama dari versi 3.1 sengaja dihapus karena berisi kode lama.

## Apa yang baru
- **GUI baru**: sidebar, bubble chat, toggle bergaya pil, tema navy–cyan sesuai karakter. Tanpa gambar besar, tanpa animasi berat.
- **Karakter baru** memakai spritesheet 5×3 dari gambar ekspresi yang kamu unggah: 15 frame transparan berganti menurut mood dan status mendengar/berpikir/berbicara, dengan animasi ringan. Karakter tetap 2D; model 3D rigged dan lip-sync fonem belum tersedia. Mode kecil mengambang (klik = panel, dobel-klik = mode besar, klik kanan = menu) tetap dipertahankan.
- **Hemat token** (lihat di bawah) + meter biaya (dalam Rupiah) + batas biaya harian yang benar-benar menolak panggilan saat habis.
- **Mode Otonom** ⚡: rencana aman dijalankan tanpa dialog. Hal berisiko tetap minta konfirmasi.
- Aksi baru: buka file/folder (di folder pengguna), tulis file ke `Documents\ClaraWorkspace`, salin teks, pindah jendela, klik kanan.
- Perbaikan bug: koordinat klik kini diskalakan benar; suara (TTS) berjalan di thread sendiri; GUI tidak lagi tersendat.

## Cara Clara menghemat billing
| Teknik | Efek |
|---|---|
| Perintah lokal (buka app/situs, cari Google, jam/tanggal, screenshot, "ingat bahwa …", stop) | **0 token**, tanpa panggilan API |
| Cache jawaban identik (12 jam) | 0 token untuk pertanyaan berulang |
| Router model otomatis: obrolan → model murah; riset/audit/strategi/"Mikir keras" → model pintar | bayar mahal hanya bila perlu |
| Memori dipotong per relevansi (±750 karakter untuk obrolan umum, dulu hingga 12.000) | input jauh lebih kecil |
| Riwayat hanya disertakan untuk pesan lanjutan ("tadi", "lanjut", …) | tidak mengirim ulang riwayat tiap kali |
| `max_output_tokens` per jenis tugas (450 / 900 / 1800, laporan panjang hingga 8000) + gaya jawaban ringkas | output terkendali |
| Awalan prompt stabil + `prompt_cache_key` | memanfaatkan diskon cache OpenAI untuk prompt panjang |
| Screenshot detail rendah (detail tinggi hanya jika diminta "baca teks/angka") | gambar jauh lebih murah |
| Rencana otomasi 2 tahap: teks dulu, screenshot hanya bila perlu klik | banyak tugas tanpa gambar sama sekali |
| Live layar: diff lokal, jeda ≥45 dtk, maks 10 kiriman/sesi, model nano, jawaban ≤90 token | pemantauan murah |
| Web search `auto` (bukan wajib) | tidak membayar pencarian tiap panggilan |

Harga pada meter adalah **perkiraan** (bisa diubah di `settings.json` → `prices`). Angka resmi ada di dashboard OpenAI. Nama model default (`gpt-4.1-mini`, `gpt-4.1-nano`, `gpt-4.1`) bisa diganti di Hemat & Pengaturan sesuai model yang tersedia di akunmu.

## Kontrol komputer
- **Tanpa key**: perintah lokal tetap jalan ("buka chrome", "cari …").
- **Dengan key**: tugas lain disusun AI menjadi maks 12 aksi, divalidasi, lalu dijalankan (dengan pratinjau, atau langsung bila Mode Otonom aktif dan tugas tidak berisiko).
- **Sengaja tidak ada**: shell/PowerShell/CMD bebas, hak admin, menjalankan .exe/.bat/.ps1, menghapus data, password/OTP, transfer/pembelian/kirim pesan otomatis. Alasannya: Clara membaca layar dan web, dan teks di sana bisa berisi instruksi jahat (prompt injection). Tanpa batas itu, satu halaman web bisa membuat Clara menghapus file atau mengirim data. Semua aksi dicatat di `%LOCALAPPDATA%\ClaraDesktopBuddy\actions_log.csv`.
- **Berhenti darurat**: tombol ■ STOP di avatar, perintah "stop", tombol Hentikan otomasi, atau gerakkan mouse ke sudut kiri-atas.

## Memori
Profil + jurnal tersimpan lokal; **Memori → Ekspor ZIP** untuk membawa ke AI lain (gunakan `MEMORY_TRANSFER_PROMPT_ID.md`). Perintah cepat: "ingat bahwa …". Ini ringkasan konteks, bukan salinan model.

## Privasi
Suara → Google Speech (online). Layar/teks → OpenAI API hanya setelah izinmu. Jendela bank/password/chat dilewati oleh Live layar. Lihat `PRIVACY.md`.

## Status pengujian (jujur)
Teruji otomatis di Linux: tes `test_core.py` untuk logika inti dan modul baru (jumlah tes dihitung oleh runner), render karakter, serta smoke-test GUI Tkinter dengan jendela virtual. **Belum teruji di Windows asli**: tampilan GUI, transparansi avatar, mikrofon, TTS, DPAPI, otomasi klik, build EXE. Jalankan `CHECK_CLARA.bat` lalu coba fitur satu per satu.


## Baru di v3.3.0

### Karakter ekspresif
Spritesheet asli dan 15 frame potongan disertakan di `assets/`. Clara memilih ekspresi berdasarkan isi pesan dan status mendengar/berpikir/berbicara, dengan animasi ringan. Ini bukan model 3D dan tidak menjamin gerak bibir sesuai fonem suara.

### Keuangan pribadi dan bisnis
Halaman **Keuangan** menyimpan transaksi di SQLite lokal di `%LOCALAPPDATA%\ClaraDesktopBuddy\finance.db`. Kategori utama meliputi Active/Passive/Portfolio Income, Productive Spending beserta mesin income, tiga kelas Consumptive Spending, dan Consumptive with Productive Effect. Tersedia aset, penyusutan perkiraan, langganan, anggaran, tujuan, ringkasan, rekomendasi dan ekspor CSV. Perhitungan kategori dan ringkasan dasar berjalan lokal tanpa token. Jika kamu meminta AI Coach, ringkasan agregat keuangan yang tampil dikirim ke model untuk menjawab; jangan sertakan rahasia yang tidak dibutuhkan. Modul ini bukan pengganti akuntan, penasihat investasi, atau pengacara.

### Pasar Saham IHSG/BEI
Halaman **Pasar Saham** mengambil data quote/historis ticker BEI `.JK` dan indeks `^JKSE` melalui Yahoo Finance serta judul berita melalui Google News RSS saat internet tersedia. Watchlist dapat diubah, headline dapat dibuka, dan pembaruan otomatis opsional berjalan tiap 15 menit selama aplikasi terbuka. Data quote dapat tertunda atau tidak tersedia; label sinyal adalah heuristik dari tren, momentum, volatilitas, volume, dan kata kunci berita, bukan prediksi terkalibrasi atau jaminan hasil. Tidak ada order/beli/jual saham otomatis. Periksa ulang harga dan informasi di aplikasi sekuritas resmi sebelum mengambil keputusan.

### Token optimization playbook
`TOKEN_OPTIMIZATION_PLAYBOOK_ID.md` mendokumentasikan 60 teknik dari praktik yang aktif hingga eksperimen masa depan, beserta tautan ke topik GitHub. Tidak semua 60 teknik merupakan fitur yang aktif: status praktik, guardrail, dan eksperimen dibedakan secara eksplisit.

### Live desktop dan diskusi
Pemantauan layar tetap opt-in; hentikan sebelum membuka password, OTP, bank, pesan pribadi, atau data pelanggan. Clara dapat menerima diskusi saat otomasi GUI berjalan, tetapi tidak menjalankan dua request AI secara bersamaan dan tidak menjamin kendali universal atas semua aplikasi. Gunakan tombol STOP, periksa langkah berisiko, dan jangan aktifkan akses layar pada data rahasia.

## Build EXE Windows

File EXE tidak dibangun di lingkungan ini karena build saat ini dilakukan dari Linux tanpa PyInstaller/Windows runtime. Untuk membuat EXE pada Windows: pasang Python 3.11/3.12 64-bit lalu jalankan `BUILD_EXE.bat`. Atau push folder proyek ke GitHub dan jalankan workflow `.github/workflows/build-windows-exe.yml`; unduh hasil dari bagian **Actions → Artifacts**. Hasil build GitHub memerlukan konfigurasi repo kamu sendiri.
