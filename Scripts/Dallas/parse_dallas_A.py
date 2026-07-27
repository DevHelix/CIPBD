"""
parse_dallas_A.py  — Parser for Dallas CIP Format A (2007–2016)

Column layout (in table):
  0  Project name
  1  Service
  2  Key Focus Area
  3  Council District
  4  Funding Source
  5  Budget as of [date]       → previous_appropriations
  6  Spent or Committed
  7  Remaining as of [date]
  8  FY YYYY-YY  (y1)
  9  FY YYYY-YY  (y2)
  10 FY YYYY-YY  (y3)
  11 Future Cost               → y4
  12 Total Estimated Cost      → project_total
  13 In Service Date           → end_year

Department comes from the ALL-CAPS banner row (row[0] of each table page).
Project IDs are extracted from the " - XXXX" suffix where present, otherwise None.
"""

import pdfplumber
import csv
import re

OUTPUT_DIR = r"C:\Users\vince\Documents\GitHub\CIPBD\Scripts\Dallas\outputs\\"
PDF_DIR    = r"C:\Users\vince\Documents\GitHub\CIPBD\Dallas\PDF\\"


class ParserA:

    def __init__(self, cip_year):
        self.cip_year = cip_year
        self.column_headers = [
            'cip_year', 'project_type', 'source_page', 'department',
            'project_name', 'project_id', 'start_year', 'end_year',
            'previous_appropriations', 'project_total',
        ]
        self.headers  = []   # raw table header row
        self.cleaned  = []   # list of cleaned rows (still in original column order + appended fields)
        self.years    = {}   # maps raw header string → 4-digit year string
        self.final    = []   # rows in final output column order

    # ── helpers ──────────────────────────────────────────────────────────────

    def clean_num(self, cell):
        """Strip commas, spaces, $ and convert parentheses to negative."""
        cell = str(cell or '').replace(',', '').replace(' ', '').replace('$', '')
        if cell.startswith('(') and cell.endswith(')'):
            cell = '-' + cell[1:-1]
        try:
            return int(cell)
        except ValueError:
            return cell

    @staticmethod
    def extract_pid(name):
        """'Airfield Surface Repair - Love Field' → (name, None)
           'Some Project - W214'                  → ('Some Project', 'W214')"""
        m = re.search(r'\s+[-–]\s+([A-Z][A-Z0-9]{1,4})\s*$', name)
        if m:
            return name[:m.start()].strip(), m.group(1)
        return name, None

    @staticmethod
    def get_dept(banner_cell):
        """Strip trailing 'CAPITAL IMPROVEMENTS' from the department banner."""
        dept = re.sub(r'\s+CAPITAL\s+IMPROVEMENTS?\s*$', '', banner_cell, flags=re.I).strip()
        return dept.title()

    # ── step 1: extract pages ─────────────────────────────────────────────

    def import_data(self):
        first_page   = True
        current_dept = ''

        with pdfplumber.open(PDF_DIR + f"{self.cip_year}.pdf") as pdf:
            for source_page, pg in enumerate(pdf.pages, start=1):
                pg_text = pg.extract_text() or ''
                tbl     = pg.extract_table()

                if not tbl or len(tbl) < 3:
                    continue
                if not (re.search(r'FY\s*\d{4}', pg_text) and
                        'Service' in pg_text and
                        'Key Focus' in pg_text):
                    continue

                # row[0] = dept banner, row[1] = column headers, row[2+] = data
                banner = str(tbl[0][0] or '').splitlines()[0].strip()  # first line only
                if banner and re.search(r'IMPROVEMENT|FACILIT|DRAINAGE|WATER|LIBRARY|AVIATION|PARK|STREET', banner, re.I):
                    current_dept = self.get_dept(banner)

                if first_page:
                    self.headers = [str(c or '').replace('\n', ' ').strip() for c in tbl[1]]
                    first_page = False

                for row in tbl[2:]:
                    cleaned_row = [str(c or '').replace('\n', ' ').strip() for c in row]
                    if not cleaned_row[0]:
                        continue
                    if any('total' in str(cell).lower() for cell in cleaned_row[:2]):
                        continue
                    cleaned_row.append(source_page)    # index 14
                    cleaned_row.append(current_dept)   # index 15
                    self.cleaned.append(cleaned_row)

        print(f"  import_data: {len(self.cleaned)} rows, dept sample='{current_dept}'")

    # ── step 2: map year headers ──────────────────────────────────────────

    def process_yrHeaders(self):
        """Indices 8-10 are FY YYYY-YY columns; index 11 is Future Cost."""
        last_yr = None
        for i in [8, 9, 10, 11]:
            h = self.headers[i] if i < len(self.headers) else ''
            m = re.search(r'(\d{4})-(\d{2})', h)
            if m:
                yr = "year_" + "20" + m.group(2)
                last_yr = yr
            elif 'future' in h.lower():
                yr = "year_" + str(int(last_yr.split('_')[1]) + 1) if last_yr else f"year_{self.cip_year}"
            else:
                yr = f"year_{self.cip_year}"
            self.years[h] = yr
            if yr not in self.column_headers:
                self.column_headers.append(yr)

        print(f"  process_yrHeaders: years={list(self.years.values())}")

    # ── step 3: add derived fields to each row ────────────────────────────

    def process_IDs(self):
        """Append project_id, start_year, end_year, cip_year to each row."""
        ids_raw = {}

        for row in self.cleaned:
            raw_name = row[0]
            clean_name, pid = self.extract_pid(raw_name)
            row[0] = clean_name  # strip the suffix from the name in-place

            # unique sub-ID counter per base ID (or name if no ID)
            key = pid or clean_name[:8]
            ids_raw[key] = ids_raw.get(key, 0) + 1
            project_id = f"{pid}.{ids_raw[key]}" if pid else f"ROW{len(ids_raw)}.{ids_raw[key]}"

            # start / end year from FY columns (indices 8-11), exclude future cost col
            future_yr  = self.years.get(self.headers[11], '') if len(self.headers) > 11 else ''
            print(row)
            print(self.headers)
            year_cells = [(self.years.get(self.headers[i], ''), row[i])
                          for i in range(8, 12)]
            start_year = next((y.split('_')[1] for y, v in year_cells if v not in ('0', '', '0.0') and y != future_yr), '')
            end_year   = next((y.split('_')[1] for y, v in reversed(year_cells) if v not in ('0', '', '0.0') and y != future_yr), '')

            row.append(project_id)  # 16
            row.append(start_year)  # 17
            row.append(end_year)    # 18
            row.append(self.cip_year)  # 19

        print(f"  process_IDs: done")

    # ── step 4: reorder into final column arrangement ─────────────────────

    def format_rows(self):
        """
        After appends, row indices are:
          0  project_name   1  service        2  key_focus      3  council
          4  funding        5  prev_approp    6  spent          7  remaining
          8  y1             9  y2             10 y3             11 future
          12 project_total  13 in_service     14 source_page    15 department
          16 project_id     17 start_year     18 end_year       19 cip_year

        Target: cip, service, src_pg, dept, name, pid, start, end, prev, total, y1, y2, y3, future
        """
        new_order = [19, 1, 14, 15, 0, 16, 17, 18, 5, 12, 8, 9, 10, 11]
        numeric_positions = {8, 9, 10, 11, 12, 13}  # prev, total, y1-y4 in new_row

        for row in self.cleaned:
            if len(row) < 20:
                continue
            new_row = [row[i] for i in new_order]
            new_row = [self.clean_num(cell) if i in numeric_positions else cell
                       for i, cell in enumerate(new_row)]
            self.final.append(new_row)

        print(f"  format_rows: {len(self.final)} rows")

    # ── step 5: write CSV ─────────────────────────────────────────────────

    def write_csv(self):
        out = OUTPUT_DIR + f"{self.cip_year}.csv"
        with open(out, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(self.column_headers)
            writer.writerows(self.final)
        print(f"  write_csv: {out}")

    def combine(self):
        print(f"\n=== {self.cip_year} ===")
        self.import_data()
        self.process_yrHeaders()
        self.process_IDs()
        self.format_rows()
        self.write_csv()


if __name__ == '__main__':
    for year in [x for x in range(2011,2012) if x != 2009]:  # Format A years: 2007–2016
        p = ParserA(year)
        p.combine()
