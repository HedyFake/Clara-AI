"""Audit statis Clara v3.3. Jalankan lewat CHECK_CLARA.bat. Tidak menggantikan tes nyata di Windows."""
from __future__ import annotations
import ast, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
errors = []

for name in ("clara_buddy.py", "clara_core.py", "clara_avatar.py", "clara_finance.py", "clara_market.py"):
    try:
        src = (ROOT / name).read_text(encoding="utf-8")
        ast.parse(src, filename=name)
        compile(src, name, "exec")
        print("PASS: sintaks", name)
    except Exception as exc:
        errors.append(f"{name}: {exc}")
        continue
    for bad in ("eval(", "exec(", "os.system(", "shell=True"):
        if bad in src:
            errors.append(f"{name}: pola berisiko {bad}")

for item in ("assets/clara_reference.png", "assets/clara.ico", "assets/expressions/expression_0_0.png", "assets/expressions/expression_2_3.png", "memory_profile.md", "requirements.txt", "TOKEN_OPTIMIZATION_PLAYBOOK_ID.md"):
    print(("PASS" if (ROOT / item).exists() else "FAIL") + ": file", item)
    if not (ROOT / item).exists():
        errors.append("hilang: " + item)

print("\nMenjalankan test_core.py ...")
r = subprocess.run([sys.executable, str(ROOT / "test_core.py")], cwd=ROOT, capture_output=True, text=True)
print(r.stdout[-1500:])
if r.returncode != 0:
    errors.append("test_core.py gagal")

try:
    import tkinter  # noqa: F401
    print("PASS: tkinter tersedia")
except Exception:
    errors.append("tkinter tidak tersedia (instal Python dari python.org dengan opsi tcl/tk)")

print("\nHASIL:", "GAGAL" if errors else "LULUS")
for e in errors:
    print(" -", e)
sys.exit(1 if errors else 0)
