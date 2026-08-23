# <= 2016

import pdfplumber
import csv
import re

def clean_num(v):
    v = str(v or '').replace(',', '').replace('$', '').strip()
    if v in ('', '-', '—'): return 0
    if v.startswith('(') and v.endswith(')'): return -int(v[1:-1])
    try: return int(float(v))
    except: return 0

def extract_field(text: str, label: str) -> str:
    next_labels = r'(?:Justification|Expenditure|Operating Budget|Relationship|Schedule|Summary)'
    m = re.search(label + r'\s*:\s*(.+?)(?=' + next_labels + r'|$)', text, re.S | re.I)
    if m:
        return re.sub(r'\s+', ' ', m.group(1)).strip()
    return ''

def extract_text_fields(txt, left_text, right_text):
    """Extract all free-text fields from page text."""
    lines = left_text.splitlines()
    department   = lines[0].strip() if lines else ''
    name_id      = re.match(r'(.+?)\s*/\s*([A-Z]\w+)', lines[1]) if len(lines) > 1 else None
    project_name = name_id.group(1).strip() if name_id else ''
    project_id   = name_id.group(2).strip() if name_id else ''
    project_type = right_text.splitlines()[0].strip() if right_text else ''

    cd_m  = re.search(r'Council District\s*:\s*(.+?)(?=Community|Priority|\n)', txt)
    cp_m  = re.search(r'Community Plan(?:ning)?\s*:\s*(.+?)(?=Project|Priority|\n)', txt)
    dur_m = re.search(r'Duration\s*:\s*(\d{4})\s*[-–]\s*(\d{4})', txt)

    address_location = '; '.join(filter(None, [
        'Council District: ' + cd_m.group(1).strip() if cd_m else '',
        'Community Plan: '   + cp_m.group(1).strip() if cp_m else '',
    ]))
    start_year = dur_m.group(1) if dur_m else ''
    end_year   = dur_m.group(2) if dur_m else ''

    description   = extract_field(left_text, 'Description')
    justification = extract_field(left_text, 'Justification') or extract_field(right_text, 'Justification')

    return {
        'department':        department,
        'project_name':      project_name,
        'project_id':        project_id,
        'project_type':      project_type,
        'address_location':  address_location,
        'start_year':        start_year,
        'end_year':          end_year,
        'project_description':       description,
        'project_justification':     justification,
    }

def extract_table_fields(pg_table):
    if not pg_table or len(pg_table) < 2:
        return {}, 0, 0

    table      = [[str(c or '').replace('\n', ' ').strip() for c in row] for row in pg_table]
    header_idx = next((i for i, r in enumerate(table) if any('Fund Name' in cell for cell in r)), None)
    total_row  = next((r for r in table if r[0].lower() == 'total'), None)

    if header_idx is None or total_row is None:
        return {}, 0, 0

    if header_idx > 0:
        above = table[header_idx - 1]
        header = [
            f"{above[i]} {table[header_idx][i]}".strip() if above[i] else table[header_idx][i]
            for i in range(len(table[header_idx]))
        ]
    else:
        header = table[header_idx]

    # Fix 2016 PDF total row shift: Exp/Enc value lands at Fund No position (col 1),
    # leaving col 2 (Exp/Enc column) empty. Swap to restore alignment.
    if len(total_row) > 2 and clean_num(total_row[1]) != 0 and total_row[2] == '':
        total_row[1], total_row[2] = total_row[2], total_row[1]

    year_cols     = {}
    prev_approp   = 0
    project_total = 0
    last_fy_year  = None

    for i, h in enumerate(header):
        if i >= len(total_row):
            break
        val = clean_num(total_row[i])

        if re.search(r'Exp|Con\s*App', h, re.I):
            prev_approp += val
        elif re.search(r'Project\s*Total|^Total$|^Project$', h, re.I):
            project_total = val
        elif m := re.search(r'FY\s*(20\d{2})', h):
            last_fy_year = int(m.group(1))
            year_cols[f'year_{last_fy_year}'] = year_cols.get(f'year_{last_fy_year}', 0) + val
        elif re.search(r'Future', h, re.I):
            future_key = f'year_{last_fy_year + 1}' if last_fy_year else 'future_cost'
            year_cols[future_key] = year_cols.get(future_key, 0) + val
        elif re.search(r'Unidentified', h, re.I):
            year_cols['unidentified_funding'] = year_cols.get('unidentified_funding', 0) + val

    return year_cols, prev_approp, project_total


def write_csv(records, filepath):
    """
    Writes a list of project dicts to CSV.
    Year columns are discovered dynamically and sorted.
    """
    if not records:
        return

    fixed_cols = [
        'cip_year', 'project_type', 'source_page', 'department',
        'project_name', 'start_year', 'end_year', 'address_location',
        'previous_appropriations', 'project_total',
        'project_description', 'project_justification',
    ]
    year_cols = sorted({
        k for r in records for k in r
        if k.startswith('year_') or k in ('future_cost', 'unidentified_funding')
    })
    fieldnames = fixed_cols + year_cols

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for r in records:
            # Fill missing year cols with 0
            for col in year_cols:
                r.setdefault(col, 0)
            writer.writerow(r)

def combine(cip_year):

    pdf_path = r"C:\Users\vince\Documents\GitHub\CIPBD\San-Diego\PDF\\" + f"{cip_year}.pdf"
    records = []

    with pdfplumber.open(pdf_path) as pdf:
        for pg in pdf.pages:
            txt       = pg.extract_text() or ''
            pg_tables = pg.extract_tables()
            pg_table  = next(
                (t for t in pg_tables if any('Fund Name' in str(cell or '') for row in t for cell in row)),
                None
            )

            if not (pg_table and "Duration" in txt and "Justification" in txt):
                continue

            mid_x      = pg.width / 2
            left_text  = pg.within_bbox((0, 0, mid_x, pg.height)).extract_text() or ''
            right_text = pg.within_bbox((mid_x, 0, pg.width, pg.height)).extract_text() or ''

            text_fields              = extract_text_fields(txt, left_text, right_text)
            text_fields['source_page'] = pg.page_number
            year_cols, prev_approp, project_total = extract_table_fields(pg_table)

            year_keys  = sorted(k for k in year_cols if k.startswith('year_'))
            start_year = next((k.split('_')[1] for k in year_keys if year_cols[k] != 0), '')
            end_year   = next((k.split('_')[1] for k in reversed(year_keys) if year_cols[k] != 0), '')

            record = {
                'cip_year':                cip_year,
                'project_type':            text_fields.get('project_type', ''),
                'source_page':             pg.page_number,
                'department':              text_fields.get('department', ''),
                'project_name':            text_fields.get('project_name', ''),
                'start_year':              start_year,
                'end_year':                end_year,
                'address_location':        text_fields.get('address_location', ''),
                'previous_appropriations': prev_approp,
                'project_total':           project_total,
                'project_description':             text_fields.get('project_description', ''),
                'project_justification':           text_fields.get('project_justification', ''),
            }
            record.update(year_cols)
            records.append(record)

    write_csv(records, r"C:\Users\vince\Documents\GitHub\CIPBD\Scripts\San-Diego\outputs\\" + f"{cip_year}.csv")

for i in range(2007,2008):
    combine(i)