"""
Retroactively fills project_description and project_justification
in an existing San Diego CIP CSV using the source PDF.
"""

import pdfplumber
import csv
import re

PDF_DIR = r"C:\Users\vince\Documents\GitHub\CIPBD\San-Diego\PDF"
CSV_DIR = r"C:\Users\vince\Documents\GitHub\CIPBD\Scripts\San-Diego\outputs"


def extract_field(text: str, label: str) -> str:
    next_labels = r'(?:Justification|Expenditure|Operating Budget|Relationship|Schedule|Summary)'
    m = re.search(label + r'\s*:\s*(.+?)(?=' + next_labels + r'|$)', text, re.S | re.I)
    if m:
        return re.sub(r'\s+', ' ', m.group(1)).strip()
    return ''


def backfill(cip_year):
    pdf_path = rf"{PDF_DIR}\{cip_year}.pdf"
    csv_path = rf"{CSV_DIR}\{cip_year}.csv"

    # Index PDF pages by page number for fast lookup
    page_texts = {}
    with pdfplumber.open(pdf_path) as pdf:
        for pg in pdf.pages:
            txt       = pg.extract_text() or ''
            mid_x     = pg.width / 2
            left_text = pg.within_bbox((0, 0, mid_x, pg.height)).extract_text() or ''
            right_text= pg.within_bbox((mid_x, 0, pg.width, pg.height)).extract_text() or ''
            page_texts[pg.page_number] = (left_text, right_text)

    # Read CSV, fill missing fields, write back
    with open(csv_path, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    fieldnames = list(rows[0].keys()) if rows else []

    for row in rows:
        if row.get('project_description') and row.get('project_justification'):
            continue  # already populated
        page_num = int(row['source_page'])
        if page_num not in page_texts:
            continue
        left_text, right_text = page_texts[page_num]
        if not row.get('project_description'):
            row['project_description'] = extract_field(left_text, 'Description')
        if not row.get('project_justification'):
            row['project_justification'] = (
                extract_field(left_text, 'Justification')
                or extract_field(right_text, 'Justification')
            )

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done: {cip_year}.csv")


backfill(2020)
