# Philadelphia CIP CSV – Manual Edit Log

All edits applied to the 2021–2025 CSVs post-generation. Edits are grouped by batch and type.

---

## Batch 1 – Delete garbage rows (32 rows removed)

Rows where `project_name` contained raw OCR noise: source funding codes (`TB`, `TO`, `SO`), single characters (`A`, `l`), or funding data that leaked into a project row.

### 2021.csv (11 rows deleted)

| source_page | project_id   | project_name                        |
|-------------|--------------|-------------------------------------|
| 99          | FIRE.697     | A                                   |
| 112         | LIB.691      | A                                   |
| 112         | LIB.691.691  | A                                   |
| 230         | STR.268      | A                                   |
| 234         | STR.46.500   | TB                                  |
| 243         | STR.268-2    | A                                   |
| 243         | STR.268.500  | TB                                  |
| 250         | TRN.75.71    | TO 45TO 37TO 43TO 43 TO 43TO        |
| 256         | WAT.78.100   | TB 100TB 100 TB 100 TB 100 TB 100   |
| 257         | WAT.78C.100  | TB 100 TB 100 TB 100 TB 100 TB 100  |
| 262         | WAT.50.100   | TB 100 TB 100 TB 100 TB 100 TB 100 TB |

### 2022.csv (0 rows deleted)

None.

### 2023.csv (3 rows deleted)

| source_page | project_id   | project_name                        |
|-------------|--------------|-------------------------------------|
| 224         | STR.500.500  | TB                                  |
| 235         | STR.267      | A                                   |
| 249         | WAT.78C.100  | TB 100 TB 100 TB 100 TB 100 TB 100  |

### 2024.csv (12 rows deleted)

| source_page | project_id      | project_name |
|-------------|-----------------|--------------|
| 36          | AVN.2025        | l            |
| 102         | LIB.2025        | l            |
| 102         | LIB.2025.195    | A            |
| 116         | MDO.2025        | l            |
| 186         | PRK.2025        | l            |
| 193         | POL.2025        | l            |
| 193         | POL.2025.361    | A            |
| 198         | PRS.2025        | l            |
| 220         | STR.2025        | l            |
| 225         | STR.661.500     | TB           |
| 235         | STR.150.500     | TB           |
| 251         | WAT.75C.100     | TB 100 TB 100 TB 100 TB 100 TB 100 |

### 2025.csv (6 rows deleted)

| source_page | project_id   | project_name                                            |
|-------------|--------------|---------------------------------------------------------|
| 97          | LIB.195      | A                                                       |
| 180         | PRK.8941     | A                                                       |
| 186         | POL.677.361  | A                                                       |
| 229         | STR.70.500   | TB                                                      |
| 238         | TRN.4.51     | TO 106TO 73TO 136 TO 282 TO 287                         |
| 238         | TRN.4.192    | SO = 10,562S0 7,262 SO 13,574 SO 28,191 SO 28,742SO    |

---

## Batch 2 – Fix B: Project name with OCR garbage appended

OCR appended a funding value to the project name. Confirmed by OCR of source page.

### 2024.csv (1 row)

| source_page | project_id | Old project_name | New project_name |
|-------------|------------|------------------|-----------------|
| 203 | PPD.4.623 | W Lehigh Renovations & Roof Replacement $500,000 587 | W Lehigh Renovations & Roof Replacement |

---

## Batch 2 – Fix C: Strip funding-code suffixes from project names

Project names had a funding amount + source code appended (e.g. `500CN`). These are OCR artefacts from the adjacent funding column bleeding into the name field.

### 2021.csv (4 rows)

| source_page | project_id  | Old project_name | New project_name |
|-------------|-------------|------------------|-----------------|
| 103 | FLEET.28.1 | Fuel Tank Replacement 500CN | Fuel Tank Replacement |
| 124 | HLTH.35.4  | Planning Study - Air Monitoring Network 100CN | Planning Study - Air Monitoring Network |
| 152 | PRK.5      | Improvements to Footways & Roadways 150CN | Improvements to Footways & Roadways |
| 266 | ZOO.82.2   | City Owned Building Renovations HVAC 250CN | City Owned Building Renovations HVAC |

### 2025.csv (6 rows)

| source_page | project_id  | Old project_name | New project_name |
|-------------|-------------|------------------|-----------------|
| 83  | FIRE.26.3 | Roof Replacements 500CN | Roof Replacements |
| 83  | FIRE.26.5 | Health and Safety Improvements 500CN | Health and Safety Improvements |
| 83  | FIRE.26.6 | Structural Renovations 500CN | Structural Renovations |
| 106 | MDO.33.3  | Improvements to Animal Care & Control Team facility 300CN | Improvements to Animal Care & Control Team facility |
| 183 | POL.58.2  | Police Districts Security Improvements 750CN | Police Districts Security Improvements |
| 256 | ZOO.80.2  | City Owned Building Renovations HVAC 500CN | City Owned Building Renovations HVAC |

---

## 2024.csv – File recovery

`2024.csv` was truncated during the Batch 1 write (filesystem sync issue), losing the last 6 ZOO rows. These were reconstructed from OCR of pages 259–260 of `2024.pdf`:

| source_page | project_id | project_name | project_total |
|-------------|------------|--------------|---------------|
| 259 | ZOO.79.2 | Philadelphia Zoo Improvements Major Zoowide Renewal | — |
| 259 | ZOO.79.3 | City Owned Building Renovations HVAC | 6,000 |
| 259 | ZOO.79.4 | City Owned Building Renovation - Electrical Infrastructure | 3,500 |
| 260 | ZOO.79A | Philadelphia Zoo Facility and Infrastructure Improvements-FY24 | 7,000 |
| 260 | ZOO.79B | Philadelphia Zoo Facility and Infrastructure Improvements-FY23 | 1,783 |
| 260 | ZOO.79C | Philadelphia Zoo Facility and Infrastructure Improvements-FY22 | 6,764 |

---

## Pending

- **Fix A** (on hold): `FIRE.9.140` in `2023.csv` — OCR confirms this should be `FIRE.9.10`. Awaiting approval.
