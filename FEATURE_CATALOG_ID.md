# Katalog Fitur Clara — 220 Ide Terstruktur

> Status harus dibaca dengan jujur: katalog ini adalah portofolio ide, bukan klaim bahwa 200 fitur sudah terpasang. Fitur yang berlabel rencana belum dibuat. Prioritas P0/P1/P2 adalah usulan urutan, bukan estimasi jadwal.

## Definisi prioritas
- **P0:** fondasi yang membuat Clara lebih andal/aman atau memberi nilai utama sejak awal.
- **P1:** fitur bernilai tinggi setelah fondasi teruji.
- **P2:** peningkatan lanjutan dan integrasi opsional.

## Daftar fitur

### Karakter & UI
- **CL-001 · Avatar anime mengambang** (P0 · Fondasi ada / perlu validasi Windows) — Karakter desktop kecil yang selalu terlihat ketika Clara berjalan.
- **CL-002 · Mode avatar besar** (P0 · Fondasi ada / perlu validasi Windows) — Jendela avatar besar untuk sesi ngobrol atau kerja fokus.
- **CL-003 · Ekspresi wajah berbasis status** (P0 · Fondasi ada / perlu validasi Windows) — Ekspresi senang, berpikir, mendengar, berbicara, dan terkejut.
- **CL-004 · Animasi idle** (P1 · Fondasi ada / perlu validasi Windows) — Gerakan mengambang dan perubahan frame sekitar setiap 90 ms.
- **CL-005 · Lip-sync audio** (P1 · Rencana / belum diimplementasikan) — Gerakan mulut diselaraskan dengan audio jawaban.
- **CL-006 · Animasi tubuh 3D** (P1 · Rencana / belum diimplementasikan) — Model rigged dengan gerakan kepala, tangan, dan badan.
- **CL-007 · Tema dan warna** (P1 · Rencana / belum diimplementasikan) — Pilihan tema gelap, terang, dan warna aksen.
- **CL-008 · Posisi avatar tersimpan** (P2 · Rencana / belum diimplementasikan) — Mengingat posisi avatar terakhir di layar.
- **CL-009 · Bubble chat kontekstual** (P2 · Fondasi ada / perlu validasi Windows) — Bubble singkat dekat avatar yang hilang otomatis.
- **CL-010 · Mode jangan ganggu** (P2 · Rencana / belum diimplementasikan) — Membisukan suara dan notifikasi saat presentasi atau belajar.

### Suara & Percakapan
- **CL-011 · Selalu mendengarkan ON/OFF** (P0 · Fondasi ada / perlu validasi Windows) — Mode mikrofon berkelanjutan yang mudah dimatikan.
- **CL-012 · Wake word lokal** (P0 · Rencana / belum diimplementasikan) — Kata panggil yang diproses lokal agar percakapan lain tidak ikut diproses; mode suara saat ini tidak memiliki wake word.
- **CL-013 · Deteksi akhir ucapan** (P0 · Fondasi ada / perlu validasi Windows) — Menentukan kapan pengguna selesai berbicara sebelum menjawab.
- **CL-014 · Interrupt saat TTS** (P1 · Rencana / belum diimplementasikan) — Pengguna dapat memotong jawaban Clara dengan mulai berbicara.
- **CL-015 · Percakapan audio streaming** (P1 · Rencana / belum diimplementasikan) — Ucapan dan jawaban terasa lebih alami tanpa menunggu satu putaran panjang.
- **CL-016 · Pilihan suara Windows** (P1 · Fondasi ada / perlu validasi Windows) — Memilih suara SAPI yang terpasang; suara perempuan dan bahasa Indonesia bergantung paket voice Windows.
- **CL-017 · Kecepatan dan volume suara** (P1 · Rencana / belum diimplementasikan) — Pengaturan laju bicara, volume, dan jeda.
- **CL-018 · Pengenalan Bahasa Indonesia** (P2 · Fondasi ada / perlu validasi Windows) — Mengirim audio ke Google Speech Recognition dengan locale `id-ID`.
- **CL-019 · Push-to-talk cadangan** (P2 · Fondasi ada / perlu validasi Windows) — Tombol untuk mendengar satu kali jika mode hands-free dimatikan.
- **CL-020 · Subtitle ucapan** (P2 · Fondasi ada / perlu validasi Windows) — Menampilkan transkrip ringkas di bubble dan jawaban sebagai teks.

### Penglihatan Desktop
- **CL-021 · Screenshot dengan izin** (P0 · Fondasi ada / perlu validasi Windows) — Mengambil frame layar hanya setelah pengguna menyetujui.
- **CL-022 · Live Screen ON/OFF** (P0 · Fondasi ada / perlu validasi Windows) — Pengamatan layar berkala yang terlihat statusnya.
- **CL-023 · Deteksi perubahan layar** (P0 · Fondasi ada / perlu validasi Windows) — Menghindari unggah frame yang sama berulang kali.
- **CL-024 · Pengenalan jendela aktif** (P1 · Fondasi ada / perlu validasi Windows) — Menampilkan judul jendela aktif saat diminta atau saat pemantauan lokal aktif.
- **CL-025 · Daftar aplikasi aktif** (P1 · Fondasi ada / perlu validasi Windows) — Menampilkan nama proses Windows atas permintaan; tidak menghentikan proses.
- **CL-026 · Penyamaran area sensitif** (P1 · Rencana / belum diimplementasikan) — Mengecualikan atau memburamkan area yang dipilih pengguna.
- **CL-027 · Jeda di aplikasi sensitif** (P1 · Fondasi ada / perlu validasi Windows) — Live Screen mencoba jeda lewat kata kunci judul jendela; deteksinya tidak sempurna.
- **CL-028 · OCR lokal opsional** (P2 · Rencana / belum diimplementasikan) — Mengenali teks lokal sebelum mengirim bagian yang disetujui.
- **CL-029 · Ringkasan aktivitas visual** (P2 · Fondasi ada / perlu validasi Windows) — Merangkum frame yang dibagikan secara berkala, bukan melihat jendela tersembunyi.
- **CL-030 · Kontrol frekuensi dan biaya** (P2 · Rencana / belum diimplementasikan) — Mengatur interval, kualitas gambar, durasi sesi, dan batas penggunaan API.

### Otomasi Desktop
- **CL-031 · Buka aplikasi yang diizinkan** (P0 · Fondasi ada / perlu validasi Windows) — Membuka aplikasi melalui daftar nama yang jelas.
- **CL-032 · Buka situs tepercaya** (P0 · Fondasi ada / perlu validasi Windows) — Membuka URL HTTP/HTTPS yang divalidasi.
- **CL-033 · Ketik teks dengan pratinjau** (P0 · Fondasi ada / perlu validasi Windows) — Meninjau teks sebelum disisipkan ke aplikasi.
- **CL-034 · Klik dan scroll terarah** (P1 · Fondasi ada / perlu validasi Windows) — Menggunakan koordinat layar setelah pengguna memeriksa pratinjau rencana.
- **CL-035 · Rencana aksi bertahap** (P1 · Fondasi ada / perlu validasi Windows) — Membuat rencana GUI berurutan dengan batas maksimum 12 tindakan.
- **CL-036 · Konfirmasi tindakan penting** (P1 · Fondasi ada / perlu validasi Windows) — Menampilkan pratinjau dan konfirmasi tambahan untuk kategori sensitif.
- **CL-037 · Tombol berhenti darurat** (P1 · Fondasi ada / perlu validasi Windows) — Menghentikan langkah berikutnya melalui tombol stop dan fail-safe PyAutoGUI.
- **CL-038 · Verifikasi setelah aksi** (P2 · Rencana / belum diimplementasikan) — Mengecek hasil melalui screenshot atau sinyal UI setelah tindakan.
- **CL-039 · Daftar aksi terlarang** (P2 · Fondasi ada / perlu validasi Windows) — Menolak shell arbitrer, elevasi admin, dan beberapa aksi sensitif.
- **CL-040 · Mode sandbox otomasi** (P2 · Rencana / belum diimplementasikan) — Menguji alur pada aplikasi dummy sebelum digunakan pada akun asli.

### Memory & Pengetahuan
- **CL-041 · Profil memory portabel** (P0 · Ditambahkan di paket v3 (uji langsung diperlukan)) — Preferensi dan konteks stabil yang dapat dibaca manusia.
- **CL-042 · Jurnal percakapan lokal** (P0 · Ditambahkan di build portable (uji langsung diperlukan)) — Menyimpan prompt dan jawaban secara default sesuai permintaan pengguna; dapat dimatikan, dan pola credential umum disamarkan sebelum penyimpanan.
- **CL-043 · Impor profil memory** (P0 · Ditambahkan di paket v3 (uji langsung diperlukan)) — Memuat file profil dari ekspor terdahulu atau AI lain.
- **CL-044 · Ekspor memory ZIP** (P1 · Ditambahkan di paket v3 (uji langsung diperlukan)) — Mengemas profil, jurnal, prompt migrasi, dan katalog fitur.
- **CL-045 · Edit memory manual** (P1 · Ditambahkan di paket v3 (uji langsung diperlukan)) — Pengguna dapat meninjau, memperbaiki, atau menghapus fakta.
- **CL-046 · Fakta dengan tanggal** (P1 · Rencana / belum diimplementasikan) — Mencatat kapan harga, preferensi, atau keputusan terakhir diverifikasi.
- **CL-047 · Kadaluarsa memory** (P1 · Rencana / belum diimplementasikan) — Menandai data yang sering berubah agar tidak dianggap masih mutakhir.
- **CL-048 · Pencarian memory** (P2 · Rencana / belum diimplementasikan) — Mencari percakapan dan keputusan terdahulu secara lokal.
- **CL-049 · Memory per proyek** (P2 · Rencana / belum diimplementasikan) — Memisahkan konteks bisnis, sekolah, cyber, dan proyek coding.
- **CL-050 · Riwayat perubahan memory** (P2 · Rencana / belum diimplementasikan) — Mengetahui siapa/apa yang mengubah catatan dan kapan.

### Bisnis E-commerce
- **CL-051 · Audit toko marketplace** (P0 · Sebagian melalui prompt/template; perlu integrasi data) — Memeriksa halaman produk dari data yang diberikan pengguna.
- **CL-052 · Audit listing produk** (P0 · Sebagian melalui prompt/template; perlu integrasi data) — Meninjau foto, judul, deskripsi, variasi, FAQ, dan CTA.
- **CL-053 · Analisis funnel** (P0 · Sebagian melalui prompt/template; perlu integrasi data) — Memisahkan impresi, klik, add-to-cart, checkout, dan pembelian.
- **CL-054 · Analisis CTR** (P1 · Rencana / belum diimplementasikan) — Mengukur hasil thumbnail, judul, serta impresi berdasarkan data asli.
- **CL-055 · Analisis konversi** (P1 · Rencana / belum diimplementasikan) — Menelusuri penurunan antara klik dan pembelian.
- **CL-056 · Analisis margin per pesanan** (P1 · Rencana / belum diimplementasikan) — Menghitung kontribusi setelah HPP, biaya marketplace, iklan, dan komisi.
- **CL-057 · Eksperimen harga** (P1 · Rencana / belum diimplementasikan) — Mengusulkan uji harga atau bundel dengan margin sebagai batas.
- **CL-058 · Analisis ulasan** (P2 · Rencana / belum diimplementasikan) — Mengelompokkan keluhan dan motif pembelian dari ulasan yang sah.
- **CL-059 · Repeat order** (P2 · Rencana / belum diimplementasikan) — Menyusun strategi pembelian ulang tanpa spam atau klaim palsu.
- **CL-060 · Dashboard seller** (P2 · Rencana / belum diimplementasikan) — Menampilkan KPI utama dari CSV atau ekspor yang diunggah pengguna.

### Pemasaran & Pertumbuhan
- **CL-061 · Riset persona pelanggan** (P0 · Sebagian melalui prompt/template; perlu integrasi data) — Membuat hipotesis persona dan menandai asumsi yang perlu diuji.
- **CL-062 · Riset pesaing publik** (P0 · Sebagian melalui prompt/template; perlu integrasi data) — Membandingkan pesan, harga yang terlihat, dan penawaran publik.
- **CL-063 · Positioning produk** (P0 · Sebagian melalui prompt/template; perlu integrasi data) — Merumuskan segmen, masalah, manfaat, alasan percaya, dan diferensiasi.
- **CL-064 · Kalender konten** (P1 · Rencana / belum diimplementasikan) — Menyusun jadwal konten 7, 14, atau 30 hari.
- **CL-065 · Hook video pendek** (P1 · Rencana / belum diimplementasikan) — Menghasilkan beberapa hook untuk diuji, bukan mengklaim viral.
- **CL-066 · Skrip video UGC** (P1 · Rencana / belum diimplementasikan) — Menyusun demonstrasi realistis dengan pengungkapan yang jujur.
- **CL-067 · Optimasi thumbnail** (P1 · Rencana / belum diimplementasikan) — Menguji satu variabel visual pada setiap eksperimen.
- **CL-068 · A/B testing** (P2 · Rencana / belum diimplementasikan) — Mendefinisikan hipotesis, kelompok pembanding, periode, dan metrik.
- **CL-069 · Optimasi ROAS dan profit** (P2 · Rencana / belum diimplementasikan) — Membedakan ROAS iklan dari keuntungan bersih bisnis.
- **CL-070 · Peringatan klaim berlebihan** (P2 · Rencana / belum diimplementasikan) — Menandai klaim efektivitas yang tidak disertai bukti.

### Pengembangan Produk & Operasional
- **CL-071 · Kalkulator HPP** (P0 · Rencana / belum diimplementasikan) — Menghitung biaya bahan, kemasan, tenaga, waste, dan overhead.
- **CL-072 · Kalkulator batch produksi** (P0 · Rencana / belum diimplementasikan) — Mengubah resep per batch menjadi kebutuhan bahan total.
- **CL-073 · Pelacakan pemasok** (P0 · Rencana / belum diimplementasikan) — Mencatat harga pemasok, MOQ, tanggal, dan mutu bahan.
- **CL-074 · QC bahan baku** (P1 · Rencana / belum diimplementasikan) — Checklist penerimaan bahan dan nomor batch.
- **CL-075 · QC produk jadi** (P1 · Rencana / belum diimplementasikan) — Checklist warna, bau, kebocoran, label, dan konsistensi batch.
- **CL-076 · Pelacakan batch** (P1 · Rencana / belum diimplementasikan) — Menghubungkan produk jadi dengan bahan dan tanggal produksi.
- **CL-077 · Perhitungan kebutuhan stok** (P1 · Rencana / belum diimplementasikan) — Memperkirakan stok aman berdasarkan penjualan historis.
- **CL-078 · Pengingat masa simpan** (P2 · Rencana / belum diimplementasikan) — Menandai bahan dan produk yang mendekati tanggal penting.
- **CL-079 · Checklist kepatuhan label** (P2 · Rencana / belum diimplementasikan) — Meninjau daftar klaim, petunjuk, komposisi, dan informasi wajib yang relevan.
- **CL-080 · Rencana eksperimen produk** (P2 · Rencana / belum diimplementasikan) — Mengatur uji formula, stabilitas, kemasan, dan hasil yang diukur.

### Keuangan & Analitik
- **CL-081 · Pencatatan biaya usaha** (P0 · Rencana / belum diimplementasikan) — Mengkategorikan biaya dari CSV yang diberikan pengguna.
- **CL-082 · Rekonsiliasi payout** (P0 · Rencana / belum diimplementasikan) — Mencocokkan pesanan, fee, refund, dan pembayaran marketplace.
- **CL-083 · Arus kas sederhana** (P0 · Rencana / belum diimplementasikan) — Membuat proyeksi uang masuk/keluar dari asumsi transparan.
- **CL-084 · Titik impas** (P1 · Rencana / belum diimplementasikan) — Menghitung jumlah penjualan yang diperlukan untuk menutup biaya tetap.
- **CL-085 · Analisis kontribusi** (P1 · Rencana / belum diimplementasikan) — Mengidentifikasi produk dan kanal yang menyumbang margin terbesar.
- **CL-086 · Alarm biaya iklan** (P1 · Rencana / belum diimplementasikan) — Memunculkan notifikasi saat biaya mencapai batas yang disetel.
- **CL-087 · Anggaran campaign** (P1 · Rencana / belum diimplementasikan) — Menyusun plafon pengeluaran dan aturan berhenti.
- **CL-088 · Forecast dengan rentang** (P2 · Rencana / belum diimplementasikan) — Menyajikan skenario rendah, dasar, dan tinggi, bukan kepastian.
- **CL-089 · Pelacakan refund** (P2 · Rencana / belum diimplementasikan) — Memantau alasan refund dan pengaruhnya terhadap margin.
- **CL-090 · Laporan mingguan** (P2 · Rencana / belum diimplementasikan) — Merangkum KPI, eksperimen, risiko, dan prioritas minggu berikutnya.

### Konten & Kreatif
- **CL-091 · Pembuat caption** (P0 · Rencana / belum diimplementasikan) — Menyusun caption lintas marketplace, Reels, TikTok, dan Shorts.
- **CL-092 · Pembuat deskripsi produk** (P0 · Rencana / belum diimplementasikan) — Menulis deskripsi terstruktur tanpa keyword stuffing.
- **CL-093 · Generator FAQ** (P0 · Rencana / belum diimplementasikan) — Menyusun jawaban untuk pertanyaan pelanggan yang sering muncul.
- **CL-094 · Storyboard video** (P1 · Rencana / belum diimplementasikan) — Membuat adegan, durasi, visual, narasi, dan CTA.
- **CL-095 · Prompt gambar produk** (P1 · Rencana / belum diimplementasikan) — Menyusun brief gambar dengan identitas kemasan yang konsisten.
- **CL-096 · Prompt video produk** (P1 · Rencana / belum diimplementasikan) — Menyusun brief video untuk alat kreatif yang dipilih pengguna.
- **CL-097 · Konten edukasi** (P1 · Rencana / belum diimplementasikan) — Mengubah fitur produk menjadi edukasi yang dapat diverifikasi.
- **CL-098 · Repurposing konten** (P2 · Rencana / belum diimplementasikan) — Mengubah satu ide menjadi format berbeda tanpa salin-tempel membabi buta.
- **CL-099 · Pemeriksa ejaan Indonesia** (P2 · Rencana / belum diimplementasikan) — Memeriksa typo, tanda baca, kejelasan, dan nada komunikasi.
- **CL-100 · Perpustakaan brand voice** (P2 · Rencana / belum diimplementasikan) — Menyimpan pedoman gaya bahasa dan contoh yang disetujui.

### Riset & Berpikir Kritis
- **CL-101 · Riset web dengan sumber** (P0 · Rencana / belum diimplementasikan) — Mencari informasi saat diperlukan dan menyertakan tautan sumber.
- **CL-102 · Prioritas sumber primer** (P0 · Rencana / belum diimplementasikan) — Mendahulukan dokumentasi, regulator, makalah, dan data asal.
- **CL-103 · Verifikasi tanggal** (P0 · Rencana / belum diimplementasikan) — Membedakan tanggal publikasi, kejadian, dan pembaruan.
- **CL-104 · Pemisahan fakta dan asumsi** (P1 · Rencana / belum diimplementasikan) — Memberi label mana yang diketahui dan mana yang dugaan.
- **CL-105 · Analisis pro-kontra** (P1 · Rencana / belum diimplementasikan) — Mengevaluasi alternatif menurut biaya, risiko, dan manfaat.
- **CL-106 · Red-team ide** (P1 · Rencana / belum diimplementasikan) — Mencari kelemahan dari rencana sendiri sebelum dijalankan.
- **CL-107 · Analisis ketidakpastian** (P1 · Rencana / belum diimplementasikan) — Mencantumkan tingkat keyakinan dan data yang kurang.
- **CL-108 · Matriks keputusan** (P2 · Rencana / belum diimplementasikan) — Membandingkan opsi berdasarkan kriteria berbobot yang transparan.
- **CL-109 · Eksperimen yang bisa dibantah** (P2 · Rencana / belum diimplementasikan) — Menyusun hipotesis dengan metrik dan hasil yang dapat menggugurkan.
- **CL-110 · Ringkasan untuk tindakan** (P2 · Rencana / belum diimplementasikan) — Mengubah riset panjang menjadi keputusan dan langkah berikutnya.

### Cyber Security Learning
- **CL-111 · Peta belajar bertahap** (P0 · Rencana / belum diimplementasikan) — Membuat kurikulum jaringan, Linux, web, dan keamanan aplikasi.
- **CL-112 · Tutor konsep web security** (P0 · Rencana / belum diimplementasikan) — Menjelaskan auth, access control, injection, SSRF, dan mitigasi.
- **CL-113 · Lab terisolasi** (P0 · Rencana / belum diimplementasikan) — Menyusun latihan pada aplikasi rentan lokal atau platform resmi.
- **CL-114 · Checklist scope** (P1 · Rencana / belum diimplementasikan) — Menentukan domain, aset, metode, waktu, dan larangan pengujian.
- **CL-115 · Pembuat laporan temuan** (P1 · Rencana / belum diimplementasikan) — Menyusun ringkasan, bukti aman, dampak, dan mitigasi.
- **CL-116 · CVSS sebagai estimasi** (P1 · Rencana / belum diimplementasikan) — Membantu menilai severity dengan alasan, bukan menggantikan penilaian manual.
- **CL-117 · Pemeriksa false positive** (P1 · Rencana / belum diimplementasikan) — Meminta verifikasi dan bukti sebelum menyebut kerentanan valid.
- **CL-118 · Pemetaan OWASP** (P2 · Rencana / belum diimplementasikan) — Mengaitkan temuan dengan kategori OWASP yang relevan.
- **CL-119 · Tutor source code review** (P2 · Rencana / belum diimplementasikan) — Menelusuri flow input, auth, sink, dan validasi dalam kode yang disediakan.
- **CL-120 · Catatan belajar** (P2 · Rencana / belum diimplementasikan) — Menyimpan konsep, perintah lab, dan pelajaran yang dipelajari.

### Tools Cyber yang Diotorisasi
- **CL-121 · Orkestrasi scanner terbatas** (P0 · Rencana / belum diimplementasikan) — Menjalankan tools hanya pada target allowlist yang disetujui.
- **CL-122 · Validasi allowlist** (P0 · Rencana / belum diimplementasikan) — Membatasi domain dan IP pada scope tertulis.
- **CL-123 · Rate limiting** (P0 · Rencana / belum diimplementasikan) — Menetapkan batas concurrency, request per detik, dan timeout.
- **CL-124 · Pengecualian endpoint sensitif** (P1 · Rencana / belum diimplementasikan) — Menghindari logout, delete, transaksi, dan fungsi destruktif.
- **CL-125 · Mode pasif** (P1 · Rencana / belum diimplementasikan) — Memprioritaskan sumber pasif bila itu cukup untuk tujuan.
- **CL-126 · Log audit scan** (P1 · Rencana / belum diimplementasikan) — Mencatat waktu, versi tool, target yang disetujui, dan hasil.
- **CL-127 · Manajemen template** (P1 · Rencana / belum diimplementasikan) — Meninjau template scanner sebelum menjalankannya.
- **CL-128 · Penyamaran rahasia** (P2 · Rencana / belum diimplementasikan) — Menyensor token dan data sensitif dalam log laporan.
- **CL-129 · Reproducibility** (P2 · Rencana / belum diimplementasikan) — Merekam perintah, versi, konfigurasi, dan langkah reproduksi.
- **CL-130 · Responsible disclosure** (P2 · Rencana / belum diimplementasikan) — Menyiapkan draft laporan dan komunikasi berdasarkan kebijakan program.

### Keamanan Digital Pribadi
- **CL-131 · Pemeriksaan pembaruan** (P0 · Rencana / belum diimplementasikan) — Mengingatkan pembaruan OS dan aplikasi penting.
- **CL-132 · Audit startup apps** (P0 · Rencana / belum diimplementasikan) — Membantu meninjau program startup tanpa mematikannya sendiri.
- **CL-133 · Audit ekstensi browser** (P0 · Rencana / belum diimplementasikan) — Mendata izin ekstensi dan membantu meninjau kebutuhan.
- **CL-134 · Checklist backup** (P1 · Rencana / belum diimplementasikan) — Mengingatkan backup file penting dan verifikasi restore.
- **CL-135 · Deteksi file berisiko** (P1 · Rencana / belum diimplementasikan) — Menjelaskan ekstensi dan indikator file sebelum dibuka.
- **CL-136 · Peringatan phishing** (P1 · Rencana / belum diimplementasikan) — Menilai indikator email atau URL yang diberikan pengguna.
- **CL-137 · Pemeriksaan izin aplikasi** (P1 · Rencana / belum diimplementasikan) — Menjelaskan permission dan opsi pengaturan yang aman.
- **CL-138 · Password hygiene** (P2 · Rencana / belum diimplementasikan) — Menyarankan password manager dan MFA tanpa meminta rahasia.
- **CL-139 · Privasi data lokal** (P2 · Rencana / belum diimplementasikan) — Membantu menemukan log dan cache aplikasi dengan konfirmasi.
- **CL-140 · Rencana pemulihan** (P2 · Rencana / belum diimplementasikan) — Membuat langkah pemulihan akun dan perangkat yang sah.

### Produktivitas & Waktu
- **CL-141 · Todo list lintas proyek** (P0 · Rencana / belum diimplementasikan) — Mengelompokkan tugas menurut proyek, urgensi, dan energi.
- **CL-142 · Kalender dan blok waktu** (P0 · Rencana / belum diimplementasikan) — Mengubah sasaran menjadi jadwal yang realistis.
- **CL-143 · Pengingat tenggat** (P0 · Rencana / belum diimplementasikan) — Memberi pengingat pada jadwal yang pengguna tetapkan.
- **CL-144 · Daily briefing** (P1 · Rencana / belum diimplementasikan) — Merangkum prioritas, agenda, dan blok waktu hari ini.
- **CL-145 · Weekly review** (P1 · Rencana / belum diimplementasikan) — Mengevaluasi hasil, hambatan, dan prioritas minggu depan.
- **CL-146 · Pomodoro fokus** (P1 · Rencana / belum diimplementasikan) — Timer fokus dan jeda dengan mode jangan ganggu.
- **CL-147 · Pencatat keputusan** (P1 · Rencana / belum diimplementasikan) — Menyimpan keputusan, alasan, tanggal, dan syarat evaluasi ulang.
- **CL-148 · Pembagi tugas besar** (P2 · Rencana / belum diimplementasikan) — Memecah proyek menjadi langkah 15–60 menit.
- **CL-149 · Peringatan multitasking** (P2 · Rencana / belum diimplementasikan) — Menyarankan satu prioritas utama jika terlalu banyak hal aktif.
- **CL-150 · Habit tracker** (P2 · Rencana / belum diimplementasikan) — Melacak kebiasaan pilihan pengguna tanpa penilaian menghakimi.

### File & Dokumen
- **CL-151 · Pencarian file** (P0 · Rencana / belum diimplementasikan) — Membantu mencari file menurut nama dan jenis melalui tindakan yang terlihat.
- **CL-152 · Ringkasan dokumen** (P0 · Rencana / belum diimplementasikan) — Merangkum dokumen yang dipilih pengguna.
- **CL-153 · Ekstraksi tabel CSV** (P0 · Rencana / belum diimplementasikan) — Membantu membersihkan dan membaca CSV yang dipilih.
- **CL-154 · Pengelompokan download** (P1 · Rencana / belum diimplementasikan) — Menyarankan kategori file unduhan sebelum memindahkannya.
- **CL-155 · Penamaan file konsisten** (P1 · Rencana / belum diimplementasikan) — Menerapkan skema nama yang disetujui.
- **CL-156 · Pemeriksaan duplikat** (P1 · Rencana / belum diimplementasikan) — Menemukan kandidat duplikat tanpa menghapus otomatis.
- **CL-157 · Backup versi file** (P1 · Rencana / belum diimplementasikan) — Membuat salinan sebelum perubahan massal.
- **CL-158 · Template laporan** (P2 · Rencana / belum diimplementasikan) — Membuat template makalah, audit, dan laporan bisnis.
- **CL-159 · Konversi format** (P2 · Rencana / belum diimplementasikan) — Membantu menyiapkan alur DOCX, PDF, CSV, dan Markdown.
- **CL-160 · Peringatan file belum tersimpan** (P2 · Rencana / belum diimplementasikan) — Mengingatkan pengecekan sebelum menutup aplikasi.

### Komunikasi
- **CL-161 · Draft email** (P0 · Rencana / belum diimplementasikan) — Menyusun email yang sopan sesuai penerima dan tujuan.
- **CL-162 · Draft chat pelanggan** (P0 · Rencana / belum diimplementasikan) — Menyiapkan jawaban yang empatik, ringkas, dan akurat.
- **CL-163 · Balasan keluhan** (P0 · Rencana / belum diimplementasikan) — Mengubah keluhan menjadi langkah penyelesaian yang terukur.
- **CL-164 · Pengingat follow-up** (P1 · Rencana / belum diimplementasikan) — Membantu melacak calon pembeli dan percakapan yang perlu ditindaklanjuti.
- **CL-165 · Pemeriksa nada** (P1 · Rencana / belum diimplementasikan) — Menyesuaikan pesan agar formal, ramah, atau persuasif.
- **CL-166 · Terjemahan konteks** (P1 · Rencana / belum diimplementasikan) — Menerjemahkan pesan sambil menjaga istilah dan maksud.
- **CL-167 · Ringkasan rapat** (P1 · Rencana / belum diimplementasikan) — Menghasilkan keputusan, action item, pemilik, dan tenggat dari catatan.
- **CL-168 · Draft posting** (P2 · Rencana / belum diimplementasikan) — Menyusun posting sosial dan CTA sesuai platform.
- **CL-169 · Approval sebelum kirim** (P2 · Rencana / belum diimplementasikan) — Menampilkan pesan lengkap dan penerima sebelum dikirim.
- **CL-170 · Riwayat template** (P2 · Rencana / belum diimplementasikan) — Menyimpan template komunikasi yang sudah disetujui pengguna.

### Coding & Pengembangan
- **CL-171 · Tutor coding** (P0 · Rencana / belum diimplementasikan) — Menjelaskan error, struktur, dan opsi perbaikan dengan contoh.
- **CL-172 · Static code review** (P0 · Rencana / belum diimplementasikan) — Menganalisis kode yang dipilih, dengan batasan yang jelas.
- **CL-173 · Unit test generator** (P0 · Rencana / belum diimplementasikan) — Menghasilkan uji untuk fungsi dan kasus tepi.
- **CL-174 · Reproduksi bug** (P1 · Rencana / belum diimplementasikan) — Mengumpulkan langkah, lingkungan, input, dan expected/actual.
- **CL-175 · Git helper** (P1 · Rencana / belum diimplementasikan) — Menjelaskan diff, commit, branch, dan konflik sebelum perubahan.
- **CL-176 · Dependency audit** (P1 · Rencana / belum diimplementasikan) — Membaca daftar dependensi dan mengecek versi yang tersedia.
- **CL-177 · Changelog** (P1 · Rencana / belum diimplementasikan) — Mendokumentasikan perubahan dan risiko rilis.
- **CL-178 · Environment checklist** (P2 · Rencana / belum diimplementasikan) — Memeriksa Python, PATH, venv, dan dependensi.
- **CL-179 · Build package** (P2 · Rencana / belum diimplementasikan) — Menyiapkan build dan pengemasan aplikasi dengan log.
- **CL-180 · Backup sebelum edit** (P2 · Rencana / belum diimplementasikan) — Membuat salinan file sebelum modifikasi otomatis.

### Info Harian & Perangkat
- **CL-181 · Cuaca dan agenda** (P0 · Rencana / belum diimplementasikan) — Menampilkan cuaca terkini jika sumber tersedia dan agenda yang dipilih.
- **CL-182 · Pengingat baterai** (P0 · Rencana / belum diimplementasikan) — Memberi peringatan baterai rendah jika data OS tersedia.
- **CL-183 · Penyimpanan disk** (P0 · Rencana / belum diimplementasikan) — Memantau ruang disk dan menyarankan pembersihan yang aman.
- **CL-184 · Status jaringan** (P1 · Rencana / belum diimplementasikan) — Memeriksa konektivitas dasar dan memberi petunjuk troubleshooting.
- **CL-185 · Kalkulator kontekstual** (P1 · Rencana / belum diimplementasikan) — Menghitung harga, diskon, persen, dan satuan.
- **CL-186 · Timer suara** (P1 · Rencana / belum diimplementasikan) — Membuat timer dengan pemberitahuan suara atau visual.
- **CL-187 · Clipboard history lokal** (P1 · Rencana / belum diimplementasikan) — Menyimpan clipboard hanya bila diaktifkan dan dapat dihapus.
- **CL-188 · Manajer jendela** (P2 · Rencana / belum diimplementasikan) — Membantu berpindah dan mengatur jendela aplikasi.
- **CL-189 · Mode presentasi** (P2 · Rencana / belum diimplementasikan) — Menjeda bubble, notifikasi, dan suara.
- **CL-190 · Pusat status** (P2 · Rencana / belum diimplementasikan) — Menampilkan mikrofon, layar, automasi, memory, dan API usage.

### Reliabilitas, Privasi & QA
- **CL-191 · Status izin selalu terlihat** (P0 · Rencana / belum diimplementasikan) — Menunjukkan kapan mikrofon, layar, dan otomasi aktif.
- **CL-192 · Penyimpanan lokal default** (P0 · Rencana / belum diimplementasikan) — Menjaga profil memory dan log di perangkat kecuali diekspor.
- **CL-193 · Kontrol retensi** (P0 · Rencana / belum diimplementasikan) — Menghapus jurnal setelah periode yang dipilih.
- **CL-194 · Ekspor dan hapus data** (P1 · Rencana / belum diimplementasikan) — Pengguna bisa mengekspor atau menghapus data Clara.
- **CL-195 · Redaksi rahasia** (P1 · Rencana / belum diimplementasikan) — Mendeteksi pola mirip API key/OTP sebelum jurnal disimpan.
- **CL-196 · Batas biaya API** (P1 · Rencana / belum diimplementasikan) — Memberi plafon penggunaan dan peringatan sebelum permintaan mahal.
- **CL-197 · Audit log otomasi** (P1 · Rencana / belum diimplementasikan) — Mencatat aksi yang direncanakan, disetujui, dan dicoba.
- **CL-198 · Mode demo** (P2 · Rencana / belum diimplementasikan) — Mendemonstrasikan fitur tanpa akses desktop atau API.
- **CL-199 · Regression tests** (P2 · Rencana / belum diimplementasikan) — Mengulang tes pada aksi, memory, dan validasi input.
- **CL-200 · Paket diagnostik** (P2 · Rencana / belum diimplementasikan) — Mengumpulkan versi Python dan error teknis tanpa file pribadi.

### Belajar & Pengembangan Diri
- **CL-201 · Tutor adaptif** (P0 · Rencana / belum diimplementasikan) — Menyesuaikan tingkat penjelasan berdasarkan pemahaman yang ditunjukkan.
- **CL-202 · Flashcards** (P0 · Rencana / belum diimplementasikan) — Membuat kartu tanya-jawab dari catatan yang dipilih.
- **CL-203 · Kuis latihan** (P0 · Rencana / belum diimplementasikan) — Menguji pemahaman dan menjelaskan jawaban yang salah.
- **CL-204 · Rencana belajar 30 hari** (P1 · Rencana / belum diimplementasikan) — Membagi materi menjadi target harian yang realistis.
- **CL-205 · Catatan istilah** (P1 · Rencana / belum diimplementasikan) — Menyusun glosarium istilah bisnis dan cybersecurity.
- **CL-206 · Review progres belajar** (P1 · Rencana / belum diimplementasikan) — Memperlihatkan materi yang dikuasai dan perlu diulang.
- **CL-207 · Pembuat mind map teks** (P1 · Rencana / belum diimplementasikan) — Mengubah topik besar menjadi hierarki konsep.
- **CL-208 · Simulasi wawancara** (P2 · Rencana / belum diimplementasikan) — Berlatih menjelaskan proyek, pengalaman, dan keputusan teknis.
- **CL-209 · Portofolio proyek** (P2 · Rencana / belum diimplementasikan) — Membantu mendokumentasikan tujuan, metode, hasil, dan pelajaran.
- **CL-210 · Pemeriksa plagiarisme proses** (P2 · Rencana / belum diimplementasikan) — Membantu parafrase dan sitasi secara etis, bukan menyamarkan penyalinan.

### Integrasi Ekosistem
- **CL-211 · Folder watch opt-in** (P0 · Rencana / belum diimplementasikan) — Mendeteksi file baru pada folder yang dipilih pengguna.
- **CL-212 · Impor data marketplace** (P0 · Rencana / belum diimplementasikan) — Mengolah ekspor CSV resmi tanpa perlu memberi kata sandi.
- **CL-213 · Integrasi kalender** (P0 · Rencana / belum diimplementasikan) — Membuat event hanya setelah izin dan dengan preview.
- **CL-214 · Sinkronisasi backup** (P1 · Rencana / belum diimplementasikan) — Mengirim backup terenkripsi ke lokasi yang dipilih pengguna.
- **CL-215 · Webhook lokal terbatas** (P1 · Rencana / belum diimplementasikan) — Menerima event dari tool yang disetujui dengan autentikasi.
- **CL-216 · Integrasi Canva workflow** (P1 · Rencana / belum diimplementasikan) — Menyiapkan brief dan aset untuk dibuka di Canva.
- **CL-217 · Integrasi GitHub** (P1 · Rencana / belum diimplementasikan) — Membantu review issue dan repo yang diotorisasi.
- **CL-218 · Integrasi email read-only** (P2 · Rencana / belum diimplementasikan) — Merangkum email yang dipilih tanpa mengirim atau menghapus.
- **CL-219 · Integrasi task manager** (P2 · Rencana / belum diimplementasikan) — Sinkronisasi todo dengan konfirmasi dan konflik yang ditampilkan.
- **CL-220 · Plugin capability registry** (P2 · Rencana / belum diimplementasikan) — Setiap plugin menjelaskan izin, data yang dibaca, dan aksi yang bisa dilakukan.

## Rekomendasi urutan implementasi
1. **Keandalan & memory:** tes Windows, memory vault, ekspor/impor, backup, audit log, biaya API, serta tombol berhenti yang konsisten.
2. **Percakapan:** wake word lokal opsional, deteksi akhir ucapan, interupsi saat TTS, dan indikator audio yang selalu jelas.
3. **Desktop observe–plan–act–verify:** penglihatan berkala dengan masking, validasi aksi lebih kuat, verifikasi hasil, undo/rollback untuk tugas yang mendukungnya.
4. **Bisnis berbasis data:** impor CSV ekspor marketplace, margin real, analisis funnel, eksperimen A/B, dan laporan mingguan.
5. **Cyber security berizin:** scope allowlist, mode pasif, rate limiting, audit trail, redaksi rahasia, lab lokal, dan laporan responsible disclosure.
6. **Avatar 3D:** baru setelah fondasi interaksi kuat; gunakan model berlisensi, rigging/lip-sync, dan pengaturan beban GPU.

## Prinsip desain
- Tiap kemampuan harus punya indikator ON/OFF, data yang dibaca, efek yang mungkin terjadi, dan cara berhenti.
- Jangan otomatis mengirim, memublikasikan, membayar, menghapus, mengubah keamanan, atau menginstal software tanpa persetujuan spesifik.
- Jangan menyatakan hasil riset sebagai fakta tanpa sumber dan tanggal. Jangan menjanjikan sales atau efektivitas produk.
- Semua data penjualan historis perlu ditandai tanggal dan diverifikasi ulang.
- Automasi cybersecurity hanya untuk lab atau aset dengan otorisasi tertulis.
- Memory bisa diekspor, diedit, dihapus, dan tidak boleh menyimpan password, OTP, token, API key, atau kredensial.


## Addendum fitur terimplementasi v3.3.0

Bagian ini membedakan fitur yang kini ada di source code dari ide lain dalam katalog. Setiap fitur tetap memerlukan uji lapangan di Windows sebelum dinyatakan siap produksi.

- **CL-221 · Sprite ekspresi dari unggahan** (P0 · Diimplementasikan, perlu validasi Windows) — 15 potongan spritesheet; ekspresi berganti berdasarkan mood dan status input/output suara.
- **CL-222 · Keuangan lokal SQLite** (P0 · Diimplementasikan) — transaksi pemasukan/pengeluaran serta audit klasifikasi.
- **CL-223 · Klasifikasi taksonomi Income** (P0 · Diimplementasikan) — Active, Passive, Portfolio Income.
- **CL-224 · Klasifikasi taksonomi Spending** (P0 · Diimplementasikan) — Productive, Consumptive, Consumptive with Productive Effect.
- **CL-225 · Skor kesehatan keuangan heuristik** (P1 · Diimplementasikan) — skor indikator untuk refleksi, bukan credit score atau nasihat profesional.
- **CL-226 · Aset dan depresiasi indikatif** (P1 · Diimplementasikan) — catatan harga beli/nilai perkiraan serta penyusutan sederhana.
- **CL-227 · Langganan berulang** (P1 · Diimplementasikan) — biaya bulanan/tahunan dan pengingat melalui data aplikasi.
- **CL-228 · Anggaran dan tujuan keuangan** (P1 · Diimplementasikan) — target dan pemantauan realisasi dasar.
- **CL-229 · Ekspor transaksi CSV** (P1 · Diimplementasikan) — file dibuat lokal saat diminta.
- **CL-230 · AI Coach keuangan** (P1 · Diimplementasikan) — menerima ringkasan agregat, bukan otomatis keseluruhan transaksi.
- **CL-231 · Watchlist saham BEI** (P1 · Diimplementasikan) — ticker `.JK` pada halaman Pasar Saham.
- **CL-232 · Ringkasan indeks IHSG** (P1 · Diimplementasikan, perlu internet) — data historis/quote dari Yahoo Finance; harga dapat tertunda.
- **CL-233 · Umpan berita finansial** (P1 · Diimplementasikan, perlu internet) — judul Google News RSS beserta analisis kata kunci lokal.
- **CL-234 · Sinyal tren 5/20/60 hari** (P1 · Diimplementasikan) — indikator aturan sederhana, tidak tervalidasi sebagai prediktor return.
- **CL-235 · Pembaruan pasar berkala** (P1 · Diimplementasikan, OFF secara default) — setiap 15 menit ketika aplikasi aktif.
- **CL-236 · Buku kerja 60 teknik token** (P1 · Dokumentasi) — memisahkan praktik aktif, pengaman, dan eksperimen.
- **CL-237 · Ekspor playbook bersama memori** (P2 · Diimplementasikan) — memungkinkan AI lain memahami teknik optimasi Clara.
- **CL-238 · Workflow build EXE di Windows** (P1 · Ditambahkan, belum diuji di runner pengguna) — menghasilkan artefak unduhan melalui GitHub Actions.

Batas yang belum diklaim: sinkronisasi rekening bank otomatis, koneksi real-time langsung ke broker, order trading, ramalan harga model terkalibrasi, lip-sync fonem, karakter 3D rigged, sinkronisasi memori ke semua percakapan ChatGPT, dan kendali semua jenis aplikasi tanpa batas.
