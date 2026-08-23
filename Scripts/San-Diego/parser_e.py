# 2017 San Diego CIP PDF parser
import pdfplumber, csv, re

def decode_cid(txt):
    return re.sub(r'\(cid:(\d+)\)', lambda m: chr(int(m.group(1)) + 29), txt or '')

pdf_path = r"C:\Users\vince\Documents\GitHub\CIPBD\San-Diego\PDF\2017.pdf"
with pdfplumber.open(pdf_path) as pdf:
    for pg in pdf.pages:
        txt = decode_cid(pg.extract_text())
        if 'Justification' not in txt or 'Fund Name' not in txt:
            continue
        pg_tables = pg.extract_tables()
        pg_table = next((t for t in pg_tables if any(
            'Fund Name' in decode_cid(str(c or '')) for row in t for c in row)), None)
        if not pg_table:
            continue
        print(f"=== Page {pg.page_number} ===")
        for i, row in enumerate(pg_table[:5]):
            print(f"  Row {i}: {[decode_cid(str(c or '')).replace(chr(10),' ')[:30] for c in row]}")
        break

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
    lines = [l for l in txt.splitlines() if l.strip()]

    # Line 0: department only
    department = lines[0].strip() if lines else ''

    # Line 1: "Project Name / ID          Project Type"
    project_name, project_id, project_type = '', '', ''
    if len(lines) > 1:
        parts = re.split(r'\s{3,}', lines[1].strip())
        left = parts[0].strip()
        project_type = parts[-1].strip() if len(parts) > 1 else ''
        m = re.match(r'(.+?)\s*/\s*([A-Z0-9]+)\s*$', left)
        if m:
            project_name, project_id = m.group(1).strip(), m.group(2).strip()
        else:
            project_name = left

    dur_m = re.search(r'Duration\s*:\s*(\d{4})\s*[-–]\s*(\d{4})', txt)
    start_year = dur_m.group(1) if dur_m else ''
    end_year   = dur_m.group(2) if dur_m else ''

    cd_m = re.search(r'Council District\s*:\s*(.+?)(?=Community|Priority|\n)', txt)
    cp_m = re.search(r'Community Plan(?:ning)?\s*:\s*(.+?)(?=Project|Priority|Description|\n|$)', txt)

    return {
        'department': department, 'project_type': project_type,
        'project_name': project_name, 'project_id': project_id,
        'start_year': start_year, 'end_year': end_year,
        'address_location': '; '.join(filter(None, [
            'Council District: ' + cd_m.group(1).strip() if cd_m else '',
            'Community Plan: ' + cp_m.group(1).strip() if cp_m else '',
        ])),
        'project_description': extract_field(txt, 'Description'),
        'project_justification': extract_field(txt, 'Justification'),
    }

def parse_table(pg_table):
    table = [[decode_cid(str(c or '')).replace('\n', ' ').strip() for c in row] for row in pg_table]

    header_idx = next((i for i, row in enumerate(table)
                       if any('Fund Name' in (c or '') for c in row)), None)
    if header_idx is None:
        return {}, 0

    # Merge two-row header
    row0 = table[header_idx]
    row1 = table[header_idx + 1] if header_idx + 1 < len(table) else [''] * len(row0)
    headers = [(row0[i] + ' ' + (row1[i] if i < len(row1) else '')).strip()
               for i in range(len(row0))]

    # col_map: key -> list of indices
    col_map = {}
    for i, h in enumerate(headers):
        if not h: continue
        if re.search(r'Exp.*Enc', h, re.I):
            col_map.setdefault('exp_enc', []).append(i)
        elif re.search(r'Con\s*Appn', h, re.I):
            col_map.setdefault('con_appn', []).append(i)
        elif re.search(r'Future\s*FY', h, re.I):
            col_map.setdefault('unidentified_funding', []).append(i)  # merged
        elif re.search(r'Unidentified', h, re.I):
            col_map.setdefault('unidentified_funding', []).append(i)
        elif re.search(r'Project\s*Total', h, re.I):
            col_map.setdefault('_skip', []).append(i)
        elif re.search(r'Fund\s*(No|Name)', h, re.I):
            pass
        else:
            fy_m = re.search(r'FY\s*(20\d{2})', h)
            if fy_m:
                col_map.setdefault(f'year_{fy_m.group(1)}', []).append(i)  # anticipated merged

    # Use Total row
    total_row = None
    for row in table[header_idx + 2:]:
        if row and (row[0] or '').strip().lower().startswith('total'):
            total_row = row
            break

    if total_row is None:
        return {}, 0

    sums = {}
    for key, indices in col_map.items():
        if key == '_skip': continue
        sums[key] = sum(clean_num(total_row[idx]) for idx in indices if idx < len(total_row))

    prev_approp = sums.pop('exp_enc', 0) + sums.pop('con_appn', 0)
    return sums, prev_approp

def write_csv(records, filepath):
    if not records: return
    fixed = ['cip_year', 'project_type', 'source_page', 'department',
             'project_name', 'project_id', 'start_year', 'end_year', 'address_location',
             'previous_appropriations', 'project_total',
             'project_description', 'project_justification']
    fixed_set = set(fixed)
    dyn = sorted({k for r in records for k in r if k not in fixed_set})
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fixed + dyn, extrasaction='ignore')
        w.writeheader()
        for r in records:
            for col in dyn: r.setdefault(col, 0)
            w.writerow(r)

def combine(cip_year):
    pdf_path = rf"C:\Users\vince\Documents\GitHub\CIPBD\San-Diego\PDF\{cip_year}.pdf"
    records = []
    with pdfplumber.open(pdf_path) as pdf:
        for pg in pdf.pages:
            txt = decode_cid(pg.extract_text())
            if 'Justification' not in txt or 'Fund Name' not in txt:
                continue
            pg_tables = pg.extract_tables()
            pg_table = next((t for t in pg_tables if any(
                'Fund Name' in decode_cid(str(c or '')) for row in t for c in row)), None)
            if not pg_table:
                continue
            text = parse_text(txt)
            yc, pa = parse_table(pg_table)
            pt = pa + sum(yc.values())

            # Derive start/end year from first/last funded year column
            funded_years = sorted(
                int(k.split('_')[1]) for k, v in yc.items()
                if k.startswith('year_') and v != 0
            )
            start_year = str(funded_years[0]) if funded_years else ''
            end_year   = str(funded_years[-1]) if funded_years else ''

            records.append({
                'cip_year': cip_year, 'source_page': pg.page_number,
                'previous_appropriations': pa, 'project_total': pt,
                'start_year': start_year, 'end_year': end_year,
                **{k: v for k, v in text.items() if k not in ('start_year', 'end_year')},
                **yc,
            })
            
    out = rf"C:\Users\vince\Documents\GitHub\CIPBD\Scripts\San-Diego\outputs\{cip_year}.csv"
    write_csv(records, out)
    print(f"Done: {cip_year}.csv — {len(records)} records")

for year in range(2017, 2018):
    combine(year)