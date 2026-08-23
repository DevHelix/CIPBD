# 2009 San Diego CIP PDF parser

import pdfplumber
import csv
import re

def clean_num(v):
    v = str(v or '').replace(',', '').replace('$', '').strip()
    if v in ('', '-', '—'): return 0
    if v.startswith('(') and v.endswith(')'): return -int(v[1:-1])
    try: return int(float(v))
    except: return 0

def extract_field(text, label):
    stop = r'(?:Justification|Expenditure|Operating Budget|Relationship|Schedule|Summary)'
    m = re.search(label + r'\s*:\s*(.+?)(?=' + stop + r'|$)', text, re.S | re.I)
    return re.sub(r'\s+', ' ', m.group(1)).strip() if m else ''

def parse_text(txt):
    # Header lines always appear before "Council District:" regardless of left/right placement
    header_part  = re.split(r'Council District:|Description:', txt, maxsplit=1)[0]
    header_lines = [l.strip() for l in header_part.splitlines() if l.strip()]

    department   = header_lines[0] if len(header_lines) > 0 else ''
    project_type = header_lines[1] if len(header_lines) > 1 else ''
    project_name, project_id = '', ''
    if len(header_lines) > 2:
        m = re.match(r'(.+?)\s+\d{2}-\d{3,4}(?:\.\d+)?\s*/\s*([A-Z][\w.-]+)\s*$', header_lines[2])
        if m:
            project_name, project_id = m.group(1).strip(), m.group(2).strip()
        else:
            m2 = re.match(r'(.+?)\s+(\d{2}-\d{3,4}(?:\.\d+)?)\s*$', header_lines[2])
            if m2:
                project_name, project_id = m2.group(1).strip(), m2.group(2).strip()
            else:
                project_name = header_lines[2]

    cd_m = re.search(r'Council District\s*:\s*(.+?)(?=Community|Priority|\n)', txt)
    cp_m = re.search(r'Community Plan(?:ning)?\s*:\s*(.+?)(?=Project|Priority|Description|\n|$)', txt)

    return {
        'department':            department,
        'project_type':          project_type,
        'project_name':          project_name,
        'project_id':            project_id,
        'address_location':      '; '.join(filter(None, [
            'Council District: ' + cd_m.group(1).strip() if cd_m else '',
            'Community Plan: '   + cp_m.group(1).strip() if cp_m else '',
        ])),
        'project_description':   extract_field(txt, 'Description'),
        'project_justification': extract_field(txt, 'Justification'),
    }

def parse_table(tables):
    # Flatten all matching tables into one row list
    table = []
    for t in tables:
        table.extend([[str(c or '').replace('\n', ' ').strip() for c in row] for row in t])
    
    year_cols = {}; prev_approp = 0

    for idx, row in enumerate(table):
        c0 = row[0]

        # Section 1
        if 'Exp/Enc' in c0:
            fy_single = re.search(r'FY(20\d{2})', row[1]) if len(row) > 1 else None
            fy_multi  = re.findall(r'FY(20\d{2})', row[2]) if len(row) > 2 else []
            for r in table[idx + 1:]:
                if r[0].lower().startswith('total'):
                    prev_approp = sum(clean_num(n) for n in re.findall(r'[\d,]+', r[0][5:]))
                    if fy_single and len(r) > 1:
                        year_cols[f'year_{fy_single.group(1)}'] = clean_num(r[1])
                    if fy_multi and len(r) > 2:
                        vals = re.findall(r'[\d,]+', r[2])
                        for k, yr in enumerate(fy_multi):
                            if k < len(vals):
                                year_cols[f'year_{yr}'] = year_cols.get(f'year_{yr}', 0) + clean_num(vals[k])
                    break
                if 'Revenue Source' in r[0] and r[0] != c0:
                    break

        # Section 2
        elif 'Revenue Source' in c0 and 'FY20' in c0:
            # Years followed by or preceded by a dash = range endpoints
            range_yrs = set()
            # Range end: year preceded by a dash
            for m in re.finditer(r'[-–]\s*FY(20\d{2})', c0):
                range_yrs.add(m.group(1))
            # Range start: orphaned year before "Revenue Source" (two-row header artifact)
            pre_src = c0[:c0.find('Revenue Source')]
            for m in re.finditer(r'FY(20\d{2})', pre_src):
                range_yrs.add(m.group(1))

            has_range        = bool(range_yrs)
            has_unidentified = bool(re.search(r'Unidentified', c0[c0.find('Revenue Source'):], re.I))
            fy_years         = [yr for yr in re.findall(r'FY(20\d{2})', c0) if yr not in range_yrs]

            for r in table[idx + 1:]:
                if r[0].lower().startswith('total'):
                    parts   = r[0].split()
                    vals    = [p for p in parts[1:] if re.search(r'\d', p)]
                    val_idx = 0
                    # Map values in header order; last val is the "Total" column — skip it
                    for yr in fy_years:
                        if val_idx < len(vals) - 1:
                            year_cols[f'year_{yr}'] = year_cols.get(f'year_{yr}', 0) + clean_num(vals[val_idx])
                            val_idx += 1
                    if has_range and val_idx < len(vals) - 1:
                        year_cols['future_cost'] = year_cols.get('future_cost', 0) + clean_num(vals[val_idx])
                        val_idx += 1
                    if has_unidentified and val_idx < len(vals) - 1:
                        year_cols['unidentified_funding'] = year_cols.get('unidentified_funding', 0) + clean_num(vals[val_idx])
                    break

    return year_cols, prev_approp


def write_csv(records, filepath):
    if not records: return
    fixed = [
        'cip_year', 'project_type', 'source_page', 'department',
        'project_name', 'project_id', 'start_year', 'end_year', 'address_location',
        'previous_appropriations', 'project_total',
        'project_description', 'project_justification',
    ]
    dyn = sorted({k for r in records for k in r
                  if k.startswith('year_') or k in ('future_cost', 'unidentified_funding')})
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fixed + dyn, extrasaction='ignore')
        w.writeheader()
        for r in records:
            for col in dyn: r.setdefault(col, 0)
            w.writerow(r)


def combine(cip_year):
    pdf_path = rf"C:\Users\vince\Documents\GitHub\CIPBD\San-Diego\PDF\{cip_year}.pdf"
    records  = []

    with pdfplumber.open(pdf_path) as pdf:
        for pg in pdf.pages:
            txt = pg.extract_text() or ''
            if 'Justification' not in txt:
                continue

            pg_tables = pg.extract_tables()
            matching = [
                t for t in pg_tables if any(
                    'Revenue Source' in str(c or '') or 'Expenditures by Revenue' in str(c or '')
                    for row in t for c in row
                )
            ]
            if not matching:
                continue

            text = parse_text(txt)
            yc, pa = parse_table(matching)
            pt         = pa + sum(yc.values())

            year_keys  = sorted(k for k in yc if k.startswith('year_'))

            start_year = next((k.split('_')[1] for k in year_keys if yc[k] != 0), '')
            end_year   = next((k.split('_')[1] for k in reversed(year_keys) if yc[k] != 0), '')

            records.append({
                'cip_year':                cip_year,
                'source_page':             pg.page_number,
                'start_year':              start_year,
                'end_year':                end_year,
                'previous_appropriations': pa,
                'project_total':           pt,
                **text,
                **yc,
            })

    out = rf"C:\Users\vince\Documents\GitHub\CIPBD\Scripts\San-Diego\outputs\{cip_year}.csv"
    write_csv(records, out)
    print(f"Done: {cip_year}.csv — {len(records)} records")


combine("2009")