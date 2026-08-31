import csv
import re
import pdfplumber
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
        pg.rotation == 90
        and len(t) > 1
        and 'Projects' in str(t[0][0] or '')
    )

def is_skip_row(row):
    name = clean_text(str(row[0] or ''))
    if not name:
        return True
    if re.match(r'^total\b', name, re.I):
        return True
    return False

SUM_FIELDS = [
    'previous_appropriations', 'spent', 'remaining',
    'year_2020', 'year_2021', 'year_2022',
    'project_total',
]
YEAR_COLS = {2020: 'year_2020', 2021: 'year_2021', 2022: 'year_2022'}
STR_FIELDS = ['spent', 'remaining']

def stringify(record):
    for f in STR_FIELDS:
        record[f] = str(record[f])
    return record

def merge_projects(records):
    groups = defaultdict(list)
    for r in records:
        key = (r['project_name'], r['department'])
        groups[key].append(r)

    merged = []
    for (project_name, department), rows in groups.items():
        base = dict(rows[0])
        for field in SUM_FIELDS:
            base[field] = sum(r[field] for r in rows)
        seen, sources = set(), []
        for r in rows:
            fs = r['funding_source']
            if fs and fs not in seen:
                sources.append(fs)
                seen.add(fs)
        base['funding_source'] = ' / '.join(sources)
        pages = sorted(set(r['source_page'] for r in rows))
        base['source_page'] = ', '.join(str(p) for p in pages)
        active = [yr for yr, col in YEAR_COLS.items() if base[col] != 0]
        base['start_year'] = min(active) if active else ''
        base['end_year']   = max(active) if active else ''
        merged.append(stringify(base))
    return merged

def split_project_id(name):
    m = re.search(r' - ([A-Za-z][A-Za-z_]*\d+|\d{3,})$', name)
    if m:
        return name[:m.start()].strip(), m.group(1)
    return name, ''

def parse_2019():
    pdf_path = r"C:\Users\vince\Documents\GitHub\CIPBD\Dallas\PDF\2019.pdf"
    cip_year = 2019
    records = []
    department = ''

    with pdfplumber.open(pdf_path) as pdf:
        for pg in pdf.pages:
            txt = pg.extract_text() or ''
            tables = pg.extract_tables()
            t = max(tables, key=len) if tables else []

            if not t or not is_data_page(pg, t):
                continue

            dept_candidate = get_department(txt)
            if dept_candidate:
                department = dept_candidate

            for row in t[1:]:  # skip header row
                if is_skip_row(row):
                    continue

                records.append({
                    'cip_year':                cip_year,
                    'source_page':             pg.page_number,
                    'department':              department,
                    'project_name':            clean_text(str(row[0] or '')),
                    'project_type':            clean_text(str(row[1] or '')),
                    'funding_source':          clean_text(str(row[2] or '')),
                    'address_location':        clean_text(str(row[3] or '')),
                    'comp_date':               clean_text(str(row[4] or '')),
                    'previous_appropriations': clean_num(row[5]),
                    'spent':                   clean_num(row[6]),
                    'remaining':               clean_num(row[7]),
                    'year_2020':               clean_num(row[8]),
                    'year_2021':               clean_num(row[9]),
                    'year_2022':               clean_num(row[10]),
                    'project_total':           clean_num(row[11]),
                })

    print(f"Raw rows before merge: {len(records)}")
    merged = merge_projects(records)
    for rec in merged:
        rec['project_name'], rec['project_id'] = split_project_id(rec['project_name'])
    print(f"Rows after merge:      {len(merged)}")

    out = r"C:\Users\vince\Documents\GitHub\CIPBD\Scripts\Dallas\outputs\2019.csv"
    fieldnames = [
        'cip_year', 'source_page', 'department', 'project_name', 'project_id', 'project_type',
        'funding_source', 'address_location', 'comp_date',
        'previous_appropriations', 'spent', 'remaining',
        'year_2020', 'year_2021', 'year_2022',
        'project_total', 'start_year', 'end_year',
    ]
    with open(out, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(merged)

    print(f"Done: 2019.csv — {len(merged)} projects")

parse_2019()