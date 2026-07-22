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
        for i in [7, 8, 9]:
            m = re.search(r'(\d{4})-(\d{2})', self.headers[i])
            if m:
                yr = "20" + m.group(2)
                self.years[self.headers[i]] = yr
                self.column_headers.append(yr)
            else: 
                self.years[self.headers[i]] = self.cip_year
                self.column_headers.append(self.cip_year)
        
        print("Headers imported")
        #print("years dict: " + str(self.years.keys()) + ', ' + str(self.years.values()))
        #print(self.column_headers)

    def process_IDs(self):
        # add id, start_year, end_year, and cip_year to rows
        ids_raw = {}

        for row in self.cleaned:
            
            project_id = ''
            start_year = ''
            end_year = ''
            
            raw_id = row[0][-4:]
            if raw_id in ids_raw: # if id already exists, increment subcount by 1
                ids_raw[raw_id] += 1
            else:
                ids_raw[raw_id] = 1 # if not, set subcount to 1

            project_id = f"{raw_id}.{ids_raw[raw_id]}"

            year_cells = []
            for i, cell in enumerate(row):
                if i >= 7 and i < 10:
                    year_cells.append((self.years[self.headers[i]], cell))

            start_year = next((y for y, cell in year_cells if cell != '0'), '')
            end_year   = next((y for y, cell in reversed(year_cells) if cell != '0'), '')
            
            row.append(project_id)
            row.append(start_year)
            row.append(end_year)
            row.append(self.cip_year) # cip_year
            
            #print(row)
        
        print("IDs processed")

    def clean_num(self, cell):
        return cell.replace(",","").replace(" ","")
    
    def format_rows(self):
        # up to this point, cleaned rows are in arrangement of 
        # project, service, funding source, council district, completion date
        # budget, previous_appropriations, y1, y2, y3, future costs, projec_total, source_page, 
        # project_id, start year, end year, cip_year

        # new arrangement:
        # cip_year, project_type, source_page, service, project_name
        # project_id, start_year, end_year, previous_appropriations
        # project_total, y1, y2, y3, ... everything else

        for row in self.cleaned:
            numeric_indices = {8, 9, 10}  # positions in new_row: previous_appropriations, project_total, y1, y2, y3
            new_order = [16, 1, 12, 2, 0, 13, 14, 15, 6, 11, 7, 8, 9, 3, 4, 5, 10]
            new_row = [row[i] for i in new_order][:-4]
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