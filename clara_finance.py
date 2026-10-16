"""Modul keuangan Clara: pencatatan lokal, klasifikasi konsisten, skor dan advisor prompt.
Data disimpan lokal dalam SQLite di %LOCALAPPDATA%/ClaraDesktopBuddy/finance.db.
"""
from __future__ import annotations
import csv, io, json, sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from clara_core import APP_DIR

DB_PATH = APP_DIR / "finance.db"
CURRENCY = "IDR"

INCOME_TYPES = {
    "Active Income": ["Business Owner / Operator", "Professional Service", "Employee / Freelancer", "Lainnya"],
    "Passive Income": ["Properti Sewa", "Rental Barang", "Dividen Saham", "Royalti / Lisensi", "Passive Income Lainnya"],
    "Portfolio Income": ["Capital Gain Properti", "Capital Gain Kendaraan", "Capital Gain Saham", "Capital Gain Barang Koleksi", "Portfolio Income Lainnya"],
}
SPENDING_TYPES = {
    "Productive Spending": {
        "Investasi Active Income Engine": ["Modal Usaha", "Alat Kerja", "Pelatihan Jasa", "Produktivitas Tim", "Lainnya"],
        "Investasi Passive Income Engine": ["Properti Sewa", "Renovasi Ruko", "Barang Rental", "Maintenance Aset Produktif", "Lainnya"],
        "Investasi Portfolio Income Engine": ["Saham", "Obligasi", "Emas", "Tanah", "Aset Apresiasi", "Lainnya"],
    },
    "Consumptive Spending": {
        "Luxury Depreciating Consumptive": ["Barang Mewah Tidak Produktif", "Merek Tidak Jelas / Nilai Jual Rendah", "Konsumtif Gengsi"],
        "Passive Spending": ["Langganan Digital / Cloud", "Bensin & Transportasi Rutin", "Karyawan Tidak Produktif", "Utilitas & Tagihan Berulang", "Passive Spending Lainnya"],
        "Invisible Spending": ["Depresiasi Kendaraan", "Depresiasi Gadget & Elektronik", "Depresiasi Perabot", "Invisible Spending Lainnya"],
    },
    "Consumptive with Productive Effect": {
        "Pendidikan & Kursus": ["Kursus", "Seminar", "Buku", "Sertifikasi", "Lainnya"],
        "Networking & Komunitas Bisnis": ["Komunitas", "Networking", "Acara Bisnis", "Lainnya"],
        "Kesehatan & Keamanan": ["Kesehatan", "Asuransi", "Keamanan", "Lainnya"],
        "Pengembangan Diri": ["Pengembangan Diri", "Coaching", "Lainnya"],
        "Konsumtif Produktif Lainnya": ["Lainnya"],
    },
}

FINANCE_ADVISOR_SYSTEM = """Kamu adalah Clara, asisten analisis keuangan pribadi dan konsultan bisnis Indonesia. Bekerjalah dengan pola pikir analis senior: teliti, profesional, berhati-hati pada ketidakpastian, dan praktis. Bukan dokter, pengacara, konsultan pajak atau penasihat investasi berizin. Jangan pernah mengaku memiliki lisensi/pengalaman nyata. Untuk pajak, hukum, investasi, atau aturan yang dapat berubah: minta/aktifkan riset web bila tersedia, prioritaskan sumber primer resmi (DJP, JDIH, OJK, BEI, Bank Indonesia, BPK, peraturan.go.id), tulis tanggal pemeriksaan, tautkan sumber, bedakan aturan yang berlaku dan yang perlu diverifikasi. Jangan mengarang pasal, tarif, kutipan atau angka. Jika web tidak tersedia, nyatakan keterbatasan dan tandai hal yang wajib diverifikasi profesional.

Saat pertanyaan membutuhkan laporan komprehensif, susun dengan heading, subheading, tabel bila membantu, ilustrasi angka yang jelas diberi label simulasi, SOP operasional, risiko dan checklist tindak lanjut. Jawaban sederhana tetap boleh ringkas; jangan memaksa 800 kata untuk setiap pertanyaan kecil. Tidak ada skema penghindaran pajak ilegal, manipulasi pembukuan atau menjamin hasil investasi. Untuk pasar modal, tampilkan skenario bullish/base/bearish dan risiko, bukan kepastian naik/turun. Minta konteks yang benar-benar dibutuhkan, jangan meminta kata sandi, OTP, PIN, data kartu, atau kredensial bank."""


def connect(path: Path | None = None):
    p = path or DB_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(p, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    return db


def init_db(path: Path | None = None) -> None:
    with connect(path) as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS accounts(id INTEGER PRIMARY KEY, name TEXT NOT NULL, type TEXT NOT NULL DEFAULT 'Kas', opening_balance REAL NOT NULL DEFAULT 0, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS transactions(id INTEGER PRIMARY KEY, date TEXT NOT NULL, direction TEXT NOT NULL CHECK(direction IN ('Income','Spending')), income_type TEXT, spending_type TEXT, engine TEXT, category TEXT NOT NULL, subcategory TEXT NOT NULL, detail TEXT NOT NULL DEFAULT 'Lainnya', amount REAL NOT NULL CHECK(amount>0), account_id INTEGER, note TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'Completed' CHECK(status IN ('Planned','Completed','Cancelled')), recurring INTEGER NOT NULL DEFAULT 0, recurring_frequency TEXT, asset_name TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY(account_id) REFERENCES accounts(id));
        CREATE TABLE IF NOT EXISTS assets(id INTEGER PRIMARY KEY, name TEXT NOT NULL, asset_type TEXT NOT NULL, purchase_date TEXT NOT NULL, purchase_price REAL NOT NULL CHECK(purchase_price>=0), current_value REAL NOT NULL CHECK(current_value>=0), useful_life_years REAL NOT NULL DEFAULT 5, residual_value REAL NOT NULL DEFAULT 0, status TEXT NOT NULL DEFAULT 'Aktif', note TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS subscriptions(id INTEGER PRIMARY KEY, name TEXT NOT NULL, provider TEXT NOT NULL DEFAULT '', monthly_cost REAL NOT NULL CHECK(monthly_cost>=0), renewal_date TEXT, active INTEGER NOT NULL DEFAULT 1, last_used_date TEXT, note TEXT NOT NULL DEFAULT '');
        CREATE TABLE IF NOT EXISTS budgets(id INTEGER PRIMARY KEY, category TEXT NOT NULL, period TEXT NOT NULL DEFAULT 'Bulanan', limit_amount REAL NOT NULL CHECK(limit_amount>=0), alert_percent REAL NOT NULL DEFAULT 80, UNIQUE(category,period));
        CREATE TABLE IF NOT EXISTS goals(id INTEGER PRIMARY KEY, name TEXT NOT NULL, target_amount REAL NOT NULL CHECK(target_amount>=0), current_amount REAL NOT NULL DEFAULT 0, deadline TEXT, goal_type TEXT NOT NULL DEFAULT 'Dana darurat');
        CREATE TABLE IF NOT EXISTS liabilities(id INTEGER PRIMARY KEY, name TEXT NOT NULL, initial_amount REAL NOT NULL, remaining_amount REAL NOT NULL, annual_interest REAL NOT NULL DEFAULT 0, due_date TEXT, status TEXT NOT NULL DEFAULT 'Aktif');
        CREATE TABLE IF NOT EXISTS audit_logs(id INTEGER PRIMARY KEY, entity TEXT NOT NULL, entity_id INTEGER, action TEXT NOT NULL, old_value TEXT, new_value TEXT, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS recommendations(id INTEGER PRIMARY KEY, type TEXT NOT NULL, title TEXT NOT NULL, description TEXT NOT NULL, priority TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Baru', created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS financial_scores(id INTEGER PRIMARY KEY, period TEXT NOT NULL, health REAL NOT NULL, productivity REAL NOT NULL, income_diversity REAL NOT NULL, leakage REAL NOT NULL, freedom REAL NOT NULL, notes TEXT NOT NULL, UNIQUE(period));
        """)
        cols = {row[1] for row in db.execute("PRAGMA table_info(transactions)").fetchall()}
        if "detail" not in cols:
            db.execute("ALTER TABLE transactions ADD COLUMN detail TEXT NOT NULL DEFAULT 'Lainnya'")
        db.execute("INSERT OR IGNORE INTO accounts(id,name,type,opening_balance,created_at) VALUES(1,'Kas / rekening utama','Bank',0,?)", (datetime.now().isoformat(timespec='seconds'),))


def classify_description(description: str, direction: str) -> dict[str, str]:
    """Rules are suggestions only; user may change category before saving."""
    text = (description or "").casefold()
    if direction == "Income":
        if any(k in text for k in ("dividen", "royalti", "sewa", "rental", "bunga deposito")):
            sub = "Dividen Saham" if "dividen" in text else ("Properti Sewa" if "sewa" in text else "Passive Income Lainnya")
            return {"income_type":"Passive Income","category":"Passive Income","subcategory":sub,"engine":""}
        if any(k in text for k in ("capital gain", "untung jual saham", "jual saham profit", "selisih jual aset")):
            return {"income_type":"Portfolio Income","category":"Portfolio Income","subcategory":"Portfolio Income Lainnya","engine":""}
        return {"income_type":"Active Income","category":"Active Income","subcategory":"Lainnya","engine":""}
    # Order prioritizes distinctive terms before general vehicle/gadget keywords.
    if any(k in text for k in ("kursus", "seminar", "buku", "networking", "komunitas bisnis", "sertifikasi", "pelatihan diri")):
        return {"spending_type":"Consumptive with Productive Effect","category":"Consumptive with Productive Effect","subcategory":"Pendidikan & Kursus" if any(k in text for k in ("kursus","seminar","buku","sertifikasi")) else "Networking & Komunitas Bisnis","engine":""}
    if any(k in text for k in ("modal usaha", "alat kerja", "pelatihan jasa", "stok odorzinc", "bahan baku", "iklan produk")):
        return {"spending_type":"Productive Spending","category":"Productive Spending","subcategory":"Investasi Active Income Engine","engine":"Active Income Engine"}
    if any(k in text for k in ("properti sewa", "renovasi ruko", "barang rental", "alat rental")):
        return {"spending_type":"Productive Spending","category":"Productive Spending","subcategory":"Investasi Passive Income Engine","engine":"Passive Income Engine"}
    if any(k in text for k in ("beli saham", "beli emas", "beli tanah", "obligasi", "aset apresiasi")):
        return {"spending_type":"Productive Spending","category":"Productive Spending","subcategory":"Investasi Portfolio Income Engine","engine":"Portfolio Income Engine"}
    if any(k in text for k in ("merek aneh", "barang mewah", "gengsi", "luxury")):
        return {"spending_type":"Consumptive Spending","category":"Consumptive Spending","subcategory":"Luxury Depreciating Consumptive","engine":""}
    if any(k in text for k in ("google cloud", "aws", "netflix", "spotify", "langganan", "subscription", "bensin", "tol", "parkir", "listrik", "air", "cloud")):
        sub="Langganan Digital / Cloud" if any(k in text for k in ("cloud", "aws", "netflix", "spotify", "langganan", "subscription")) else "Bensin & Transportasi Rutin"
        return {"spending_type":"Consumptive Spending","category":"Consumptive Spending","subcategory":"Passive Spending","engine":"" ,"detail":sub}
    if any(k in text for k in ("mobil", "motor", "iphone", "gadget", "laptop", "elektronik", "furnitur", "perabot")):
        sub="Depresiasi Kendaraan" if any(k in text for k in ("mobil","motor")) else "Depresiasi Gadget & Elektronik"
        return {"spending_type":"Consumptive Spending","category":"Consumptive Spending","subcategory":"Invisible Spending","engine":"","detail":sub}
    return {"spending_type":"Consumptive Spending","category":"Consumptive Spending","subcategory":"Passive Spending","engine":"","detail":"Passive Spending Lainnya"}


def add_transaction(data: dict[str, Any], path: Path | None = None) -> int:
    direction = data.get("direction", "Spending")
    amount = float(data.get("amount", 0))
    when = str(data.get("date") or date.today().isoformat())
    note = str(data.get("note", "")).strip()
    if direction not in ("Income", "Spending"):
        raise ValueError("Jenis transaksi harus Income atau Spending.")
    if amount <= 0:
        raise ValueError("Jumlah transaksi harus lebih besar dari nol.")
    try: date.fromisoformat(when)
    except ValueError: raise ValueError("Tanggal harus berformat YYYY-MM-DD.")
    status = data.get("status", "Completed")
    if status == "Completed" and date.fromisoformat(when) > date.today():
        raise ValueError("Transaksi Completed tidak boleh bertanggal di masa depan; gunakan Planned.")
    inferred = classify_description(note, direction)
    income_type = data.get("income_type") or inferred.get("income_type")
    spending_type = data.get("spending_type") or inferred.get("spending_type")
    category = data.get("category") or inferred.get("category") or (income_type if direction == "Income" else spending_type)
    subcategory = data.get("subcategory") or inferred.get("subcategory") or "Lainnya"
    detail = data.get("detail") or inferred.get("detail", "Lainnya")
    engine = data.get("engine") or inferred.get("engine", "")
    if direction == "Income":
        if income_type not in INCOME_TYPES: raise ValueError("Pilih kategori Active, Passive, atau Portfolio Income.")
        if income_type == "Portfolio Income" and not data.get("asset_sold", False):
            raise ValueError("Portfolio Income dicatat ketika capital gain sudah direalisasikan (aset benar-benar dijual).")
        spending_type = None
    else:
        if spending_type not in SPENDING_TYPES: raise ValueError("Pilih kategori pengeluaran yang tersedia.")
        if spending_type == "Productive Spending" and engine not in ("Active Income Engine", "Passive Income Engine", "Portfolio Income Engine"):
            raise ValueError("Pengeluaran produktif harus dihubungkan ke salah satu mesin income.")
        income_type = None
    now = datetime.now().isoformat(timespec='seconds')
    with connect(path) as db:
        cur=db.execute("""INSERT INTO transactions(date,direction,income_type,spending_type,engine,category,subcategory,detail,amount,account_id,note,status,recurring,recurring_frequency,asset_name,created_at,updated_at)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (when,direction,income_type,spending_type,engine,category,subcategory,detail,amount,data.get('account_id',1),note,status,int(bool(data.get('recurring'))),data.get('recurring_frequency'),data.get('asset_name'),now,now))
        tid=cur.lastrowid
        db.execute("INSERT INTO audit_logs(entity,entity_id,action,old_value,new_value,created_at) VALUES('transactions',?,'create',NULL,?,?)", (tid,json.dumps(data,ensure_ascii=False,default=str),now))
        return int(tid)


def dashboard(path: Path | None = None, period: str | None = None) -> dict[str, Any]:
    init_db(path)
    period=period or date.today().strftime('%Y-%m')
    start=period+'-01'
    with connect(path) as db:
        rows=db.execute("SELECT * FROM transactions WHERE substr(date,1,7)=? AND status='Completed'",(period,)).fetchall()
        income=sum(r['amount'] for r in rows if r['direction']=='Income')
        spending=sum(r['amount'] for r in rows if r['direction']=='Spending')
        passive=sum(r['amount'] for r in rows if r['direction']=='Income' and r['income_type']=='Passive Income')
        portfolio=sum(r['amount'] for r in rows if r['direction']=='Income' and r['income_type']=='Portfolio Income')
        productive=sum(r['amount'] for r in rows if r['direction']=='Spending' and r['spending_type']=='Productive Spending')
        consumptive=sum(r['amount'] for r in rows if r['direction']=='Spending' and r['spending_type']=='Consumptive Spending')
        consumptive_effect=sum(r['amount'] for r in rows if r['direction']=='Spending' and r['spending_type']=='Consumptive with Productive Effect')
        sub_total=db.execute("SELECT COALESCE(SUM(monthly_cost),0) FROM subscriptions WHERE active=1").fetchone()[0]
        assets=db.execute("SELECT COALESCE(SUM(current_value),0) FROM assets WHERE status='Aktif'").fetchone()[0]
        liabilities=db.execute("SELECT COALESCE(SUM(remaining_amount),0) FROM liabilities WHERE status='Aktif'").fetchone()[0]
        tops=[dict(r) for r in db.execute("SELECT date,note,category,amount FROM transactions WHERE substr(date,1,7)=? AND status='Completed' AND direction='Spending' ORDER BY amount DESC LIMIT 5",(period,)).fetchall()]
        diversity=sum(1 for typ in ('Active Income','Passive Income','Portfolio Income') if any(r['direction']=='Income' and r['income_type']==typ and r['amount']>0 for r in rows))/3*100
    net=income-spending
    prod_ratio=productive/spending*100 if spending else 0
    consum_ratio=consumptive/spending*100 if spending else 0
    passive_ratio=passive/income*100 if income else 0
    freedom=(passive+portfolio)/spending*100 if spending else (100.0 if passive+portfolio>0 else 0)
    sub_burden=sub_total/income*100 if income else (100.0 if sub_total>0 else 0)
    cash_score=100 if net>0 and income>0 else (45 if net==0 and income>0 else 0)
    # Heuristic score; transparency matters more than false precision.
    health=max(0,min(100,prod_ratio*.30 + min(passive_ratio,100)*.25 + cash_score*.20 + max(0,100-min(100,sub_burden))*.10 + diversity*.15))
    notes=[]
    if net<0: notes.append("Arus kas negatif: pengeluaran melampaui pendapatan.")
    if sub_burden>10: notes.append("Biaya langganan melewati 10% pendapatan bulan ini.")
    if consum_ratio>60: notes.append("Pengeluaran konsumtif relatif tinggi; tinjau kebutuhan dan manfaatnya.")
    if prod_ratio<15 and spending>0: notes.append("Rasio pengeluaran produktif di bawah 15%; evaluasi tujuan, bukan asal meningkatkan investasi.")
    if not notes: notes.append("Belum terlihat tanda bahaya dari transaksi tercatat; pastikan data lengkap.")
    return {"period":period,"income":income,"spending":spending,"net_cashflow":net,"active_income":sum(r['amount'] for r in rows if r['direction']=='Income' and r['income_type']=='Active Income'),"passive_income":passive,"portfolio_income":portfolio,"productive_spending":productive,"consumptive_spending":consumptive,"consumptive_effect":consumptive_effect,"productive_ratio":prod_ratio,"consumptive_ratio":consum_ratio,"passive_income_ratio":passive_ratio,"freedom_ratio":freedom,"subscription_monthly":sub_total,"subscription_burden":sub_burden,"asset_value":assets,"liability_value":liabilities,"net_worth":assets-liabilities,"health_score":health,"income_diversity":diversity,"top_spending":tops,"notes":notes}


def export_csv(path: Path | None = None) -> str:
    init_db(path)
    with connect(path) as db:
        rows=db.execute("SELECT date,direction,income_type,spending_type,engine,category,subcategory,detail,amount,note,status,recurring,recurring_frequency,asset_name FROM transactions ORDER BY date DESC,id DESC").fetchall()
    sio=io.StringIO(); writer=csv.writer(sio)
    writer.writerow(["Tanggal","Jenis","Tipe Pendapatan","Tipe Pengeluaran","Mesin Income","Kategori","Subkategori","Detail","Jumlah IDR","Catatan","Status","Berulang","Frekuensi","Aset"])
    for r in rows: writer.writerow(list(r))
    return sio.getvalue()


def recommendations(path: Path | None = None) -> list[str]:
    d=dashboard(path)
    out=list(d['notes'])
    if d['income']>0 and d['subscription_burden']>5: out.append("Periksa langganan yang jarang digunakan; potensi penghematan maksimal dari biaya bulanan yang bisa dihentikan.")
    if d['passive_income']+d['portfolio_income']<d['spending'] and d['spending']>0: out.append("Pendapatan pasif/portofolio terealisasi belum menutup pengeluaran. Jangan mengejar imbal hasil tinggi tanpa menilai risiko.")
    if d['net_cashflow']>0: out.append("Pisahkan surplus untuk dana darurat, kewajiban dekat jatuh tempo, tujuan dan investasi sesuai profil risiko.")
    return out


def company_advisor_prompt(question: str, context: str = "") -> str:
    return ("KONTEKS TUGAS: Konsultan bisnis, manajemen arus kas, investasi korporasi, turnaround, SDM, perencanaan pajak yang legal, dan kepatuhan hukum perusahaan Indonesia. "
            "Gunakan hukum dan tarif yang telah diverifikasi saat ini bila tersedia; jangan mengasumsikan contoh regulasi di prompt lama masih berlaku. "
            "Berikan analisis sistematis, contoh angka ilustratif, SOP, risiko, opsi, serta sumber resmi. Untuk setiap klaim yang belum bisa diverifikasi, beri label.\n\n"
            + ("KONTEKS PENGGUNA:\n"+context.strip()[:6000]+"\n\n" if context.strip() else "") + "PERTANYAAN:\n"+question.strip()[:12000])


def add_asset(data: dict[str, Any], path: Path | None = None) -> int:
    name=str(data.get('name','')).strip(); typ=str(data.get('type','Lainnya'))
    if not name: raise ValueError('Nama aset wajib diisi.')
    purchase=float(data.get('purchase_price',0)); current=float(data.get('current_value',0)); life=float(data.get('useful_life_years',5)); residual=float(data.get('residual_value',0))
    if min(purchase,current,life,residual)<0 or life<=0: raise ValueError('Nilai harga/umur aset tidak valid.')
    dt=str(data.get('purchase_date') or date.today().isoformat()); date.fromisoformat(dt)
    now=datetime.now().isoformat(timespec='seconds')
    with connect(path) as db:
        cur=db.execute("INSERT INTO assets(name,asset_type,purchase_date,purchase_price,current_value,useful_life_years,residual_value,status,note,updated_at) VALUES(?,?,?,?,?,?,?,'Aktif',?,?)",(name,typ,dt,purchase,current,life,residual,str(data.get('note',''))[:1000],now))
        db.execute("INSERT INTO audit_logs(entity,entity_id,action,new_value,created_at) VALUES('assets',?,'create',?,?)",(cur.lastrowid,json.dumps(data,ensure_ascii=False),now))
        return int(cur.lastrowid)


def add_subscription(data: dict[str, Any], path: Path | None = None) -> int:
    name=str(data.get('name','')).strip(); cost=float(data.get('monthly_cost',0))
    if not name: raise ValueError('Nama langganan wajib diisi.')
    if cost<0: raise ValueError('Biaya langganan tidak boleh negatif.')
    renewal=data.get('renewal_date') or None
    if renewal: date.fromisoformat(str(renewal))
    last=data.get('last_used_date') or None
    if last: date.fromisoformat(str(last))
    with connect(path) as db:
        cur=db.execute("INSERT INTO subscriptions(name,provider,monthly_cost,renewal_date,active,last_used_date,note) VALUES(?,?,?,?,?,?,?)",(name,str(data.get('provider',''))[:150],cost,renewal,int(bool(data.get('active',True))),last,str(data.get('note',''))[:1000]))
        return int(cur.lastrowid)


def upsert_budget(category: str, limit_amount: float, period: str = 'Bulanan', alert_percent: float = 80, path: Path | None = None) -> None:
    category=category.strip(); limit_amount=float(limit_amount); alert_percent=float(alert_percent)
    if not category: raise ValueError('Kategori anggaran wajib diisi.')
    if limit_amount<0 or not 1<=alert_percent<=100: raise ValueError('Batas anggaran atau persentase alert tidak valid.')
    with connect(path) as db:
        db.execute("INSERT INTO budgets(category,period,limit_amount,alert_percent) VALUES(?,?,?,?) ON CONFLICT(category,period) DO UPDATE SET limit_amount=excluded.limit_amount,alert_percent=excluded.alert_percent",(category,period,limit_amount,alert_percent))


def budget_report(path: Path | None = None) -> list[dict[str, Any]]:
    month=date.today().strftime('%Y-%m')
    with connect(path) as db:
        budgets=db.execute("SELECT * FROM budgets WHERE period='Bulanan'").fetchall()
        output=[]
        for b in budgets:
            spent=float(db.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE status='Completed' AND direction='Spending' AND category=? AND substr(date,1,7)=?",(b['category'],month)).fetchone()[0])
            pct=spent/b['limit_amount']*100 if b['limit_amount'] else (100 if spent else 0)
            output.append({"category":b['category'],"limit":b['limit_amount'],"spent":spent,"percent":pct,"alert":pct>=b['alert_percent']})
        return output


def add_goal(name: str, target_amount: float, current_amount: float = 0, deadline: str | None = None, goal_type: str = 'Dana darurat', path: Path | None = None) -> int:
    name=name.strip(); target_amount=float(target_amount); current_amount=float(current_amount)
    if not name or target_amount<=0 or current_amount<0: raise ValueError('Nama/target tujuan tidak valid.')
    if deadline: date.fromisoformat(deadline)
    with connect(path) as db:
        cur=db.execute("INSERT INTO goals(name,target_amount,current_amount,deadline,goal_type) VALUES(?,?,?,?,?)",(name,target_amount,current_amount,deadline,goal_type))
        return int(cur.lastrowid)


def list_assets(path: Path | None = None) -> list[dict[str, Any]]:
    with connect(path) as db: rows=db.execute("SELECT * FROM assets ORDER BY id DESC").fetchall()
    out=[]
    for r in rows:
        elapsed=max(0,(date.today()-date.fromisoformat(r['purchase_date'])).days/365.25)
        straight_line=max(r['residual_value'],r['purchase_price']-(r['purchase_price']-r['residual_value'])*min(1,elapsed/r['useful_life_years']))
        out.append({**dict(r),"book_value_estimate":straight_line,"market_loss":r['purchase_price']-r['current_value'],"annual_depreciation_estimate":max(0,(r['purchase_price']-r['residual_value'])/r['useful_life_years'])})
    return out


def list_subscriptions(path: Path | None = None) -> list[dict[str, Any]]:
    today=date.today()
    with connect(path) as db: rows=db.execute("SELECT * FROM subscriptions ORDER BY active DESC,monthly_cost DESC").fetchall()
    out=[]
    for r in rows:
        d=dict(r); due=None
        if d['renewal_date']:
            try: due=(date.fromisoformat(d['renewal_date'])-today).days
            except ValueError: pass
        d['days_to_renewal']=due
        d['annual_cost']=d['monthly_cost']*12
        d['possibly_unused']=bool(d['active'] and d['last_used_date'] and (today-date.fromisoformat(d['last_used_date'])).days>=45)
        out.append(d)
    return out
