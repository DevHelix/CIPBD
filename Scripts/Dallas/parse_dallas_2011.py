# project_total = total estimated cost - future costs; line 132

import csv
import re
import pdfplumber
from collections import defaultdict


def clean_num(v):
    s = str(v or '').strip().replace(',', '').replace(' ', '')
    if not s or s in ('-', '—', 'N/A', 'n/a', 'TBD'):
        return 0
    try:
        return int(float(s))
    except:
        return 0


def clean_text(v):
    return ' '.join(str(v or '').split())


def extract_department(row0_cell):
    s = clean_text(row0_cell)
    s = re.sub(r'\s+CAPITAL IMPROVEMENTS\s*$', '', s, flags=re.I)
    s = re.sub(r'\s+FACILITIES IMPROVEMENTS\s*$', '', s, flags=re.I)
    return s.title().strip()


def is_data_page(table):
    if len(table) < 3:
        return False
    cell = str(table[0][0] or '')
    return bool(re.search(r'IMPROVEMENTS|INITIATIVES|ACQUISITION', cell, re.I))


def is_skip_row(row):
    first = clean_text(row[0])
    if not first:
        return True
    if re.search(r'^total\b|^project$', first, re.I):
        return True
    return False


SUM_FIELDS = [
    'previous_appropriations', 'spent', 'remaining',
    'year_2012', 'year_2013', 'year_2014',
    'future_cost', 'project_total',
]
YEAR_COLS = {2012: 'year_2012', 2013: 'year_2013', 2014: 'year_2014'}
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


def parse_2011():
    pdf_path = r"C:\Users\vince\Documents\GitHub\CIPBD\Dallas\PDF\2011.pdf"
    cip_year = 2011
    records = []

    with pdfplumber.open(pdf_path) as pdf:
        for pg in pdf.pages:
            tables = pg.extract_tables()
            if not tables:
                continue
            t = max(tables, key=len)
            if not is_data_page(t):
                continue

            department = extract_department(t[0][0])

            for row in t[2:]:
                if len(row) < 13 or is_skip_row(row):
                    continue
                project_name = clean_text(row[0])
                if not project_name:
                    continue
                records.append({
                    'cip_year':                cip_year,
                    'source_page':             pg.page_number,
                    'department':              department,
                    'project_name':            project_name,
                    'project_type':            clean_text(row[1]),
                    'funding_source':          clean_text(row[4]),
                    'address_location':        clean_text(row[3]),
                    'comp_date':               clean_text(row[13]) if len(row) > 13 else '',
                    'previous_appropriations': clean_num(row[5]),
                    'spent':                   clean_num(row[6]),
                    'remaining':               clean_num(row[7]),
                    'year_2012':               clean_num(row[8]),
                    'year_2013':               clean_num(row[9]),
                    'year_2014':               clean_num(row[10]),
                    'future_cost':             clean_num(row[11]),
                    'project_total':           clean_num(row[12]) - clean_num(row[11]),  # strip future_cost
                })

    print(f"Raw rows before merge: {len(records)}")
    merged = merge_projects(records)
    print(f"Rows after merge:      {len(merged)}")

    out = r"C:\Users\vince\Documents\GitHub\CIPBD\Scripts\Dallas\outputs\2011.csv"
    fieldnames = [
        'cip_year', 'source_page', 'department', 'project_name', 'project_type',
        'funding_source', 'address_location', 'comp_date',
        'previous_appropriations', 'spent', 'remaining',
        'year_2012', 'year_2013', 'year_2014', 'future_cost', 'project_total',
        'start_year', 'end_year',
    ]
    with open(out, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(merged)

    print(f"Done: 2011.csv — {len(merged)} projects")


parse_2011()