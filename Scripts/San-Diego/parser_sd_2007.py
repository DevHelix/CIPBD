import csv
import re
import pdfplumber

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

NUM_RE = re.compile(r'^-?[\d,]+$')

def is_num(s):
    return bool(NUM_RE.match(str(s or '').strip().replace(',', '')))

def assign_col(x, midpoints):
    return min(midpoints, key=lambda k: abs(midpoints[k] - x))

FIRST_COL_MARKERS = {
    'Exp/Enc': 'exp_enc',
    'Appn':    'con_appn',
    'FY2008':  'year_2008',
    'FY2009':  'year_2009',
    'FY2010':  'year_2010',
    'FY2011':  'year_2011',
    'FY2012':  'year_2012',
}
SECOND_COL_MARKERS = {
    'FY2013': 'year_2013',
    'FY2014': 'year_2014',
    'FY2015': 'year_2015',
    'FY2016': 'year_2016',
    'FY2017': 'year_2017',
    'FY2018': 'year_2018',
    'Total':  'project_total',
}

GATED_FIRST  = {'year_2009', 'year_2010', 'year_2011', 'year_2012'}
GATED_SECOND = {'year_2013', 'year_2014', 'year_2015', 'year_2016', 'year_2017', 'year_2018'}


def get_financial(pg):
    words = pg.extract_words(x_tolerance=4, y_tolerance=3)
    rows = {}
    for w in words:
        rkey = round(w['top'] / 3) * 3
        rows.setdefault(rkey, []).append(w)

    exp_top = None
    for rkey, rws in rows.items():
        if any(w['text'] == 'Expenditures' for w in rws):
            exp_top = rkey
            break
    if exp_top is None:
        return None

    fin_rows = {k: sorted(v, key=lambda w: w['x0'])
                for k, v in rows.items() if k >= exp_top - 3}

    first_midpoints  = {}
    second_midpoints = {}
    first_total_row      = None
    second_total_row     = None
    first_workcodes_row  = None
    second_workcodes_row = None

    sorted_rkeys = sorted(fin_rows.keys())

    for i, rkey in enumerate(sorted_rkeys):
        rws = fin_rows[rkey]
        texts = [w['text'] for w in rws]
        left  = rws[0]['text'] if rws else ''

        if 'Exp/Enc' in texts or 'FY2008' in texts:
            for w in rws:
                if w['text'] in FIRST_COL_MARKERS:
                    first_midpoints[FIRST_COL_MARKERS[w['text']]] = (w['x0'] + w['x1']) / 2
            for peek_i in [i - 1, i + 1]:
                if 0 <= peek_i < len(sorted_rkeys):
                    peek_rkey = sorted_rkeys[peek_i]
                    if abs(peek_rkey - rkey) <= 9:
                        for w in fin_rows[peek_rkey]:
                            field = FIRST_COL_MARKERS.get(w['text'])
                            if field and field not in first_midpoints:
                                first_midpoints[field] = (w['x0'] + w['x1']) / 2
            continue

        if 'FY2013' in texts:
            for w in rws:
                if w['text'] in SECOND_COL_MARKERS:
                    second_midpoints[SECOND_COL_MARKERS[w['text']]] = (w['x0'] + w['x1']) / 2
            # Peek ±1 row for split column headers (e.g., 'Total' on a slightly different y)
            for peek_i in [i - 1, i + 1]:
                if 0 <= peek_i < len(sorted_rkeys):
                    peek_rkey = sorted_rkeys[peek_i]
                    if abs(peek_rkey - rkey) <= 9:
                        for w in fin_rows[peek_rkey]:
                            field = SECOND_COL_MARKERS.get(w['text'])
                            if field and field not in second_midpoints:
                                second_midpoints[field] = (w['x0'] + w['x1']) / 2
            continue

        if left == 'Total':
            total_words = list(rws)

            # Forward peek: numbers split onto the row(s) below the label
            for j in range(i + 1, min(i + 3, len(sorted_rkeys))):
                next_rkey = sorted_rkeys[j]
                if next_rkey > rkey + 9:
                    break
                next_rws = fin_rows[next_rkey]
                if next_rws and all(is_num(w['text']) for w in next_rws):
                    total_words.extend(next_rws)
                else:
                    break

            # Backward peek: numbers split onto the row immediately above the label
            if i > 0:
                prev_rkey = sorted_rkeys[i - 1]
                if rkey - prev_rkey <= 9:
                    prev_rws = fin_rows[prev_rkey]
                    if prev_rws and all(is_num(w['text']) for w in prev_rws):
                        total_words.extend(prev_rws)

            if first_midpoints and first_total_row is None:
                first_total_row = total_words
            elif second_midpoints and second_total_row is None:
                second_total_row = total_words
            continue

        if left == 'Work':
            if first_total_row is not None and first_workcodes_row is None:
                first_workcodes_row = rws
            elif second_total_row is not None and second_workcodes_row is None:
                second_workcodes_row = rws
            continue

    result = {f: 0 for f in list(FIRST_COL_MARKERS.values()) + list(SECOND_COL_MARKERS.values())}

    def fill_total(total_row, midpoints, label=''):
        if not total_row or not midpoints:
            return
        for w in total_row:
            if w['text'] == 'Total':
                continue
            if is_num(w['text']):
                field = assign_col((w['x0'] + w['x1']) / 2, midpoints)
                result[field] = clean_num(w['text'])
                # if field == 'project_total':
                #     print(f"  [p{pg.page_number}] {label} project_total = {result[field]}")


    fill_total(first_total_row,  first_midpoints)
    fill_total(second_total_row, second_midpoints)

    # if result.get('project_total', 0) == 0:
    #     print(f"  [p{pg.page_number}] MISSING project_total")
    #     print(f"    second_total_row = {[(w['text'], round(w['x0'],1)) for w in second_total_row] if second_total_row else None}")
    #     print(f"    second_midpoints = {second_midpoints}")

    def active_cols(workcodes_row, midpoints, radius=30):
        if not workcodes_row or not midpoints:
            return None
        active = set()
        for w in workcodes_row:
            if w['text'] in ('Work', 'Codes'):
                continue
            if is_num(w['text']):
                continue
            x = (w['x0'] + w['x1']) / 2
            for field, mid in midpoints.items():
                if abs(mid - x) <= radius:
                    active.add(field)
        return active

    first_active  = active_cols(first_workcodes_row,  first_midpoints)
    second_active = active_cols(second_workcodes_row, second_midpoints)

    if first_active is not None:
        for field in GATED_FIRST:
            if field not in first_active:
                result[field] = 0

    if second_active is not None:
        for field in GATED_SECOND:
            if field not in second_active:
                result[field] = 0

    result['previous_appropriations'] = result.pop('exp_enc', 0) + result.pop('con_appn', 0)
    return result


PROJECT_ID_RE = re.compile(r'\b(\d{2,}-\d{3,4}\.\d+)\s*$')

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
        'department':            department,
        'project_type':          project_type,
        'project_name':          project_name,
        'project_id':            project_id,
        'address_location':      address_location,
        'project_description':   description,
        'project_justification': justification,
    }


YEAR_COLS = {
    2008: 'year_2008', 2009: 'year_2009', 2010: 'year_2010',
    2011: 'year_2011', 2012: 'year_2012', 2013: 'year_2013',
    2014: 'year_2014', 2015: 'year_2015', 2016: 'year_2016',
    2017: 'year_2017', 2018: 'year_2018',
}

def is_project_page(txt):
    return ('Description:' in txt
            and 'Justification:' in txt
            and 'Expenditures by Revenue Source' in txt)

def parse_2007():
    pdf_path = r"C:\Users\vince\Documents\GitHub\CIPBD\San-Diego\PDF\2007.pdf"
    cip_year = 2007
    records  = []

    with pdfplumber.open(pdf_path) as pdf:
        for pg in pdf.pages:
            txt = pg.extract_text() or ''
            if not is_project_page(txt):
                continue
            info = parse_text(txt)
            fin  = get_financial(pg)
            if fin is None:
                continue
            active = [yr for yr, col in YEAR_COLS.items() if fin.get(col, 0) != 0]
            records.append({
                'cip_year':               cip_year,
                'source_page':            pg.page_number,
                'department':             info['department'],
                'project_type':           info['project_type'],
                'project_name':           info['project_name'],
                'project_id':             info['project_id'],
                'address_location':       info['address_location'],
                'project_description':    info['project_description'],
                'project_justification':  info['project_justification'],
                'previous_appropriations':fin['previous_appropriations'],
                'project_total':          fin.get('project_total', 0),
                'year_2008':              fin.get('year_2008', 0),
                'year_2009':              fin.get('year_2009', 0),
                'year_2010':              fin.get('year_2010', 0),
                'year_2011':              fin.get('year_2011', 0),
                'year_2012':              fin.get('year_2012', 0),
                'year_2013':              fin.get('year_2013', 0),
                'year_2014':              fin.get('year_2014', 0),
                'year_2015':              fin.get('year_2015', 0),
                'year_2016':              fin.get('year_2016', 0),
                'year_2017':              fin.get('year_2017', 0),
                'year_2018':              fin.get('year_2018', 0),
                'start_year':             min(active) if active else '',
                'end_year':               max(active) if active else '',
            })

    out = r"C:\Users\vince\Documents\GitHub\CIPBD\Scripts\San-Diego\outputs\2007.csv"
    fieldnames = [
        'cip_year', 'source_page', 'department', 'project_type',
        'project_name', 'project_id', 'address_location',
        'previous_appropriations', 'project_total',
        'project_description', 'project_justification',
        'year_2008', 'year_2009', 'year_2010', 'year_2011', 'year_2012',
        'year_2013', 'year_2014', 'year_2015', 'year_2016', 'year_2017', 'year_2018',
        'start_year', 'end_year',
    ]
    with open(out, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(records)

    print(f"Done: {len(records)} projects → 2007.csv")

parse_2007()