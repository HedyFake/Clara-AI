# Clara — Buku Kerja Optimasi Token (edisi 3.3.0)

Dokumen ini memetakan 60 teknik efisiensi. Status **AKTIF** berarti telah diterapkan di kode Clara atau workflow produk; **PENGAMAN** berarti menjaga kualitas/privasi; **EKSPERIMEN** berarti opsi untuk benchmark lanjutan, belum dinyalakan secara default karena dapat menurunkan akurasi atau menambah kompleksitas.

## Teknik yang aktif atau diterapkan pada workflow

1. **Local-first intent routing** — perintah sederhana dijalankan lokal tanpa panggilan model.
2. **Exact-response cache** — jawaban identik dapat dipakai ulang.
3. **Normalisasi cache key** — spasi dan huruf besar/kecil tidak menciptakan duplikasi cache.
4. **Cache TTL** — jawaban usang kedaluwarsa sesuai pengaturan.
5. **Bypass cache saat dipaksa segar** — pengguna bisa meminta jawaban baru.
6. **Tidak cache jawaban web** — mengurangi risiko memakai berita/konten web usang.
7. **Model tier routing** — model hemat untuk chat sederhana, model pintar untuk tugas kompleks.
8. **Manual deep mode** — pengguna menentukan kapan ingin analisis intensif.
9. **Output-token caps** — batas jawaban berdasarkan tingkat tugas.
10. **Batas output ekstra untuk laporan panjang** — request laporan panjang mendapat budget output lebih besar.
11. **Budget meter** — pencatatan token masuk/keluar dan estimasi biaya.
12. **Daily spend guard** — panggilan ditolak setelah batas biaya tercapai.
13. **Prompt prefix stabil** — instruksi inti diletakkan konsisten.
14. **Prompt-cache key stabil** — memberi kesempatan pada provider untuk memakai prompt caching saat didukung.
15. **Konteks memori terpilih** — hanya bagian profil yang berkaitan dengan pertanyaan.
16. **Character budget untuk memori** — konteks profil dipotong sesuai batas.
17. **History-on-follow-up** — riwayat hanya masuk saat pesan tampak sebagai kelanjutan.
18. **Riwayat singkat** — jumlah giliran sebelumnya dibatasi.
19. **Business context scoped** — konteks OdorZinc hanya dikirim untuk tugas penjualan.
20. **Local financial calculations** — total, rasio, skor, budget dan depresiasi dihitung Python/SQLite, bukan model.
21. **Local transaction categorization** — kata kunci memberi saran kategori tanpa token.
22. **CSV export local** — ekspor transaksi tidak memanggil AI.
23. **Market data local analysis** — return 5/20/60 hari serta heuristik sinyal dihitung lokal.
24. **News sentiment first-pass** — label kata kunci lokal; tidak meminta LLM untuk setiap judul.
25. **Market refresh on demand** — fetch tidak otomatis berjalan sebelum pengguna mengaktifkannya.
26. **Opt-in 15-minute market refresh** — pembaruan berkala tersedia saat aplikasi berjalan.
27. **Screen resolution reduction** — screenshot dikirim dengan ukuran/kualitas terbatas.
28. **Local screen-difference filter** — perubahan kecil bisa diabaikan sebelum upload.
29. **Live-screen interval throttling** — pengamatan dibatasi jeda waktu.
30. **Live upload cap** — jumlah gambar per sesi dibatasi.
31. **Capture-on-demand** — analisis layar satu kali saat diminta pengguna.
32. **Sensitive-window exclusion** — jendela berisiko dikecualikan dari pemantauan.
33. **Text-first desktop planning** — rencana aksi disusun terlebih dahulu, screenshot hanya saat dibutuhkan.
34. **Structured action plan** — aksi berbentuk JSON dengan validasi lokal.
35. **Action allowlist** — shell bebas dan tindakan berisiko tidak diizinkan.
36. **Per-action confirmation** — tindakan berisiko memerlukan persetujuan.
37. **Maximum action count** — rencana otomasi tidak boleh tak terbatas.
38. **Safe path checks** — operasi berkas dibatasi pada folder yang diizinkan.
39. **Tool-error trimming** — kesalahan dibatasi panjangnya sebelum ditampilkan.
40. **Secret redaction** — pola token, OTP, API key, dan kata sandi disamarkan pada jurnal.
41. **Task-scoped advisor prompt** — prompt konsultan hanya digunakan bila pengguna meminta analisis keuangan.
42. **Aggregate-only finance snapshot** — AI Coach menerima total agregat; tidak mengirim seluruh database.
43. **No AI for repetitive UI animation** — karakter dianimasikan lokal dari sprite sheet.
44. **Rendered-frame cache** — frame avatar disimpan lokal dalam cache.
45. **Concurrent market fetch with a cap** — pembaruan harga/berita memakai jumlah worker terbatas.
46. **Headline deduplication** — berita dengan URL/judul sama tidak ditampilkan berkali-kali.
47. **Ticker watchlist** — hanya ticker yang dipilih pengguna yang diperiksa untuk kuotasi.
48. **Source-separated feeds** — harga/berita disegarkan terpisah dari chat AI.
49. **API retry only on transient errors** — pengulangan dibatasi untuk error sementara.
50. **Timeouts** — permintaan web/API tidak dibiarkan tanpa batas.
51. **Token/model settings centralized** — model dan budget dapat diganti tanpa mengedit kode.
52. **Memory journal autosave** — percakapan Clara dapat disimpan lokal saat pengaturan memori aktif.
53. **Portable memory export** — profil dan jurnal dapat diekspor tanpa API call.
54. **DPAPI for optional key storage** — kunci disimpan terenkripsi pada Windows bila pengguna mengaktifkan.
55. **Cache-hit metrics** — hit cache dan kerja lokal dihitung dalam meter.
56. **Output reuse across UI surfaces** — teks jawaban yang sama dipakai di chat, bubble dan panel besar.
57. **Category-specific prompt shaping** — instruksi AI disesuaikan untuk task penjualan/keuangan tanpa membawa semua konteks.
58. **Risk-aware escalation** — tugas berisiko beralih ke pratinjau/konfirmasi alih-alih mencoba otomatis tanpa kontrol.
59. **No external summarizer by default** — tidak ada panggilan model kedua hanya untuk mengompresi prompt.
60. **Evidence/uncertainty rules** — prompt advisor meminta sumber resmi, tanggal, serta label ketidakpastian untuk aturan yang berubah.

## Eksperimen yang layak diuji sebelum diaktifkan

- Kompresi semantik berbasis model (mis. LLMLingua) harus diukur pada benchmark jawaban Clara karena dapat membuang angka, nama pasal, atau detail yang penting.
- Retrieval lokal berbasis SQLite FTS/vector dapat dipakai untuk arsip panjang; saat ini Clara memakai pemilihan bagian profil dan jurnal pendek, bukan vector database.
- Tokenizer provider dapat dipakai untuk menghitung token sebelum request; meter saat ini memakai usage resmi setelah panggilan dan tarif konfigurasi.
- Adaptive output budget bisa memakai tingkat ketidakpastian dan anggaran tersisa, tetapi perlu guardrail agar jawaban kompleks tidak terpotong.
- Prompt/output compression proxy, multi-agent voting, semantic cache, speculative decoding, dan model lokal memerlukan benchmark privasi, akurasi, latensi, dan total biaya sebelum diadopsi.
- Cache lintas pengguna tidak digunakan karena dapat membocorkan konteks. Cache lokal juga tidak diterapkan ke pertanyaan web yang mudah kedaluwarsa.

## Sumber eksplorasi GitHub Topics

- https://github.com/topics/token-optimization
- https://github.com/topics/token-optimizer
- https://github.com/topics/tokenoptimization
- https://github.com/topics/prompt-compression
- https://github.com/topics/context-compression
- https://github.com/topics/llm-compression
- https://github.com/topics/model-routing
- https://github.com/topics/ai-model-routing
- https://github.com/topics/prompt-caching
- https://github.com/topics/context-engineering

Topik ini adalah katalog repositori komunitas yang dinamis, bukan rekomendasi keamanan/akurasi otomatis. Jumlah repo dan aktivitasnya bisa berubah. Implementasi Clara sengaja memilih teknik lokal sederhana terlebih dahulu agar hemat tanpa menambah panggilan model atau mengorbankan detail penting.
