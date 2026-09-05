import csv, re
import pdfplumber

NUM_RE = re.compile(r'^\(?-?[\d,]+\)?$')

def clean_num(s):
    s = str(s or '').strip().replace(',', '').replace(' ', '')
    if s.startswith('(') and s.endswith(')'):
        s = '-' + s[1:-1]
    if not s or s in ('-', '—', 'N/A', 'n/a', 'TBD'):
        return 0
    try:
        return int(float(s))
    except:
        return 0

def clean_text(s):
    return ' '.join(str(s or '').replace('\n', ' ').split())

PROJECT_ID_RE = re.compile(r'\b(\d{2,}-\d{3,4}\.\d+)\s*$')

LABEL_MAP = {
    'Exp/Enc': 'exp_enc',   'Appn': 'con_appn',
    'FY2008': 'year_2008',  'FY2009': 'year_2009',  'FY2010': 'year_2010',
    'FY2011': 'year_2011',  'FY2012': 'year_2012',  'FY2013': 'year_2013',
    'FY2014': 'year_2014',  'FY2015': 'year_2015',  'FY2016': 'year_2016',
    'FY2017': 'year_2017',  'FY2018': 'year_2018',
    'Total':  'project_total',
}
FY_TOKENS = {f'FY{y}' for y in range(2008, 2019)}

# ---------- geometry helpers ----------

def group_lines(words, tol=2.5):
    """Cluster words into visual lines by their 'top' coordinate."""
    lines = []
    for w in sorted(words, key=lambda w: (w['top'], w['x0'])):
        for ln in lines:
            if abs(ln['top'] - w['top']) <= tol:
                ln['words'].append(w)
                break
        else:
            lines.append({'top': w['top'], 'words': [w]})
    for ln in lines:
        ln['words'].sort(key=lambda w: w['x0'])
        ln['text'] = ' '.join(w['text'] for w in ln['words'])
    lines.sort(key=lambda l: l['top'])
    return lines

def centre(w):
    return (w['x0'] + w['x1']) / 2.0

def header_columns(line):
    """If this line is a financial-table header, return [(field, centre_x), ...]."""
    toks = line['words']
    fy_count = sum(1 for w in toks if w['text'] in FY_TOKENS)
    if fy_count < 2:
        return None                      # not a header row
    cols = []
    for w in toks:
        field = LABEL_MAP.get(w['text'])
        if field:
            cols.append((field, centre(w)))
    return cols or None

def assign_by_x(number_words, cols):
    """Assign each number to the column whose centre is nearest in x."""
    vals = {}
    for w in number_words:
        cx = centre(w)
        field, _ = min(cols, key=lambda c: abs(c[1] - cx))
        vals[field] = clean_num(w['text'])
    return vals

# ---------- page parsing ----------

def parse_text(txt):
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    department   = lines[0] if len(lines) >= 1 else ''
    project_type = lines[1] if len(lines) >= 2 else ''
    project_name = project_id = ''
    if len(lines) >= 3:
        m = PROJECT_ID_RE.search(lines[2])
        if m:
            project_id   = m.group(1)
            project_name = lines[2][:m.start()].strip()
        else:
            project_name = lines[2]
    council_lines = []
    for l in lines[3:]:
        if l.startswith('Council District'):
            council_lines.append(l)
        elif council_lines and not l.startswith('Description'):
            council_lines.append(l)
        elif council_lines:
            break
    address_location = ''
    if council_lines:
        raw = re.sub(r'(?<=\S)\s+(Community Plan:)', r'; \1', ' '.join(council_lines))
        address_location = clean_text(raw)
    desc_m = re.search(r'Description:\s*', txt)
    just_m = re.search(r'Justification:\s*', txt)
    oper_m = re.search(r'Operating Budget Effect:\s*', txt)
    description   = clean_text(txt[desc_m.end():just_m.start()]) if desc_m and just_m else ''
    justification = clean_text(txt[just_m.end():oper_m.start()]) if just_m and oper_m else ''
    return {
        'department': department, 'project_type': project_type,
        'project_name': project_name, 'project_id': project_id,
        'address_location': address_location,
        'project_description': description, 'project_justification': justification,
    }

def get_financial(pg):
    words = pg.extract_words(use_text_flow=False, keep_blank_chars=False)
    if not words:
        return None
    lines = group_lines(words)

    # financial table starts at the 'Expenditures by Revenue Source' banner
    start = next((i for i, ln in enumerate(lines)
                  if 'Expenditures by Revenue Source' in ln['text']), None)
    if start is None:
        return None

    result = {f: 0 for f in set(LABEL_MAP.values())}
    found  = False

    # locate every header row, then the 'Total' data row inside THAT header's block
    hdr_idx = [i for i in range(start, len(lines)) if header_columns(lines[i])]
    for n, hi in enumerate(hdr_idx):
        cols = header_columns(lines[hi])
        stop = hdr_idx[n + 1] if n + 1 < len(hdr_idx) else len(lines)

        for j in range(hi + 1, stop):                 # bounded — no cross-table leakage
            ws = lines[j]['words']
            if not ws or ws[0]['text'] != 'Total':
                continue
            nums = [w for w in ws[1:] if NUM_RE.match(w['text'])]
            if nums:
                result.update(assign_by_x(nums, cols))
                found = True
            break

    if not found:
        return None

    result['previous_appropriations'] = result.pop('exp_enc', 0) + result.pop('con_appn', 0)
    return result

def is_project_page(txt):
    return ('Description:' in txt and 'Justification:' in txt
            and 'Expenditures by Revenue Source' in txt)

YEAR_COLS = {yr: f'year_{yr}' for yr in range(2008, 2019)}

def parse_2007():
    pdf_path = r"C:\Users\vince\Documents\GitHub\CIPBD\San-Diego\PDF\2007.pdf"
    records, bad = [], 0
    with pdfplumber.open(pdf_path) as pdf:
        for pg in pdf.pages:
            txt = pg.extract_text() or ''
            if not is_project_page(txt):
                continue
            info = parse_text(txt)
            fin  = get_financial(pg)
            if fin is None:
                continue

            years  = {col: fin.get(col, 0) for col in YEAR_COLS.values()}
            prev   = fin['previous_appropriations']
            total  = fin.get('project_total', 0)
            computed = prev + sum(years.values())
            residual = computed - total
            if residual != 0:
                bad += 1

            active = [yr for yr, col in YEAR_COLS.items() if years[col] != 0]
            records.append({
                'cip_year': 2007, 'source_page': pg.page_number,
                **info,
                'previous_appropriations': prev,
                'project_total': total,
                **years,
                'start_year': min(active) if active else '',
                'end_year':   max(active) if active else '',
                'computed_total': computed,
                'residual': residual,
            })

    out = r"C:\Users\vince\Documents\GitHub\CIPBD\Scripts\San-Diego\outputs\2007.csv"
    fieldnames = [
        'cip_year', 'source_page', 'department', 'project_type',
        'project_name', 'project_id', 'address_location',
        'previous_appropriations', 'project_total',
        'project_description', 'project_justification',
        *(f'year_{yr}' for yr in range(2008, 2019)),
        'start_year', 'end_year',
        'computed_total', 'residual',
    ]
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        w.writeheader()
        w.writerows(records)

    print(f"Done: {len(records)} projects -> 2007.csv")
    print(f"Residual check: {len(records)-bad} balance, {bad} do not "
          f"({100*bad/len(records):.1f}% off)" if records else "no records")

    for r in records:
        if r['residual'] != 0:
            print(f"  p{r['source_page']:>4}  prev={r['previous_appropriations']:>12,}  "
                  f"computed={r['computed_total']:>13,}  total={r['project_total']:>13,}  "
                  f"resid={r['residual']:>13,}  {r['project_name'][:45]}")

parse_2007()