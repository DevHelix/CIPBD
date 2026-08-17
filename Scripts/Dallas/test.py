def import_data(self):
    first_page = True
    # Maps project_name -> index in self.cleaned for O(1) duplicate lookup
    seen: dict[str, int] = {}
    NAME_COL = 0  # adjust if project name is in a different column

    with pdfplumber.open(
        r"C:\Users\vince\Documents\GitHub\CIPBD\Dallas\PDF\\" + f"{self.cip_year}.pdf"
    ) as pdf:
        source_page = 0
        for pg in pdf.pages:
            pg_text  = pg.extract_text() or ''
            pg_table = pg.extract_table()
            source_page += 1

            if pg_table and "District" in pg_text and "Service" in pg_text and "Comp" in pg_text:
                if first_page:
                    self.headers = pg_table[0]
                    first_page = False

                for row in pg_table[1:]:
                    cleaned_row = [
                        cell.replace('\n', ' ').strip() if cell else ''
                        for cell in row
                    ]
                    if any('grand total' in str(cell).lower() for cell in cleaned_row):
                        continue

                    cleaned_row.append(source_page)
                    project_name = cleaned_row[NAME_COL]

                    if project_name and project_name in seen:
                        # Merge: add numeric column values into the existing row
                        existing = self.cleaned[seen[project_name]]
                        for i, (old_val, new_val) in enumerate(zip(existing, cleaned_row)):
                            try:
                                existing[i] = float(old_val or 0) + float(new_val or 0)
                            except (ValueError, TypeError):
                                pass  # non-numeric columns (name, dept, etc.) stay unchanged
                    else:
                        if project_name:
                            seen[project_name] = len(self.cleaned)
                        self.cleaned.append(cleaned_row)

    print("Data imported")
    print(self.headers)