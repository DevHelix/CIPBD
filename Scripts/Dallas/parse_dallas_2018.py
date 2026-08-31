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
    return ' '.join(str(v or '').split())


def rev(s):
    return (str(s) if s else '')[::-1]


def extract_department(txt):
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    dept_lines = []
    for l in lines:
        if l.startswith('YF') or (l and l[0].isdigit()):
            break
        dept_lines.append(rev(l))
    dept = ' '.join(reversed(dept_lines))
    dept = re.sub(r'\s*CAPITAL\s+IMPROVEMENTS?\s*', '', dept, flags=re.I)
    dept = re.sub(r'\s*FACILITIES?\s+IMPROVEMENTS?\s*', '', dept, flags=re.I)
    dept = re.sub(r'\s*IMPROVEMENTS?\s*', '', dept, flags=re.I)
    dept = dept.title().strip()
    # FIX 1: strip spurious "Total" prefix that comes from page bookmarks
    dept = re.sub(r'^Total\s+', '', dept, flags=re.I)
    return dept


def is_data_page(pg, t):
    return (
        pg.rotation == 270
        and len(t) >= 13          # FIX 3: >= instead of == so pages with extra rows still parse
        and 'tegduB' in str(t[0][0] or '')
    )


def is_skip_col(t, ci):
    name = clean_text(rev(str(t[12][ci] or '')))
    if not name:
        return True
    if re.match(r'^total\b', name, re.I):
        return True
    # FIX 2a: drop ACTIVITY category headers
    if name.upper() == 'ACTIVITY':
        return True
    return False


def is_zero_row(rec):
    # FIX 2b: drop category-separator rows where all financials are zero
    financial_fields = [
        'previous_appropriations', 'spent', 'remaining',
        'year_2019', 'year_2020', 'year_2021', 'year_2022', 'year_2023',
        'project_total',
    ]
    return all(rec[f] == 0 for f in financial_fields)


SUM_FIELDS = [
    'previous_appropriations', 'spent', 'remaining',
    'year_2019', 'year_2020', 'year_2021', 'year_2022', 'year_2023',
    'project_total',
]
YEAR_COLS = {
    2019: 'year_2019', 2020: 'year_2020', 2021: 'year_2021',
    2022: 'year_2022', 2023: 'year_2023',
}
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


def parse_2018():
    pdf_path = r"C:\Users\vince\Documents\GitHub\CIPBD\Dallas\PDF\2018.pdf"
    cip_year = 2018
    records = []
    department = ''

    with pdfplumber.open(pdf_path) as pdf:
        for pg in pdf.pages:
            txt = pg.extract_text() or ''
            tables = pg.extract_tables()
            t = max(tables, key=len) if tables else []

            if pg.rotation == 0 and txt.strip():
                candidate = extract_department(txt)
                if candidate:
                    department = candidate

            if not t or not is_data_page(pg, t):
                continue

            dept_candidate = extract_department(txt)
            if dept_candidate:
                department = dept_candidate

            for ci in range(1, len(t[0])):
                if is_skip_col(t, ci):
                    continue
                project_name = clean_text(rev(str(t[12][ci] or '')))
                if not project_name:
                    continue

                prev  = clean_num(rev(str(t[8][ci] or '')))
                yr19  = clean_num(rev(str(t[5][ci] or '')))
                yr20  = clean_num(rev(str(t[4][ci] or '')))
                yr21  = clean_num(rev(str(t[3][ci] or '')))
                yr22  = clean_num(rev(str(t[2][ci] or '')))
                yr23  = clean_num(rev(str(t[1][ci] or '')))
                total = clean_num(rev(str(t[0][ci] or '')))

                rec = {
                    'cip_year':                cip_year,
                    'source_page':             pg.page_number,
                    'department':              department,
                    'project_name':            project_name,
                    'project_type':            clean_text(rev(str(t[11][ci] or ''))),
                    'funding_source':          clean_text(rev(str(t[10][ci] or ''))),
                    'address_location':        clean_text(rev(str(t[9][ci]  or ''))),
                    'comp_date':               '',
                    'previous_appropriations': prev,
                    'spent':                   clean_num(rev(str(t[7][ci] or ''))),
                    'remaining':               clean_num(rev(str(t[6][ci] or ''))),
                    'year_2019':               yr19,
                    'year_2020':               yr20,
                    'year_2021':               yr21,
                    'year_2022':               yr22,
                    'year_2023':               yr23,
                    'project_total':           total,
                }

                # FIX 2b: drop category-separator rows
                if is_zero_row(rec):
                    continue

                records.append(rec)

    merged = merge_projects(records)
    out = r"C:\Users\vince\Documents\GitHub\CIPBD\Scripts\Dallas\outputs\2018.csv"
    fieldnames = [
        'cip_year', 'source_page', 'department', 'project_name', 'project_type',
        'funding_source', 'address_location', 'comp_date',
        'previous_appropriations', 'spent', 'remaining',
        'year_2019', 'year_2020', 'year_2021', 'year_2022', 'year_2023',
        'project_total', 'start_year', 'end_year',
    ]
    with open(out, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(merged)


parse_2018()