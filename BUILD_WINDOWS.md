# Cara membuat EXE Windows Clara

## Opsi A — langsung di laptop Windows
1. Ekstrak folder proyek ke lokasi yang bisa ditulis.
2. Pasang Python 3.11/3.12 64-bit dari python.org dan pastikan Tcl/Tk diikutkan.
3. Klik dua kali `BUILD_EXE.bat` dan tunggu instalasi dependensi serta proses PyInstaller selesai.
4. File `ClaraDesktopBuddy.exe` akan muncul di folder proyek. Jalankan terlebih dahulu di akun Windows yang akan dipakai dan uji mikrofon, TTS, transparansi avatar, dan otomasi.

## Opsi B — GitHub Actions
1. Buat repository milikmu dan unggah source proyek ini.
2. Buka tab **Actions**, pilih **Build Clara Windows EXE**, lalu pilih **Run workflow**. Workflow juga berjalan saat tag dengan awalan `v` di-push.
3. Setelah job sukses, unduh artifact `ClaraDesktopBuddy-Windows-x64` di halaman run. Artifact disimpan 14 hari.
4. Karena ini executable, build hanya dijalankan dari source yang kamu tinjau sendiri. Build workflow bukan hasil build yang sudah dibuktikan dalam ZIP ini.

## Catatan
- Lingkungan pembuat ZIP saat ini Linux dan tidak memiliki PyInstaller/Windows runtime, maka EXE belum dikompilasi atau dites pada Windows di sini.
- Auto-refresh saham OFF secara default; mikrofon dan Live Screen memerlukan izin eksplisit. Tidak ada order trading otomatis.
- Jangan menerbitkan API key, token, data akun, atau database finansial ke GitHub.
