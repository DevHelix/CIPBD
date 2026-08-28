# 2018

import pdfplumber, csv, re

def clean_num(v):
    v = str(v or '').replace(',', '').replace('$', '').strip()
    if v in ('', '-', '—'): return 0
    try: return int(float(v))
    except: return 0

def field(txt, label, stop):
    m = re.search(label + r'\s+(.+?)(?=' + stop + r'|$)', txt, re.S | re.I)
    return re.sub(r'\s+', ' ', m.group(1)).strip() if m else ''

def parse_page(txt, page_num, cip_year):
    lines = [l for l in txt.splitlines() if l.strip()]

    department   = lines[0].strip() if lines else ''
    project_name, project_id = '', ''
    if len(lines) > 1:
        # Line 1 project name/ID — allow alphanumeric IDs like AP1070
        m = re.match(r'(.+?)\s+([A-Z]{0,3}\d{4,12})\s*$', lines[1].strip())
        if m:
            project_name, project_id = m.group(1).strip(), m.group(2).strip()
        else:
            project_name = lines[1].strip()

    stops = r'(?:Estimated Operating|Project Timeline|Department Contact|Funding Sources)'
    description  = field(txt, r'Project Description', stops)
    timeline     = field(txt, r'Project Timeline',    r'(?:Department Contact|Funding Sources)')
    dept_contact = field(txt, r'Department Contact',  r'Funding Sources')

    # Header — handle both spellings
    header_m = re.search(
        r'Funding Source\s+Begi?ning Balance\s+((?:FY \d{2}\s+)+)3 Year Total', txt
    )
    years = [2000 + int(y) for y in re.findall(r'FY (\d{2})', header_m.group(1))] if header_m else []

    # Parse Total row: "Total $338,178 $800,000 $800,000 $800,000 $2,738,178"
    total_m = re.search(r'^Total\s+(.+)$', txt, re.M)
    amounts = re.findall(r'\$[\d,]+', total_m.group(0)) if total_m else []

    # amounts order: Beginning Balance, FY26, FY27, FY28, 3 Year Total
    prev_approp = clean_num(amounts[0]) if amounts else 0
    year_cols   = {
        f'year_{yr}': clean_num(amounts[i + 1])
        for i, yr in enumerate(years)
        if i + 1 < len(amounts) - 1  # skip last (3 Year Total)
    }
    project_total = prev_approp + sum(year_cols.values())

    return {
        'cip_year':                cip_year,
        'source_page':             page_num,
        'department':              department,
        'project_name':            project_name,
        'project_id':              project_id,
        'previous_appropriations': prev_approp,
        'project_total':           project_total,
        'project_description':     description,
        'project_timeline':        timeline,
        'department_contact':      dept_contact,
        **year_cols,
    }

def write_csv(records, filepath):
    if not records: return
    fixed = [
        'cip_year', 'source_page', 'department', 'project_name', 'project_id',
        'previous_appropriations', 'project_total',
        'project_description', 'project_timeline', 'department_contact',
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
    with pdfplumber.open(pdf_path) as pdf:
        for pg in pdf.pages:
            txt = pg.extract_text() or ''
            if 'Funding Source' not in txt or ('Beginning Balance' not in txt and 'Begining Balance' not in txt):
                continue
            records.append(parse_page(txt, pg.page_number, cip_year))
    write_csv(records, r"C:\Users\vince\Documents\GitHub\CIPBD\Scripts\Long Beach\outputs\\" + f"{cip_year}.csv")
    print(f"Done: {cip_year}.csv — {len(records)} records")

for i in range(2011,2019):
    combine(i)