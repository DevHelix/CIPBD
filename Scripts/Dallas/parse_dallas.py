import pdfplumber
import csv
import re

class Parser:
    
    def __init__(self, cip_year):
        self.cip_year=cip_year
        self.column_headers = ['cip_year', 'project_type', 'source_page', 'department','project_name','project_id','start_year','end_year', 
                        'previous_appropriations', 'project_total']
        self.years = {}
        self.column_headers
        self.headers = []
        self.cleaned = []
        self.years = {}
        self.final = []
    
    def import_data(self):
        first_page = True

        with pdfplumber.open(r"C:\Users\vince\Documents\GitHub\CIPBD\Dallas\PDF\\" + f"{self.cip_year}.pdf") as pdf:
            source_page = 0
            for pg in pdf.pages:

                pg_text = pg.extract_text() or ''
                pg_table = pg.extract_table()
                
                source_page += 1

                if pg_table and "District" in pg_text and "Service" in pg_text and "Completion" in pg_text:
                    if first_page:
                        self.headers = pg_table[0]
                        first_page = False
                    for row in pg_table[1:]:
                        
                        cleaned_row = [cell.replace('\n', ' ').strip() if cell else '' for cell in row]
                        if any('grand total' in str(cell).lower() for cell in cleaned_row):
                            continue
                        cleaned_row.append(source_page)
                        self.cleaned.append(cleaned_row)
        print("Data imported")
        #print(self.cleaned)
        #print("headers: "+self.headers)

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

    def process_IDs(self):
        ids_raw = {}
        for row in self.cleaned:
            project_id = start_year = end_year = ''
            raw_id = row[0][-4:]
            ids_raw[raw_id] = ids_raw.get(raw_id, 0) + 1
            project_id = f"{raw_id}.{ids_raw[raw_id]}"

            year_cells = [(self.years[self.headers[i]], cell)
                        for i, cell in enumerate(row) if 7 <= i <= 10]  # extended to 10

            start_year = next((y for y, cell in year_cells if cell != '0' and y != 'future_costs'), '')
            end_year   = next((y for y, cell in reversed(year_cells) if cell != '0' and y != 'future_costs'), '')

            row += [project_id, start_year, end_year, self.cip_year]
        print("IDs processed")

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
        # original: project(0), service(1), funding(2), council(3), completion(4),
        #           budget(5), prev_approp(6), y1(7), y2(8), y3(9), future(10), total(11),
        #           source_page(12), project_id(13), start_yr(14), end_yr(15), cip_yr(16)
        # new: cip_yr, service, source_page, funding, project, id, start, end,
        #      prev_approp, total, y1, y2, y3, future_costs
        for row in self.cleaned:
            numeric_indices = {8, 9, 10, 11, 12, 13}  # prev_approp, total, y1, y2, y3, future
            new_order = [16, 1, 12, 2, 0, 13, 14, 15, 6, 11, 7, 8, 9, 10]  # future costs now included
            new_row = [row[i] for i in new_order]
            new_row = [self.clean_num(cell) if i in numeric_indices else cell
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
        self.process_IDs()
        self.format_rows()
        self.write_csv()
        #print(self.column_headers)

for i in range(2022,2026):
    p = Parser(i)
    p.combine()