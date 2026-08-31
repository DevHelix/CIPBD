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

def rev(s):
    return (str(s) if s else '')[::-1]

def extract_cell_name(cell_words):
    """Sort words by x0 asc, top desc within each x0 group; reverse each word's chars."""
    if not cell_words:
        return ''
    groups = defaultdict(list)
    for w in cell_words:
        groups[round(w['x0'] / 5) * 5].append(w)
    result = []
    for k in sorted(groups):
        for w in sorted(groups[k], key=lambda w: -w['top']):
            result.append(w['text'][::-1])
    return ' '.join(result)

def get_cell_tokens(cell_raw):
    """Get all individual word tokens from a table cell's raw text."""
    lines = [l.strip() for l in str(cell_raw or '').splitlines() if l.strip()]
    tokens = set()
    for line in lines:
        tokens.update(line.split())
    return tokens

def extract_department(txt):
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    dept_words = []
    for l in lines:
        if '.tsE' in l or 'tsiL' in l or l.startswith('YF') or (l and l[0].isdigit()):
            if 'tsiL' in l:
                prefix = l.split('tsiL')[0].strip()
                if prefix:
                    dept_words.append(prefix[::-1])
            break
        dept_words.append(l[::-1])
    dept = ' '.join(reversed(dept_words))
    dept = dept.title().strip()
    dept = re.sub(r'\bAnd\b', '&', dept)
    return dept

def is_data_page(pg, t):
    return (
        pg.rotation == 270
        and len(t) == 12
        and 'tcejorP' in str(t[11][0] or '')
    )

def is_skip_col(t, ci):
    name = clean_text(rev(str(t[11][ci] or '')))
    if not name or name.lower() == 'project':
        return True
    if re.match(r'^total\b', name, re.I):
        return True
    if re.match(r'^department\s+total\b', name, re.I):
        return True
    return False

# Add this function alongside the other helpers
def split_project_id(name):
    m = re.search(r' - ([A-Za-z][A-Za-z_]*\d+|\d{3,})', name)
    if m:
        return name[:m.start()].strip(), m.group(1)
    return name, ''

# 1. Add to SUM_FIELDS
SUM_FIELDS = [
    'previous_appropriations', 'spent', 'remaining',
    'year_2022', 'year_2023',
    'project_total', 'future_cost',
]
YEAR_COLS = {2022: 'year_2022', 2023: 'year_2023'}
STR_FIELDS = ['spent', 'remaining']
NROWS = 12       # 2021 data pages always have 12 field rows
BBOX_INSET = 2   # shrink cell crop to avoid bleeding from adjacent cells

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

def parse_2021():
    pdf_path = r"C:\Users\vince\Documents\GitHub\CIPBD\Dallas\PDF\2021.pdf"
    cip_year = 2021
    records = []
    department = ''

    with pdfplumber.open(pdf_path) as pdf:
        for pg in pdf.pages:
            txt = pg.extract_text() or ''
            tables = pg.extract_tables()
            t = max(tables, key=len) if tables else []

            if not t or not is_data_page(pg, t):
                continue

            dept_candidate = extract_department(txt)
            if dept_candidate:
                department = dept_candidate

            found_tables = pg.find_tables()
            tbl_obj = max(found_tables, key=lambda tb: len(tb.cells)) if found_tables else None

            for ci in range(1, len(t[0])):
                if is_skip_col(t, ci):
                    continue

                # Coordinate-sorted project name extraction
                project_name = None
                if tbl_obj:
                    try:
                        x0, top, x1, bottom = tbl_obj.cells[ci * NROWS + 11]
                        cell_bbox = (x0 + BBOX_INSET, top, x1 - BBOX_INSET, bottom)
                        raw_words = pg.crop(cell_bbox).extract_words(x_tolerance=3, y_tolerance=3)
                        cell_tokens = get_cell_tokens(t[11][ci])
                        cell_words = [w for w in raw_words if w['text'] in cell_tokens]
                        project_name = extract_cell_name(cell_words)
                    except Exception:
                        pass
                if not project_name:
                    project_name = clean_text(rev(str(t[11][ci] or '')))

                total_cost  = clean_num(rev(str(t[0][ci] or '')))
                future_cost = clean_num(rev(str(t[1][ci] or '')))

                records.append({
                    'cip_year':                cip_year,
                    'source_page':             pg.page_number,
                    'department':              department,
                    'project_name':            project_name,
                    'project_type':            clean_text(rev(str(t[10][ci] or ''))),
                    'funding_source':          clean_text(rev(str(t[9][ci]  or ''))),
                    'address_location':        clean_text(rev(str(t[8][ci]  or ''))),
                    'comp_date':               clean_text(rev(str(t[7][ci]  or ''))),
                    'previous_appropriations': clean_num(rev(str(t[6][ci]  or ''))),
                    'spent':                   clean_num(rev(str(t[5][ci]  or ''))),
                    'remaining':               clean_num(rev(str(t[4][ci]  or ''))),
                    'year_2022':               clean_num(rev(str(t[3][ci]  or ''))),
                    'year_2023':               clean_num(rev(str(t[2][ci]  or ''))),
                    'project_total':           total_cost - future_cost,
                    'future_cost':             future_cost,
                })

    print(f"Raw rows before merge: {len(records)}")
    merged = merge_projects(records)
    for rec in merged:
        rec['project_name'], rec['project_id'] = split_project_id(rec['project_name'])
    print(f"Rows after merge:      {len(merged)}")

    out = r"C:\Users\vince\Documents\GitHub\CIPBD\Scripts\Dallas\outputs\2021.csv"
    fieldnames = [
        'cip_year', 'source_page', 'department', 'project_name', 'project_id', 'project_type',
        'funding_source', 'address_location', 'comp_date',
        'previous_appropriations', 'spent', 'remaining',
        'year_2022', 'year_2023',
        'project_total', 'future_cost', 'start_year', 'end_year',
    ]
    with open(out, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(merged)

    print(f"Done: 2021.csv — {len(merged)} projects")

parse_2021()