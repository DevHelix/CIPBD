# 2016

import pdfplumber, csv, re

def clean_num(v):
    v = str(v or '').replace(',', '').replace('$', '').strip()
    if v in ('', '-', '—'): return 0
    if v.startswith('(') and v.endswith(')'): return -int(v[1:-1])
    try: return int(float(v))
    except: return 0

def field(txt, label, stop):
    m = re.search(label + r'\s+(.+?)(?=' + stop + r'|$)', txt, re.S | re.I)
    return re.sub(r'\s+', ' ', m.group(1)).strip() if m else ''

def parse_page(txt, page_num, cip_year):
    lines = [l for l in txt.splitlines() if l.strip()]

    # Title: first line, strip leading "N) "
    project_name = re.sub(r'^\d+\)\s*', '', lines[0].strip()) if lines else ''

    # Department and contact (strip leading "N) " if numbered)
    dept_m = re.search(r'Department:\s*(.+)', txt)
    cont_m = re.search(r'Contact:\s*(.+)', txt)
    department   = dept_m.group(1).strip() if dept_m else ''
    dept_contact = cont_m.group(1).strip() if cont_m else ''

    # Program Number
    id_m = re.search(r'Program Number\s+(\S+)', txt)
    project_id = id_m.group(1).strip() if id_m else ''

    # Description (best-effort — two-column layout causes noise)
    description = field(txt, r'Program Description', r'(?:Work to be initiated|FY\s*\d+\s+New Funding|Program Historical)')
    description = re.sub(r'^[\uf000-\uf0ff\s]+', '', description)  # strip encoded bullets
    description = re.sub(
        r'^\s*(?:Construction|Bid\s*&\s*Award|Crosswalk\s+Installation|Design):\s*'
        r'(?:(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}|\d{4})'
        r'(?:\s*[-–,]\s*(?:(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}|\d{4}))?\s*[-–,]?\s*',
        '', description).strip()
    description = re.sub(r'^(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\s+', '', description).strip()
    description = re.sub(r'^\d{2,4}(?:\s*[–-]\s*\w+\s+\d{4})?\s+', '', description).strip()
    description = re.sub(r'\s*\d+\)\s*$', '', description).strip()

    # FY year from "FY 17 New Funding"
    fy_m = re.search(r'FY\s*(\d+)\s+New Funding', txt)
    fy_year = (2000 + int(fy_m.group(1))) if fy_m else cip_year

    # New Funding total: last "Total $X" before "Program Historical Summary"
    pre_hist = txt.split('Program Historical Summary')[0] if 'Program Historical Summary' in txt else txt
    new_fund_m = re.search(r'\bTotal\s+(\$[\d,]+)\s*$', pre_hist, re.M)
    new_funding = clean_num(new_fund_m.group(1)) if new_fund_m else 0

    # Historical Summary Total row — first dollar amount = Inception Budget
    # Historical Summary Total row — last dollar amount = carryover/balance
    hist = txt.split('Program Historical Summary')[-1] if 'Program Historical Summary' in txt else ''
    hist_total_m = re.search(r'(?m)^Total\s+((?:[\(\$][\d,\)]+\s*)+)', hist)
    if hist_total_m:
        amounts = re.findall(r'\$[\d,]+|\(\$?[\d,]+\)', hist_total_m.group(0))
        prev_approp = clean_num(amounts[-1]) if amounts else 0
    else:
        prev_approp = 0

    # Total Adopted Budget
    tab_m = re.search(r'Total Adopted Budget\s+(\$[\d,]+)', txt)
    project_total = clean_num(tab_m.group(1)) if tab_m else 0

    return {
        'cip_year':                cip_year,
        'source_page':             page_num,
        'department':              department,
        'project_name':            project_name,
        'project_id':              project_id,
        'previous_appropriations': prev_approp,
        'project_total':           project_total,
        'project_description':     description,
        'department_contact':      dept_contact,
        f'year_{fy_year}':         new_funding,
    }

def write_csv(records, filepath):
    if not records: return
    fixed = [
        'cip_year', 'source_page', 'department', 'project_name', 'project_id',
        'previous_appropriations', 'project_total',
        'project_description', 'department_contact',
    ]
    year_cols  = sorted({k for r in records for k in r if k.startswith('year_')})
    fieldnames = fixed + year_cols
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for r in records:
            for col in year_cols: r.setdefault(col, 0)
            writer.writerow(r)

def combine(cip_year):
    pdf_path = r"C:\Users\vince\Documents\GitHub\CIPBD\Long Beach\PDF\\" + f"{cip_year}.pdf"
    records  = []
    seen_ids = set()
    with pdfplumber.open(pdf_path) as pdf:
        for pg in pdf.pages:
            txt = pg.extract_text() or ''
            if ('Funding Sources' not in txt or 'New Funding' not in txt
                    or 'Program Number' not in txt or 'Continued' in txt):
                continue
            rec = parse_page(txt, pg.page_number, cip_year)
            if rec['project_id'] in seen_ids:
                continue
            seen_ids.add(rec['project_id'])
            records.append(rec)
    write_csv(records, r"C:\Users\vince\Documents\GitHub\CIPBD\Scripts\Long Beach\outputs\\" + f"{cip_year}.csv")
    print(f"Done: {cip_year}.csv — {len(records)} records")

combine(2016)