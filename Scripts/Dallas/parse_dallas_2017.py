# project_total computed as previous_appropriations + year cols (future_cost excluded)

import csv
import re
import pdfplumber
from collections import defaultdict


def clean_num(v):
    s = str(v or '').strip().lstrip('$').replace(',', '').replace(' ', '')
    if not s or s in ('-', '—', 'N/A', 'n/a', 'TBD'):
        return 0
    try:
        return int(float(s))
    except:
        return 0


def clean_text(v):
    return ' '.join(str(v or '').split())


def extract_department(txt):
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    if not lines:
        return ''
    dept = lines[0]
    # Handle split lines e.g. "CONVENTION AND EVENT SERVICES FACILITIES" / "IMPROVEMENTS"
    if len(lines) > 1 and re.match(r'^IMPROVEMENTS?$|^INITIATIVES?$', lines[1], re.I):
        dept = dept + ' ' + lines[1]
    dept = re.sub(r'\s+CAPITAL IMPROVEMENTS?\s*$', '', dept, flags=re.I)
    dept = re.sub(r'\s+FACILITIES IMPROVEMENTS?\s*$', '', dept, flags=re.I)
    dept = re.sub(r'\s+IMPROVEMENTS?\s*$', '', dept, flags=re.I)
    dept = re.sub(r'\s+INITIATIVES?\s*$', '', dept, flags=re.I)
    return dept.title().strip()


def is_data_page(table):
    if not table or len(table) < 2:
        return False
    return clean_text(str(table[0][0] or '')).lower() == 'project name'


def is_skip_row(row):
    first = clean_text(row[0])
    if not first or first.lower() == 'project name':
        return True
    if re.search(r'^total\b', first, re.I):
        return True
    return False


def parse_row(row, ncols):
    """Return field dict from a data row, handling 12- vs 13-col layout."""
    if ncols >= 13:
        # 0:name 1:service 2:key_focus(skip) 3:council 4:funding
        # 5:budget 6:spent 7:remaining 8:yr1 9:yr2 10:yr3 11:future 12:comp_date
        return dict(
            project_name   = clean_text(row[0]),
            project_type   = clean_text(row[1]),
            address_location = clean_text(row[3]),
            funding_source = clean_text(row[4]),
            previous_appropriations = clean_num(row[5]),
            spent          = clean_num(row[6]),
            remaining      = clean_num(row[7]),
            year_2018      = clean_num(row[8]),
            year_2019      = clean_num(row[9]),
            year_2020      = clean_num(row[10]),
            future_cost    = clean_num(row[11]),
            comp_date      = clean_text(row[12]) if len(row) > 12 else '',
        )
    else:
        # 0:name 1:service 2:council 3:funding
        # 4:budget 5:spent 6:remaining 7:yr1 8:yr2 9:yr3 10:future 11:comp_date
        return dict(
            project_name   = clean_text(row[0]),
            project_type   = clean_text(row[1]),
            address_location = clean_text(row[2]),
            funding_source = clean_text(row[3]),
            previous_appropriations = clean_num(row[4]),
            spent          = clean_num(row[5]),
            remaining      = clean_num(row[6]),
            year_2018      = clean_num(row[7]),
            year_2019      = clean_num(row[8]),
            year_2020      = clean_num(row[9]),
            future_cost    = clean_num(row[10]),
            comp_date      = clean_text(row[11]) if len(row) > 11 else '',
        )


SUM_FIELDS = [
    'previous_appropriations', 'spent', 'remaining',
    'year_2018', 'year_2019', 'year_2020',
    'future_cost', 'project_total',
]
YEAR_COLS = {2018: 'year_2018', 2019: 'year_2019', 2020: 'year_2020'}
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


def parse_2017():
    pdf_path = r"C:\Users\vince\Documents\GitHub\CIPBD\Dallas\PDF\2017.pdf"
    cip_year = 2017
    records = []

    with pdfplumber.open(pdf_path) as pdf:
        for pg in pdf.pages:
            tables = pg.extract_tables()
            if not tables:
                continue
            t = max(tables, key=len)
            if not is_data_page(t):
                continue

            txt = pg.extract_text() or ''
            department = extract_department(txt)
            ncols = len(t[0])

            for row in t[1:]:   # row 0 is header
                if len(row) < 11 or is_skip_row(row):
                    continue
                fields = parse_row(row, ncols)
                if not fields['project_name']:
                    continue
                fields['project_total'] = (
                    fields['previous_appropriations']
                    + fields['year_2018']
                    + fields['year_2019']
                    + fields['year_2020']
                )
                fields['cip_year']    = cip_year
                fields['source_page'] = pg.page_number
                fields['department']  = department
                records.append(fields)

    print(f"Raw rows before merge: {len(records)}")
    merged = merge_projects(records)
    print(f"Rows after merge:      {len(merged)}")

    out = r"C:\Users\vince\Documents\GitHub\CIPBD\Scripts\Dallas\outputs\2017.csv"
    fieldnames = [
        'cip_year', 'source_page', 'department', 'project_name', 'project_type',
        'funding_source', 'address_location', 'comp_date',
        'previous_appropriations', 'spent', 'remaining',
        'year_2018', 'year_2019', 'year_2020', 'future_cost', 'project_total',
        'start_year', 'end_year',
    ]
    with open(out, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(merged)

    print(f"Done: 2017.csv — {len(merged)} projects")


parse_2017()