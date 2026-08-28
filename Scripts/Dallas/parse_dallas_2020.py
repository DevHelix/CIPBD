# Dallas 2020 CIP PDF parser
import pdfplumber, csv, re

PDF_PATH = r"C:\Users\vince\Documents\GitHub\CIPBD\Dallas\PDF\2020.pdf"
OUT_PATH = r"C:\Users\vince\Documents\GitHub\CIPBD\Dallas\CSV\2020.csv"

# Pages (1-indexed) that belong to Transportation/Street Services
# (no explicit dept header exists in this PDF for this section)
STREET_PAGES = set(range(57, 84))

def clean_num(v):
    v = str(v or '').replace(',', '').replace('$', '').strip()
    if v in ('', '-', '—'): return 0
    try: return int(float(v))
    except: return 0


def is_dept_header(lines):
    """True if this page starts with a department name line."""
    if not lines: return False
    first = lines[0]
    second = lines[1] if len(lines) > 1 else ''
    return (
        len(first) < 50
        and not first[0].isdigit()
        and first not in ('Estimated',)
        and any(kw in second for kw in ('MISSION', 'Project list', 'Project List', 'HIGHLIGHTED'))
    )

def parse_project_table(table, dept, source_page):
    """Extract records from a project-list table."""
    records = []
    # Identify header row (contains 'Project Name')
    header_idx = next((i for i, row in enumerate(table)
                       if any('Project Name' in str(c or '') for c in row)), None)
    if header_idx is None:
        return records

    # Identify column indices from merged 3-row header
    # Row: Project Name | Service Name | Funding Source | Council District | Completion Date | FY 2020-21 | FY 2021-22 | FY 2022-23
    # pdfplumber splits the header across 3 rows; col positions are fixed:
    col_name   = 0
    col_type   = 1
    col_dist   = 3
    col_date   = 4
    col_2021   = 7
    col_2022   = 8
    col_2023   = 9

    data_start = header_idx + 3  # skip 3 header rows

    for row in table[data_start:]:
        if not row or not row[0]: continue
        name = str(row[0] or '').replace('\n', ' ').strip()
        if not name or name.lower().startswith('grand total'): continue

        project_type   = str(row[col_type] or '').replace('\n', ' ').strip() if col_type < len(row) else ''
        council_dist   = str(row[col_dist] or '').replace('\n', ' ').strip() if col_dist < len(row) else ''
        yr_2021        = clean_num(row[col_2021]) if col_2021 < len(row) else 0
        yr_2022        = clean_num(row[col_2022]) if col_2022 < len(row) else 0
        yr_2023        = clean_num(row[col_2023]) if col_2023 < len(row) else 0

        year_vals = {'year_2021': yr_2021, 'year_2022': yr_2022, 'year_2023': yr_2023}
        funded = [yr for yr, val in sorted(year_vals.items()) if val != 0]
        start_year = funded[0].split('_')[1] if funded else ''
        end_year   = funded[-1].split('_')[1] if funded else ''

        project_total  = yr_2021 + yr_2022 + yr_2023
        addr           = f"Council District: {council_dist}" if council_dist and council_dist != '-' else ''

        records.append({
            'cip_year':               2020,
            'project_type':           project_type,
            'source_page':            source_page,
            'department':             dept,
            'project_name':           name,
            'start_year':             start_year,
            'end_year':               end_year,
            'address_location':       addr,
            'previous_appropriations': 0,
            'project_total':          project_total,
            'year_2021':              yr_2021,
            'year_2022':              yr_2022,
            'year_2023':              yr_2023,
        })
    return records

def combine():
    records = []
    current_dept = ''

    with pdfplumber.open(PDF_PATH) as pdf:
        for pg in pdf.pages:
            pg_num = pg.page_number  # 1-indexed
            txt = pg.extract_text() or ''
            lines = [l.strip() for l in txt.splitlines() if l.strip()]

            # Update current department
            if pg_num in STREET_PAGES:
                current_dept = 'Street Services'
            elif is_dept_header(lines):
                current_dept = lines[0]

            # Find project list table
            tables = pg.extract_tables()
            proj_table = next(
                (t for t in tables if any(
                    'Project Name' in str(c or '') for row in t for c in row)),
                None
            )
            if proj_table is None:
                continue

            records.extend(parse_project_table(proj_table, current_dept, pg_num))

    # Write CSV
    fieldnames = ['cip_year', 'project_type', 'source_page', 'department',
                  'project_name', 'start_year', 'end_year', 'address_location',
                  'previous_appropriations', 'project_total',
                  'year_2021', 'year_2022', 'year_2023']
    with open(OUT_PATH, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        w.writeheader()
        w.writerows(records)

    print(f"Done: 2020.csv — {len(records)} records")
    # Department breakdown
    from collections import Counter
    depts = Counter(r['department'] for r in records)
    for d, n in depts.most_common():
        print(f"  {d}: {n}")

combine()
