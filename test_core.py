"""Tes otomatis untuk clara_core + clara_avatar (tanpa tkinter). Jalankan: python test_core.py"""
import json, os, sys, tempfile, types
from pathlib import Path
import clara_core as C

fails = []
def check(name, cond):
    print(("OK   " if cond else "FAIL ") + name)
    if not cond: fails.append(name)

# --- router lokal (0 token)
R = C.parse_local_command
check("buka chrome", R("Clara tolong buka chrome dong") == {"type": "open_app", "app": "chrome.exe", "label": "Buka chrome"})
check("buka shopee seller", R("buka shopee seller")["url"].startswith("https://seller.shopee"))
check("cari google", "q=harga+spray" in R("cari harga spray")["url"])
check("buka domain", R("buka openai.com")["url"] == "https://openai.com")
check("jam", R("jam berapa sekarang?")["type"] == "reply")
check("stop", R("stop")["type"] == "stop")
check("ingat", R("ingat bahwa harga naik 40rb")["type"] == "remember")
check("analisis kompleks -> AI", R("buat strategi marketing odorzinc minggu ini") is None)
check("buka aplikasi tak dikenal -> AI", R("buka aplikasi rahasia xyz") is None)
check("cmd tak dibuka", R("buka cmd") is None)

# --- klasifikasi model
S = dict(C.DEFAULT_SETTINGS)
check("chat murah", C.classify_request("apa kabar", S)["tier"] == "chat")
check("deep", C.classify_request("tolong riset dan audit iklan saya", S)["model"] == "gpt-4.1")
check("sales", C.classify_request("ide konten odorzinc", S)["max_out"] == 900)
S2 = dict(S, deep_mode=True)
check("deep mode paksa", C.classify_request("hai", S2)["tier"] == "deep")
long_route = C.classify_request("laporan lengkap keuangan perusahaan mendalam " + ("angka " * 400), S)
check("laporan panjang mendapat budget output besar", long_route["tier"] == "deep-long" and long_route["max_out"] == 8000)

# --- kompresi memori
prof = Path("memory_profile.md").read_text(encoding="utf-8")
m_chat = C.compact_memory(prof, "apa kabar")
m_sales = C.compact_memory(prof, "audit shopee odorzinc")
check("memori ringkas < profil", len(m_chat) < len(prof) * 0.6)
check("memori bisnis ikut bila relevan", "OdorZinc" in m_sales and len(m_sales) <= 2600)
print("   profil", len(prof), "chat", len(m_chat), "sales", len(m_sales))

# --- cache
with tempfile.TemporaryDirectory() as td:
    ac = C.AnswerCache(Path(td) / "c.json")
    k = ac.key("m", "Halo  Dunia", "x")
    ac.put(k, "jawab")
    check("cache hit (normalisasi spasi/kapital)", ac.get(ac.key("m", "halo dunia", "x"), 1) == "jawab")
    check("cache TTL kedaluwarsa", ac.get(k, 0) is None)

    um = C.UsageMeter(Path(td) / "u.json")
    cost = um.record("gpt-4.1-mini", {"input_tokens": 1000, "output_tokens": 200, "input_tokens_details": {"cached_tokens": 500}})
    exp = (500 * .40 + 500 * .10 + 200 * 1.6) / 1e6
    check("hitung biaya", abs(cost - exp) < 1e-9)
    check("anggaran", um.over_budget(0.0000001) and not um.over_budget(10))

# --- payload & retry param opsional
p = C.build_text_payload("gpt-4.1-mini", "hai", "mem", "", 450, False, "k")
check("payload cache key + max_out", p["prompt_cache_key"] == "k" and p["max_output_tokens"] == 450)
p2 = C.build_text_payload("gpt-4.1-mini", "hai", "", "", 450, True, "k")
check("web tool auto (bukan required)", p2["tool_choice"] == "auto")
calls = []
class Resp:
    def __init__(s, ok, status, js): s.ok, s.status_code, s._js, s.text = ok, status, js, json.dumps(js)
    def json(s): return s._js
class Req:
    def post(s, url, headers=None, json=None, timeout=0):
        calls.append(dict(json))
        if "prompt_cache_key" in json:
            return Resp(False, 400, {"error": {"message": "Unknown parameter: 'prompt_cache_key'."}})
        return Resp(True, 200, {"output": [{"type": "message", "content": [{"type": "output_text", "text": "halo"}]}], "usage": {"input_tokens": 5, "output_tokens": 2}})
txt, usage = C.call_openai(Req(), "sk-x", p)
check("retry tanpa parameter ditolak", txt == "halo" and len(calls) == 2 and "prompt_cache_key" not in calls[1])

# --- validasi aksi + skala koordinat
v = C.validate_action({"type": "click", "x": 800, "y": 450}, 1920, 1080, scale=1.2)
check("skala koordinat (1600->1920)", v == {"type": "click", "x": 960, "y": 540})
check("klik di luar layar ditolak", C.validate_action({"type": "click", "x": 1600, "y": 10}, 1920, 1080, 1.5) is None)
check("powershell ditolak", C.validate_action({"type": "type_text", "text": "powershell -c x"}, 100, 100) is None)
check("open_app terminal ditolak", C.validate_action({"type": "open_app", "app": "Windows Terminal"}, 100, 100) is None)
check("open_file exe ditolak", C.validate_action({"type": "open_file", "path": str(Path.home() / "x.exe")}, 1, 1) is None)
check("open_file di luar home ditolak", C.validate_action({"type": "open_file", "path": "C:\\Windows\\system32\\a.txt"}, 1, 1) is None)
check("write_file .bat ditolak", C.validate_action({"type": "write_file", "name": "a.bat", "text": "x"}, 1, 1) is None)
check("write_file path traversal dinetralkan", C.validate_action({"type": "write_file", "name": "../../a.txt", "text": "x"}, 1, 1)["name"] == "a.txt")
check("hotkey tak diizinkan", C.validate_action({"type": "hotkey", "keys": ["win", "r"]}, 1, 1) is None)
check("file:// ditolak", C.validate_action({"type": "open_url", "url": "file:///c:/x"}, 1, 1) is None)
check("risky task", C.task_is_risky("tolong hapus semua file") and not C.task_is_risky("buka youtube"))
check("sensitive window", C.is_sensitive_window("Bank BCA - Chrome") and not C.is_sensitive_window("Notepad"))
check("diff layar", C.screen_diff_score(bytes([0]*10), bytes([10]*10)) == 10)
check("redaksi key", "REDACTED" in C.redact_memory_secrets("api key: sk-abcdefghijklmnopqrstuvwxyz"))
check("parse plan json", C.parse_plan_json('```json\n{"actions":[],"summary":"x"}\n```')["summary"] == "x")

# --- avatar
import clara_avatar as A
im = A.render_frame(120, "thinking", 1.0)
check("avatar render", im.size[0] == 120 and im.mode == "RGBA")
a = A.AvatarAnimator(); keys = {a.step() for _ in range(200)}
check("animator tidak error", len(keys) > 1)

print("\n%d tes inti gagal sampai tahap ini" % len(fails))

# --- extension: uploaded expression sheet + finance module + stock heuristics
from datetime import date as _date
def date_today_for_test(): return _date.today().isoformat()
from io import BytesIO
import clara_finance as F
import clara_market as M
from clara_avatar import uploaded_expression_frame_png
try:
    from PIL import Image
    frame = Image.open(BytesIO(uploaded_expression_frame_png(120, "speaking", 5, False, 2, False, 1, 2, 1)))
    check("avatar uploaded-expression frame PNG", frame.width == 120 and frame.mode == "RGBA" and frame.getbbox() is not None)
except Exception as exc:
    check("avatar uploaded-expression frame PNG", False)

with tempfile.TemporaryDirectory() as td:
    fp = Path(td) / "finance.db"
    F.init_db(fp)
    tid = F.add_transaction({"direction":"Income", "income_type":"Active Income", "category":"Active Income",
                             "subcategory":"Employee / Freelancer", "amount":5_000_000, "date":date_today_for_test(),
                             "note":"Gaji", "status":"Completed"}, fp)
    check("finance transaction insert", tid == 1 and F.dashboard(fp)["income"] == 5_000_000)
    F.add_transaction({"direction":"Spending", "spending_type":"Productive Spending", "category":"Productive Spending",
                       "subcategory":"Investasi Active Income Engine", "detail":"Alat Kerja", "engine":"Active Income Engine",
                       "amount":500_000, "date":date_today_for_test(), "note":"alat kerja"}, fp)
    d=F.dashboard(fp)
    check("finance productive ratio local formula", d["productive_ratio"] == 100.0 and d["net_cashflow"] == 4_500_000)
    F.add_asset({"name":"Laptop","type":"Gadget","purchase_date":date_today_for_test(),"purchase_price":5_000_000,"current_value":3_500_000,"useful_life_years":4},fp)
    F.add_subscription({"name":"Layanan digital","monthly_cost":65_000,"last_used_date":"2026-07-01"},fp)
    F.upsert_budget("Consumptive Spending",1_000_000,path=fp)
    F.add_goal("Dana darurat",10_000_000,2_000_000,path=fp)
    check("finance assets/subscriptions/budgets/goals", len(F.list_assets(fp))==1 and len(F.list_subscriptions(fp))==1 and len(F.budget_report(fp))==1)
    bad=False
    try: F.add_transaction({"direction":"Income","income_type":"Portfolio Income","amount":1000,"date":date_today_for_test(),"note":"belum jual"},fp)
    except ValueError: bad=True
    check("portfolio income requires realized gain",bad)
    bad=False
    try: F.add_transaction({"direction":"Spending","spending_type":"Consumptive Spending","amount":0,"date":date_today_for_test()},fp)
    except ValueError: bad=True
    check("finance rejects zero amount",bad)
    check("finance CSV export", "Jumlah IDR" in F.export_csv(fp))

check("market ticker normalization", M._clean_symbol("bbca") == "BBCA.JK" and M._clean_symbol("^JKSE") == "^JKSE")
bad=False
try: M._clean_symbol("BBCA.JK;rm -rf")
except ValueError: bad=True
check("market ticker validation", bad)
sample_q={"symbol":"BBCA.JK","name":"Bank Central Asia","change_pct":1.4,"return_5d":3,"return_20d":8,"return_60d":11,"volatility_daily_pct":1.2,"volume_ratio":1.1}
sample_news=[{"title":"BBCA laba naik, dividen meningkat","sentiment":1}]
sig=M.signal_for_quote(sample_q,sample_news)
check("market signal uses price momentum + news", sig["score"] > 0 and sig["daily_bias"] == "Bullish")
check("market signal states uncertainty", "confidence" in sig and "rendah" in sig["confidence"].casefold() or "sedang" in sig["confidence"].casefold())
print("Extension tests selesai.")

print("\nTOTAL HASIL: %d tes gagal" % len(fails)); sys.exit(1 if fails else 0)
