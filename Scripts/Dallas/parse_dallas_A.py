# parse_dallas_A.py — Format A (2007–2016), no project IDs, merges duplicates

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
            'project_name', 'start_year', 'end_year',
            'previous_appropriations', 'project_total',
        ]
        self.headers = []
        self.cleaned = []
        self.years   = {}
        self.final   = []

    @staticmethod
    def get_dept(banner_cell):
        dept = re.sub(r'\s+CAPITAL\s+IMPROVEMENTS?\s*$', '', banner_cell, flags=re.I).strip()
        return dept.title()

    def clean_num(self, cell):
        cell = str(cell or '').replace(',', '').replace(' ', '').replace('$', '')
        if cell.startswith('(') and cell.endswith(')'):
            cell = '-' + cell[1:-1]
        try:
            return int(cell)
        except ValueError:
            return cell

    # ── Step 1 ────────────────────────────────────────────────────────────────

    def import_data(self):
        first_page   = True
        current_dept = ''
        seen         = {}

        def parse(v):
            if isinstance(v, (int, float)):
                return int(v)
            v = (v or '').replace(',', '').replace('$', '').replace(' ', '').strip()
            if v.startswith('(') and v.endswith(')'):
                return -int(v[1:-1])
            try:
                return int(v)
            except:
                return 0

        def fmt(n):
            return f'({-n})' if n < 0 else str(n)

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

                # tbl[0] = dept banner, tbl[1] = column headers, tbl[2+] = data
                banner = str(tbl[0][0] or '').splitlines()[0].strip()
                if banner and re.search(
                    r'IMPROVEMENT|FACILIT|DRAINAGE|WATER|LIBRARY|AVIATION|PARK|STREET|SANITATION|POLICE|FIRE',
                    banner, re.I
                ):
                    current_dept = self.get_dept(banner)

                if first_page:
                    self.headers = [str(c or '').replace('\n', ' ').strip() for c in tbl[1]]
                    first_page = False

                for row in tbl[2:]:
                    cleaned_row = [
                        cell.replace('\n', ' ').replace(',', '').replace('$', '').strip() if cell else ''
                        for cell in row
                    ]

                    if not cleaned_row[0]:
                        continue
                    if any('total' in str(cell).lower() for cell in cleaned_row[:2]):
                        continue

                    parts = cleaned_row[0].split(' - ')
                    cleaned_row[0] = ' - '.join(parts[:-1]) if len(parts) > 1 else parts[0]
                    project_name = cleaned_row[0]

                    cleaned_row.append(str(source_page))  # 14
                    cleaned_row.append(current_dept)       # 15

                    if project_name in seen:
                        # merge numeric cols 5-12 (prev_approp → project_total); skip 13 (date)
                        merge_end = min(13, len(seen[project_name]), len(cleaned_row))
                        for i in range(5, merge_end):
                            result = parse(seen[project_name][i]) + parse(cleaned_row[i])
                            seen[project_name][i] = fmt(result)
                    else:
                        seen[project_name] = cleaned_row

        for k in seen:
            self.cleaned.append(seen[k])

        print(f"  import_data: {len(self.cleaned)} rows")
        print(self.headers)

    # ── Step 2 ────────────────────────────────────────────────────────────────

    def process_yrHeaders(self):
        """Format A: FY year cols at indices 8, 9, 10; Future Cost at 11."""
        last_yr = None
        for i in [8, 9, 10, 11]:
            h = (self.headers[i] if i < len(self.headers) else '') or ''
            m = re.search(r'(\d{4})-(\d{2})', h)
            if m:
                last_yr = "20" + m.group(2)
                self.years[h] = "year_" + last_yr
                self.column_headers.append("year_" + last_yr)
            elif 'future' in h.lower():
                yr = "year_" + str(int(last_yr) + 1) if last_yr else f"year_{self.cip_year}"
                self.years[h] = yr
                self.column_headers.append(yr)
            else:
                self.years[h] = f"year_{self.cip_year}"
                self.column_headers.append(f"year_{self.cip_year}")

        print(f"  process_yrHeaders: {list(self.years.values())}")

    # ── Step 3 ────────────────────────────────────────────────────────────────

    def process_years(self):
        """
        Row layout entering this method:
          0  project_name   1  service     2  key_focus   3  council
          4  funding        5  prev_approp 6  spent       7  remaining
          8  y1             9  y2          10 y3          11 future
          12 project_total  13 in_service  14 source_page 15 department

        Appends: 16 start_yr, 17 end_yr, 18 cip_yr
        """
        future_key = self.years.get(self.headers[11], '') if len(self.headers) > 11 else ''

        for row in self.cleaned:
            year_cells = [
                (self.years.get(self.headers[i], ''), row[i])
                for i in range(8, 12)
                if i < len(self.headers) and i < len(row)
            ]
            start_year = next(
                (y.split('_')[-1] for y, v in year_cells
                 if v not in ('0', '', '0.0') and y != future_key), ''
            )
            end_year = next(
                (y.split('_')[-1] for y, v in reversed(year_cells)
                 if v not in ('0', '', '0.0') and y != future_key), ''
            )
            row += [start_year, end_year, self.cip_year]

        print("  process_years: done")

    # ── Step 4 ────────────────────────────────────────────────────────────────

    def format_rows(self):
        """
        Source indices after process_years:
          0  project_name   1  service     2  key_focus   3  council
          4  funding        5  prev_approp 6  spent       7  remaining
          8  y1             9  y2          10 y3          11 future
          12 project_total  13 in_service  14 source_page 15 department
          16 start_yr       17 end_yr      18 cip_yr

        Output: cip_yr, service, source_page, dept, project_name,
                start_yr, end_yr, prev_approp, total, y1, y2, y3, future
        """
        NEW_ORDER       = [18, 1, 14, 15, 0, 16, 17, 5, 12, 8, 9, 10, 11]
        NUMERIC_INDICES = {7, 8, 9, 10, 11, 12}

        for row in self.cleaned:
            if len(row) < 19:
                continue
            new_row = [row[i] for i in NEW_ORDER]
            new_row = [self.clean_num(cell) if i in NUMERIC_INDICES else cell
                       for i, cell in enumerate(new_row)]
            self.final.append(new_row)

        print(f"  format_rows: {len(self.final)} rows")

    # ── Step 5 ────────────────────────────────────────────────────────────────

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
        self.process_years()
        self.format_rows()
        self.write_csv()


if __name__ == '__main__':
    for year in range(2010, 2011):
        p = ParserA(year)
        p.combine()