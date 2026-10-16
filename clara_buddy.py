# Clara Desktop Buddy v3.3.0 - asisten desktop Windows, finance, pasar saham, hemat token
# Modul: clara_core.py (logika/hemat token), clara_avatar.py (karakter animasi).
from __future__ import annotations

import base64
import hashlib
import io
import concurrent.futures
import json
import os
import queue
import re
import subprocess
import sys
import threading
import time
import webbrowser
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog

try:
    import requests
    import psutil
    import pyautogui
    from PIL import Image
    import pyperclip
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Dependensi belum lengkap. Jalankan INSTALL_CLARA.bat.\nDetail: %s" % exc)

import clara_core as core
from clara_core import APP_DIR, WORKSPACE, VERSION
from clara_avatar import AvatarAnimator, AvatarRenderer, KEY_COLOR
import clara_finance as finance
import clara_market as market

# ----------------------------------------------------------------------------- tema
BG, SIDE, CARD, CARD2, LINE = "#0a0f1c", "#0d1426", "#111a30", "#17253f", "#22335a"
TXT, MUTED, ACC, ACC2 = "#e8eefc", "#8fa1c7", "#5fd0ff", "#2f6fe0"
USER_BG, WARN, OK = "#1c3c7a", "#ff7a7a", "#59e0a4"
FONT, FONT_B, FONT_H = ("Segoe UI", 10), ("Segoe UI Semibold", 10), ("Segoe UI Semibold", 17)
KEY_HEX = "#%02x%02x%02x" % KEY_COLOR

MEMORY_PROFILE_FILE = APP_DIR / "memory_profile.md"
MEMORY_JOURNAL_FILE = APP_DIR / "memory_journal.jsonl"
CONTEXT_FILE = APP_DIR / "sales_context.txt"
ACTIVITY_CSV = APP_DIR / "activity_log.csv"
KEY_FILE = APP_DIR / "apikey.dat"
SCREENSHOT_DIR = Path.home() / "Pictures" / "ClaraBuddy"

DEFAULT_SALES_CONTEXT = (
    "Produk: OdorZinc, spray penghilang bau 100 ml (sepatu, helm, tas, jok mobil, kain).\n"
    "Pesan utama: membantu mengurangi bau, bukan sekadar pewangi. Hindari klaim 'pasti hilang 100%'.\n"
    "Marketplace: Shopee. Catatan lama (cek ulang sebelum dipakai): harga sekitar Rp36.000, komisi afiliasi 4%, ROAS sekitar 1,86 vs target 7.\n"
    "Prioritas: thumbnail/CTR, kejelasan manfaat, kepercayaan, konversi, video pendek, evaluasi biaya iklan.\n"
    "CATATAN: ini catatan awal, bukan data penjualan terkini. Minta angka terbaru saat analisis."
)


def resource_path(name: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / name


def tail_lines(path: Path, n: int, maxbytes: int = 40000) -> list[str]:
    try:
        with path.open("rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - maxbytes))
            data = f.read().decode("utf-8", errors="ignore")
        return [l for l in data.splitlines() if l.strip()][-n:]
    except Exception:
        return []



def role_is_journalable(text: str) -> bool:
    t=(text or "").strip()
    return bool(t) and len(t)>1 and not t.startswith("API HTTP ")

def image_to_data_url(img: "Image.Image", max_edge: int, quality: int = 70):
    """Kecilkan gambar. Mengembalikan (data_url, scale) dengan scale = lebar_asli / lebar_terkirim."""
    img = img.convert("RGB")
    ow = img.width
    img.thumbnail((max_edge, max_edge))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii"), ow / float(img.width)


def active_window_title() -> str:
    if sys.platform != "win32":
        return ""
    try:
        import ctypes
        u = ctypes.windll.user32
        h = u.GetForegroundWindow()
        n = u.GetWindowTextLengthW(h)
        if n <= 0:
            return ""
        buf = ctypes.create_unicode_buffer(n + 1)
        u.GetWindowTextW(h, buf, n + 1)
        return buf.value
    except Exception:
        return ""


def focus_window_by_title(fragment: str) -> bool:
    if sys.platform != "win32":
        return False
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    found = []
    EnumProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

    def cb(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            n = user32.GetWindowTextLengthW(hwnd)
            if n:
                b = ctypes.create_unicode_buffer(n + 1)
                user32.GetWindowTextW(hwnd, b, n + 1)
                if fragment.casefold() in b.value.casefold():
                    found.append(hwnd)
        return True

    user32.EnumWindows(EnumProc(cb), 0)
    if not found:
        return False
    user32.ShowWindow(found[0], 9)
    user32.SetForegroundWindow(found[0])
    return True


class Pill(tk.Label):
    """Toggle bergaya pil (lebih ringan & rapi daripada Checkbutton)."""

    def __init__(self, parent, text, var: tk.BooleanVar, command=None, accent=ACC):
        super().__init__(parent, text=text, font=FONT, padx=11, pady=5, cursor="hand2", bd=0)
        self.var, self.command, self.accent = var, command, accent
        self.bind("<Button-1>", self._click)
        var.trace_add("write", lambda *_: self._paint())
        self._paint()

    def _click(self, _e=None):
        self.var.set(not self.var.get())
        if self.command:
            self.command()

    def _paint(self):
        on = bool(self.var.get())
        self.configure(bg=self.accent if on else CARD2, fg="#06101f" if on else MUTED)


class ClaraApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Clara")
        root.geometry("1060x720")
        root.minsize(880, 600)
        root.configure(bg=BG)
        root.protocol("WM_DELETE_WINDOW", self.hide_dashboard)

        self.settings = core.load_settings()
        self.meter = core.UsageMeter()
        self.cache = core.AnswerCache()
        self.ui_q: "queue.Queue" = queue.Queue()
        self.tts_q: "queue.Queue" = queue.Queue()
        self.anim = AvatarAnimator()
        self.renderer = AvatarRenderer()
        self.photos: dict = {}
        self.market_watchlist = list(market.DEFAULT_WATCHLIST)
        self.market_quotes: list[dict] = []
        self.market_headlines: list[dict] = []
        self.market_index: dict | None = None
        self.market_last_refresh = 0.0
        self.market_refreshing = False
        self.market_errors: list[str] = []
        try:
            finance.init_db()
            saved_watchlist = core.load_json(APP_DIR / "market_watchlist.json", {})
            if isinstance(saved_watchlist, dict) and isinstance(saved_watchlist.get("symbols"), list):
                clean = []
                for symbol in saved_watchlist["symbols"]:
                    try:
                        v = market._clean_symbol(str(symbol))
                        if v != market.INDEX_SYMBOL and v not in clean:
                            clean.append(v)
                    except Exception:
                        continue
                if clean:
                    self.market_watchlist = clean[:100]
        except Exception:
            pass

        self.busy = False
        self.automation_stop = threading.Event()
        self.automation_running = False
        self.planning = False
        self.continuous = False
        self.stop_listening = None
        self.tts_speaking = False
        self.tts_ok = True
        self.tts_voices: list = []
        self.ignore_audio_until = 0.0
        self.last_voice = ("", 0.0)
        self.live_on = False
        self.live_busy = False
        self.live_ref = None
        self.live_last_upload = 0.0
        self.live_uploads = 0
        self.live_end = 0.0
        self.live_obs = (0.0, "")
        self.monitoring = False
        self.last_title = None
        self.last_answer = ""
        self.last_prompt = ""
        self.pet_drag = (0, 0, 0, 0, False)
        self.bubble = None
        self.large = None

        S = self.settings
        self.v_deep = tk.BooleanVar(value=S["deep_mode"])
        self.v_web = tk.BooleanVar(value=S["use_web"])
        self.v_speak = tk.BooleanVar(value=S["speak"])
        self.v_auto = tk.BooleanVar(value=S["autopilot"])
        self.v_mic = tk.BooleanVar(value=False)
        self.v_live = tk.BooleanVar(value=False)
        self.v_key = tk.StringVar(value=os.environ.get("OPENAI_API_KEY", ""))
        self.v_remember = tk.BooleanVar(value=S["remember_key"])
        self.v_voice = tk.StringVar(value="")
        self.v_status = tk.StringVar(value="Siap.")
        self.v_usage = tk.StringVar(value="")
        self.v_memauto = tk.BooleanVar(value=S["memory_autosave"])
        self.v_memuse = tk.BooleanVar(value=True)
        self.v_market_auto = tk.BooleanVar(value=S.get("market_auto_refresh", False))
        self.v_mon = tk.StringVar(value="Pemantauan: MATI")
        self.v_active = tk.StringVar(value="")
        self.setting_vars: dict = {}

        self._load_saved_key()
        self._ensure_memory_files()
        self._build_ui()
        self._build_pet()
        threading.Thread(target=self._tts_loop, daemon=True, name="ClaraTTS").start()
        self.root.after(60, self._pump)
        self.root.after(100, self._animate)
        self.root.after(1500, self._monitor_tick)
        self.root.after(2000, self._refresh_usage)
        self.root.after(60000, self._market_auto_tick)
        self.chat_add("sys", "Clara v%s siap. Perintah sederhana (buka app/situs, cari, jam, screenshot, 'ingat ...') "
                      "dikerjakan lokal tanpa token." % VERSION)
        if not self.api_key():
            self.chat_add("clara", "Halo Hedy! Isi API key di menu Hemat & Pengaturan agar aku bisa berpikir lewat OpenAI. "
                          "Tanpa key pun aku tetap bisa membuka aplikasi/situs dan mencatat memori.")

    # ------------------------------------------------------------------ infrastruktur UI
    def ui(self, fn, *a):
        self.ui_q.put((fn, a))

    def _pump(self):
        try:
            for _ in range(40):
                fn, a = self.ui_q.get_nowait()
                try:
                    fn(*a)
                except Exception:
                    pass
        except queue.Empty:
            pass
        self.root.after(60, self._pump)

    def status(self, text: str):
        self.ui(self.v_status.set, text[:200])

    def api_key(self) -> str:
        return (self.v_key.get() or os.environ.get("OPENAI_API_KEY", "")).strip()

    def _load_saved_key(self):
        if self.settings.get("remember_key") and KEY_FILE.exists() and not self.v_key.get():
            try:
                k = core.dpapi_decrypt(KEY_FILE.read_text(encoding="utf-8").strip())
                if k:
                    self.v_key.set(k)
            except Exception:
                pass

    def _ensure_memory_files(self):
        try:
            APP_DIR.mkdir(parents=True, exist_ok=True)
            if not MEMORY_PROFILE_FILE.exists():
                seed = resource_path("memory_profile.md")
                MEMORY_PROFILE_FILE.write_text(seed.read_text(encoding="utf-8") if seed.exists() else "# Profil Clara\n", encoding="utf-8")
            if not MEMORY_JOURNAL_FILE.exists():
                MEMORY_JOURNAL_FILE.write_text("", encoding="utf-8")
            SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass

    def save_settings(self):
        S = self.settings
        S.update(deep_mode=self.v_deep.get(), use_web=self.v_web.get(), speak=self.v_speak.get(),
                 autopilot=self.v_auto.get(), remember_key=self.v_remember.get(), memory_autosave=self.v_memauto.get(),
                 market_auto_refresh=self.v_market_auto.get())
        core.save_settings(S)

    # ------------------------------------------------------------------ layout
    def _build_ui(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TCombobox", fieldbackground=CARD2, background=CARD2, foreground=TXT, arrowcolor=ACC)
        style.configure("Vertical.TScrollbar", background=CARD2, troughcolor=BG, bordercolor=BG, arrowcolor=MUTED)

        self.side = tk.Frame(self.root, bg=SIDE, width=214)
        self.side.pack(side="left", fill="y")
        self.side.pack_propagate(False)
        self.main = tk.Frame(self.root, bg=BG)
        self.main.pack(side="left", fill="both", expand=True)

        self.portrait = None
        try:
            p = resource_path("assets/expressions/expression_0_0.png")
            if p.exists():
                img = Image.open(p).convert("RGBA")
                img.thumbnail((96, 96), Image.Resampling.LANCZOS)
                canvas = Image.new("RGBA", (96, 96), (0, 0, 0, 0))
                canvas.alpha_composite(img, ((96-img.width)//2, (96-img.height)//2))
                buf = io.BytesIO(); canvas.save(buf, "PNG", optimize=True)
                self.portrait = tk.PhotoImage(data=base64.b64encode(buf.getvalue()))
        except Exception:
            self.portrait = None
        top = tk.Frame(self.side, bg=SIDE)
        top.pack(fill="x", pady=(20, 8))
        if self.portrait:
            tk.Label(top, image=self.portrait, bg=SIDE).pack()
        else:
            tk.Label(top, text="C", font=("Segoe UI Semibold", 30), bg=SIDE, fg=ACC).pack()
        tk.Label(top, text="Clara", font=FONT_H, bg=SIDE, fg=TXT).pack(pady=(6, 0))
        tk.Label(top, text="asisten desktop • v" + VERSION, font=("Segoe UI", 8), bg=SIDE, fg=MUTED).pack()

        self.pages: dict = {}
        self.nav: dict = {}
        items = [("chat", "💬  Chat"), ("jual", "🛍  Bantu Jualan"), ("keuangan", "💰  Keuangan"), ("saham", "📈  Pasar Saham"),
                 ("akt", "🖥  Aktivitas"), ("aksi", "⚡  Aksi Cepat"), ("mem", "🧠  Memori"), ("hemat", "🪙  Hemat & Pengaturan")]
        navf = tk.Frame(self.side, bg=SIDE)
        navf.pack(fill="x", pady=(10, 0))
        for key, label in items:
            lb = tk.Label(navf, text=label, anchor="w", font=FONT, bg=SIDE, fg=MUTED, padx=22, pady=9, cursor="hand2")
            lb.pack(fill="x")
            lb.bind("<Button-1>", lambda _e, k=key: self.show_page(k))
            self.nav[key] = lb
            self.pages[key] = tk.Frame(self.main, bg=BG)

        bottom = tk.Frame(self.side, bg=SIDE)
        bottom.pack(side="bottom", fill="x", padx=16, pady=14)
        tk.Button(bottom, text="Mode avatar besar", command=self.toggle_large, bg=CARD2, fg=TXT, relief="flat", bd=0,
                  font=FONT, activebackground=LINE, activeforeground=TXT, cursor="hand2", pady=7).pack(fill="x", pady=(0, 6))
        tk.Button(bottom, text="Sembunyikan panel", command=self.hide_dashboard, bg=CARD2, fg=MUTED, relief="flat", bd=0,
                  font=FONT, activebackground=LINE, cursor="hand2", pady=6).pack(fill="x", pady=(0, 6))
        tk.Button(bottom, text="Keluar", command=self.quit_app, bg=SIDE, fg=WARN, relief="flat", bd=0, font=FONT,
                  activebackground=SIDE, activeforeground=WARN, cursor="hand2").pack(fill="x")
        tk.Label(self.side, textvariable=self.v_usage, font=("Segoe UI", 8), bg=SIDE, fg=MUTED, justify="left", wraplength=180).pack(side="bottom", fill="x", padx=16)
        self.usage_bar = tk.Canvas(self.side, height=6, bg=CARD2, highlightthickness=0)
        self.usage_bar.pack(side="bottom", fill="x", padx=16, pady=(0, 6))

        sb = tk.Label(self.main, textvariable=self.v_status, anchor="w", font=("Segoe UI", 9), bg=SIDE, fg=MUTED, padx=14, pady=6)
        sb.pack(side="bottom", fill="x")

        self._build_chat()
        self._build_sales()
        self._build_finance()
        self._build_market()
        self._build_activity()
        self._build_actions()
        self._build_memory()
        self._build_saver()
        self.show_page("chat")

    def show_page(self, key: str):
        for k, f in self.pages.items():
            f.pack_forget()
            self.nav[k].configure(bg=SIDE, fg=MUTED)
        self.pages[key].pack(fill="both", expand=True)
        self.nav[key].configure(bg=CARD, fg=ACC)
        if key == "hemat":
            self._refresh_usage()
        elif key == "keuangan":
            self._refresh_finance_view()
        elif key == "saham" and self.v_market_auto.get() and time.time() - self.market_last_refresh > 900:
            self.refresh_market()

    def _title(self, parent, text, sub=""):
        tk.Label(parent, text=text, font=FONT_H, bg=BG, fg=TXT, anchor="w").pack(fill="x", padx=24, pady=(20, 0))
        if sub:
            tk.Label(parent, text=sub, font=("Segoe UI", 9), bg=BG, fg=MUTED, anchor="w", justify="left", wraplength=720).pack(fill="x", padx=24, pady=(2, 10))

    def _btn(self, parent, text, cmd, primary=True, **kw):
        return tk.Button(parent, text=text, command=cmd, relief="flat", bd=0, cursor="hand2", font=FONT_B, padx=14, pady=7,
                         bg=ACC2 if primary else CARD2, fg="#ffffff" if primary else TXT,
                         activebackground=ACC if primary else LINE, activeforeground="#06101f" if primary else TXT, **kw)

    def _textbox(self, parent, height=6):
        return scrolledtext.ScrolledText(parent, height=height, wrap="word", bg=CARD, fg=TXT, insertbackground=ACC, relief="flat",
                                         font=FONT, padx=10, pady=8, bd=0, highlightthickness=1, highlightbackground=LINE, highlightcolor=ACC)

    # ------------------------------------------------------------------ halaman chat
    def _build_chat(self):
        page = self.pages["chat"]
        wrap = tk.Frame(page, bg=BG)
        wrap.pack(fill="both", expand=True, padx=20, pady=(16, 4))
        self.chat = tk.Text(wrap, wrap="word", bg=BG, fg=TXT, relief="flat", font=("Segoe UI", 10), bd=0, padx=6, pady=6,
                            cursor="arrow", highlightthickness=0, spacing2=2)
        sb = ttk.Scrollbar(wrap, orient="vertical", command=self.chat.yview)
        self.chat.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.chat.pack(side="left", fill="both", expand=True)
        self.chat.tag_configure("u", background=USER_BG, foreground="#ffffff", justify="right", lmargin1=160, lmargin2=160, rmargin=10, spacing1=8, spacing3=8)
        self.chat.tag_configure("c", background=CARD2, foreground=TXT, lmargin1=12, lmargin2=12, rmargin=150, spacing1=8, spacing3=8)
        self.chat.tag_configure("who_u", foreground=ACC, justify="right", rmargin=10, font=("Segoe UI", 8), spacing1=10)
        self.chat.tag_configure("who_c", foreground=ACC, lmargin1=12, font=("Segoe UI", 8), spacing1=10)
        self.chat.tag_configure("sys", foreground=MUTED, justify="center", font=("Segoe UI", 9, "italic"), spacing1=8)
        self.chat.tag_configure("meta", foreground=MUTED, lmargin1=12, font=("Segoe UI", 8))
        self.chat.configure(state="disabled")

        comp = tk.Frame(page, bg=BG)
        comp.pack(fill="x", padx=20, pady=(4, 12))
        pills = tk.Frame(comp, bg=BG)
        pills.pack(fill="x", pady=(0, 6))
        Pill(pills, "🎙 Dengar terus", self.v_mic, self.toggle_mic).pack(side="left", padx=(0, 6))
        Pill(pills, "👁 Live layar", self.v_live, self.toggle_live).pack(side="left", padx=(0, 6))
        Pill(pills, "🧠 Mikir keras", self.v_deep, self.save_settings, accent="#b69cff").pack(side="left", padx=(0, 6))
        Pill(pills, "🌐 Web", self.v_web, self.save_settings).pack(side="left", padx=(0, 6))
        Pill(pills, "⚡ Otonom", self.v_auto, self._autopilot_changed, accent=OK).pack(side="left", padx=(0, 6))
        Pill(pills, "🔊 Suara", self.v_speak, self.save_settings).pack(side="left")
        row = tk.Frame(comp, bg=BG)
        row.pack(fill="x")
        self.entry = tk.Text(row, height=3, wrap="word", bg=CARD, fg=TXT, insertbackground=ACC, relief="flat", font=("Segoe UI", 11),
                             padx=12, pady=8, bd=0, highlightthickness=1, highlightbackground=LINE, highlightcolor=ACC)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self._enter_pressed)
        btns = tk.Frame(row, bg=BG)
        btns.pack(side="left", padx=(8, 0), fill="y")
        self._btn(btns, "Kirim", self.send_from_entry).pack(fill="x")
        self._btn(btns, "🎙", self.listen_once, primary=False).pack(fill="x", pady=(4, 0))
        row2 = tk.Frame(comp, bg=BG)
        row2.pack(fill="x", pady=(6, 0))
        for text, cmd in (("Analisis layar", self.analyze_screen), ("Ulangi (tanpa cache)", self.regenerate),
                          ("Salin jawaban", self.copy_answer), ("■ Hentikan otomasi", self.stop_automation)):
            tk.Button(row2, text=text, command=cmd, relief="flat", bd=0, bg=BG, fg=WARN if "Hentikan" in text else MUTED,
                      activebackground=BG, activeforeground=ACC, font=("Segoe UI", 9), cursor="hand2").pack(side="left", padx=(0, 14))
        tk.Label(row2, text="Enter = kirim • Shift+Enter = baris baru • diskusi tetap bisa saat otomasi berjalan", font=("Segoe UI", 8), bg=BG, fg=MUTED).pack(side="right")

    def _enter_pressed(self, event):
        if event.state & 0x1:  # Shift: biarkan baris baru
            return None
        self.send_from_entry()
        return "break"

    def chat_add(self, role: str, text: str, meta: str = ""):
        def w():
            c = self.chat
            c.configure(state="normal")
            if role == "sys":
                c.insert("end", text + "\n", "sys")
            else:
                c.insert("end", ("Kamu" if role == "user" else "Clara") + "\n", "who_u" if role == "user" else "who_c")
                c.insert("end", " " + text.strip() + " \n", "u" if role == "user" else "c")
                if meta:
                    c.insert("end", meta + "\n", "meta")
            c.configure(state="disabled")
            c.see("end")
        self.ui(w)

    def send_from_entry(self):
        text = self.entry.get("1.0", "end").strip()
        if not text:
            return
        self.entry.delete("1.0", "end")
        self.submit(text)

    # ------------------------------------------------------------------ alur utama submit
    def submit(self, text: str, from_voice: bool = False, force_fresh: bool = False, sales: bool = False):
        self.last_prompt = text
        self.anim.mood = self._emotion_from_text(text, user_input=True)
        self.chat_add("user", text if not sales else text.split("\n\n")[0])
        cmd = None if sales else core.parse_local_command(text)
        if cmd:  # 1) perintah lokal = 0 token
            self.meter.hit_local()
            self.run_local(cmd)
            return
        if not sales and self._asks_about_screen(text) and self.live_obs[1] and time.time() - self.live_obs[0] < 90:
            self.meter.hit_local()
            self.reply("Terakhir kulihat (%s): %s" % (datetime.fromtimestamp(self.live_obs[0]).strftime("%H:%M:%S"), self.live_obs[1]), meta="dari Live layar • 0 token")
            return
        if not sales and self.looks_like_desktop_action(text):
            self.plan_desktop(text)
            return
        self.ask_ai(text, force_fresh=force_fresh, sales=sales)

    @staticmethod
    def _asks_about_screen(text: str) -> bool:
        return bool(re.search(r"\bapa yang (?:kamu )?lihat\b|\bapa di layar\b|\blagi ngapain\b", text.casefold()))

    @staticmethod
    def looks_like_desktop_action(text: str) -> bool:
        t = core.normalize_command(text).casefold()
        return t.startswith(("klik ", "ketik ", "tuliskan ", "scroll ", "gulir ", "tutup ", "pindah ke ", "buka tab ", "minimize ",
                             "maksimalkan ", "salin ", "simpan ", "pergi ke ", "buka ", "jalankan ", "click ", "type ", "go to ", "open "))

    @staticmethod
    def _emotion_from_text(text: str, user_input: bool = False) -> str:
        low = (text or "").casefold()
        if any(w in low for w in ("marah", "kesal", "menyebalkan", "bodoh", "kecewa banget")):
            return "angry"
        if any(w in low for w in ("sedih", "takut", "cemas", "khawatir", "gagal", "maaf")):
            return "worried"
        if any(w in low for w in ("wow", "wah", "serius?", "kaget", "mengejutkan")):
            return "surprised"
        if any(w in low for w in ("haha", "wkwk", "lucu", "terima kasih", "makasih", "bagus", "mantap", "halo", "hai")):
            return "happy"
        if user_input and ("?" in low or any(w in low for w in ("bagaimana", "kenapa", "coba analisis", "menurutmu"))):
            return "curious"
        return "neutral" if user_input else "happy"

    def reply(self, text: str, meta: str = "", speak: bool = True, journal_prompt: str | None = None):
        self.last_answer = text
        self.anim.mood = self._emotion_from_text(text, user_input=False)
        try:
            target_prompt = journal_prompt if journal_prompt is not None else self.last_prompt
            if self.v_memauto.get() and target_prompt and role_is_journalable(text):
                self._journal(target_prompt, text)
        except Exception:
            pass
        self.chat_add("clara", text, meta)
        self.ui(self.show_bubble, text)
        if speak:
            self.speak(text)

    def regenerate(self):
        if self.last_prompt:
            self.ask_ai(self.last_prompt, force_fresh=True)

    # ------------------------------------------------------------------ perintah lokal
    def run_local(self, cmd: dict):
        k = cmd["type"]
        if k == "reply":
            self.reply(cmd["text"], meta="lokal • 0 token")
        elif k == "stop":
            self.stop_automation()
            self.reply("Oke, kuhentikan.", meta="lokal • 0 token", speak=False)
        elif k == "screenshot":
            threading.Thread(target=self.take_screenshot_local, daemon=True).start()
        elif k == "remember":
            try:
                core.append_memory_fact(MEMORY_PROFILE_FILE, cmd["text"])
                self._reload_memory_editor()
                self.reply("Tersimpan di memori: " + cmd["text"], meta="lokal • 0 token")
            except Exception as exc:
                self.reply("Gagal menyimpan memori: %s" % exc)
        elif k == "open_url":
            webbrowser.open(cmd["url"])
            core.log_action(cmd["label"], "lokal")
            self.reply(cmd["label"] + " ✔", meta="lokal • 0 token", speak=False)
        elif k == "open_app":
            threading.Thread(target=self._open_app_safe, args=(cmd["app"], cmd["label"]), daemon=True).start()

    def _open_app_safe(self, exe: str, label: str):
        try:
            if sys.platform != "win32":
                raise OSError("Hanya Windows")
            os.startfile(exe)  # type: ignore[attr-defined]
            core.log_action(label, "lokal")
            self.ui(self.reply, label + " ✔", "lokal • 0 token", False)
        except Exception:
            try:
                self._open_via_search(exe.replace(".exe", ""))
                self.ui(self.reply, label + " (lewat pencarian Windows)", "lokal • 0 token", False)
            except Exception as exc:
                self.ui(self.reply, "Gagal membuka %s: %s" % (exe, exc), "", False)

    @staticmethod
    def _open_via_search(name: str):
        pyautogui.hotkey("win", "s")
        time.sleep(0.6)
        pyperclip.copy(name)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.3)
        pyautogui.press("enter")

    # ------------------------------------------------------------------ AI chat
    def ask_ai(self, prompt: str, force_fresh: bool = False, sales: bool = False,
               system_override: str | None = None, cache_scope: str = "chat"):
        S = self.settings
        key = self.api_key()
        if not key:
            self.reply("API key belum diisi (menu Hemat & Pengaturan). Perintah lokal tetap jalan.", speak=False)
            return
        if self.busy:
            self.status("Masih memproses permintaan sebelumnya.")
            return
        if self.meter.over_budget(S["budget_usd_day"]):
            self.reply("Batas biaya harian tercapai ($%.2f). Naikkan batas di Hemat & Pengaturan bila ingin lanjut." % S["budget_usd_day"], speak=False)
            return
        S["deep_mode"] = self.v_deep.get()
        route = core.classify_request(prompt, S, is_sales=sales)
        model, use_web = route["model"], self.v_web.get()
        profile = ""
        if self.v_memuse.get():
            try:
                profile = MEMORY_PROFILE_FILE.read_text(encoding="utf-8")
            except Exception:
                pass
        memory = core.compact_memory(profile, prompt) if profile else ""
        history = core.recent_turns(tail_lines(MEMORY_JOURNAL_FILE, 4), prompt) if self.v_memuse.get() else ""
        scope_hash = hashlib.md5(((memory + history) + (system_override or "")).encode("utf-8")).hexdigest()[:12]
        ck = self.cache.key(model, prompt, cache_scope + ":" + scope_hash)
        if not use_web and not force_fresh:
            hit = self.cache.get(ck, S["cache_ttl_h"])
            if hit:
                self.meter.hit_cache()
                self.reply(hit, meta="dari cache • 0 token")
                self._refresh_usage()
                return
        self.busy = True
        self.anim.thinking = True
        self.status("Berpikir (%s)…" % model)
        def work():
            try:
                system_prompt = system_override or core.SYSTEM_PROMPT
                payload = core.build_text_payload(model, prompt, memory, history, route["max_out"], use_web,
                                                  cache_key="clara-" + cache_scope + "-" + route["tier"], system=system_prompt)
                text, usage = core.call_openai(requests, key, payload, timeout=120 if str(route["tier"]).startswith("deep") else 70)
                cost = self.meter.record(model, usage, S)
                text = text or "Model tidak mengembalikan teks."
                if not use_web:
                    self.cache.put(ck, text)
                meta = "%s • %s masuk (%s cache) • %s keluar • ≈Rp%s" % (
                    model, usage.get("input_tokens", 0), (usage.get("input_tokens_details") or {}).get("cached_tokens", 0),
                    usage.get("output_tokens", 0), format(round(cost * S["usd_idr"]), ",").replace(",", "."))
                self.ui(self.reply, text, meta, True, prompt)
            except Exception as exc:
                self.ui(self.reply, "Permintaan gagal: %s\nPeriksa koneksi, API key, saldo, dan nama model." % str(exc)[:500], "", False, prompt)
            finally:
                self.busy = False
                self.anim.thinking = False
                self.ui(self._refresh_usage)
                self.status("Siap.")
        threading.Thread(target=work, daemon=True, name="ClaraAI").start()

    def _journal(self, prompt: str, answer: str):
        try:
            rec = {"timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
                   "user": core.redact_memory_secrets(prompt[:6000]), "assistant": core.redact_memory_secrets(answer[:8000])}
            with MEMORY_JOURNAL_FILE.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except Exception:
            pass

    # ------------------------------------------------------------------ layar
    def capture_screen(self):
        """Ambil screenshot. Aman dipanggil dari thread mana pun: menyembunyikan jendela Clara lewat antrean UI."""
        wins = [w for w in (self.root, self.pet, self.bubble, self.large) if w is not None]
        done = threading.Event()

        def hide():
            self._hidden = []
            for w in wins:
                try:
                    if w.winfo_exists() and w.winfo_viewable():
                        w.withdraw()
                        self._hidden.append(w)
                except Exception:
                    pass
            done.set()
        self.ui(hide)
        done.wait(2)
        time.sleep(0.3)
        try:
            return pyautogui.screenshot()
        finally:
            def show():
                for w in getattr(self, "_hidden", []):
                    try:
                        w.deiconify()
                        if w is self.pet:
                            w.attributes("-topmost", True)
                    except Exception:
                        pass
            self.ui(show)

    def take_screenshot_local(self):
        try:
            shot = self.capture_screen()
            path = SCREENSHOT_DIR / ("desktop_%s.png" % datetime.now().strftime("%Y%m%d_%H%M%S"))
            shot.save(path)
            self.ui(self.reply, "Screenshot disimpan: %s" % path, "lokal • 0 token", False)
        except Exception as exc:
            self.ui(self.reply, "Screenshot gagal: %s" % exc, "", False)

    def analyze_screen(self):
        key = self.api_key()
        if not key:
            threading.Thread(target=self.take_screenshot_local, daemon=True).start()
            return
        if self.busy:
            return
        if self.meter.over_budget(self.settings["budget_usd_day"]):
            self.reply("Batas biaya harian tercapai.", speak=False)
            return
        if not messagebox.askyesno("Kirim screenshot?", "Screenshot layar akan dikirim ke OpenAI API untuk dianalisis. "
                                   "Tutup data pribadi/OTP/password dulu. Lanjutkan?", parent=self.root):
            return
        text = self.entry.get("1.0", "end").strip() or "Jelaskan apa yang terlihat di layar dan beri satu saran langkah berikutnya."
        self.entry.delete("1.0", "end")
        self.chat_add("user", "👁 " + text)
        need_detail = bool(re.search(r"\b(baca|teks|tulisan|angka|tabel|detail|rinci)\b", text.casefold()))
        self.busy = True
        self.anim.thinking = True
        self.status("Menganalisis layar…")

        def work():
            try:
                shot = self.capture_screen()
                url, _ = image_to_data_url(shot, 1280 if need_detail else 768, 70)
                model = self.settings["model_fast"]
                payload = core.build_text_payload(model, text + "\nAnalisis hanya yang terlihat. Jangan melakukan tindakan.", "", "", 500, False,
                                                  "clara-vision", image_url=url, detail="high" if need_detail else "low")
                ans, usage = core.call_openai(requests, key, payload, 90)
                self.meter.record(model, usage, self.settings)
                self.ui(self.reply, ans, "%s • gambar %s • %s token masuk" % (model, "detail tinggi" if need_detail else "detail rendah", usage.get("input_tokens", 0)))
            except Exception as exc:
                self.ui(self.reply, "Analisis layar gagal: %s" % str(exc)[:400], "", False)
            finally:
                self.busy = False
                self.anim.thinking = False
                self.ui(self._refresh_usage)
        threading.Thread(target=work, daemon=True, name="ClaraVision").start()

    # --- live screen (hemat: diff lokal, interval panjang, model nano, batas upload)
    def toggle_live(self):
        if self.v_live.get():
            if not self.api_key():
                messagebox.showwarning("API key", "Live layar memerlukan API key.", parent=self.root)
                self.v_live.set(False)
                return
            if not messagebox.askyesno("Aktifkan Live layar", "Clara memantau layar secara lokal dan hanya mengirim gambar yang berubah banyak "
                                       "(maks. %d kali per sesi, minimal %d detik antar kiriman). Jendela sensitif (bank, password, chat) dilewati. "
                                       "Lanjutkan?" % (self.settings["live_max_uploads"], self.settings["live_interval_s"]), parent=self.root):
                self.v_live.set(False)
                return
            self.live_on, self.live_ref, self.live_uploads = True, None, 0
            self.live_last_upload = 0.0
            self.live_end = time.time() + 30 * 60
            self.status("Live layar aktif (hemat).")
            self.root.after(600, self._live_tick)
        else:
            self.live_on = False
            self.status("Live layar mati.")

    def _live_tick(self):
        if not self.live_on:
            return
        S = self.settings
        if time.time() > self.live_end or self.live_uploads >= S["live_max_uploads"]:
            self.live_on = False
            self.v_live.set(False)
            self.chat_add("sys", "Sesi Live layar selesai (batas waktu/kiriman tercapai). Aktifkan lagi bila perlu.")
            return
        if not (self.busy or self.automation_running or self.live_busy or core.is_sensitive_window(active_window_title())):
            threading.Thread(target=self._live_probe, daemon=True, name="ClaraLiveProbe").start()
        self.root.after(9000, self._live_tick)

    def _live_probe(self):
        S = self.settings
        try:
            shot = self.capture_screen()
            g = shot.convert("L")
            g.thumbnail((64, 36))
            cur = g.tobytes()
            score = core.screen_diff_score(self.live_ref, cur) if self.live_ref else 255.0
            ready = time.time() - self.live_last_upload >= S["live_interval_s"]
            if score >= S["live_diff_threshold"] and ready and self.live_on and not self.meter.over_budget(S["budget_usd_day"]):
                self.live_ref = cur
                self.live_last_upload = time.time()
                self.live_uploads += 1
                self.live_busy = True
                url, _ = image_to_data_url(shot, 768, 60)
                self._live_send(url, active_window_title())
        except Exception as exc:
            self.status("Live layar: %s" % str(exc)[:120])

    def _live_send(self, url: str, title: str):
        model = self.settings["model_nano"]
        try:
            prompt = ("Jendela aktif: %s. Amati layar pengguna. Balas MAKS 2 kalimat Indonesia: apa yang terlihat + satu bantuan relevan bila jelas. "
                      "Jika tidak ada yang penting balas persis: -" % (title or "?"))
            payload = core.build_text_payload(model, prompt, "", "", 90, False, "clara-live", image_url=url, detail="low")
            ans, usage = core.call_openai(requests, self.api_key(), payload, 40)
            self.meter.record(model, usage, self.settings)
            if ans and ans.strip() != "-":
                self.live_obs = (time.time(), ans.strip())
                self.ui(self.chat_add, "sys", "👁 " + ans.strip())
                self.ui(self.show_bubble, ans.strip())
        except Exception as exc:
            self.status("Live layar gagal: %s" % str(exc)[:120])
        finally:
            self.live_busy = False
            self.ui(self._refresh_usage)

    # ------------------------------------------------------------------ otomasi desktop (2 tahap, hemat)
    def _autopilot_changed(self):
        if self.v_auto.get():
            if not messagebox.askyesno("Mode Otonom", "Mode Otonom menjalankan rencana langsung tanpa dialog pratinjau, selama tugasnya tidak "
                                       "menyentuh hal berisiko (hapus, bayar/transfer, kirim pesan, instal, login, password). "
                                       "Tombol 'Hentikan otomasi', perintah 'stop', dan sudut kiri-atas layar tetap bisa menghentikannya.\n\nAktifkan?", parent=self.root):
                self.v_auto.set(False)
                return
        self.save_settings()

    def plan_desktop(self, task: str):
        if not self.api_key():
            self.reply("Perintah ini butuh AI dan API key belum diisi. Perintah sederhana seperti 'buka chrome' tetap jalan tanpa key.", speak=False)
            return
        if self.busy or self.automation_running or self.planning:
            self.status("Clara sedang sibuk.")
            return
        if self.meter.over_budget(self.settings["budget_usd_day"]):
            self.reply("Batas biaya harian tercapai.", speak=False)
            return
        if any(w in active_window_title().casefold() for w in ("powershell", "command prompt", "cmd.exe", "windows terminal")):
            self.reply("Jendela terminal aktif. Untuk keamanan aku tidak mengetik ke terminal; pindah ke aplikasi GUI dulu.", speak=False)
            return
        self.planning = True
        self.anim.thinking = True
        self.status("Menyusun rencana…")
        risky = core.task_is_risky(task)
        S = self.settings
        key = self.api_key()

        def work():
            try:
                model = S["model_fast"]
                # Tahap A: tanpa gambar (murah). Gambar dikirim hanya bila perlu klik/scroll.
                p = core.build_text_payload(model, "Tugas: %s\n%s" % (task, core.PLAN_SCHEMA_HELP), "", "", 450, False, "clara-plan")
                raw, usage = core.call_openai(requests, key, p, 60)
                self.meter.record(model, usage, S)
                plan = core.parse_plan_json(raw)
                actions = plan.get("actions") or []
                scale = 1.0
                try:
                    sw, sh = pyautogui.size()
                except Exception:
                    sw, sh = 100000, 100000
                wants_xy = any(isinstance(a, dict) and a.get("type") in ("click", "double_click", "right_click", "scroll") for a in actions)
                if plan.get("need_screen") or wants_xy:
                    if not self.live_on:
                        ok = self._ask_main(lambda: messagebox.askyesno("Perlu melihat layar", "Untuk menentukan klik, Clara perlu mengirim screenshot ke OpenAI. Lanjutkan?", parent=self.root))
                        if not ok:
                            raise RuntimeError("Dibatalkan: screenshot tidak diizinkan.")
                    shot = self.capture_screen()
                    url, scale = image_to_data_url(shot, 1280, 72)
                    sw, sh = shot.width, shot.height
                    p2 = core.build_text_payload(model, "Tugas: %s\nGambar yang kamu lihat berukuran %dx%d piksel; semua koordinat harus relatif ke gambar ini.\n%s"
                                                 % (task, int(round(sw / scale)), int(round(sh / scale)), core.PLAN_SCHEMA_HELP), "", "", 500, False,
                                                 "clara-plan", image_url=url, detail="high")
                    raw, usage = core.call_openai(requests, key, p2, 90)
                    self.meter.record(model, usage, S)
                    plan = core.parse_plan_json(raw)
                    actions = plan.get("actions") or []
                if not isinstance(actions, list) or len(actions) > 12:
                    raise ValueError("Rencana tidak valid atau lebih dari 12 aksi.")
                checked = [core.validate_action(a, sw, sh, scale) for a in actions]
                if any(c is None for c in checked):
                    raise ValueError("AI mengusulkan aksi yang tidak diizinkan; tidak ada yang dijalankan.")
                self.ui(self._present_plan, checked, str(plan.get("summary", ""))[:400], task, risky)
            except Exception as exc:
                self.ui(self.reply, "Rencana tidak jadi dijalankan: %s" % str(exc)[:400], "", False)
                self.planning = False
            finally:
                self.anim.thinking = False
                self.ui(self._refresh_usage)
        threading.Thread(target=work, daemon=True, name="ClaraPlanner").start()

    def _ask_main(self, fn):
        """Jalankan dialog di thread UI dan tunggu hasilnya dari thread kerja."""
        box, ev = [], threading.Event()

        def go():
            try:
                box.append(fn())
            finally:
                ev.set()
        self.ui(go)
        ev.wait(120)
        return bool(box and box[0])

    def _present_plan(self, actions, summary, task, risky):
        if not actions:
            self.planning = False
            self.reply("Belum ada langkah yang cukup pasti. %s" % summary, speak=False)
            return
        preview = "Ringkasan: %s\n\n%s" % (summary, "\n".join("%d. %s" % (i + 1, core.format_action(a)) for i, a in enumerate(actions)))
        if self.v_auto.get() and not risky:
            self.chat_add("sys", "⚡ Mode Otonom menjalankan:\n" + preview)
        else:
            if not messagebox.askyesno("Tinjau rencana Clara", preview[:3000] + "\n\nJalankan sekarang?", parent=self.root):
                self.planning = False
                self.chat_add("sys", "Rencana dibatalkan.")
                return
            if risky and not messagebox.askyesno("Konfirmasi tambahan", "Tugas ini bisa berdampak penting (hapus/bayar/kirim/instal/login). Periksa lagi. Tetap lanjut?", parent=self.root):
                self.planning = False
                return
        self.planning = False
        self.automation_stop.clear()
        self.automation_running = True
        self._set_stop_badge(True)
        threading.Thread(target=self._execute, args=(actions, task), daemon=True, name="ClaraAutomation").start()

    def stop_automation(self):
        self.automation_stop.set()
        self.status("Menghentikan otomasi setelah langkah ini…")

    def _execute(self, actions, task_prompt: str | None = None):
        done, err = [], None
        try:
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.15
            for a in actions:
                if self.automation_stop.is_set():
                    break
                k = a["type"]
                if k == "open_app":
                    low = a["app"].casefold()
                    if low in core.APPS and sys.platform == "win32":
                        os.startfile(core.APPS[low])  # type: ignore[attr-defined]
                    else:
                        self._open_via_search(a["app"])
                elif k == "open_url":
                    webbrowser.open(a["url"])
                elif k in ("open_file", "open_folder"):
                    os.startfile(a["path"])  # type: ignore[attr-defined]
                elif k == "write_file":
                    WORKSPACE.mkdir(parents=True, exist_ok=True)
                    (WORKSPACE / a["name"]).write_text(a["text"], encoding="utf-8")
                elif k == "copy_text":
                    pyperclip.copy(a["text"])
                elif k == "focus_window":
                    if not focus_window_by_title(a["title"]):
                        raise RuntimeError("Jendela '%s' tidak ditemukan" % a["title"])
                elif k == "click":
                    pyautogui.click(a["x"], a["y"])
                elif k == "double_click":
                    pyautogui.doubleClick(a["x"], a["y"])
                elif k == "right_click":
                    pyautogui.rightClick(a["x"], a["y"])
                elif k == "type_text":
                    pyperclip.copy(a["text"])
                    pyautogui.hotkey("ctrl", "v")
                elif k == "press_key":
                    pyautogui.press(a["key"])
                elif k == "hotkey":
                    pyautogui.hotkey(*a["keys"])
                elif k == "scroll":
                    pyautogui.moveTo(a["x"], a["y"])
                    pyautogui.scroll(a["amount"])
                elif k == "wait":
                    end = time.time() + a["seconds"]
                    while time.time() < end and not self.automation_stop.is_set():
                        time.sleep(0.1)
                txt = core.format_action(a)
                done.append(txt)
                core.log_action(txt)
                self.status("Otomasi %d/%d" % (len(done), len(actions)))
        except pyautogui.FailSafeException:
            err = "Failsafe: mouse di sudut kiri-atas."
        except Exception as exc:
            err = str(exc)
        finally:
            self.automation_running = False
            report = "Dicoba %d dari %d aksi (hasil belum diverifikasi otomatis, cek layar)." % (len(done), len(actions))
            if self.automation_stop.is_set():
                report += " Dihentikan pengguna."
            if err:
                report += " Kendala: " + err[:300]
            self.ui(self.reply, report, "log: actions_log.csv", False, task_prompt)
            self.ui(self._set_stop_badge, False)

    # ------------------------------------------------------------------ suara
    def _tts_loop(self):
        try:
            try:
                import pythoncom  # type: ignore
                pythoncom.CoInitialize()
            except Exception:
                pass
            import pyttsx3
            eng = pyttsx3.init()
            eng.setProperty("rate", 175)
            eng.setProperty("volume", 0.95)
            voices = eng.getProperty("voices") or []
            names = [(v.name, v.id) for v in voices]
            pick = next((v for v in voices if any(k in (v.name or "").lower() for k in ("indonesia", "gadis", "zira", "aria", "jenny", "female", "hazel", "susan"))), None)
            if pick:
                eng.setProperty("voice", pick.id)
            self.ui(self._set_voices, names, pick.name if pick else (names[0][0] if names else ""))
        except Exception:
            self.tts_ok = False
            return
        while True:
            cmd, arg = self.tts_q.get()
            try:
                if cmd == "voice":
                    eng.setProperty("voice", arg)
                elif cmd == "say":
                    self.tts_speaking = True
                    self.anim.speaking = True
                    self.ignore_audio_until = time.time() + 0.8
                    eng.say(arg)
                    eng.runAndWait()
                elif cmd == "quit":
                    break
            except Exception:
                pass
            finally:
                self.tts_speaking = False
                self.anim.speaking = False
                self.ignore_audio_until = time.time() + 1.0

    def _set_voices(self, names, current):
        self.tts_voices = names
        try:
            self.voice_combo.configure(values=[n for n, _ in names])
        except Exception:
            pass
        self.v_voice.set(current)

    def change_voice(self, _e=None):
        vid = next((i for n, i in self.tts_voices if n == self.v_voice.get()), None)
        if vid:
            self.tts_q.put(("voice", vid))

    def speak(self, text: str):
        if not (self.v_speak.get() and self.tts_ok and text):
            return
        t = re.sub(r"[*_`#>]+", "", text)
        if self.settings.get("speak_short"):
            sent = re.split(r"(?<=[.!?])\s+", t.strip())
            t = " ".join(sent[:2])[:300]
        else:
            t = t[:1500]
        while not self.tts_q.empty():
            try:
                self.tts_q.get_nowait()
            except queue.Empty:
                break
        self.tts_q.put(("say", t))

    def toggle_mic(self):
        if self.v_mic.get():
            if not messagebox.askyesno("Mikrofon berkelanjutan", "Mikrofon aktif terus sampai dimatikan. Ucapan dikirim ke layanan Google Speech untuk "
                                       "ditranskripsi, lalu teksnya bisa dikirim ke OpenAI. Hindari menyebut password/OTP. Aktifkan?", parent=self.root):
                self.v_mic.set(False)
                return
            self.continuous = True
            self.anim.listening = True
            self.status("Menyiapkan mikrofon…")

            def setup():
                try:
                    import speech_recognition as sr
                    rec = sr.Recognizer()
                    rec.pause_threshold = 0.7
                    with sr.Microphone() as src:
                        rec.adjust_for_ambient_noise(src, duration=0.45)

                    def cb(r, audio):
                        if not self.continuous or self.tts_speaking or time.time() < self.ignore_audio_until:
                            return
                        try:
                            t = r.recognize_google(audio, language="id-ID").strip()
                        except Exception:
                            return
                        now = time.time()
                        if not t or (t.casefold() == self.last_voice[0].casefold() and now - self.last_voice[1] < 5) or self.tts_speaking:
                            return
                        self.last_voice = (t, now)
                        self.ui(self._on_voice, t)
                    self.stop_listening = rec.listen_in_background(sr.Microphone(), cb, phrase_time_limit=8)
                    self.status("Mikrofon aktif. Bicara kapan saja.")
                    self.ui(self.show_bubble, "Aku mendengarkan 🎧")
                except Exception as exc:
                    self.continuous = False
                    self.anim.listening = False
                    self.ui(self.v_mic.set, False)
                    self.ui(messagebox.showerror, "Mikrofon", "Gagal: %s\nPeriksa izin mikrofon Windows dan PyAudio." % str(exc)[:400])
            threading.Thread(target=setup, daemon=True).start()
        else:
            self.continuous = False
            self.anim.listening = False
            if callable(self.stop_listening):
                try:
                    self.stop_listening(wait_for_stop=False)
                except Exception:
                    pass
            self.stop_listening = None
            self.status("Mikrofon dimatikan.")

    def _on_voice(self, text: str):
        # Diskusi boleh berlangsung saat otomasi sedang mengeksekusi langkah.
        # Perintah desktop kedua tetap ditolak oleh plan_desktop sampai tugas pertama selesai.
        if self.continuous and not (self.busy or self.planning):
            self.submit(text, from_voice=True)

    def listen_once(self):
        if self.continuous:
            self.status("Mikrofon sudah aktif terus.")
            return
        self.anim.listening = True
        self.status("Mendengarkan satu ucapan…")

        def work():
            try:
                import speech_recognition as sr
                rec = sr.Recognizer()
                with sr.Microphone() as src:
                    rec.adjust_for_ambient_noise(src, duration=0.4)
                    audio = rec.listen(src, timeout=7, phrase_time_limit=15)
                t = rec.recognize_google(audio, language="id-ID")
                self.ui(self.submit, t, True)
            except Exception as exc:
                self.ui(self.status, "Suara belum tertangkap: %s" % str(exc)[:120])
            finally:
                self.anim.listening = self.continuous
        threading.Thread(target=work, daemon=True).start()

    # ------------------------------------------------------------------ avatar mengambang
    def _build_pet(self):
        self.pet = tk.Toplevel(self.root)
        self.pet.overrideredirect(True)
        self.pet.geometry("+40+160")
        self.pet.attributes("-topmost", True)
        self.pet.configure(bg=KEY_HEX)
        try:
            self.pet.wm_attributes("-transparentcolor", KEY_HEX)
        except tk.TclError:
            pass
        self.pet_img = tk.Label(self.pet, bg=KEY_HEX, bd=0, cursor="hand2")
        self.pet_img.pack()
        self.stop_badge = tk.Label(self.pet, text="■ STOP", bg=WARN, fg="#1a0505", font=("Segoe UI", 8, "bold"), padx=8, cursor="hand2")
        self.stop_badge.bind("<Button-1>", lambda e: self.stop_automation())
        for w in (self.pet, self.pet_img):
            w.bind("<ButtonPress-1>", self._pet_press)
            w.bind("<B1-Motion>", self._pet_move)
            w.bind("<ButtonRelease-1>", self._pet_release)
            w.bind("<Button-3>", self._pet_menu)
            w.bind("<Double-Button-1>", lambda e: self.toggle_large())
        m = tk.Menu(self.pet, tearoff=0, bg=CARD, fg=TXT, activebackground=ACC2, bd=0)
        m.add_command(label="Buka Clara", command=self.show_dashboard)
        m.add_command(label="Mode avatar besar", command=self.toggle_large)
        m.add_command(label="Dengarkan terus ON/OFF", command=self._menu_mic)
        m.add_command(label="Live layar ON/OFF", command=self._menu_live)
        m.add_command(label="■ Hentikan otomasi", command=self.stop_automation)
        m.add_separator()
        m.add_command(label="Keluar", command=self.quit_app)
        self.pet_menu_obj = m

    def _menu_mic(self):
        self.v_mic.set(not self.v_mic.get())
        self.toggle_mic()

    def _menu_live(self):
        self.v_live.set(not self.v_live.get())
        self.toggle_live()

    def _set_stop_badge(self, on: bool):
        if on:
            self.stop_badge.pack(pady=(0, 2))
        else:
            self.stop_badge.pack_forget()

    def _pet_press(self, e):
        self.pet_drag = (e.x_root, e.y_root, self.pet.winfo_x(), self.pet.winfo_y(), False)

    def _pet_move(self, e):
        sx, sy, ox, oy, _ = self.pet_drag
        dx, dy = e.x_root - sx, e.y_root - sy
        if abs(dx) > 4 or abs(dy) > 4:
            self.pet.geometry("+%d+%d" % (ox + dx, oy + dy))
            self.pet_drag = (sx, sy, ox, oy, True)

    def _pet_release(self, e):
        if not self.pet_drag[4]:
            self.root.after(250, self._maybe_open)

    def _maybe_open(self):
        # Klik tunggal membuka panel; dobel-klik (mode besar) membatalkannya.
        if self.large is None and not self.pet_drag[4]:
            self.show_dashboard()

    def _pet_menu(self, e):
        try:
            self.pet_menu_obj.tk_popup(e.x_root, e.y_root)
        finally:
            self.pet_menu_obj.grab_release()

    def _photo(self, data: bytes):
        k = hashlib.md5(data).digest()
        ph = self.photos.get(k)
        if ph is None:
            if len(self.photos) > 60:
                self.photos.clear()
            ph = tk.PhotoImage(data=base64.b64encode(data))
            self.photos[k] = ph
        return ph

    def _animate(self):
        try:
            self.anim.step()
            d = self.renderer.request(self.anim.key(150))
            if d is not None:
                ph = self._photo(d)
                if getattr(self.pet_img, "image", None) is not ph:
                    self.pet_img.configure(image=ph)
                    self.pet_img.image = ph
            if self.large is not None and self.large.winfo_exists() and self.anim._tick % 2 == 0:
                d2 = self.renderer.request(self.anim.key(300, True))
                if d2 is not None:
                    ph2 = self._photo(d2)
                    if getattr(self.large_img, "image", None) is not ph2:
                        self.large_img.configure(image=ph2)
                        self.large_img.image = ph2
        except Exception:
            pass
        self.root.after(110, self._animate)

    def show_bubble(self, text: str):
        snippet = (text or "").strip()
        if not snippet:
            return
        if len(snippet) > 200:
            snippet = snippet[:197].rsplit(" ", 1)[0] + "…"
        try:
            if self.bubble is not None and self.bubble.winfo_exists():
                self.bubble.destroy()
            b = tk.Toplevel(self.pet)
            self.bubble = b
            b.overrideredirect(True)
            b.attributes("-topmost", True)
            f = tk.Frame(b, bg=CARD2, highlightbackground=ACC, highlightthickness=2, padx=12, pady=9)
            f.pack()
            tk.Label(f, text="Clara", bg=CARD2, fg=ACC, font=("Segoe UI", 8, "bold")).pack(anchor="w")
            tk.Label(f, text=snippet, bg=CARD2, fg=TXT, justify="left", wraplength=270, font=FONT).pack(anchor="w")
            x = min(self.pet.winfo_x() + 150, max(0, self.root.winfo_screenwidth() - 310))
            b.geometry("+%d+%d" % (x, max(0, self.pet.winfo_y() + 10)))
            b.after(9000, lambda: b.destroy() if b.winfo_exists() else None)
        except Exception:
            pass
        if self.large is not None:
            try:
                self.large_bubble.configure(text=snippet)
            except Exception:
                pass

    # --- mode besar
    def toggle_large(self):
        if self.large is not None:
            try:
                if self.large.winfo_exists():
                    self.large.destroy()
            except Exception:
                pass
            self.large = None
            return
        w = tk.Toplevel(self.root)
        self.large = w
        w.title("Clara • Mode besar")
        w.configure(bg=BG)
        w.geometry("400x700")
        w.attributes("-topmost", True)
        self.large_img = tk.Label(w, bg=KEY_HEX, bd=0)
        self.large_img.pack(pady=(14, 0))
        self.large_bubble = tk.Label(w, text="Hai Hedy! Ngobrol lewat suara atau chat 💙", bg=CARD2, fg=TXT, wraplength=340, justify="left",
                                     padx=14, pady=10, font=FONT)
        self.large_bubble.pack(fill="x", padx=22, pady=10)
        row = tk.Frame(w, bg=BG)
        row.pack(fill="x", padx=22)
        ent = tk.Entry(row, bg=CARD, fg=TXT, insertbackground=ACC, relief="flat", font=("Segoe UI", 11), highlightthickness=1,
                       highlightbackground=LINE, highlightcolor=ACC)
        ent.pack(side="left", fill="x", expand=True, ipady=8)

        def send(_e=None):
            t = ent.get().strip()
            if t:
                ent.delete(0, "end")
                self.submit(t)
        ent.bind("<Return>", send)
        self._btn(row, "Kirim", send).pack(side="left", padx=(6, 0))
        r2 = tk.Frame(w, bg=BG)
        r2.pack(fill="x", padx=22, pady=10)
        self._btn(r2, "🎙 Bicara", self.listen_once, primary=False).pack(side="left", expand=True, fill="x", padx=(0, 4))
        self._btn(r2, "💬 Panel", self.show_dashboard, primary=False).pack(side="left", expand=True, fill="x", padx=4)
        self._btn(r2, "Mode kecil", self.toggle_large, primary=False).pack(side="left", expand=True, fill="x", padx=(4, 0))
        w.protocol("WM_DELETE_WINDOW", self.toggle_large)

    # ------------------------------------------------------------------ halaman jualan
    def _build_sales(self):
        p = self.pages["jual"]
        self._title(p, "Bantu Jualan", "Konteks toko dikirim hanya pada tugas jualan (bukan setiap chat) supaya hemat. Perbarui angka sebelum dipakai.")
        self.ctx_box = self._textbox(p, 9)
        self.ctx_box.pack(fill="both", expand=True, padx=24, pady=(0, 10))
        try:
            self.ctx_box.insert("1.0", CONTEXT_FILE.read_text(encoding="utf-8") if CONTEXT_FILE.exists() else DEFAULT_SALES_CONTEXT)
        except Exception:
            self.ctx_box.insert("1.0", DEFAULT_SALES_CONTEXT)
        grid = tk.Frame(p, bg=BG)
        grid.pack(fill="x", padx=24)
        tasks = [
            ("Audit penjualan", "Audit penjualan: diagnosis dari konteks, data yang kurang, lalu rencana uji 7 hari. Jangan mengarang angka."),
            ("Judul & deskripsi Shopee", "Buat 5 judul Shopee jelas (tidak clickbait) dan 1 deskripsi siap tempel tanpa klaim tak terbukti."),
            ("Ide video 15 detik", "5 konsep video 15 detik: hook 0-3 dtk, demonstrasi, teks layar, CTA. Hemat biaya, realistis."),
            ("Audit iklan", "Kerangka diagnosis iklan Shopee: bedakan masalah tayangan, CTR, konversi, margin. Minta data yang perlu."),
            ("Kalender konten 7 hari", "Kalender konten 7 hari: edukasi, demonstrasi, bukti sosial sah, FAQ, penawaran; hook + CTA."),
            ("Balasan chat pembeli", "Template balasan chat pembeli: sopan, ringkas, bantu pilih varian, tanpa janji berlebihan."),
        ]
        for i, (lab, t) in enumerate(tasks):
            self._btn(grid, lab, lambda t=t: self.run_sales(t), primary=(i < 3)).grid(row=i // 3, column=i % 3, sticky="ew", padx=3, pady=3)
        for c in range(3):
            grid.columnconfigure(c, weight=1)
        self._btn(p, "Simpan konteks", self.save_context, primary=False).pack(anchor="w", padx=24, pady=10)

    def save_context(self):
        try:
            CONTEXT_FILE.write_text(self.ctx_box.get("1.0", "end").strip(), encoding="utf-8")
            self.status("Konteks tersimpan.")
        except Exception as exc:
            messagebox.showerror("Clara", str(exc), parent=self.root)

    def run_sales(self, task: str):
        self.save_context()
        ctx = self.ctx_box.get("1.0", "end").strip()[:1800]
        self.show_page("chat")
        self.submit(task + "\n\nKonteks toko:\n" + ctx, sales=True)

    # ------------------------------------------------------------------ keuangan: pembukuan, aset, anggaran, AI Coach
    @staticmethod
    def _idr(value) -> str:
        try: return "Rp" + format(round(float(value)), ",").replace(",", ".")
        except Exception: return "Rp0"

    def _build_finance(self):
        p = self.pages["keuangan"]
        self._title(p, "Keuangan cerdas", "Pencatatan lokal di SQLite • klasifikasi dapat dikoreksi • skor adalah indikator sederhana, bukan diagnosis mutlak. Data transaksi tidak dikirim ke AI kecuali kamu meminta analisis.")
        summary = tk.Frame(p, bg=BG)
        summary.pack(fill="x", padx=20, pady=(4, 10))
        self.fin_metric_vars = [tk.StringVar(value="—") for _ in range(4)]
        self.fin_metric_labels = []
        for i, (title, var) in enumerate(zip(("Pendapatan bulan ini", "Pengeluaran bulan ini", "Arus kas bersih", "Skor kesehatan"), self.fin_metric_vars)):
            card = tk.Frame(summary, bg=CARD, padx=12, pady=9, highlightthickness=1, highlightbackground=LINE)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 5, 0 if i == 3 else 5))
            tk.Label(card, text=title, bg=CARD, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w")
            lab=tk.Label(card, textvariable=var, bg=CARD, fg=ACC if i != 2 else OK, font=("Segoe UI Semibold", 12))
            lab.pack(anchor="w", pady=(2,0)); self.fin_metric_labels.append(lab)
            summary.columnconfigure(i, weight=1, uniform="financecards")
        style=ttk.Style(self.root)
        style.configure("Clara.TNotebook", background=BG, borderwidth=0)
        style.configure("Clara.TNotebook.Tab", background=CARD2, foreground=TXT, padding=(12,7))
        style.map("Clara.TNotebook.Tab", background=[("selected", ACC2)], foreground=[("selected", "#ffffff")])
        nb=ttk.Notebook(p, style="Clara.TNotebook")
        nb.pack(fill="both", expand=True, padx=20, pady=(0,10))
        self.fin_nb=nb
        self.fin_tab_transactions=tk.Frame(nb,bg=BG); self.fin_tab_assets=tk.Frame(nb,bg=BG); self.fin_tab_budgets=tk.Frame(nb,bg=BG); self.fin_tab_advisor=tk.Frame(nb,bg=BG)
        nb.add(self.fin_tab_transactions,text="Transaksi")
        nb.add(self.fin_tab_assets,text="Aset & Langganan")
        nb.add(self.fin_tab_budgets,text="Anggaran & Tujuan")
        nb.add(self.fin_tab_advisor,text="AI Coach / Konsultan")
        self._build_finance_transactions(); self._build_finance_assets(); self._build_finance_budgets(); self._build_finance_advisor()
        self._refresh_finance_view()

    def _build_finance_transactions(self):
        tab=self.fin_tab_transactions
        card=tk.Frame(tab,bg=CARD,padx=10,pady=8); card.pack(fill="x",padx=8,pady=7)
        self.fin_direction=tk.StringVar(value="Income")
        self.fin_type=tk.StringVar(value="Active Income")
        self.fin_subtype=tk.StringVar(value="Lainnya")
        self.fin_detail=tk.StringVar(value="Lainnya")
        self.fin_date=tk.StringVar(value=datetime.now().date().isoformat())
        self.fin_amount=tk.StringVar(value="")
        self.fin_current_value=tk.StringVar(value="")
        self.fin_note=tk.StringVar(value="")
        self.fin_status=tk.StringVar(value="Completed")
        self.fin_recurring=tk.BooleanVar(value=False)
        self.fin_frequency=tk.StringVar(value="Bulanan")
        self.fin_asset_sold=tk.BooleanVar(value=False)
        fields=[("Jenis",0,self.fin_direction), ("Kategori utama",1,self.fin_type), ("Subkategori",2,self.fin_subtype), ("Detail",3,self.fin_detail)]
        tk.Label(card,text="Jenis",bg=CARD,fg=MUTED,font=("Segoe UI",8)).grid(row=0,column=0,sticky="w",padx=4)
        self.fin_direction_combo=ttk.Combobox(card,textvariable=self.fin_direction,values=["Income","Spending"],state="readonly",width=15)
        self.fin_direction_combo.grid(row=1,column=0,sticky="ew",padx=4,pady=(1,5)); self.fin_direction_combo.bind("<<ComboboxSelected>>",lambda _e:self._finance_taxonomy_changed())
        tk.Label(card,text="Kategori utama",bg=CARD,fg=MUTED,font=("Segoe UI",8)).grid(row=0,column=1,sticky="w",padx=4)
        self.fin_type_combo=ttk.Combobox(card,textvariable=self.fin_type,state="readonly",width=23)
        self.fin_type_combo.grid(row=1,column=1,sticky="ew",padx=4,pady=(1,5)); self.fin_type_combo.bind("<<ComboboxSelected>>",lambda _e:self._finance_taxonomy_changed())
        tk.Label(card,text="Subkategori",bg=CARD,fg=MUTED,font=("Segoe UI",8)).grid(row=0,column=2,sticky="w",padx=4)
        self.fin_sub_combo=ttk.Combobox(card,textvariable=self.fin_subtype,state="readonly",width=26)
        self.fin_sub_combo.grid(row=1,column=2,sticky="ew",padx=4,pady=(1,5)); self.fin_sub_combo.bind("<<ComboboxSelected>>",lambda _e:self._finance_detail_changed())
        tk.Label(card,text="Detail",bg=CARD,fg=MUTED,font=("Segoe UI",8)).grid(row=0,column=3,sticky="w",padx=4)
        self.fin_detail_combo=ttk.Combobox(card,textvariable=self.fin_detail,state="readonly",width=23)
        self.fin_detail_combo.grid(row=1,column=3,sticky="ew",padx=4,pady=(1,5))
        for c in range(4): card.columnconfigure(c,weight=1)
        labs=[("Tanggal (YYYY-MM-DD)",0), ("Jumlah (Rp)",1), ("Nilai pasar aset (opsional)",2), ("Status",3)]
        for label,c in labs: tk.Label(card,text=label,bg=CARD,fg=MUTED,font=("Segoe UI",8)).grid(row=2,column=c,sticky="w",padx=4)
        tk.Entry(card,textvariable=self.fin_date,bg=CARD2,fg=TXT,insertbackground=ACC,relief="flat",width=16).grid(row=3,column=0,sticky="ew",padx=4,pady=(1,5),ipady=4)
        tk.Entry(card,textvariable=self.fin_amount,bg=CARD2,fg=TXT,insertbackground=ACC,relief="flat",width=16).grid(row=3,column=1,sticky="ew",padx=4,pady=(1,5),ipady=4)
        tk.Entry(card,textvariable=self.fin_current_value,bg=CARD2,fg=TXT,insertbackground=ACC,relief="flat",width=18).grid(row=3,column=2,sticky="ew",padx=4,pady=(1,5),ipady=4)
        ttk.Combobox(card,textvariable=self.fin_status,values=["Completed","Planned","Cancelled"],state="readonly",width=16).grid(row=3,column=3,sticky="ew",padx=4,pady=(1,5))
        tk.Label(card,text="Catatan / nama aset",bg=CARD,fg=MUTED,font=("Segoe UI",8)).grid(row=4,column=0,sticky="w",padx=4)
        tk.Entry(card,textvariable=self.fin_note,bg=CARD2,fg=TXT,insertbackground=ACC,relief="flat").grid(row=5,column=0,columnspan=2,sticky="ew",padx=4,pady=(1,5),ipady=4)
        tk.Checkbutton(card,text="Berulang",variable=self.fin_recurring,bg=CARD,fg=TXT,selectcolor=CARD2,activebackground=CARD,activeforeground=TXT).grid(row=5,column=2,sticky="w",padx=4)
        ttk.Combobox(card,textvariable=self.fin_frequency,values=["Mingguan","Bulanan","Tahunan"],state="readonly",width=13).grid(row=5,column=3,sticky="ew",padx=4,pady=(1,5))
        tk.Checkbutton(card,text="Capital gain sudah terealisasi (aset benar-benar dijual)",variable=self.fin_asset_sold,bg=CARD,fg=MUTED,selectcolor=CARD2,activebackground=CARD).grid(row=6,column=0,columnspan=2,sticky="w",padx=4)
        row=tk.Frame(card,bg=CARD); row.grid(row=6,column=2,columnspan=2,sticky="e")
        self._btn(row,"Klasifikasi otomatis",self._finance_autoclassify,primary=False).pack(side="left",padx=3)
        self._btn(row,"Simpan transaksi",self._finance_save_transaction).pack(side="left",padx=3)
        self._finance_taxonomy_changed()
        toolbar=tk.Frame(tab,bg=BG); toolbar.pack(fill="x",padx=8)
        tk.Label(toolbar,text="Riwayat transaksi selesai & rencana",bg=BG,fg=ACC,font=FONT_B).pack(side="left")
        self._btn(toolbar,"Ekspor CSV",self._finance_export_csv,primary=False).pack(side="right",padx=2)
        self._btn(toolbar,"Muat ulang",self._refresh_finance_view,primary=False).pack(side="right",padx=2)
        cols=("date","direction","category","subcategory","detail","amount","note","status")
        fin_table_wrap=tk.Frame(tab,bg=BG); fin_table_wrap.pack(fill="both",expand=True,padx=8,pady=(4,8))
        self.fin_tree=ttk.Treeview(fin_table_wrap,columns=cols,show="headings",height=7)
        heads={"date":"Tanggal","direction":"Jenis","category":"Kategori","subcategory":"Subkategori","detail":"Detail","amount":"Jumlah","note":"Catatan","status":"Status"}
        widths={"date":82,"direction":68,"category":125,"subcategory":150,"detail":115,"amount":105,"note":190,"status":80}
        for c in cols: self.fin_tree.heading(c,text=heads[c]); self.fin_tree.column(c,width=widths[c],anchor="w" if c in ("date","direction","category","subcategory","detail","note","status") else "e",stretch=True)
        fin_xbar=ttk.Scrollbar(fin_table_wrap,orient="horizontal",command=self.fin_tree.xview); self.fin_tree.configure(xscrollcommand=fin_xbar.set)
        self.fin_tree.pack(side="top",fill="both",expand=True); fin_xbar.pack(side="bottom",fill="x")

    def _finance_taxonomy_changed(self):
        direction=self.fin_direction.get()
        if direction=="Income":
            vals=list(finance.INCOME_TYPES.keys())
        else: vals=list(finance.SPENDING_TYPES.keys())
        if self.fin_type.get() not in vals: self.fin_type.set(vals[0])
        self.fin_type_combo.configure(values=vals)
        if direction=="Income": subvals=finance.INCOME_TYPES.get(self.fin_type.get(),["Lainnya"])
        else: subvals=list(finance.SPENDING_TYPES.get(self.fin_type.get(),{"Lainnya":["Lainnya"]}).keys())
        self.fin_sub_combo.configure(values=subvals)
        if self.fin_subtype.get() not in subvals: self.fin_subtype.set(subvals[0] if subvals else "Lainnya")
        self._finance_detail_changed()

    def _finance_detail_changed(self):
        if self.fin_direction.get()=="Income": vals=["—"]
        else: vals=finance.SPENDING_TYPES.get(self.fin_type.get(),{}).get(self.fin_subtype.get(),["Lainnya"])
        self.fin_detail_combo.configure(values=vals)
        if self.fin_detail.get() not in vals: self.fin_detail.set(vals[0] if vals else "Lainnya")

    def _finance_autoclassify(self):
        direction=self.fin_direction.get(); inferred=finance.classify_description(self.fin_note.get(),direction)
        if direction=="Income":
            self.fin_type.set(inferred.get("income_type","Active Income")); self.fin_subtype.set(inferred.get("subcategory","Lainnya"))
        else:
            self.fin_type.set(inferred.get("spending_type","Consumptive Spending")); self.fin_subtype.set(inferred.get("subcategory","Passive Spending"))
        self._finance_taxonomy_changed()
        if inferred.get("detail"):
            vals=list(self.fin_detail_combo.cget("values"))
            if inferred["detail"] in vals: self.fin_detail.set(inferred["detail"])
        self.status("Saran klasifikasi diterapkan; cek kategori sebelum menyimpan.")

    def _finance_save_transaction(self):
        try:
            direction=self.fin_direction.get(); broad=self.fin_type.get(); mid=self.fin_subtype.get(); detail=self.fin_detail.get()
            engine=""
            if broad=="Productive Spending":
                engine={"Investasi Active Income Engine":"Active Income Engine","Investasi Passive Income Engine":"Passive Income Engine","Investasi Portfolio Income Engine":"Portfolio Income Engine"}.get(mid,"")
            amount=float(self.fin_amount.get().replace(".","").replace(",","."))
            data={"direction":direction,"date":self.fin_date.get().strip(),"amount":amount,"note":self.fin_note.get().strip(),"status":self.fin_status.get(),
                  "recurring":self.fin_recurring.get(),"recurring_frequency":self.fin_frequency.get(),"category":broad,"subcategory":mid,"detail":detail,"engine":engine,
                  "asset_sold":self.fin_asset_sold.get(),"asset_name":self.fin_note.get().strip()}
            if direction=="Income": data["income_type"]=broad
            else: data["spending_type"]=broad
            if direction=="Spending" and mid=="Invisible Spending":
                if not data["asset_name"]: raise ValueError("Masukkan nama aset pada catatan untuk pengeluaran Invisible Spending.")
                raw=self.fin_current_value.get().strip()
                if not raw: raise ValueError("Masukkan estimasi nilai pasar saat ini untuk aset yang menyusut.")
                current=float(raw.replace(".","").replace(",","."))
                if current<0: raise ValueError("Nilai pasar tidak boleh negatif.")
            finance.add_transaction(data)
            if direction=="Spending" and mid=="Invisible Spending":
                finance.add_asset({"name":data["asset_name"],"type":"Kendaraan / gadget / barang konsumtif","purchase_date":data["date"],"purchase_price":amount,"current_value":current,"useful_life_years":5,"note":"Dibuat dari transaksi ID pengeluaran; perbarui umur ekonomis sesuai aset."})
            self.fin_amount.set(""); self.fin_note.set(""); self.fin_current_value.set(""); self.fin_asset_sold.set(False)
            self._refresh_finance_view(); self.status("Transaksi tersimpan lokal. Periksa klasifikasi dan bukti transaksi bila diperlukan.")
        except Exception as exc:
            messagebox.showwarning("Transaksi belum tersimpan",str(exc),parent=self.root)

    def _finance_export_csv(self):
        path=filedialog.asksaveasfilename(parent=self.root,title="Ekspor transaksi",defaultextension=".csv",initialfile="Clara_Keuangan.csv",filetypes=[("CSV","*.csv")])
        if not path: return
        try:
            Path(path).write_text(finance.export_csv(),encoding="utf-8-sig"); self.status("CSV keuangan diekspor.")
        except Exception as exc: messagebox.showerror("Ekspor CSV",str(exc),parent=self.root)

    def _build_finance_assets(self):
        tab=self.fin_tab_assets
        split=tk.Frame(tab,bg=BG); split.pack(fill="both",expand=True,padx=8,pady=8)
        left=tk.Frame(split,bg=CARD,padx=10,pady=8); left.pack(side="left",fill="both",expand=True,padx=(0,4))
        right=tk.Frame(split,bg=CARD,padx=10,pady=8); right.pack(side="left",fill="both",expand=True,padx=(4,0))
        tk.Label(left,text="Daftarkan aset",bg=CARD,fg=ACC,font=FONT_B).pack(anchor="w")
        self.fa_name=tk.StringVar(); self.fa_type=tk.StringVar(value="Barang rental"); self.fa_purchase=tk.StringVar(value=datetime.now().date().isoformat()); self.fa_price=tk.StringVar(); self.fa_value=tk.StringVar(); self.fa_life=tk.StringVar(value="5")
        for lab,var in (("Nama aset",self.fa_name),("Tanggal beli YYYY-MM-DD",self.fa_purchase),("Harga beli (Rp)",self.fa_price),("Nilai pasar kini (Rp)",self.fa_value),("Umur ekonomis (tahun)",self.fa_life)):
            tk.Label(left,text=lab,bg=CARD,fg=MUTED,font=("Segoe UI",8)).pack(anchor="w",pady=(4,1))
            tk.Entry(left,textvariable=var,bg=CARD2,fg=TXT,insertbackground=ACC,relief="flat").pack(fill="x",ipady=4)
        ttk.Combobox(left,textvariable=self.fa_type,values=["Properti","Kendaraan","Saham","Emas","Barang rental","Gadget & elektronik","Perabot","Lainnya"],state="readonly").pack(fill="x",pady=(6,4))
        self._btn(left,"Simpan aset",self._finance_add_asset).pack(anchor="e",pady=(2,8))
        self.asset_tree=ttk.Treeview(left,columns=("name","price","value","loss"),show="headings",height=6)
        for c,t in (("name","Aset"),("price","Harga beli"),("value","Nilai kini"),("loss","Selisih")): self.asset_tree.heading(c,text=t); self.asset_tree.column(c,width=100,stretch=True)
        self.asset_tree.pack(fill="both",expand=True)
        tk.Label(right,text="Langganan & biaya berulang",bg=CARD,fg=ACC,font=FONT_B).pack(anchor="w")
        self.fs_name=tk.StringVar(); self.fs_provider=tk.StringVar(); self.fs_cost=tk.StringVar(); self.fs_due=tk.StringVar(); self.fs_last=tk.StringVar(); self.fs_active=tk.BooleanVar(value=True)
        for lab,var in (("Nama langganan",self.fs_name),("Penyedia",self.fs_provider),("Biaya per bulan (Rp)",self.fs_cost),("Tanggal perpanjangan (opsional)",self.fs_due),("Terakhir dipakai (opsional, YYYY-MM-DD)",self.fs_last)):
            tk.Label(right,text=lab,bg=CARD,fg=MUTED,font=("Segoe UI",8)).pack(anchor="w",pady=(4,1))
            tk.Entry(right,textvariable=var,bg=CARD2,fg=TXT,insertbackground=ACC,relief="flat").pack(fill="x",ipady=4)
        tk.Checkbutton(right,text="Langganan aktif",variable=self.fs_active,bg=CARD,fg=TXT,selectcolor=CARD2,activebackground=CARD).pack(anchor="w",pady=3)
        self._btn(right,"Simpan langganan",self._finance_add_subscription).pack(anchor="e",pady=(2,8))
        self.sub_tree=ttk.Treeview(right,columns=("name","monthly","annual","renewal"),show="headings",height=6)
        for c,t in (("name","Langganan"),("monthly","/bulan"),("annual","/tahun"),("renewal","Pengingat")): self.sub_tree.heading(c,text=t); self.sub_tree.column(c,width=100,stretch=True)
        self.sub_tree.pack(fill="both",expand=True)
        tk.Label(tab,text="Catatan: nilai pasar dan penyusutan adalah estimasi; untuk aset keuangan, harga bisa naik maupun turun. Pengingat langganan tampil saat data dimuat.",bg=BG,fg=MUTED,font=("Segoe UI",8),wraplength=750,justify="left").pack(anchor="w",padx=10,pady=(0,6))

    def _finance_add_asset(self):
        try:
            finance.add_asset({"name":self.fa_name.get(),"type":self.fa_type.get(),"purchase_date":self.fa_purchase.get(),"purchase_price":float(self.fa_price.get().replace(".","").replace(",",".")),"current_value":float(self.fa_value.get().replace(".","").replace(",",".")),"useful_life_years":float(self.fa_life.get())})
            self.fa_name.set(""); self.fa_price.set(""); self.fa_value.set(""); self._refresh_finance_view(); self.status("Aset disimpan.")
        except Exception as exc: messagebox.showwarning("Aset",str(exc),parent=self.root)

    def _finance_add_subscription(self):
        try:
            finance.add_subscription({"name":self.fs_name.get(),"provider":self.fs_provider.get(),"monthly_cost":float(self.fs_cost.get().replace(".","").replace(",",".")),"renewal_date":self.fs_due.get().strip() or None,"last_used_date":self.fs_last.get().strip() or None,"active":self.fs_active.get()})
            self.fs_name.set(""); self.fs_provider.set(""); self.fs_cost.set(""); self.fs_due.set(""); self.fs_last.set(""); self._refresh_finance_view(); self.status("Langganan disimpan.")
        except Exception as exc: messagebox.showwarning("Langganan",str(exc),parent=self.root)

    def _build_finance_budgets(self):
        tab=self.fin_tab_budgets
        card=tk.Frame(tab,bg=CARD,padx=12,pady=10); card.pack(fill="x",padx=8,pady=8)
        tk.Label(card,text="Anggaran bulanan per kategori",bg=CARD,fg=ACC,font=FONT_B).grid(row=0,column=0,columnspan=3,sticky="w")
        self.fb_category=tk.StringVar(value="Consumptive Spending"); self.fb_limit=tk.StringVar(); self.fb_alert=tk.StringVar(value="80")
        choices=list(finance.INCOME_TYPES.keys())+list(finance.SPENDING_TYPES.keys())
        ttk.Combobox(card,textvariable=self.fb_category,values=choices,state="readonly",width=32).grid(row=1,column=0,sticky="ew",padx=4,pady=6)
        tk.Entry(card,textvariable=self.fb_limit,bg=CARD2,fg=TXT,insertbackground=ACC,relief="flat",width=22).grid(row=1,column=1,sticky="ew",padx=4,pady=6,ipady=4)
        tk.Entry(card,textvariable=self.fb_alert,bg=CARD2,fg=TXT,insertbackground=ACC,relief="flat",width=8).grid(row=1,column=2,sticky="ew",padx=4,pady=6,ipady=4)
        tk.Label(card,text="Kategori",bg=CARD,fg=MUTED).grid(row=2,column=0,sticky="w",padx=4); tk.Label(card,text="Batas Rp",bg=CARD,fg=MUTED).grid(row=2,column=1,sticky="w",padx=4); tk.Label(card,text="Alert %",bg=CARD,fg=MUTED).grid(row=2,column=2,sticky="w",padx=4)
        self._btn(card,"Simpan anggaran",self._finance_add_budget).grid(row=1,column=3,padx=8)
        tk.Label(card,text="Target keuangan",bg=CARD,fg=ACC,font=FONT_B).grid(row=3,column=0,columnspan=3,sticky="w",pady=(14,2))
        self.fg_name=tk.StringVar(); self.fg_target=tk.StringVar(); self.fg_current=tk.StringVar(value="0"); self.fg_date=tk.StringVar(); self.fg_type=tk.StringVar(value="Dana darurat")
        tk.Entry(card,textvariable=self.fg_name,bg=CARD2,fg=TXT,insertbackground=ACC,relief="flat",width=22).grid(row=4,column=0,sticky="ew",padx=4,pady=5,ipady=4)
        tk.Entry(card,textvariable=self.fg_target,bg=CARD2,fg=TXT,insertbackground=ACC,relief="flat",width=15).grid(row=4,column=1,sticky="ew",padx=4,pady=5,ipady=4)
        tk.Entry(card,textvariable=self.fg_current,bg=CARD2,fg=TXT,insertbackground=ACC,relief="flat",width=12).grid(row=4,column=2,sticky="ew",padx=4,pady=5,ipady=4)
        ttk.Combobox(card,textvariable=self.fg_type,values=["Dana darurat","Beli aset","Bebas utang","Target passive income","Pendidikan","Lainnya"],state="readonly",width=22).grid(row=5,column=0,sticky="ew",padx=4,pady=4)
        tk.Entry(card,textvariable=self.fg_date,bg=CARD2,fg=TXT,insertbackground=ACC,relief="flat",width=15).grid(row=5,column=1,sticky="ew",padx=4,pady=4,ipady=4)
        tk.Label(card,text="Nama | Target Rp | Sudah terkumpul Rp | Jenis | Tenggat opsional",bg=CARD,fg=MUTED,font=("Segoe UI",8)).grid(row=6,column=0,columnspan=3,sticky="w",padx=4)
        self._btn(card,"Simpan tujuan",self._finance_add_goal).grid(row=4,column=3,padx=8)
        for c in range(4): card.columnconfigure(c,weight=1)
        self.budget_text=self._textbox(tab,10); self.budget_text.pack(fill="both",expand=True,padx=8,pady=(0,8))

    def _finance_add_budget(self):
        try:
            finance.upsert_budget(self.fb_category.get(),float(self.fb_limit.get().replace(".","").replace(",",".")),alert_percent=float(self.fb_alert.get()))
            self.fb_limit.set(""); self._refresh_finance_view(); self.status("Anggaran tersimpan.")
        except Exception as exc: messagebox.showwarning("Anggaran",str(exc),parent=self.root)

    def _finance_add_goal(self):
        try:
            finance.add_goal(self.fg_name.get(),float(self.fg_target.get().replace(".","").replace(",",".")),float(self.fg_current.get() or "0"),self.fg_date.get().strip() or None,self.fg_type.get())
            self.fg_name.set(""); self.fg_target.set(""); self._refresh_finance_view(); self.status("Tujuan tersimpan.")
        except Exception as exc: messagebox.showwarning("Tujuan",str(exc),parent=self.root)

    def _build_finance_advisor(self):
        tab=self.fin_tab_advisor
        tk.Label(tab,text="Pilih gaya analisis",bg=BG,fg=ACC,font=FONT_B).pack(anchor="w",padx=10,pady=(8,2))
        self.finance_mode=tk.StringVar(value="Keuangan pribadi")
        ttk.Combobox(tab,textvariable=self.finance_mode,values=["Keuangan pribadi","Bisnis & cash flow","Investasi perusahaan","Turnaround perusahaan","SDM & organisasi","Pajak legal Indonesia","Hukum & tata kelola"],state="readonly",width=32).pack(anchor="w",padx=10)
        tk.Label(tab,text="Tanya Clara. Untuk aturan terbaru, aktifkan Web di halaman Chat; sistem akan diminta memprioritaskan sumber resmi dan menyebutkan ketidakpastian.",bg=BG,fg=MUTED,wraplength=730,justify="left",font=("Segoe UI",8)).pack(anchor="w",padx=10,pady=5)
        self.finance_question=self._textbox(tab,7); self.finance_question.pack(fill="both",expand=True,padx=10,pady=5)
        bar=tk.Frame(tab,bg=BG); bar.pack(fill="x",padx=10,pady=(0,8))
        self._btn(bar,"Analisis dengan AI",self._finance_ask_ai).pack(side="left")
        self._btn(bar,"Buka Chat",lambda:self.show_page("chat"),primary=False).pack(side="left",padx=6)
        tk.Label(bar,text="AI bukan pengganti akuntan, konsultan pajak, pengacara atau penasihat investasi berizin.",bg=BG,fg=MUTED,font=("Segoe UI",8)).pack(side="right")

    def _finance_ask_ai(self):
        question=self.finance_question.get("1.0","end").strip()
        if not question: messagebox.showinfo("AI Coach","Tulis pertanyaan dulu.",parent=self.root); return
        d=finance.dashboard()
        context=(f"Snapshot {d['period']}: pendapatan {self._idr(d['income'])}; pengeluaran {self._idr(d['spending'])}; arus kas {self._idr(d['net_cashflow'])}; "
                 f"pendapatan aktif {self._idr(d['active_income'])}; pasif {self._idr(d['passive_income'])}; portfolio terealisasi {self._idr(d['portfolio_income'])}; "
                 f"rasio produktif {d['productive_ratio']:.1f}%; rasio kebebasan finansial {d['freedom_ratio']:.1f}%; skor kesehatan heuristik {d['health_score']:.1f}/100. "
                 "Data hanya berdasarkan transaksi Completed yang dimasukkan pengguna dan bisa tidak lengkap.")
        mode=self.finance_mode.get()
        pref=f"Mode konsultan terpilih: {mode}. Analisis dalam Bahasa Indonesia."
        prompt=pref+"\n\nKONTEKS DATA LOKAL (hanya data agregat):\n"+context+"\n\nPERTANYAAN:\n"+question
        if mode!="Keuangan pribadi": prompt=finance.company_advisor_prompt(question,context)
        self.last_prompt=prompt; self.chat_add("user",question,meta="AI Coach • "+mode)
        self.show_page("chat")
        self.ask_ai(prompt,force_fresh=True,system_override=finance.FINANCE_ADVISOR_SYSTEM,cache_scope="finance-"+re.sub(r"[^a-z0-9]+","-",mode.casefold()))

    def _refresh_finance_view(self):
        try:
            d=finance.dashboard()
            for var,val in zip(self.fin_metric_vars,(self._idr(d['income']),self._idr(d['spending']),self._idr(d['net_cashflow']),f"{d['health_score']:.0f}/100")):
                var.set(val)
            self.fin_metric_labels[2].configure(fg=OK if d['net_cashflow']>=0 else WARN)
            for x in self.fin_tree.get_children(): self.fin_tree.delete(x)
            with finance.connect() as db:
                rows=db.execute("SELECT date,direction,category,subcategory,detail,amount,note,status FROM transactions ORDER BY date DESC,id DESC LIMIT 150").fetchall()
                for r in rows: self.fin_tree.insert("","end",values=(r['date'],r['direction'],r['category'],r['subcategory'],r['detail'],self._idr(r['amount']),r['note'],r['status']))
            for x in self.asset_tree.get_children(): self.asset_tree.delete(x)
            for a in finance.list_assets(): self.asset_tree.insert("","end",values=(a['name'],self._idr(a['purchase_price']),self._idr(a['current_value']),self._idr(a['market_loss'])))
            for x in self.sub_tree.get_children(): self.sub_tree.delete(x)
            for sub in finance.list_subscriptions():
                reminder=(f"{sub['days_to_renewal']} hari lagi" if sub['days_to_renewal'] is not None else "—")
                if sub['possibly_unused']: reminder+=" • jarang dipakai?"
                self.sub_tree.insert("","end",values=(sub['name'],self._idr(sub['monthly_cost']),self._idr(sub['annual_cost']),reminder))
            lines=[f"Ringkasan {d['period']}","="*32,
                   f"Pendapatan: {self._idr(d['income'])} | Pengeluaran: {self._idr(d['spending'])} | Arus kas: {self._idr(d['net_cashflow'])}",
                   f"Produktif: {d['productive_ratio']:.1f}% | Konsumtif: {d['consumptive_ratio']:.1f}% | Pendapatan pasif / total income: {d['passive_income_ratio']:.1f}%",
                   f"Rasio kebebasan finansial: {d['freedom_ratio']:.1f}% | Subscription burden: {d['subscription_burden']:.1f}%",
                   f"Aset tercatat: {self._idr(d['asset_value'])} | Utang tercatat: {self._idr(d['liability_value'])} | Kekayaan bersih sederhana: {self._idr(d['net_worth'])}","","Peringatan / coach lokal:"]
            lines.extend("• "+x for x in finance.recommendations())
            lines.extend(["","Anggaran bulanan:"])
            budgets=finance.budget_report()
            if budgets:
                for b in budgets: lines.append(f"• {b['category']}: {self._idr(b['spent'])} / {self._idr(b['limit'])} ({b['percent']:.1f}%)"+("  ⚠ OVER / mendekati batas" if b['alert'] else ""))
            else: lines.append("• Belum ada anggaran. Buat anggaran pada panel ini.")
            if hasattr(self,"budget_text"):
                self.budget_text.delete("1.0","end"); self.budget_text.insert("1.0","\n".join(lines))
        except Exception as exc:
            self.status("Keuangan belum dapat dimuat: "+str(exc)[:150])

    # ------------------------------------------------------------------ pasar saham IHSG, watchlist dan berita
    def _build_market(self):
        p=self.pages["saham"]
        self._title(p,"Pasar Saham Indonesia • IHSG / BEI","Data diambil saat refresh dari Yahoo Finance dan Google News RSS; provider dapat menunda atau membatasi permintaan. Sinyal teknikal + sentimen bersifat heuristik, bukan ramalan pasti.")
        head=tk.Frame(p,bg=CARD,padx=12,pady=9); head.pack(fill="x",padx=20,pady=(3,8))
        self.market_index_var=tk.StringVar(value="IHSG: belum dimuat")
        self.market_update_var=tk.StringVar(value="Belum diperbarui")
        tk.Label(head,textvariable=self.market_index_var,bg=CARD,fg=ACC,font=("Segoe UI Semibold",13)).pack(anchor="w")
        tk.Label(head,textvariable=self.market_update_var,bg=CARD,fg=MUTED,font=("Segoe UI",8)).pack(anchor="w",pady=(2,4))
        bar=tk.Frame(p,bg=BG); bar.pack(fill="x",padx=20,pady=(0,6))
        self.market_symbol_var=tk.StringVar(value="BBCA.JK")
        tk.Entry(bar,textvariable=self.market_symbol_var,bg=CARD,fg=TXT,insertbackground=ACC,relief="flat",width=15).pack(side="left",ipady=6,padx=(0,5))
        self._btn(bar,"Tambah kode",self.add_market_symbol,primary=False).pack(side="left",padx=3)
        self.market_refresh_btn=self._btn(bar,"Perbarui harga & berita",self.refresh_market); self.market_refresh_btn.pack(side="left",padx=3)
        self._btn(bar,"Hapus pilihan",self.remove_market_symbol,primary=False).pack(side="left",padx=3)
        tk.Checkbutton(bar,text="Auto-update tiap 15 menit",variable=self.v_market_auto,bg=BG,fg=TXT,selectcolor=CARD2,activebackground=BG,command=self._market_auto_changed).pack(side="right")
        split=tk.Frame(p,bg=BG); split.pack(fill="both",expand=True,padx=20,pady=(0,10))
        left=tk.Frame(split,bg=BG); left.pack(side="left",fill="both",expand=True,padx=(0,5))
        right=tk.Frame(split,bg=BG); right.pack(side="left",fill="both",expand=True,padx=(5,0))
        tk.Label(left,text="Watchlist & sinyal",bg=BG,fg=ACC,font=FONT_B).pack(anchor="w")
        cols=("symbol","price","day","r5","r20","daily","monthly","signal")
        market_table_wrap=tk.Frame(left,bg=BG); market_table_wrap.pack(fill="both",expand=True,pady=(4,0))
        self.market_tree=ttk.Treeview(market_table_wrap,columns=cols,show="headings",height=13)
        labels={"symbol":"Kode","price":"Harga","day":"Hari %","r5":"5h %","r20":"20h %","daily":"Harian","monthly":"Bulanan","signal":"Analisis"}
        widths={"symbol":70,"price":82,"day":62,"r5":56,"r20":60,"daily":78,"monthly":78,"signal":170}
        for c in cols: self.market_tree.heading(c,text=labels[c]); self.market_tree.column(c,width=widths[c],anchor="e" if c in ("price","day","r5","r20") else "w",stretch=True)
        market_xbar=ttk.Scrollbar(market_table_wrap,orient="horizontal",command=self.market_tree.xview); self.market_tree.configure(xscrollcommand=market_xbar.set)
        self.market_tree.pack(side="top",fill="both",expand=True); market_xbar.pack(side="bottom",fill="x"); self.market_tree.bind("<Double-1>",self._market_open_selected)
        tk.Label(right,text="Berita & alasan",bg=BG,fg=ACC,font=FONT_B).pack(anchor="w")
        self.market_news_list=tk.Listbox(right,bg=CARD,fg=TXT,selectbackground=ACC2,relief="flat",bd=0,font=("Segoe UI",9),height=10,activestyle="none")
        self.market_news_list.pack(fill="both",expand=True,pady=(4,0)); self.market_news_list.bind("<Double-1>",self._market_open_news)
        self.market_news_text=self._textbox(right,7); self.market_news_text.pack(fill="both",expand=True,pady=(6,0))
        tk.Label(p,text="Catatan: rekomendasi bukan ajakan transaksi. Pertimbangkan fundamental, likuiditas, biaya, risiko, profil, dan diversifikasi; periksa pengumuman resmi BEI/OJK/emiten sebelum bertindak.",bg=BG,fg=MUTED,font=("Segoe UI",8),wraplength=800,justify="left").pack(fill="x",padx=20,pady=(0,7))

    def _market_auto_changed(self):
        self.save_settings()
        self.status("Auto-update pasar "+("aktif (15 menit saat Clara berjalan)" if self.v_market_auto.get() else "mati"))
        if self.v_market_auto.get() and time.time()-self.market_last_refresh>=900:
            self.refresh_market()

    def add_market_symbol(self):
        try:
            s=market._clean_symbol(self.market_symbol_var.get())
            if s==market.INDEX_SYMBOL: raise ValueError("IHSG ditampilkan terpisah, bukan sebagai saham.")
            if s not in self.market_watchlist:
                if len(self.market_watchlist)>=100: raise ValueError("Watchlist maksimal 100 kode.")
                self.market_watchlist.append(s); core.save_json(APP_DIR/"market_watchlist.json",{"symbols":self.market_watchlist})
            self.market_symbol_var.set(s); self.status("Kode ditambahkan; klik Perbarui harga & berita.")
        except Exception as exc: messagebox.showwarning("Kode saham",str(exc),parent=self.root)

    def remove_market_symbol(self):
        sel=self.market_tree.selection()
        if not sel: return
        sym=str(self.market_tree.item(sel[0],"values")[0])
        self.market_watchlist=[x for x in self.market_watchlist if x.replace(".JK","")!=sym]
        core.save_json(APP_DIR/"market_watchlist.json",{"symbols":self.market_watchlist})
        for item in self.market_tree.get_children():
            if str(self.market_tree.item(item,"values")[0])==sym: self.market_tree.delete(item)
        self.status("Kode dihapus dari watchlist lokal.")

    def refresh_market(self):
        if self.market_refreshing: self.status("Pembaruan pasar sedang berjalan."); return
        self.market_refreshing=True; self.market_refresh_btn.configure(state="disabled")
        self.market_update_var.set("Mengambil kuotasi & berita terbaru…")
        self.status("Mengambil data pasar. Ini memerlukan koneksi internet.")
        symbols=list(self.market_watchlist)
        queries=["IHSG OR saham BEI Indonesia", "BBCA OR BBRI OR BMRI OR TLKM saham", "ANTM OR MDKA OR GOTO OR ASII saham"]
        def worker():
            quotes=[]; errors=[]; index_data=None; all_news=[]
            tasks={}
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
                    tasks[pool.submit(market.fetch_quote,market.INDEX_SYMBOL)]=("index",market.INDEX_SYMBOL)
                    for sym in symbols: tasks[pool.submit(market.fetch_quote,sym)]=("quote",sym)
                    for query in queries: tasks[pool.submit(market.fetch_news,query,max_items=12)]=("news",query)
                    for fut in concurrent.futures.as_completed(tasks,timeout=75):
                        kind,label=tasks[fut]
                        try:
                            val=fut.result()
                            if kind=="index": index_data=val
                            elif kind=="quote": quotes.append(val)
                            else: all_news.extend(val)
                        except Exception as exc: errors.append(f"{label}: {str(exc)[:150]}")
            except Exception as exc: errors.append("Pembaruan: "+str(exc)[:150])
            dedup=[]; seen=set()
            for n in sorted(all_news,key=lambda x:x.get("published",""),reverse=True):
                k=n.get("url") or n.get("title")
                if k and k not in seen: seen.add(k); dedup.append(n)
            self.ui(self._market_render,index_data,quotes,dedup,errors)
        threading.Thread(target=worker,daemon=True,name="ClaraMarketUpdate").start()

    def _market_render(self,index_data,quotes,headlines,errors):
        self.market_refreshing=False
        try:self.market_refresh_btn.configure(state="normal")
        except Exception:pass
        self.market_index=index_data; self.market_quotes=quotes; self.market_headlines=headlines; self.market_errors=errors; self.market_last_refresh=time.time()
        if index_data:
            sign="+" if index_data['change_pct']>=0 else ""
            self.market_index_var.set(f"IHSG {index_data['price']:,.2f}  {sign}{index_data['change_pct']:.2f}%  | {index_data['timestamp']}")
        else: self.market_index_var.set("IHSG: data tidak tersedia (lihat kendala koneksi/provider)")
        self.market_update_var.set(f"Diperbarui {datetime.now().strftime('%d-%m-%Y %H:%M:%S')} • sumber kuotasi Yahoo Finance (mungkin tertunda) • {len(quotes)}/{len(self.market_watchlist)} kode")
        for x in self.market_tree.get_children(): self.market_tree.delete(x)
        signals=market.analysis_summary(quotes,headlines)
        bysym={s['symbol']:s for s in signals}
        for q in sorted(quotes,key=lambda x:self.market_watchlist.index(x['symbol']) if x['symbol'] in self.market_watchlist else 999):
            sig=bysym.get(q['symbol'],{}); day=q['change_pct']; fmt=lambda v:f"{v:+.2f}%"
            self.market_tree.insert("","end",values=(q['symbol'].replace('.JK',''),f"{q['price']:,.0f}",fmt(day),fmt(q['return_5d']),fmt(q['return_20d']),sig.get('daily_bias','—'),sig.get('monthly_bias','—'),sig.get('stance','—')))
        self.market_news_list.delete(0,"end")
        for n in headlines[:60]:
            tag={1:"[POSITIF]",-1:"[NEGATIF]",0:"[NETRAL]"}.get(n['sentiment'],"[NETRAL]")
            self.market_news_list.insert("end",f"{tag} {n['published']} | {n['publisher']} | {n['title']}")
        note=["Ringkasan analisis heuristik", "="*30,
              "Sinyal menggabungkan return 5/20 hari dan kata kunci pada berita yang judulnya cocok dengan kode/nama perusahaan.",
              "Berita berbahasa alami dapat disalahklasifikasikan; sinyal bukan valuasi fundamental dan bukan model prediksi teruji.",""]
        for sig in signals:
            note.append(f"{sig['symbol']}: {sig['stance']} | confidence {sig['confidence']}")
            note.append("  Harian: "+sig['daily_bias']+" • Bulanan: "+sig['monthly_bias'])
            note.append("  "+sig['reasoning'])
        if errors: note.extend(["","Kendala sumber (data untuk kode/berita ini mungkin tidak lengkap):"]+["• "+e for e in errors[:18]])
        if not quotes: note.extend(["","Belum ada kuotasi. Periksa koneksi, coba lagi, atau buka link sumber di browser."])
        self.market_news_text.delete("1.0","end"); self.market_news_text.insert("1.0","\n".join(note))
        self.status("Pembaruan pasar selesai; cek kelengkapan data dan tanggal sumber.")

    def _market_auto_tick(self):
        try:
            if self.v_market_auto.get() and not self.market_refreshing and time.time()-self.market_last_refresh>=900:
                self.refresh_market()
        finally:
            try:self.root.after(60000,self._market_auto_tick)
            except Exception:pass

    def _market_open_selected(self,_event=None):
        sel=self.market_tree.selection()
        if sel:
            sym=str(self.market_tree.item(sel[0],"values")[0]).upper()
            webbrowser.open("https://finance.yahoo.com/quote/"+sym+".JK/")

    def _market_open_news(self,_event=None):
        sel=self.market_news_list.curselection()
        if not sel or sel[0]>=len(self.market_headlines): return
        url=self.market_headlines[sel[0]].get("url")
        if url: webbrowser.open(url)

    # ------------------------------------------------------------------ halaman aktivitas
    def _build_activity(self):
        p = self.pages["akt"]
        self._title(p, "Aktivitas laptop", "Hanya mencatat waktu + judul jendela aktif setelah kamu menyalakannya. Tanpa keylogger, tanpa screenshot otomatis, tanpa upload.")
        tk.Label(p, textvariable=self.v_mon, bg=BG, fg=ACC, font=FONT_B, anchor="w").pack(fill="x", padx=24)
        tk.Label(p, textvariable=self.v_active, bg=BG, fg=MUTED, font=FONT, anchor="w", wraplength=700, justify="left").pack(fill="x", padx=24, pady=(2, 8))
        bar = tk.Frame(p, bg=BG)
        bar.pack(fill="x", padx=24)
        self.mon_btn = self._btn(bar, "Mulai pemantauan", self.toggle_monitor)
        self.mon_btn.pack(side="left")
        self._btn(bar, "Cek jendela aktif", lambda: self.v_active.set("Jendela aktif: " + (active_window_title() or "-")), primary=False).pack(side="left", padx=6)
        self._btn(bar, "Hapus log", self.clear_activity, primary=False).pack(side="left")
        self._btn(bar, "Muat ulang proses", self.refresh_processes, primary=False).pack(side="right")
        wrap = tk.Frame(p, bg=BG)
        wrap.pack(fill="both", expand=True, padx=24, pady=12)
        self.proc = tk.Listbox(wrap, bg=CARD, fg=TXT, selectbackground=ACC2, relief="flat", font=("Consolas", 10), activestyle="none", bd=0, highlightthickness=1, highlightbackground=LINE)
        sb = ttk.Scrollbar(wrap, orient="vertical", command=self.proc.yview)
        self.proc.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.proc.pack(side="left", fill="both", expand=True)
        self.refresh_processes()

    def refresh_processes(self):
        self.proc.delete(0, "end")
        names = set()
        try:
            for pr in psutil.process_iter(attrs=["name"]):
                if pr.info.get("name"):
                    names.add(pr.info["name"])
        except Exception:
            pass
        for n in sorted(names, key=str.lower)[:300]:
            self.proc.insert("end", n)
        self.status("%d proses terdeteksi." % len(names))

    def toggle_monitor(self):
        if not self.monitoring:
            if not messagebox.askyesno("Pemantauan", "Clara akan mencatat judul jendela aktif ke file lokal. Aktifkan?", parent=self.root):
                return
            self.monitoring = True
            self.v_mon.set("Pemantauan: AKTIF (log lokal)")
            self.mon_btn.configure(text="Hentikan pemantauan")
        else:
            self.monitoring = False
            self.v_mon.set("Pemantauan: MATI")
            self.mon_btn.configure(text="Mulai pemantauan")

    def _monitor_tick(self):
        if self.monitoring:
            t = active_window_title()
            if t and t != self.last_title:
                self.last_title = t
                try:
                    import csv
                    new = not ACTIVITY_CSV.exists()
                    with ACTIVITY_CSV.open("a", newline="", encoding="utf-8-sig") as f:
                        w = csv.writer(f)
                        if new:
                            w.writerow(["waktu", "judul_jendela"])
                        w.writerow([datetime.now().isoformat(timespec="seconds"), t])
                except Exception:
                    pass
                self.v_active.set("Jendela aktif: " + t)
        self.root.after(3000, self._monitor_tick)

    def clear_activity(self):
        if messagebox.askyesno("Hapus log", "Hapus log aktivitas lokal?", parent=self.root):
            try:
                ACTIVITY_CSV.unlink(missing_ok=True)
            except Exception:
                pass

    # ------------------------------------------------------------------ halaman aksi cepat
    def _build_actions(self):
        p = self.pages["aksi"]
        self._title(p, "Aksi cepat", "Semua tombol ini jalan lokal: 0 token.")

        def group(title, items, cols=3):
            tk.Label(p, text=title, bg=BG, fg=ACC, font=FONT_B, anchor="w").pack(fill="x", padx=24, pady=(10, 4))
            g = tk.Frame(p, bg=BG)
            g.pack(fill="x", padx=24)
            for i, (lab, cmd) in enumerate(items):
                self._btn(g, lab, cmd, primary=False).grid(row=i // cols, column=i % cols, sticky="ew", padx=3, pady=3)
            for c in range(cols):
                g.columnconfigure(c, weight=1)

        def U(u):
            return lambda: webbrowser.open(u)

        def A(a):
            return lambda: threading.Thread(target=self._open_app_safe, args=(a, "Buka " + a), daemon=True).start()
        group("Situs jualan", [("Shopee Seller", U(core.SITES["shopee seller"])), ("WhatsApp Web", U(core.SITES["whatsapp"])),
                               ("Canva", U(core.SITES["canva"])), ("TikTok", U(core.SITES["tiktok"])),
                               ("Tokopedia", U(core.SITES["tokopedia"])), ("Google Drive", U(core.SITES["google drive"]))])
        group("Aplikasi Windows", [("Notepad", A("notepad.exe")), ("Kalkulator", A("calc.exe")), ("File Explorer", A("explorer.exe")),
                                   ("Excel", A("excel.exe")), ("Word", A("winword.exe")), ("Task Manager", A("taskmgr.exe"))])
        group("File & folder", [("Folder data Clara", lambda: self.open_folder(APP_DIR)), ("Folder screenshot", lambda: self.open_folder(SCREENSHOT_DIR)),
                                ("Folder ClaraWorkspace", lambda: self.open_folder(WORKSPACE)),
                                ("Screenshot sekarang", lambda: threading.Thread(target=self.take_screenshot_local, daemon=True).start())])

    def open_folder(self, path: Path):
        try:
            path.mkdir(parents=True, exist_ok=True)
            if sys.platform == "win32":
                os.startfile(str(path))  # type: ignore[attr-defined]
            else:
                subprocess.Popen(["xdg-open", str(path)])
        except Exception as exc:
            messagebox.showerror("Folder", str(exc), parent=self.root)

    # ------------------------------------------------------------------ halaman memori
    def _build_memory(self):
        p = self.pages["mem"]
        self._title(p, "Memori portabel", "Profil di bawah dikirim ke AI secara terpilih (bagian relevan saja). Ekspor ZIP untuk membawa ingatan Clara ke AI lain atau komputer lain.")
        opts = tk.Frame(p, bg=BG)
        opts.pack(fill="x", padx=24, pady=(0, 6))
        Pill(opts, "Pakai profil di prompt", self.v_memuse).pack(side="left", padx=(0, 6))
        Pill(opts, "Simpan percakapan otomatis", self.v_memauto, self.save_settings).pack(side="left")
        self.mem_box = self._textbox(p, 14)
        self.mem_box.pack(fill="both", expand=True, padx=24, pady=6)
        self._reload_memory_editor()
        bar = tk.Frame(p, bg=BG)
        bar.pack(fill="x", padx=24, pady=(4, 12))
        self._btn(bar, "Simpan profil", self.save_profile).pack(side="left", padx=(0, 6))
        self._btn(bar, "Impor", self.import_profile, primary=False).pack(side="left", padx=6)
        self._btn(bar, "Ekspor ZIP", self.export_memory, primary=False).pack(side="left", padx=6)
        self._btn(bar, "Hapus jurnal", self.clear_journal, primary=False).pack(side="right")
        tk.Label(p, text="Jurnal tidak boleh berisi password/OTP/API key; pola umum disamarkan, tetapi tidak sempurna.", bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w", padx=24, pady=(0, 10))

    def _reload_memory_editor(self):
        def w():
            self.mem_box.delete("1.0", "end")
            try:
                self.mem_box.insert("1.0", MEMORY_PROFILE_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        self.ui(w)

    def save_profile(self):
        try:
            MEMORY_PROFILE_FILE.write_text(self.mem_box.get("1.0", "end").strip() + "\n", encoding="utf-8")
            self.status("Profil memori tersimpan.")
        except Exception as exc:
            messagebox.showerror("Memori", str(exc), parent=self.root)

    def import_profile(self):
        path = filedialog.askopenfilename(parent=self.root, filetypes=[("Markdown/Teks", "*.md *.txt"), ("Semua", "*.*")])
        if path:
            try:
                self.mem_box.delete("1.0", "end")
                self.mem_box.insert("1.0", Path(path).read_text(encoding="utf-8"))
                self.status("Dimuat ke editor. Klik Simpan profil.")
            except Exception as exc:
                messagebox.showerror("Impor", str(exc), parent=self.root)

    def export_memory(self):
        try:
            self.save_profile()
            path = filedialog.asksaveasfilename(parent=self.root, defaultextension=".zip", initialfile="Clara_Memory_Export.zip")
            if not path:
                return
            import zipfile
            files = [(MEMORY_PROFILE_FILE, "memory_profile.md"), (MEMORY_JOURNAL_FILE, "memory_journal.jsonl"), (CONTEXT_FILE, "sales_context.txt")]
            for n in ("MEMORY_TRANSFER_PROMPT_ID.md", "MEMORY_SCHEMA.json", "PORTABLE_MEMORY_README_ID.md", "TOKEN_OPTIMIZATION_PLAYBOOK_ID.md"):
                files.append((resource_path(n), n))
            with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
                for src, arc in files:
                    if Path(src).exists():
                        z.write(src, arc)
            messagebox.showinfo("Ekspor", "Tersimpan: %s\nJurnal bisa berisi data pribadi; simpan dengan aman." % path, parent=self.root)
        except Exception as exc:
            messagebox.showerror("Ekspor", str(exc), parent=self.root)

    def clear_journal(self):
        if messagebox.askyesno("Hapus jurnal", "Hapus semua jurnal percakapan? Profil tetap ada.", parent=self.root):
            MEMORY_JOURNAL_FILE.write_text("", encoding="utf-8")

    # ------------------------------------------------------------------ halaman hemat & pengaturan
    def _build_saver(self):
        p = self.pages["hemat"]
        self._title(p, "Hemat & Pengaturan", "Atur kunci, model, dan batas biaya. Angka rupiah adalah perkiraan; tagihan resmi ada di dashboard OpenAI.")
        wrap = tk.Frame(p, bg=BG)
        wrap.pack(fill="both", expand=True, padx=24)
        card = tk.Frame(wrap, bg=CARD, padx=16, pady=12)
        card.pack(fill="x")
        tk.Label(card, text="API key OpenAI", bg=CARD, fg=ACC, font=FONT_B).grid(row=0, column=0, sticky="w")
        ke = tk.Entry(card, textvariable=self.v_key, show="•", bg=CARD2, fg=TXT, insertbackground=ACC, relief="flat", font=FONT, highlightthickness=1, highlightbackground=LINE)
        ke.grid(row=1, column=0, sticky="ew", ipady=6, pady=(2, 6))
        Pill(card, "Ingat key (terenkripsi Windows)", self.v_remember, self.save_key).grid(row=2, column=0, sticky="w")
        tk.Label(card, text="Suara", bg=CARD, fg=ACC, font=FONT_B).grid(row=3, column=0, sticky="w", pady=(10, 0))
        self.voice_combo = ttk.Combobox(card, textvariable=self.v_voice, values=[], state="readonly", width=42)
        self.voice_combo.grid(row=4, column=0, sticky="w", pady=(2, 0))
        self.voice_combo.bind("<<ComboboxSelected>>", self.change_voice)
        card.columnconfigure(0, weight=1)

        grid = tk.Frame(wrap, bg=CARD, padx=16, pady=12)
        grid.pack(fill="x", pady=10)
        fields = [("model_fast", "Model obrolan (murah)"), ("model_smart", "Model tugas berat"), ("model_nano", "Model live layar"),
                  ("budget_usd_day", "Batas biaya/hari (USD)"), ("usd_idr", "Kurs USD→Rp"), ("live_interval_s", "Live: jeda kirim (detik)"),
                  ("live_max_uploads", "Live: maks kiriman/sesi"), ("cache_ttl_h", "Umur cache (jam)")]
        for i, (k, lab) in enumerate(fields):
            tk.Label(grid, text=lab, bg=CARD, fg=MUTED, font=("Segoe UI", 9)).grid(row=i // 2 * 2, column=i % 2, sticky="w", padx=(0, 14))
            v = tk.StringVar(value=str(self.settings[k]))
            self.setting_vars[k] = v
            tk.Entry(grid, textvariable=v, bg=CARD2, fg=TXT, insertbackground=ACC, relief="flat", font=FONT, width=24, highlightthickness=1,
                     highlightbackground=LINE).grid(row=i // 2 * 2 + 1, column=i % 2, sticky="w", ipady=4, pady=(0, 6), padx=(0, 14))
        bar = tk.Frame(wrap, bg=BG)
        bar.pack(fill="x")
        self._btn(bar, "Simpan pengaturan", self.apply_settings).pack(side="left")
        self._btn(bar, "Kosongkan cache jawaban", self._clear_cache, primary=False).pack(side="left", padx=8)
        self.usage_text = tk.Label(wrap, text="", bg=BG, fg=TXT, font=FONT, justify="left", anchor="w")
        self.usage_text.pack(fill="x", pady=12)
        tips = ("Cara Clara menghemat: perintah lokal 0 token • cache jawaban identik • model murah untuk obrolan, model pintar hanya untuk tugas berat/Mikir keras "
                "• memori dipotong sesuai relevansi • batas panjang jawaban • gambar detail rendah • Live layar pakai diff lokal + model nano • batas biaya harian.")
        tk.Label(wrap, text=tips, bg=BG, fg=MUTED, font=("Segoe UI", 9), wraplength=700, justify="left").pack(fill="x")

    def _clear_cache(self):
        self.cache.clear()
        self.status("Cache dikosongkan.")

    def save_key(self):
        try:
            if self.v_remember.get() and self.api_key():
                enc = core.dpapi_encrypt(self.api_key())
                if enc:
                    KEY_FILE.write_text(enc, encoding="utf-8")
                else:
                    self.v_remember.set(False)
                    messagebox.showinfo("Key", "Enkripsi Windows tidak tersedia; key tidak disimpan.", parent=self.root)
            else:
                KEY_FILE.unlink(missing_ok=True)
        except Exception:
            pass
        self.save_settings()

    def apply_settings(self):
        S = self.settings
        for k, v in self.setting_vars.items():
            raw = v.get().strip()
            default = core.DEFAULT_SETTINGS[k]
            try:
                if isinstance(default, bool):
                    continue
                S[k] = type(default)(float(raw)) if isinstance(default, (int, float)) else raw
            except ValueError:
                pass
        self.save_key()
        self.status("Pengaturan tersimpan.")
        self._refresh_usage()

    def _refresh_usage(self):
        try:
            S = self.settings
            cost = self.meter.cost_today()
            budget = max(S["budget_usd_day"], 0.0001)
            idr = lambda usd: format(round(usd * S["usd_idr"]), ",").replace(",", ".")
            self.v_usage.set("Hari ini ≈ Rp%s\nbatas Rp%s" % (idr(cost), idr(budget)))
            self.usage_bar.delete("all")
            frac = min(1.0, cost / budget)
            w = max(1, self.usage_bar.winfo_width())
            self.usage_bar.create_rectangle(0, 0, w * frac, 6, fill=WARN if frac > 0.85 else ACC, width=0)
            self.usage_text.configure(text=self.meter.summary(S))
        except Exception:
            pass

    # ------------------------------------------------------------------ util
    def copy_answer(self):
        if self.last_answer:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.last_answer)
            self.status("Jawaban disalin.")

    def show_dashboard(self):
        self.root.deiconify()
        self.root.state("normal")
        self.root.lift()
        self.root.focus_force()

    def hide_dashboard(self):
        self.root.withdraw()

    def quit_app(self):
        self.live_on = False
        self.continuous = False
        self.automation_stop.set()
        try:
            if callable(self.stop_listening):
                self.stop_listening(wait_for_stop=False)
        except Exception:
            pass
        self.tts_q.put(("quit", None))
        self.meter.save()
        self.root.destroy()


def main():
    root = tk.Tk()
    ClaraApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
