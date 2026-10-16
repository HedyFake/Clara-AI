# Ringkasan privasi Clara Desktop Buddy

Clara punya mode yang sengaja harus diaktifkan secara eksplisit. Status ON/OFF ditampilkan di panel.

- **Mikrofon berkelanjutan:** mati secara default. Setelah pengguna mengaktifkannya, audio frase diproses oleh Google Speech Recognition online untuk transkripsi. Jika API key telah disetel, transkrip diteruskan ke OpenAI API untuk jawaban. Tidak ada wake word lokal; suara di sekitar mikrofon dapat tertangkap selama mode aktif.
- **TTS:** suara balasan menggunakan speech engine lokal Windows jika tersedia. Audio keluaran dapat tertangkap mikrofon; aplikasi mencoba mengabaikan ucapan saat Clara sedang berbicara.
- **Live Screen AI:** mati secara default dan hanya dimulai sesudah dialog persetujuan. Clara membandingkan frame secara lokal, lalu frame yang berubah dikirim ke OpenAI API paling cepat sekali per 20 detik. Sesi berakhir otomatis setelah 30 menit. Jeda berdasarkan judul jendela sensitif bersifat heuristik dan tidak sempurna.
- **Rencana otomasi desktop:** screenshot dan instruksi dikirim ke AI untuk membuat rencana. Clara memperlihatkan langkah-langkah sebelum dieksekusi. Maksimum 12 langkah yang diizinkan per rencana; beberapa kategori aksi sistem sengaja ditolak. Jika Live Screen sudah aktif, izin berbagi layar itu juga dipakai untuk screenshot perencanaan. Mode responsif opsional (mati secara default) hanya melewati pratinjau untuk maksimal 3 aksi membuka aplikasi/situs. Persetujuan tidak menjamin bahwa setiap aksi GUI tidak berisiko.
- **API key:** disimpan di memori aplikasi, tidak ditulis sengaja ke file. Pengguna harus memasukkan ulang setelah aplikasi dimulai ulang.
- **Aktivitas laptop:** pemantauan judul jendela lokal mati secara default dan membutuhkan persetujuan. Log lokal tidak diunggah oleh fitur pemantauan tersebut.
- **Penyimpanan:** screenshot Live Screen tidak disimpan ke file oleh loop; image dikirim untuk analisis jika frame dinilai berubah. Screenshot manual bisa disimpan lokal tanpa API key.
- **Biaya:** penggunaan OpenAI API terpisah dari langganan ChatGPT. Live Screen dapat menghasilkan beberapa permintaan API setiap sesi aktif.
- **Tidak ada startup otomatis:** aplikasi berjalan hanya saat pengguna meluncurkannya. Gunakan menu avatar Keluar untuk menghentikan aplikasi.

Pengguna harus mematikan mode pengamatan sebelum membuka data sensitif, termasuk kredensial, OTP, akun finansial, pesan pribadi, data pelanggan, serta dokumen rahasia. Deteksi judul jendela tidak dapat menjamin bahwa semua data sensitif tertangkap atau terhindar dari screenshot.

- **Memory Vault:** profil memory disimpan lokal di `%LOCALAPPDATA%\ClaraDesktopBuddy\memory_profile.md`. Atas permintaan pengguna, jurnal otomatis **ON secara default** dan menyimpan prompt serta jawaban AI di `memory_journal.jsonl`. Preferensi dapat dimatikan dan disimpan lintas sesi. Beberapa pola credential umum disamarkan sebelum ditulis, tetapi ini bukan jaminan deteksi sempurna. Lima percakapan terakhir dapat digunakan sebagai konteks request berikutnya. Jurnal dapat berisi informasi pribadi; tinjau sebelum ekspor/backup dan jangan masukkan password, OTP, API key, token, credential bank, atau data pelanggan rahasia.


## Modul Keuangan dan Pasar Saham v3.3
- **Keuangan pribadi/bisnis:** transaksi, aset, langganan, anggaran, tujuan, dan audit klasifikasi disimpan dalam SQLite lokal `finance.db` di `%LOCALAPPDATA%\ClaraDesktopBuddy`. Perhitungan dashboard dan klasifikasi kata kunci berjalan lokal. Ekspor CSV dibuat hanya ketika diminta. Database finance tidak otomatis dimasukkan ke ZIP memori.
- **AI Coach keuangan:** ketika pengguna menekan tombol analisis, aplikasi mengirim ringkasan agregat yang dipilih (bukan otomatis seluruh basis transaksi) ke API untuk mendapat saran. Periksa data yang ditampilkan dan jangan kirim rekening, identitas, atau detail transaksi sensitif yang tidak diperlukan.
- **Data saham/berita:** saat pengguna menekan refresh atau mengaktifkan auto-refresh, aplikasi meminta data quote/historis kepada Yahoo Finance dan berita kepada Google News RSS. Auto-refresh OFF secara default dan berlangsung hanya selama aplikasi terbuka. Penyedia dapat menerima metadata koneksi seperti alamat IP; harga/berita mungkin tertunda, tidak lengkap atau berbeda dari broker.
- **Rekomendasi:** sinyal dibuat dengan heuristik transparan sederhana, bukan model yang terkalibrasi untuk meramalkan harga. Data pasar tidak membentuk perintah transaksi dan Clara tidak menempatkan order. Pengguna wajib melakukan verifikasi mandiri.
- **Memori ekspor:** ZIP memori mencakup profil/jurnal dan dokumentasi panduan yang dipilih, bukan `finance.db`, API key atau kredensial broker. Tinjau jurnal sebelum berbagi karena masih mungkin mengandung informasi pribadi; penyamaran rahasia bersifat best-effort, tidak sempurna.
