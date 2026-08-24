import pdfplumber, csv, re, os

def decode_cid(txt):
    return re.sub(r'\(cid:(\d+)\)', lambda m: chr(int(m.group(1)) + 29), txt or '')

def extract_project_id(txt):
    lines = [l.strip() for l in decode_cid(txt).splitlines() if l.strip()]
    if len(lines) > 1:
        m = re.search(r'/\s*([A-Z][A-Z0-9]+)\b', lines[1])
        if m:
            return m.group(1)
    return ''

CSV_DIR = r"C:\Users\vince\Documents\GitHub\CIPBD\San-Diego\CSV"
PDF_DIR = r"C:\Users\vince\Documents\GitHub\CIPBD\San-Diego\PDF"

for year in range(2018, 2026):
    csv_path = os.path.join(CSV_DIR, f"{year}.csv")
    pdf_path = os.path.join(PDF_DIR, f"{year}.pdf")
    if not os.path.exists(csv_path) or not os.path.exists(pdf_path):
        continue

    with open(csv_path, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
        fieldnames = list(csv.DictReader(open(csv_path)).fieldnames)
        if 'project_id' not in fieldnames:
            idx = fieldnames.index('project_name') + 1
            fieldnames.insert(idx, 'project_id')

    if not rows:
        continue

    filled = 0
    with pdfplumber.open(pdf_path) as pdf:
        for row in rows:
            if row.get('project_id'):
                continue
            page_num = int(row['source_page']) - 1
            if page_num >= len(pdf.pages):
                continue
            pid = extract_project_id(pdf.pages[page_num].extract_text() or '')
            if pid:
                row['project_id'] = pid
                filled += 1

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)

    print(f"{year}: filled {filled} project_ids")