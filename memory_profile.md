# Profil Memori Portabel Clara — Hedy

**Versi:** 1.1  
**Dibuat:** 15 Oktober 2026  
**Tujuan:** ringkasan konteks yang bisa dibawa ke asisten AI lain. Ini bukan transkrip lengkap dan bukan salinan model AI. Verifikasi informasi yang berubah sebelum bertindak.

## Identitas dan preferensi kerja
- Nama panggilan percakapan: Hedy.
- Bahasa utama: Bahasa Indonesia.
- Suka jawaban rinci, tajam, kritis, berorientasi tindakan, tetapi mudah dipahami dan mudah disalin ke aplikasi lain.
- Menginginkan riset mendalam ketika topiknya niche/terkini; utamakan sumber primer/tepercaya, tautan, tanggal, dan pembedaan antara fakta, inferensi, asumsi, serta hal yang belum diketahui.
- Lebih suka langkah implementasi konkret, pengujian, audit, daftar risiko, metrik keberhasilan, dan laporan jujur tentang apa yang benar-benar telah diuji.
- Menginginkan asisten desktop bernama Clara yang menjadi teman kerja virtual untuk bisnis, cyber security yang etis, coding, belajar, dokumen, produktivitas, dan tugas sehari-hari.

## Bisnis: OdorZinc
- Produk yang berulang kali dibahas: OdorZinc, spray penghilang bau ukuran 100 ml.
- Penggunaan yang pernah disebut untuk pemasaran: sepatu, helm, tas, jok mobil, pakaian/kain, dan area kaki. Validasi instruksi label dan kesesuaian bahan sebelum klaim penggunaan yang lebih spesifik.
- Kanal marketplace yang sering dibahas: Shopee; ide konten dapat diadaptasi ke TikTok dan kanal sosial lain.
- Arah marketing: thumbnail, CTR, konversi, video demonstrasi, FAQ, bukti sosial yang sah, repeat order, margin, dan efisiensi iklan.
- Kendala historis: impresi iklan pernah relatif ada sedangkan klik/pembelian dinilai kurang; ROAS 1,86 dan target 7 pernah disebut sebelumnya, namun **jangan perlakukan sebagai angka terkini**.
- Harga sekitar Rp36.000, komisi affiliate 4%, biaya bahan, HPP, stok, dan data lainnya pernah dibahas pada tanggal berbeda. Semua itu perlu dikonfirmasi kembali sebelum dipakai menghitung harga atau profit.
- Jangan membuat klaim seperti “pasti hilang 100%”, klaim kesehatan, keamanan, sertifikasi, atau hasil uji tanpa bukti yang benar.

## Cyber security dan pengembangan
- Minat pada web application security, source-code auditing, Linux/Windows, scanner, automation, dan dokumentasi proyek.
- Proyek/repositori yang pernah disebut: [nucleiweb](https://github.com/HedyFake/nucleiweb), [AISCAN](https://github.com/HedyFake/AISCAN), [TrackMe](https://github.com/HedyFake/TrackMe), [CamHack](https://github.com/HedyFake/CamHack), [Photo](https://github.com/HedyFake/Photo), serta OmniScan dan Waymap Scanner sebagai konteks proyek.
- Link repositori bukan bukti bahwa fitur masih sama atau tersedia; buka dan verifikasi kode aktual sebelum review.
- Bantuan pengujian keamanan harus dibatasi pada lab sendiri atau target yang memiliki izin jelas. Prioritaskan scope allowlist, rate limit, mode pasif bila cukup, pengecualian endpoint destruktif, log, dan responsible disclosure.

## Pendidikan dan dokumen
- Pernah meminta bantuan tugas Keperawatan di STIKES Husada Jombang dan materi akademik yang dijelaskan bahasa Indonesia, rinci namun mudah dipahami, serta siap dipindahkan ke Word/PDF/PPT. Konfirmasi kelas, semester, dosen, dan format setiap tugas baru karena dapat berubah.

## Proyek Clara Desktop Buddy
- Target perangkat yang dibahas saat ini: Windows 10/11, Python 3.11/3.12.
- Preferensi karakter: gadis anime 3D (prototipe sekarang masih menggambar avatar 2D menggunakan Tkinter), suara perempuan natural, mode kecil mengambang dan mode besar.
- Fitur yang diinginkan: percakapan suara hands-free dengan tombol ON/OFF, analisis layar berkala dengan izin, bubble chat dan ekspresi, kontrol GUI, bantuan bisnis, riset, serta memory portabel.
- Status 13 Oktober 2026: Clara Desktop Buddy v3.1.0 dibangun sebagai EXE portable pada Windows 11 64-bit dengan Python 3.12.10; uji startup berhasil membuka jendela aplikasi. Tes mikrofon fisik, suara terdengar, Live Screen/API, dan otomasi GUI end-to-end belum dilakukan.
- Memory lokal: atas permintaan pengguna, jurnal prompt/jawaban AI aktif secara default, dapat dimatikan, dan menyimpan preferensi ON/OFF. Credential umum disamarkan best-effort; jangan memasukkan password, OTP, API key, token, atau data pelanggan rahasia. Jurnal lokal tidak menyinkronkan riwayat chat ChatGPT lain secara otomatis.
- Suara yang terdeteksi pada lingkungan build adalah Microsoft David dan Zira Desktop (en-US); suara natural Bahasa Indonesia dan avatar 3D rigged belum tersedia.
- Kontrol komputer yang tersedia adalah otomasi GUI yang ditinjau pengguna dengan batas aksi dan tombol stop; eksekusi shell/admin tanpa batas tidak disediakan.
- API key jangan ditulis ke file memory atau prompt. API OpenAI ditagih terpisah dari langganan ChatGPT. Periksa biaya sebelum mengaktifkan pengamatan layar.


## Pembaruan proyek Clara v3.3.0 (15 Oktober 2026)
- Pengguna mengunggah `ClaraDesktopBuddy_Windows_3_2_0.zip` serta spritesheet ekspresi karakter anime 5×3. Prioritasnya mengembangkan kode yang ada, bukan mengganti seluruh proyek.
- Fitur versi 3.3.0 yang ditambahkan: 15 frame ekspresi transparan dari gambar baru; pilihan ekspresi sesuai mood/status; modul keuangan lokal SQLite dengan Income/Spending, mesin income, kategori produktif/konsumtif, aset, langganan, anggaran, tujuan, skor heuristik, rekomendasi, ekspor CSV; halaman pasar saham/watchlist IHSG dan saham BEI `.JK`, berita RSS, sinyal heuristik, auto-refresh opsional 15 menit.
- Ada playbook `TOKEN_OPTIMIZATION_PLAYBOOK_ID.md` berisi 60 teknik dengan penanda praktik aktif/pengaman/eksperimen. Jangan mengklaim seluruh teknik eksperimen sudah diterapkan.
- Diskusi teks/suara ketika otomasi berjalan sebagian didukung, tetapi request AI masih satu per satu. Live desktop memerlukan persetujuan pengguna dan harus dimatikan untuk data sensitif.
- Saham: jangan membuat jaminan akan naik atau menganggap heuristik sebagai rekomendasi pasti. Data Yahoo Finance/Google News perlu internet dan dapat tertunda. Auto-refresh mati secara default.
- Build Windows: `BUILD_EXE.bat` dan GitHub Actions workflow merupakan metode build. Jangan menyatakan file EXE sudah dihasilkan kecuali EXE benar-benar tersedia dan sudah diverifikasi.
- Pengujian di lingkungan pengembangan Linux mencakup tes otomatis dan GUI smoke-test; koneksi quote/news online dan pengujian mikrofon, suara, desktop nyata, Windows DPAPI serta EXE masih perlu dilakukan di Windows dengan internet.

## Cara kerja yang diharapkan dari AI penerus
1. Tanyakan tujuan hanya ketika informasi penting benar-benar kurang; jika memungkinkan lakukan best-effort dengan asumsi yang ditandai.
2. Riset mendalam saat fakta mudah berubah atau perlu pembuktian, kutip sumber yang jelas dan terbaru.
3. Untuk keputusan: diagnosis -> bukti -> opsi -> pro/kontra -> eksperimen -> metrik -> rekomendasi -> langkah eksekusi.
4. Jangan pura-pura telah menjalankan, melihat, memasang, mengirim, atau mengubah sesuatu. Beri batasan dan tes yang belum dilakukan.
5. Otomasi komputer harus memiliki indikator status, tombol stop, log, scope yang jelas, serta konfirmasi sebelum aksi berisiko.
6. Memory adalah ringkasan yang dapat diperbarui, bukan “semua kenangan” yang sempurna. Tanyakan/konfirmasi fakta yang sudah lama.
7. Jangan simpan password, OTP, API key, token login, data bank, dokumen identitas, atau rahasia pelanggan.
8. Untuk OdorZinc, optimasi profit dan bukti lebih penting daripada vanity metrics atau klaim penjualan pasti.
9. Untuk cyber security, utamakan otorisasi, akurasi, minimisasi dampak, dan pelaporan yang bertanggung jawab.

## Bagian yang sengaja tidak dimasukkan
Profil ini tidak menyimpan transkrip penuh, rahasia pribadi, kredensial, atau informasi yang tidak dibutuhkan untuk melanjutkan proyek utama. Jika perlu, tambahkan sendiri konteks yang dianggap layak dan aman untuk diekspor.
