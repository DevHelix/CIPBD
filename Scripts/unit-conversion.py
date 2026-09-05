"""Rescale CIP dollar columns to thousands.

Converts previous_appropriations, project_total and every year_XXXX column
in a CSV (or a whole directory of CSVs) from dollars to $1k units.

    python to_thousands.py outputs\2015.csv
    python to_thousands.py outputs --decimals 1
    python to_thousands.py outputs --in-place
"""
import argparse, csv, os, re, sys
from decimal import Decimal, ROUND_HALF_UP

MONEY = re.compile(r'^(year_\d{4}|previous_appropriations|project_total)$')
SCALE = Decimal(1000)

def is_money(col): return bool(MONEY.match(col))

def parse_money(raw):
    """'$1,234' / '(500)' / '' -> (Decimal|None, ok_flag)."""
    s = str(raw if raw is not None else '').strip()
    if s == '': return None, True
    neg  = s.startswith('(') and s.endswith(')')
    body = (s[1:-1] if neg else s).replace('$', '').replace(',', '')
    try: v = Decimal(body)
    except Exception: return None, False
    return (-v if neg else v), True

def convert(path, out_path, places):
    with open(path, newline='', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
        cols = list(rows[0].keys()) if rows else []
    if not rows:
        print(f"  {os.path.basename(path)}: empty, skipped"); return

    money = [c for c in cols if is_money(c)]
    if not money:
        print(f"  {os.path.basename(path)}: no money columns, skipped"); return

    ycols   = [c for c in money if c.startswith('year_')]
    has_inv = 'previous_appropriations' in cols and 'project_total' in cols and ycols

    def val(r, c):
        v, _ = parse_money(r.get(c))
        return v or Decimal(0)

    def balanced():
        return sum(1 for r in rows
                   if val(r, 'previous_appropriations') + sum(val(r, c) for c in ycols)
                   == val(r, 'project_total'))

    before = balanced() if has_inv else 0

    q = Decimal(1) if places == 0 else Decimal(1).scaleb(-places)
    unparsed = 0
    for r in rows:
        for c in money:
            v, ok = parse_money(r.get(c))
            if not ok:
                unparsed += 1; continue      # leave anything unparseable untouched
            if v is None: continue           # blanks stay blank
            out = (v / SCALE).quantize(q, rounding=ROUND_HALF_UP)
            r[c] = str(int(out)) if places == 0 else str(out)

    after = balanced() if has_inv else 0

    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader(); w.writerows(rows)

    note = ''
    if has_inv:
        note = f" | balanced {before}/{len(rows)} -> {after}/{len(rows)}"
        if before - after > 0:
            note += f"  ({before-after} broken by rounding; try --decimals {places+1})"
    if unparsed:
        note += f" | {unparsed} non-numeric left as-is"
    print(f"  {os.path.basename(path)} -> {os.path.basename(out_path)}: "
          f"{len(rows)} rows, {len(money)} cols{note}")

def main():
    ap = argparse.ArgumentParser(description="Rescale CIP dollar columns to $1k units.")
    ap.add_argument('target', help='CSV file or directory of CSVs')
    ap.add_argument('--decimals', type=int, default=0,
                    help='decimal places to keep (default 0 = whole thousands)')
    ap.add_argument('--suffix', default='_k', help="output suffix (default '_k')")
    ap.add_argument('--in-place', action='store_true',
                    help='overwrite the source files instead of writing copies')
    a = ap.parse_args()

    if os.path.isdir(a.target):
        files = sorted(os.path.join(a.target, f) for f in os.listdir(a.target)
                       if f.lower().endswith('.csv') and not f.endswith(a.suffix + '.csv'))
    elif os.path.isfile(a.target):
        files = [a.target]
    else:
        sys.exit(f"not found: {a.target}")
    if not files: sys.exit("no CSVs found")

    print(f"Converting {len(files)} file(s) to $1k, {a.decimals} decimal place(s):")
    for p in files:
        stem, ext = os.path.splitext(p)
        convert(p, p if a.in_place else stem + a.suffix + ext, a.decimals)

if __name__ == '__main__':
    main()