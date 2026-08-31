# ── SHARED HELPERS ────────────────────────────────────────────────────────────
import csv, re, pdfplumber
from collections import defaultdict

def clean_num(v):
    s = str(v or '').strip().replace(',', '').replace(' ', '')
    if s.startswith('(') and s.endswith(')'):
        s = '-' + s[1:-1]
    if not s or s in ('-', '—', 'N/A', 'n/a', 'TBD'):
        return 0
    try:
        return int(float(s))
    except:
        return 0

def clean_text(v):
    return ' '.join(str(v or '').replace('\n', ' ').split())

def get_department(txt):
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    return lines[0].title().strip() if lines else ''

def is_data_page(pg, t):
    return (
        pg.rotation == 0
        and len(t) >= 3
        and len(t[0]) == 12
        and 'Project' in str(t[0][0] or '')
    )

def is_skip_row(row):
    name = clean_text(str(row[0] or ''))
    if not name:
        return True
    if re.match(r'^total\b', name, re.I):
        return True
    return False

def stringify(record, str_fields):
    for f in str_fields:
        record[f] = str(record[f])
    return record

def merge_projects(records, sum_fields, year_cols, str_fields):
    groups = defaultdict(list)
    for r in records:
        key = (r['project_name'], r['department'])
        groups[key].append(r)

    merged = []
    for (project_name, department), rows in groups.items():
        base = dict(rows[0])
        for field in sum_fields:
            base[field] = sum(r[field] for r in rows)
        seen, sources = set(), []
        for r in rows:
            fs = r['funding_source']
            if fs and fs not in seen:
                sources.append(fs); seen.add(fs)
        base['funding_source'] = ' / '.join(sources)
        pages = sorted(set(r['source_page'] for r in rows))
        base['source_page'] = ', '.join(str(p) for p in pages)
        active = [yr for yr, col in year_cols.items() if base[col] != 0]
        base['start_year'] = min(active) if active else ''
        base['end_year']   = max(active) if active else ''
        merged.append(stringify(base, str_fields))
    return merged

def split_project_id(name):
    # ' - ' (with spaces) avoids false splits on:
    #   intra-word hyphens:  'DAL-Entrance Road - W167'  →  splits only on ' - W167'
    #   highway refs:        'Bridge at IH-30 - W722'    →  splits only on ' - W722'
    #   road names ending:   'Chalk Hill Rd - Davis St to IH-30'  →  no split (IH-30 has no ' - ')
    # \d{3,} avoids matching highway numbers (IH-30, US-75) even if spaced
    m = re.search(r' - ([A-Za-z][A-Za-z_]*\d+|\d{3,})$', name)
    if m:
        return name[:m.start()].strip(), m.group(1)
    return name, ''

# ── 2022 PARSER ───────────────────────────────────────────────────────────────
# Cols: Project | Service | Funding | Council District | Comp Date |
#       Budget ITD | Spent | Remaining | FY2022-23 | FY2023-24 | Future Costs | Total
# Year cols: year_2023, year_2024

def parse_2022():
    pdf_path = r"C:\Users\vince\Documents\GitHub\CIPBD\Dallas\PDF\2022.pdf"
    cip_year = 2022
    year_cols = {2023: 'year_2023', 2024: 'year_2024'}
    sum_fields = ['previous_appropriations', 'spent', 'remaining',
                  'year_2023', 'year_2024', 'project_total']
    str_fields = ['spent', 'remaining']
    records = []
    department = ''

    with pdfplumber.open(pdf_path) as pdf:
        for pg in pdf.pages:
            txt = pg.extract_text() or ''
            tables = pg.extract_tables()
            t = max(tables, key=len) if tables else []
            if not t or not is_data_page(pg, t):
                continue
            dept = get_department(txt)
            if dept:
                department = dept
            for row in t[1:]:
                if is_skip_row(row):
                    continue
                total_cost  = clean_num(row[11])
                future_cost = clean_num(row[10])
                records.append({
                    'cip_year': cip_year, 'source_page': pg.page_number,
                    'department': department,
                    'project_name':            clean_text(row[0]),
                    'project_type':            clean_text(row[1]),
                    'funding_source':          clean_text(row[2]),
                    'address_location':        clean_text(row[3]),
                    'comp_date':               clean_text(row[4]),
                    'previous_appropriations': clean_num(row[5]),
                    'spent':                   clean_num(row[6]),
                    'remaining':               clean_num(row[7]),
                    'year_2023':               clean_num(row[8]),
                    'year_2024':               clean_num(row[9]),
                    'project_total':           total_cost - future_cost,
                })

    merged = merge_projects(records, sum_fields, year_cols, str_fields)
    for rec in merged:
        rec['project_name'], rec['project_id'] = split_project_id(rec['project_name'])

    out = r"C:\Users\vince\Documents\GitHub\CIPBD\Scripts\Dallas\outputs\2022.csv"
    fieldnames = ['cip_year','source_page','department','project_name','project_id','project_type',
              'funding_source','address_location','comp_date',
              'previous_appropriations','spent','remaining',
              'year_2023','year_2024','project_total','start_year','end_year']
    with open(out, 'w', newline='', encoding='utf-8') as f:
        csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore').writeheader()
        csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore').writerows(merged)
    print(f"Raw: {len(records)}  Merged: {len(merged)}  → 2022.csv")

# ── 2023 PARSER ───────────────────────────────────────────────────────────────
# Same layout as 2022; numbers may contain spaces (e.g. '1 ,521,648') — clean_num handles it
# Year cols: year_2024, year_2025

def parse_2023():
    pdf_path = r"C:\Users\vince\Documents\GitHub\CIPBD\Dallas\PDF\2023.pdf"
    cip_year = 2023
    year_cols = {2024: 'year_2024', 2025: 'year_2025'}
    sum_fields = ['previous_appropriations', 'spent', 'remaining',
                  'year_2024', 'year_2025', 'project_total']
    str_fields = ['spent', 'remaining']
    records = []
    department = ''

    with pdfplumber.open(pdf_path) as pdf:
        for pg in pdf.pages:
            txt = pg.extract_text() or ''
            tables = pg.extract_tables()
            t = max(tables, key=len) if tables else []
            if not t or not is_data_page(pg, t):
                continue
            dept = get_department(txt)
            if dept:
                department = dept
            for row in t[1:]:
                if is_skip_row(row):
                    continue
                total_cost  = clean_num(row[11])
                future_cost = clean_num(row[10])
                records.append({
                    'cip_year': cip_year, 'source_page': pg.page_number,
                    'department': department,
                    'project_name':            clean_text(row[0]),
                    'project_type':            clean_text(row[1]),
                    'funding_source':          clean_text(row[2]),
                    'address_location':        clean_text(row[3]),
                    'comp_date':               clean_text(row[4]),
                    'previous_appropriations': clean_num(row[5]),
                    'spent':                   clean_num(row[6]),
                    'remaining':               clean_num(row[7]),
                    'year_2024':               clean_num(row[8]),
                    'year_2025':               clean_num(row[9]),
                    'project_total':           total_cost - future_cost,
                })

    merged = merge_projects(records, sum_fields, year_cols, str_fields)
    for rec in merged:
        rec['project_name'], rec['project_id'] = split_project_id(rec['project_name'])

    out = r"C:\Users\vince\Documents\GitHub\CIPBD\Scripts\Dallas\outputs\2023.csv"
    fieldnames = ['cip_year','source_page','department','project_name','project_id','project_type',
              'funding_source','address_location','comp_date',
              'previous_appropriations','spent','remaining',
              'year_2024','year_2025','project_total','start_year','end_year']
    with open(out, 'w', newline='', encoding='utf-8') as f:
        csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore').writeheader()
        csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore').writerows(merged)
    print(f"Raw: {len(records)}  Merged: {len(merged)}  → 2023.csv")

# ── 2024 PARSER ───────────────────────────────────────────────────────────────
# Same layout as 2022/2023; spaces in numbers continue
# Year cols: year_2025, year_2026

def parse_2024():
    pdf_path = r"C:\Users\vince\Documents\GitHub\CIPBD\Dallas\PDF\2024.pdf"
    cip_year = 2024
    year_cols = {2025: 'year_2025', 2026: 'year_2026'}
    sum_fields = ['previous_appropriations', 'spent', 'remaining',
                  'year_2025', 'year_2026', 'project_total']
    str_fields = ['spent', 'remaining']
    records = []
    department = ''

    with pdfplumber.open(pdf_path) as pdf:
        for pg in pdf.pages:
            txt = pg.extract_text() or ''
            tables = pg.extract_tables()
            t = max(tables, key=len) if tables else []
            if not t or not is_data_page(pg, t):
                continue
            dept = get_department(txt)
            if dept:
                department = dept
            for row in t[1:]:
                if is_skip_row(row):
                    continue
                total_cost  = clean_num(row[11])
                future_cost = clean_num(row[10])
                records.append({
                    'cip_year': cip_year, 'source_page': pg.page_number,
                    'department': department,
                    'project_name':            clean_text(row[0]),
                    'project_type':            clean_text(row[1]),
                    'funding_source':          clean_text(row[2]),
                    'address_location':        clean_text(row[3]),
                    'comp_date':               clean_text(row[4]),
                    'previous_appropriations': clean_num(row[5]),
                    'spent':                   clean_num(row[6]),
                    'remaining':               clean_num(row[7]),
                    'year_2025':               clean_num(row[8]),
                    'year_2026':               clean_num(row[9]),
                    'project_total':           total_cost - future_cost,
                })

    merged = merge_projects(records, sum_fields, year_cols, str_fields)
    for rec in merged:
        rec['project_name'], rec['project_id'] = split_project_id(rec['project_name'])

    out = r"C:\Users\vince\Documents\GitHub\CIPBD\Scripts\Dallas\outputs\2024.csv"
    fieldnames = ['cip_year','source_page','department','project_name','project_id','project_type',
              'funding_source','address_location','comp_date',
              'previous_appropriations','spent','remaining',
              'year_2025','year_2026','project_total','start_year','end_year']
    with open(out, 'w', newline='', encoding='utf-8') as f:
        csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore').writeheader()
        csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore').writerows(merged)
    print(f"Raw: {len(records)}  Merged: {len(merged)}  → 2024.csv")

# ── 2025 PARSER ───────────────────────────────────────────────────────────────
# DIFFERENCE: col6 and col7 are SWAPPED vs 2022-2024
#   col6 = Remaining (not Spent)
#   col7 = Spent or Committed (not Remaining)
# No space artifacts in numbers (back to normal formatting)
# Year cols: year_2026, year_2027

def parse_2025():
    pdf_path = r"C:\Users\vince\Documents\GitHub\CIPBD\Dallas\PDF\2025.pdf"
    cip_year = 2025
    year_cols = {2026: 'year_2026', 2027: 'year_2027'}
    sum_fields = ['previous_appropriations', 'spent', 'remaining',
                  'year_2026', 'year_2027', 'project_total']
    str_fields = ['spent', 'remaining']
    records = []
    department = ''

    with pdfplumber.open(pdf_path) as pdf:
        for pg in pdf.pages:
            txt = pg.extract_text() or ''
            tables = pg.extract_tables()
            t = max(tables, key=len) if tables else []
            if not t or not is_data_page(pg, t):
                continue
            dept = get_department(txt)
            if dept:
                department = dept
            for row in t[1:]:
                if is_skip_row(row):
                    continue
                total_cost  = clean_num(row[11])
                future_cost = clean_num(row[10])
                records.append({
                    'cip_year': cip_year, 'source_page': pg.page_number,
                    'department': department,
                    'project_name':            clean_text(row[0]),
                    'project_type':            clean_text(row[1]),
                    'funding_source':          clean_text(row[2]),
                    'address_location':        clean_text(row[3]),
                    'comp_date':               clean_text(row[4]),
                    'previous_appropriations': clean_num(row[5]),
                    'remaining':               clean_num(row[6]),   # ← swapped
                    'spent':                   clean_num(row[7]),   # ← swapped
                    'year_2026':               clean_num(row[8]),
                    'year_2027':               clean_num(row[9]),
                    'project_total':           total_cost - future_cost,
                })

    merged = merge_projects(records, sum_fields, year_cols, str_fields)
    for rec in merged:
        rec['project_name'], rec['project_id'] = split_project_id(rec['project_name'])

    out = r"C:\Users\vince\Documents\GitHub\CIPBD\Scripts\Dallas\outputs\2025.csv"
    fieldnames = ['cip_year','source_page','department','project_name','project_type',
                  'funding_source','address_location','comp_date',
                  'previous_appropriations','spent','remaining',
                  'year_2026','year_2027','project_total','start_year','end_year']
    with open(out, 'w', newline='', encoding='utf-8') as f:
        csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore').writeheader()
        csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore').writerows(merged)
    print(f"Raw: {len(records)}  Merged: {len(merged)}  → 2025.csv")

# parse_2025()
# parse_2024()
# parse_2023()
parse_2022()