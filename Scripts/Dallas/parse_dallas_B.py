# typical parser, Dallas 2022-2025

import pdfplumber
import csv
import re

class Parser:
    
    def __init__(self, cip_year):
        self.cip_year=cip_year
        self.column_headers = ['cip_year', 'project_type', 'source_page', 'department', 'project_name',
                   'start_year', 'end_year', 'address_location',
                   'previous_appropriations', 'project_total']
        self.years = {}
        self.column_headers
        self.headers = []
        self.cleaned = []
        self.years = {}
        self.final = []
    
    def import_data(self):
        first_page = True
        seen = {}

        def parse(v):
            if isinstance(v, (int, float)):   # guard against source_page int
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

        with pdfplumber.open(r"C:\Users\vince\Documents\GitHub\CIPBD\Dallas\PDF\\" + f"{self.cip_year}.pdf") as pdf:
            source_page = 0
            for pg in pdf.pages:

                pg_text = pg.extract_text() or ''
                pg_table = pg.extract_table()
                
                source_page += 1

                if pg_table and len(pg_table[0]) >= 8 and "District" in pg_text and "Service" in pg_text and "Comp" in pg_text:
                    
                    if first_page:
                        for candidate in pg_table:
                            if candidate[0] and candidate[0].isupper() and all(c is None for c in candidate[1:]):
                                continue  # section title row, skip
                            self.headers = candidate
                            first_page = False
                            break
                    for row in pg_table[1:]:
                        
                        cleaned_row = [
                            cell.replace('\n', ' ').replace(',', '').replace('$', '').strip() if cell else ''
                            for cell in row
                        ]

                        parts = cleaned_row[0].split(' - ')
                        cleaned_row[0] = ' - '.join(parts[:-1]) if len(parts) > 1 else parts[0]
                        project_name = cleaned_row[0]

                        if any('grand total' in str(cell).lower() for cell in cleaned_row):
                            continue
                        cleaned_row.append(str(source_page))


                        if project_name in seen:
                            merge_end = min(12, len(seen[project_name]), len(cleaned_row))
                            for i in range(5, merge_end):
                                result = parse(seen[project_name][i]) + parse(cleaned_row[i])
                                seen[project_name][i] = fmt(result)
                        else:
                            seen[project_name] = cleaned_row



        for i in seen.keys():
            self.cleaned.append(seen[i])

        print("Data imported")
        #print(self.cleaned)
        print(self.headers)

    def process_yrHeaders(self):
        last_yr = None
        for i in [7, 8, 9, 10]:
            m = re.search(r'(\d{4})-(\d{2})', self.headers[i])
            if m:
                last_yr = "20" + m.group(2)
                self.years[self.headers[i]] = "year_" + last_yr
                self.column_headers.append("year_" + last_yr)
            elif 'future' in self.headers[i].lower():
                yr = "year_" + str(int(last_yr) + 1) if last_yr else str("year_"+self.cip_year)
                self.years[self.headers[i]] = yr
                self.column_headers.append(yr)
            else:
                self.years[self.headers[i]] = "year_"+str(self.cip_year)
                self.column_headers.append("year_"+str(self.cip_year))
        print("Headers imported")

    def process_years(self):
        # Row layout after appending: 0-11 original, 12 source_page,
        #   13 start_yr, 14 end_yr, 15 cip_yr
        for row in self.cleaned:
            year_cells = [(self.years[self.headers[i]], cell)
                        for i, cell in enumerate(row) if 7 <= i <= 10]

            start_year = next((y for y, cell in year_cells if cell != '0' and y != 'future_costs'), '')
            end_year   = next((y for y, cell in reversed(year_cells) if cell != '0' and y != 'future_costs'), '')

            row += [start_year.split('_')[-1], end_year.split('_')[-1], self.cip_year]
        print("Years processed")

    def clean_num(self, cell):
        if cell=='' or cell=='-':
            return 0
        cleaned_cell = cell.replace(",", "").replace(" ", "").replace("$", "")
        if cleaned_cell.startswith("(") and cleaned_cell.endswith(")"):
            cleaned_cell = "-" + cleaned_cell[1:-1]
        try:
            return int(cleaned_cell)
        except ValueError:
            return cleaned_cell

    def format_rows(self):
        # source: project(0), service(1), funding(2), council(3), completion(4),
        #         budget(5), prev_approp(6), y1(7), y2(8), y3(9), future(10), total(11),
        #         source_page(12), start_yr(13), end_yr(14), cip_yr(15)
        # output: cip_yr, service, source_page, funding, project,
        #         start_yr, end_yr, council, prev_approp, total, y1, y2, y3, future
        NEW_ORDER       = [15, 1, 12, 2, 0, 13, 14, 3, 6, 11, 7, 8, 9, 10]
        NUMERIC_INDICES = {8, 9, 10, 11, 12, 13}

        for row in self.cleaned:
            new_row = [row[i] for i in NEW_ORDER]
            new_row = [self.clean_num(cell) if i in NUMERIC_INDICES else cell
                    for i, cell in enumerate(new_row)]
            self.final.append(new_row)
        print("Rows formatted")

    def write_csv(self):
        with open(r"C:\Users\vince\Documents\GitHub\CIPBD\Scripts\Dallas\outputs\\"+str(self.cip_year)+".csv", "a", newline="",
                  encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(self.column_headers)
            writer.writerows(self.final)
        print("CSV written")

    def combine(self):
        self.import_data()
        self.process_yrHeaders()
        self.process_years()
        self.format_rows()
        self.write_csv()
        #print(self.column_headers)

for i in range(2008, 2014):
    p = Parser(i)
    p.combine()