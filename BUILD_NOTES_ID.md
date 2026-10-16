# Catatan Build Clara Desktop Buddy v3.3.0

- Proyek adalah aplikasi Python/Tkinter untuk Windows 10/11, ditargetkan pada Python 3.11/3.12 64-bit.
- ZIP source ini **tidak menyertakan EXE yang sudah dibangun**. Lingkungan pembuatan ZIP berbasis Linux tanpa runtime Windows/PyInstaller, sehingga file EXE harus dibangun di Windows atau melalui workflow GitHub Actions yang disediakan.
- Di Windows, jalankan `BUILD_EXE.bat`. Untuk menjalankan source, `START_CLARA.bat` akan menyiapkan `.venv` dan menjalankan aplikasi.
- Build memasukkan aset spritesheet ekspresi, dokumentasi memori dan playbook optimasi token. Uji kembali setelah build: startup GUI, karakter transparan, suara, toggle mikrofon, Live Screen, dan otomasi GUI.
- Build tidak menambahkan Clara ke Windows startup, tidak memasang layanan latar belakang, dan tidak mengubah konfigurasi keamanan sistem. EXE tidak ditandatangani; SmartScreen dapat menampilkan peringatan.
- Jurnal prompt/jawaban bisa aktif secara default sesuai setting pengguna; matikan bila tidak ingin menyimpan percakapan. Pola rahasia hanya disamarkan best-effort.
- API key OpenAI ditagih terpisah dari langganan ChatGPT. Tidak ada API key atau credential yang harus disertakan dalam source repository.
- Avatar menggunakan 15 frame 2D; model 3D rigged, lip-sync fonem, dan wake word lokal belum tersedia.
- Katalog utama berisi 220 konsep fitur, disusul addendum implementasi v3.3.0. Status rencana dan implemented dibedakan.

Lihat `README_ID.md`, `PRIVACY.md`, `AUDIT_REPORT_ID.md`, dan `BUILD_WINDOWS.md` untuk batasan serta panduan.
