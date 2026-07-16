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

## Batch 2 – Remaining OCR corrections

### 2021.csv (1 row)

| project_id | Field | Old value | New value |
|------------|-------|-----------|-----------|
| ZOO.82.1 | project_name | City-owned Building Renovation Roofs and Building Envelope 2500N | City-owned Building Renovation Roofs and Building Envelope |

### 2022.csv (5 fields across 4 rows)

| project_id | Field | Old value | New value | Notes |
|------------|-------|-----------|-----------|-------|
| OIT.38C | project_total | 12.536 | 12536 | comma-decimal |
| TRN.75.1 | year_2023 | 1096.823 | 1096 | decimal noise stripped |
| TRN.75.1 | project_total | 7030.823 | 7030 | decimal noise stripped |
| COM.6.4 | project_total | 7002.5 | 9500 | updated to match year-sum after year_2026 fix |
| TRN.74.1 | project_total | 4748.272 | 6019 | updated to match year-sum after year_2025 fix; still incomplete multi-source |

### 2024.csv (24 rows)

**Description bleeds (3 rows)**

| project_id | Old project_description (truncated) | New project_description |
|------------|-------------------------------------|------------------------|
| FIN.25C | See description under line item 25. 171 25D. City Council - ITEF CD10-FY21 See description under line item 25. | See description under line item 25. |
| OHS.34A | See description under line item 34. 2,500 | See description under line item 34. |
| POL.58A | See description under line item 58. 10,457 | See description under line item 58. |

**Value-duplicated carry-through rows (21 rows) — year_2030 zeroed, project_total halved**

| project_id | Old total | New total |
|------------|-----------|-----------|
| FIN.161 | 56 | 28 |
| FIN.17C | 82 | 41 |
| FIN.21C | 180 | 90 |
| FIN.221 | 158 | 79 |
| FIN.230 | 68 | 34 |
| PRK.401 | 64 | 32 |
| PRK.43B | 110 | 55 |
| PRK.430 | 80 | 40 |
| PRK.441 | 112 | 56 |
| PRK.440 | 20 | 10 |
| PRK.451 | 116 | 58 |
| PRK.450 | 100 | 50 |
| PRK.46C | 82 | 41 |
| PRK.500 | 118 | 59 |
| PRK.53A | 182 | 91 |
| PRK.54A | 116 | 58 |
| PRK.56A | 30 | 15 |
| REC.62B | 186 | 93 |
| REC.62C | 58 | 29 |
| TRN.73A | 88 | 44 |
| TRN.73B | 190 | 95 |

### 2025.csv (2 rows)

| project_id | Fields corrected | Notes |
|------------|-----------------|-------|
| ART.1.1 | project_description, project_total, year_2026–2031, start_year, end_year | All year values were absorbed into description; extracted from PDF p.28. total=12500, year_2026=2500, year_2027–2031=2000 each |
| ART.1A | project_description, year_2026, year_2031, start_year, end_year | Description bleed stripped; year_2031 cleared, year_2026=2000 set; start/end year corrected from 2031→2026 |

---

## Pending

- **Fix A** (on hold): `FIRE.9.140` in `2023.csv` — OCR confirms this should be `FIRE.9.10`. Awaiting approval.

## 2021.csv — Description Bleed Reconstruction (2026-07-14)

Auto-extracted year values from project_description for 108 `incorrect` rows.
OCR noise corrections applied; fund codes used to assign values to year_2022–year_2027 columns.
3 AVN rows flagged for PDF verification (truncated descriptions).
2 rows (COM.13.1, FIN.15.1) used manual overrides.

- `AVN.2.1` (row 1): extracted year values, set project_total=128053
- `AVN.3.1` (row 2): extracted year values, set project_total=171642
- `AVN.4.1` (row 3): extracted year values, set project_total=155285
- `AVN.5.1` (row 5): extracted year values, set project_total=55275
- `COM.6.1` (row 6): extracted year values, set project_total=12600
- `COM.6.2` (row 7): extracted year values, set project_total=3500
- `AVN.7.1` (row 11): extracted year values, set project_total=3000
- `AVN.8.1` (row 15): extracted year values, set project_total=1500
- `AVN.9.1` (row 18): extracted year values, set project_total=1500
- `COM.13.1` (row 26): extracted year values, set project_total=7000
- `COM.14.1` (row 30): extracted year values, set project_total=1900
- `COM.14B` (row 32): extracted year values, set project_total=500
- `FIN.15.1` (row 34): extracted year values, set project_total=51500
- `FIN.16.1` (row 38): extracted year values, set project_total=1530
- `FIN.17.1` (row 43): extracted year values, set project_total=1530
- `FIN.18.1` (row 48): extracted year values, set project_total=1530
- `FIN.19.1` (row 53): extracted year values, set project_total=1530
- `FIN.19B` (row 55): extracted year values, set project_total=1
- `FIN.20.1` (row 58): extracted year values, set project_total=1530
- `FIN.21.1` (row 64): extracted year values, set project_total=1530
- `FIN.22.1` (row 69): extracted year values, set project_total=1530
- `FIN.23.1` (row 74): extracted year values, set project_total=1530
- `FIN.24.1` (row 79): extracted year values, set project_total=1530
- `FIN.241` (row 83): extracted year values, set project_total=1
- `FIN.25.1` (row 84): extracted year values, set project_total=1530
- `FIN.251` (row 88): extracted year values, set project_total=2
- `FIRE.26.1` (row 89): extracted year values, set project_total=350
- `FIRE.26.2` (row 90): extracted year values, set project_total=800
- `FIRE.26.3` (row 91): extracted year values, set project_total=1400
- `FIRE.26.5` (row 93): extracted year values, set project_total=300
- `FIRE.26.6` (row 94): extracted year values, set project_total=750
- `FIRE.26.7` (row 95): extracted year values, set project_total=750
- `FLEET.28.2` (row 106): extracted year values, set project_total=3000
- `FLEET.28.3` (row 107): extracted year values, set project_total=2000
- `FLEET.29.1` (row 111): extracted year values, set project_total=50500
- `LIB.30.1` (row 115): extracted year values, set project_total=1000
- `LIB.30.2` (row 116): extracted year values, set project_total=9000
- `HLTH.32.1` (row 121): extracted year values, set project_total=3000
- `HLTH.33.1` (row 126): extracted year values, set project_total=5800
- `HLTH.35.1` (row 134): extracted year values, set project_total=22800
- `HLTH.35.2` (row 135): extracted year values, set project_total=500
- `HLTH.35.3` (row 136): extracted year values, set project_total=1300
- `HLTH.35.4` (row 137): extracted year values, set project_total=400
- `HLTH.36.3` (row 145): extracted year values, set project_total=3000
- `OHS.37.3` (row 150): extracted year values, set project_total=900
- `OIT.38.1` (row 154): extracted year values, set project_total=19830
- `OIT.38.2` (row 155): extracted year values, set project_total=71012
- `PRK.39.1` (row 159): extracted year values, set project_total=10259
- `PRK.2` (row 160): extracted year values, set project_total=3305
- `PRK.2.3` (row 161): extracted year values, set project_total=2500
- `PRK.40.1` (row 165): extracted year values, set project_total=21000
- `PRK.40C.1` (row 169): extracted year values, set project_total=1700
- `PRK.40C.3` (row 171): extracted year values, set project_total=55000
- `PRK.42.4` (row 178): extracted year values, set project_total=7470
- `PRK.5.6` (row 180): extracted year values, set project_total=7000
- `PRK.5.7` (row 181): extracted year values, set project_total=950
- `PRK.5.8` (row 182): extracted year values, set project_total=3500
- `PRK.43.1` (row 186): extracted year values, set project_total=9000
- `PRK.43.2` (row 187): extracted year values, set project_total=305
- `PRK.3` (row 188): extracted year values, set project_total=250
- `PRK.3.4` (row 189): extracted year values, set project_total=5500
- `PRK.44.1` (row 193): extracted year values, set project_total=2370
- `PRK.45.1` (row 198): extracted year values, set project_total=2370
- `PRK.46.1` (row 204): extracted year values, set project_total=2370
- `PRK.47.1` (row 210): extracted year values, set project_total=2370
- `PRK.49.1` (row 219): extracted year values, set project_total=2370
- `PRK.50.1` (row 224): extracted year values, set project_total=2370
- `PRK.51.1` (row 230): extracted year values, set project_total=2370
- `PRK.52.1` (row 236): extracted year values, set project_total=2370
- `PRK.53.1` (row 241): extracted year values, set project_total=2370
- `PRK.54.2` (row 247): extracted year values, set project_total=900
- `PRK.56B` (row 255): extracted year values, set project_total=3
- `POL.60.3` (row 267): extracted year values, set project_total=1000
- `PRS.61.1` (row 271): extracted year values, set project_total=1100
- `PRS.61.2` (row 272): extracted year values, set project_total=21500
- `PPD.62.1` (row 276): extracted year values, set project_total=3000
- `STR.65.2` (row 292): extracted year values, set project_total=600
- `STR.65.3` (row 293): extracted year values, set project_total=12000
- `STR.66.2` (row 299): extracted year values, set project_total=13750
- `STR.66.3` (row 300): extracted year values, set project_total=2200
- `STR.68.1` (row 305): extracted year values, set project_total=3000
- `STR.68.2` (row 306): extracted year values, set project_total=500
- `STR.69.2` (row 311): extracted year values, set project_total=43257
- `STR.69.4` (row 313): extracted year values, set project_total=10400
- `STR.5` (row 314): extracted year values, set project_total=16000
- `STR.70.1` (row 318): extracted year values, set project_total=1500
- `STR.70.2` (row 319): extracted year values, set project_total=400
- `STR.70.4` (row 321): extracted year values, set project_total=300
- `STR.70C` (row 324): extracted year values, set project_total=7
- `STR.71.1` (row 325): extracted year values, set project_total=4750
- `STR.71.2` (row 326): extracted year values, set project_total=1500
- `STR.71.3` (row 327): extracted year values, set project_total=1750
- `STR.72.4` (row 331): extracted year values, set project_total=600
- `STR.72.2` (row 332): extracted year values, set project_total=600
- `STR.72.3` (row 333): extracted year values, set project_total=350
- `STR.73.2` (row 337): extracted year values, set project_total=70100
- `TRN.74C` (row 354): extracted year values, set project_total=1
- `TRN.75.1` (row 355): extracted year values, set project_total=8728
- `TRN.75.2` (row 356): extracted year values, set project_total=22290
- `TRN.75.3` (row 357): extracted year values, set project_total=5088
- `TRN.76.1` (row 360): extracted year values, set project_total=10358
- `TRN.77.1` (row 362): extracted year values, set project_total=66739
- `WAT.78.1` (row 363): extracted year values, set project_total=937000
- `WAT.79.4` (row 369): extracted year values, set project_total=600
- `WAT.79.2` (row 370): extracted year values, set project_total=25000
- `WAT.79.3` (row 371): extracted year values, set project_total=350
- `WAT.80.1` (row 374): extracted year values, set project_total=30638
- `WAT.80.2` (row 375): extracted year values, set project_total=60000

## 2021.csv — Zero-total unlabeled row fixes (2026-07-14)

Fixed 12 unlabeled rows with zero project_total. OCR noise patterns corrected:
- "Z→2" (PIDC Z fund code misread as digit 2) in COM.10.1, COM.11.1
- "cT→CT" (lowercase c OCR noise) in FIN.161, FIN.221, PRK.55C
- "7OOCN→700CN" (letter O misread as digit 0) in HLTH.33.2
- FIN.21, TRN.76A: unfunded placeholders → validated (no data)
- Row 387: blank pid, truncated row → deleted

- `AVN.4A` (row 4): Single-year XT allocation extracted from description bleed
- `COM.10.1` (row 19): 6-year Z fund allocation; OCR noise "10,0002" = "10,000 Z" (Z misread as 2); yea
- `COM.11.1` (row 20): 6-year Z fund allocation; OCR noise "20,0002", "10,000 2", "10,0002" = Z misread
- `FIN.161` (row 42): OCR noise "2cT" corrected to "2 CT"; single year carry-through
- `FIN.21` (row 63): No funding data present; description is placeholder dash; project may be unfunde
- `FIN.221` (row 73): OCR noise "2cT" corrected to "2 CT"; adjacent row bleed stripped; single year ca
- `HLTH.33.2` (row 127): OCR noise "7OOCN" = "700 CN" (letters O misread as digit 0); single-year CN allo
- `PRK.54.1` (row 246): Single-year CA allocation extracted from description bleed
- `PRK.55C` (row 253): OCR noise "2cT" corrected to "2 CT"; page footer bleed stripped; single year car
- `TRN.76A` (row 361): References TRN.76; no independent funding allocation in this CIP year
- `WAT.78.2` (row 364): 6-year PB allocation of 10 per year extracted from description bleed; trailing o
- `(empty pid row 387)` (row 387): Truncated OCR row: project_id blank, name incomplete, no description data

## 2021.csv — Three-pass description cleanup (2026-07-14)

Fixed 23 rows across three passes:
- Pass 1: Residual funding values not stripped by batch cleaner
- Pass 2: Adjacent-row bleed (duplicate see-descriptions, FY tags, duplicate text)  
- Pass 3: OCR text quality (garbled words, bare numbers, page footers, truncated sentences)
Two rows (PRK.42.2, ZOO.82.1) also had year columns and totals corrected.

- `FIN.251` (row 88): Stripped adjacent-row bleed (FY11 reference, duplicate see-description, '71: CT' fragment)
- `FIRE.26.5` (row 93): Added terminal period; description was complete but lacked punctuation
- `FIRE.26C` (row 101): Stripped residual '697 A' carry-through value from description
- `FLEET.28.1` (row 105): Added terminal period
- `HLTH.32.1` (row 121): Fixed garbled OCR: 'Implement and Electronic Health Records (EHR) improve system' → proper
- `HLTH.34A` (row 131): Stripped residual '1,000 CR' value and 'ee' OCR artifact from mid-description bleed
- `HLTH.34B` (row 132): Stripped residual '364 CR' value from mid-description bleed
- `PRK.41C` (row 174): Stripped multi-row bleed: 41D/41E/41F sub-item descriptions and FY15/FY17/FY18 tags; page 
- `PRK.42.2` (row 176): Residual '100 PB' values stripped from description; year_2022–2026 corrected to 100 PB eac
- `PRK.48.1` (row 214): Stripped page footer bleed (FISCAL YEARS 2022-2027); fixed word-order OCR error 'the Depar
- `PRK.57A` (row 257): Added terminal period to truncated description
- `PRK.59C` (row 265): Stripped adjacent-row bleed: '59D. Grant Funded Recreation Improvements-FY11' + duplicate 
- `PRS.61.2` (row 272): Stripped residual '5,000' bare number from mid-description; added period to truncated end
- `STR.65.1` (row 291): Stripped residual '4CA' value from mid-description bleed
- `STR.66.1` (row 298): Stripped residual '163 CA' value from mid-description bleed
- `STR.69.1` (row 310): Stripped '39 CA', '20,000', '16,000' residual values; fixed word-order OCR error 'eligible
- `STR.71C` (row 330): Stripped multi-row bleed: '71D. Alley Lighting Improvements-FY12' + duplicate see-descript
- `STR.73A` (row 343): Stripped residual '800' + '749000' bare numbers and page footer from description
- `TRN.74.3` (row 348): Stripped '12,918' and '469' bare OCR numbers and page footer bleed from mid-description
- `WAT.78A` (row 365): Stripped residual '133,050 XT' value from description
- `WAT.81.1` (row 379): Stripped all residual funding values (FB, SB, XN series incl. OCR noise SOFB/5OFB/S0SB) fr
- `WAT.81A` (row 380): Stripped residual '163,807 XT' value from description
- `ZOO.82.1` (row 383): Stripped '250 CN' values (×5) from description; year_2022–2026 corrected to 250 CN each (t

## 2021.csv — Description number cleanup (2026-07-16)

Stripped bare numbers from 51 descriptions via clean_descriptions.py.

- `ART.1.1` (row 0): bare numbers stripped from description
- `AVN.2.1` (row 1): bare numbers stripped from description
- `AVN.3.1` (row 2): bare numbers stripped from description
- `AVN.4.1` (row 3): bare numbers stripped from description
- `AVN.5.1` (row 5): bare numbers stripped from description
- `COM.12.2` (row 22): bare numbers stripped from description
- `COM.12.3` (row 23): bare numbers stripped from description
- `COM.13.1` (row 26): bare numbers stripped from description
- `FIN.21` (row 63): bare numbers stripped from description
- `FIRE.26.4` (row 92): bare numbers stripped from description
- `FIRE.8` (row 96): bare numbers stripped from description
- `FIRE.8.9` (row 97): bare numbers stripped from description
- `HLTH.32.2` (row 122): bare numbers stripped from description
- `HLTH.35.2` (row 135): bare numbers stripped from description
- `HLTH.35.3` (row 136): bare numbers stripped from description
- `HLTH.35.4` (row 137): bare numbers stripped from description
- `HLTH.36.1` (row 143): bare numbers stripped from description
- `HLTH.36.2` (row 144): bare numbers stripped from description
- `OHS.37.3` (row 150): bare numbers stripped from description
- `OIT.38.2` (row 155): bare numbers stripped from description
- `PRK.39.1` (row 159): bare numbers stripped from description
- `PRK.42.4` (row 178): bare numbers stripped from description
- `PRK.3.4` (row 189): bare numbers stripped from description
- `PRK.54.2` (row 247): bare numbers stripped from description
- `PPD.63.1` (row 280): bare numbers stripped from description
- `PPD.63.2` (row 281): bare numbers stripped from description
- `STR.65.2` (row 292): bare numbers stripped from description
- `STR.65.3` (row 293): bare numbers stripped from description
- `STR.66.2` (row 299): bare numbers stripped from description
- `STR.69.2` (row 311): bare numbers stripped from description
- `STR.69.3` (row 312): bare numbers stripped from description
- `STR.5` (row 314): bare numbers stripped from description
- `STR.70.2` (row 319): bare numbers stripped from description
- `STR.70.4` (row 321): bare numbers stripped from description
- `STR.71.3` (row 327): bare numbers stripped from description
- `STR.72.4` (row 331): bare numbers stripped from description
- `STR.73.1` (row 336): bare numbers stripped from description
- `STR.3` (row 338): bare numbers stripped from description
- `STR.3.4` (row 339): bare numbers stripped from description
- `STR.3.5` (row 340): bare numbers stripped from description
- `STR.3.6` (row 341): bare numbers stripped from description
- `STR.3.7` (row 342): bare numbers stripped from description
- `TRN.74.1` (row 346): bare numbers stripped from description
- `TRN.74.2` (row 347): bare numbers stripped from description
- `TRN.4.5` (row 350): bare numbers stripped from description
- `TRN.75.2` (row 356): bare numbers stripped from description
- `TRN.4-2` (row 358): bare numbers stripped from description
- `WAT.78.1` (row 363): bare numbers stripped from description
- `WAT.79.2` (row 370): bare numbers stripped from description
- `WAT.79.3` (row 371): bare numbers stripped from description
- `ZOO.82.3` (row 385): bare numbers stripped from description

## 2022.csv — Description number cleanup (2026-07-16)

Stripped bare numbers from 215 descriptions via clean_descriptions.py.

- `AVN.2.1` (row 0): bare numbers stripped from description
- `AVN.2A` (row 1): bare numbers stripped from description
- `AVN.3.1` (row 2): bare numbers stripped from description
- `AVN.4.14` (row 4): bare numbers stripped from description
- `AVN.5.1` (row 7): bare numbers stripped from description
- `AVN.5A` (row 8): bare numbers stripped from description
- `COM.6.4` (row 9): bare numbers stripped from description
- `COM.6.2` (row 10): bare numbers stripped from description
- `COM.6C` (row 13): bare numbers stripped from description
- `COM.7.1` (row 14): bare numbers stripped from description
- `COM.7B` (row 16): bare numbers stripped from description
- `COM.7C` (row 17): bare numbers stripped from description
- `COM.8.1` (row 18): bare numbers stripped from description
- `COM.10.1` (row 21): bare numbers stripped from description
- `COM.12.1` (row 23): bare numbers stripped from description
- `COM.12.2` (row 24): bare numbers stripped from description
- `COM.12.3` (row 25): bare numbers stripped from description
- `COM.13.4` (row 29): bare numbers stripped from description
- `COM.13C` (row 32): bare numbers stripped from description
- `COM.14.1` (row 33): bare numbers stripped from description
- `FIN.15.1` (row 37): bare numbers stripped from description
- `FIN.15.2` (row 38): bare numbers stripped from description
- `FIN.15C` (row 41): bare numbers stripped from description
- `FIN.16.1` (row 43): bare numbers stripped from description
- `FIN.16C` (row 46): bare numbers stripped from description
- `FIN.161` (row 47): bare numbers stripped from description
- `FIN.17.1` (row 48): bare numbers stripped from description
- `FIN.17A` (row 49): bare numbers stripped from description
- `FIN.17C` (row 51): bare numbers stripped from description
- `FIN.171` (row 52): bare numbers stripped from description
- `FIN.18.1` (row 53): bare numbers stripped from description
- `FIN.18C` (row 56): bare numbers stripped from description
- `FIN.19.1` (row 57): bare numbers stripped from description
- `FIN.20.1` (row 62): bare numbers stripped from description
- `FIN.20B` (row 64): bare numbers stripped from description
- `FIN.20C` (row 65): bare numbers stripped from description
- `FIN.201` (row 66): bare numbers stripped from description
- `FIN.21` (row 67): bare numbers stripped from description
- `FIN.21.1` (row 68): bare numbers stripped from description
- `FIN.21A` (row 69): bare numbers stripped from description
- `FIN.21B` (row 70): bare numbers stripped from description
- `FIN.21C` (row 71): bare numbers stripped from description
- `FIN.22.1` (row 72): bare numbers stripped from description
- `FIN.23.1` (row 77): bare numbers stripped from description
- `FIN.23C` (row 80): bare numbers stripped from description
- `FIN.231` (row 81): bare numbers stripped from description
- `FIN.24.1` (row 82): bare numbers stripped from description
- `FIN.24C` (row 85): bare numbers stripped from description
- `FIN.241` (row 86): bare numbers stripped from description
- `FIN.25.1` (row 87): bare numbers stripped from description
- `FIN.25C` (row 90): bare numbers stripped from description
- `FIN.251` (row 91): bare numbers stripped from description
- `FIRE.26.2` (row 93): bare numbers stripped from description
- `FIRE.26.4` (row 95): bare numbers stripped from description
- `FIRE.6.7` (row 98): bare numbers stripped from description
- `FIRE.6.9` (row 100): bare numbers stripped from description
- `FIRE.6.10` (row 101): bare numbers stripped from description
- `FIRE.26C` (row 104): bare numbers stripped from description
- `FIRE.27.1` (row 105): bare numbers stripped from description
- `FIRE.28.1` (row 109): bare numbers stripped from description
- `FIRE.28C` (row 114): bare numbers stripped from description
- `FIRE.29.1` (row 115): bare numbers stripped from description
- `FIRE.29.2` (row 116): bare numbers stripped from description
- `FIRE.3` (row 117): bare numbers stripped from description
- `FIRE.29C` (row 120): bare numbers stripped from description
- `LIB.30.4` (row 121): bare numbers stripped from description
- `LIB.30C` (row 125): bare numbers stripped from description
- `HLTH.32.1` (row 126): bare numbers stripped from description
- `HLTH.32.2` (row 127): bare numbers stripped from description
- `HLTH.32C` (row 130): bare numbers stripped from description
- `HLTH.33.1` (row 131): bare numbers stripped from description
- `HLTH.33C` (row 135): bare numbers stripped from description
- `HLTH.34C` (row 136): bare numbers stripped from description
- `MDO.35.1` (row 137): bare numbers stripped from description
- `MDO.35.3` (row 139): bare numbers stripped from description
- `OHS.36.1` (row 145): bare numbers stripped from description
- `OHS.36.2` (row 146): bare numbers stripped from description
- `OHS.36B` (row 149): bare numbers stripped from description
- `SUST.37.1` (row 151): bare numbers stripped from description
- `SUST.37.2` (row 152): bare numbers stripped from description
- `SUST.37.3` (row 153): bare numbers stripped from description
- `SUST.37A` (row 155): bare numbers stripped from description
- `SUST.37C` (row 157): bare numbers stripped from description
- `OIT.38.1` (row 158): bare numbers stripped from description
- `OIT.38.2` (row 159): bare numbers stripped from description
- `OIT.38C` (row 162): bare numbers stripped from description
- `PRK.39.2` (row 164): bare numbers stripped from description
- `PRK.40.1` (row 169): bare numbers stripped from description
- `PRK.41.1` (row 173): bare numbers stripped from description
- `PRK.41.3` (row 175): bare numbers stripped from description
- `PRK.41A` (row 176): bare numbers stripped from description
- `PRK.41B` (row 177): bare numbers stripped from description
- `PRK.41C` (row 178): bare numbers stripped from description
- `PRK.42.1` (row 179): bare numbers stripped from description
- `PRK.2` (row 180): bare numbers stripped from description
- `PRK.2.3` (row 181): bare numbers stripped from description
- `PRK.2.4` (row 182): bare numbers stripped from description
- `PRK.2.5` (row 183): bare numbers stripped from description
- `PRK.6` (row 184): bare numbers stripped from description
- `PRK.6.7` (row 185): bare numbers stripped from description
- `PRK.6.8` (row 186): bare numbers stripped from description
- `PRK.42B` (row 188): bare numbers stripped from description
- `PRK.42C` (row 189): bare numbers stripped from description
- `PRK.43.1` (row 190): bare numbers stripped from description
- `PRK.2.3-2` (row 192): bare numbers stripped from description
- `PRK.2.4-2` (row 193): bare numbers stripped from description
- `PRK.2.5-2` (row 194): bare numbers stripped from description
- `PRK.43C` (row 198): bare numbers stripped from description
- `PRK.44.1` (row 199): bare numbers stripped from description
- `PRK.44C` (row 201): bare numbers stripped from description
- `PRK.45C` (row 203): bare numbers stripped from description
- `PRK.451` (row 204): bare numbers stripped from description
- `PRK.450` (row 205): bare numbers stripped from description
- `PRK.46.1` (row 206): bare numbers stripped from description
- `PRK.461` (row 210): bare numbers stripped from description
- `PRK.461-2` (row 211): bare numbers stripped from description
- `PRK.47.1` (row 212): bare numbers stripped from description
- `PRK.47C` (row 215): bare numbers stripped from description
- `PRK.48.1` (row 216): bare numbers stripped from description
- `PRK.48C` (row 219): bare numbers stripped from description
- `PRK.481` (row 220): bare numbers stripped from description
- `PRK.480` (row 221): bare numbers stripped from description
- `PRK.49.1` (row 222): bare numbers stripped from description
- `PRK.49C` (row 225): bare numbers stripped from description
- `PRK.50.1` (row 226): bare numbers stripped from description
- `PRK.50A` (row 227): bare numbers stripped from description
- `PRK.51.1` (row 231): bare numbers stripped from description
- `PRK.51A` (row 232): bare numbers stripped from description
- `PRK.51B` (row 233): bare numbers stripped from description
- `PRK.51C` (row 234): bare numbers stripped from description
- `PRK.511` (row 235): bare numbers stripped from description
- `PRK.510` (row 236): bare numbers stripped from description
- `PRK.52.1` (row 237): bare numbers stripped from description
- `PRK.52C` (row 240): bare numbers stripped from description
- `PRK.521` (row 241): bare numbers stripped from description
- `PRK.53.1` (row 242): bare numbers stripped from description
- `PRK.53C` (row 245): bare numbers stripped from description
- `PRK.531` (row 246): bare numbers stripped from description
- `PRK.54.1` (row 248): bare numbers stripped from description
- `PRK.54.2` (row 249): bare numbers stripped from description
- `PRK.54B` (row 251): bare numbers stripped from description
- `PRK.54C` (row 252): bare numbers stripped from description
- `PRK.56A` (row 256): bare numbers stripped from description
- `PRK.56C` (row 258): bare numbers stripped from description
- `PRK.57A` (row 259): bare numbers stripped from description
- `PRK.57B` (row 260): bare numbers stripped from description
- `PRK.57C` (row 261): bare numbers stripped from description
- `PRK.58A` (row 262): bare numbers stripped from description
- `PRK.58B` (row 263): bare numbers stripped from description
- `POL.60.1` (row 267): bare numbers stripped from description
- `POL.4` (row 270): bare numbers stripped from description
- `POL.60C` (row 273): bare numbers stripped from description
- `PRS.61` (row 274): bare numbers stripped from description
- `PRS.61.1` (row 275): bare numbers stripped from description
- `PRS.61.3` (row 277): bare numbers stripped from description
- `PRS.61.4` (row 278): bare numbers stripped from description
- `PRS.61A` (row 279): bare numbers stripped from description
- `PRS.61B` (row 280): bare numbers stripped from description
- `PRS.61C` (row 281): bare numbers stripped from description
- `PPD.62.1` (row 282): bare numbers stripped from description
- `PPD.63.1` (row 286): bare numbers stripped from description
- `PPD.63.2` (row 287): bare numbers stripped from description
- `PPD.63C` (row 295): bare numbers stripped from description
- `REC.64A` (row 296): bare numbers stripped from description
- `STR.65.1` (row 299): bare numbers stripped from description
- `STR.65.2` (row 300): bare numbers stripped from description
- `STR.65.3` (row 301): bare numbers stripped from description
- `STR.65C` (row 305): bare numbers stripped from description
- `STR.66.1` (row 306): bare numbers stripped from description
- `STR.66.3` (row 308): bare numbers stripped from description
- `STR.66C` (row 311): bare numbers stripped from description
- `STR.68.1` (row 312): bare numbers stripped from description
- `STR.68C` (row 315): bare numbers stripped from description
- `STR.69.1` (row 316): bare numbers stripped from description
- `STR.69.2` (row 317): bare numbers stripped from description
- `STR.69.3` (row 318): bare numbers stripped from description
- `STR.69A` (row 322): bare numbers stripped from description
- `STR.69C` (row 324): bare numbers stripped from description
- `STR.70.1` (row 325): bare numbers stripped from description
- `STR.70.2` (row 326): bare numbers stripped from description
- `STR.70.3` (row 327): bare numbers stripped from description
- `STR.70.4` (row 328): bare numbers stripped from description
- `STR.71.1` (row 333): bare numbers stripped from description
- `STR.71.2` (row 334): bare numbers stripped from description
- `STR.71.3` (row 335): bare numbers stripped from description
- `STR.714A` (row 336): bare numbers stripped from description
- `STR.71B` (row 337): bare numbers stripped from description
- `STR.71C` (row 338): bare numbers stripped from description
- `STR.72.2` (row 340): bare numbers stripped from description
- `STR.72.3` (row 341): bare numbers stripped from description
- `STR.72C` (row 344): bare numbers stripped from description
- `STR.73.1` (row 345): bare numbers stripped from description
- `STR.2` (row 346): bare numbers stripped from description
- `STR.2.3` (row 347): bare numbers stripped from description
- `STR.2.4` (row 348): bare numbers stripped from description
- `STR.2.5` (row 349): bare numbers stripped from description
- `STR.2.6` (row 350): bare numbers stripped from description
- `STR.7` (row 351): bare numbers stripped from description
- `TRN.74.2` (row 356): bare numbers stripped from description
- `TRN.74.3` (row 357): bare numbers stripped from description
- `TRN.4` (row 358): bare numbers stripped from description
- `TRN.4.5` (row 359): bare numbers stripped from description
- `TRN.4.6` (row 360): bare numbers stripped from description
- `TRN.75.1` (row 364): bare numbers stripped from description
- `TRN.75.2` (row 365): bare numbers stripped from description
- `TRN.3.4` (row 367): bare numbers stripped from description
- `TRN.76.1` (row 369): bare numbers stripped from description
- `TRN.77.1` (row 371): bare numbers stripped from description
- `WAT.78.14` (row 372): bare numbers stripped from description
- `WAT.78C` (row 376): bare numbers stripped from description
- `WAT.79C` (row 382): bare numbers stripped from description
- `WAT.80.2` (row 384): bare numbers stripped from description
- `WAT.80A` (row 385): bare numbers stripped from description
- `WAT.81A` (row 388): bare numbers stripped from description
- `WAT.81C` (row 390): bare numbers stripped from description

## 2023.csv — Description number cleanup (2026-07-16)

Stripped bare numbers from 223 descriptions via clean_descriptions.py.

- `AVN.2.1` (row 0): bare numbers stripped from description
- `AVN.2A` (row 1): bare numbers stripped from description
- `AVN.3.1` (row 2): bare numbers stripped from description
- `AVN.4.14` (row 4): bare numbers stripped from description
- `AVN.5.1` (row 6): bare numbers stripped from description
- `COM.6.1` (row 7): bare numbers stripped from description
- `COM.6.2` (row 8): bare numbers stripped from description
- `COM.6C` (row 11): bare numbers stripped from description
- `COM.7.1` (row 12): bare numbers stripped from description
- `COM.7C` (row 15): bare numbers stripped from description
- `COM.8.1` (row 16): bare numbers stripped from description
- `COM.10.14` (row 20): bare numbers stripped from description
- `COM.11.1` (row 21): bare numbers stripped from description
- `COM.12.2` (row 23): bare numbers stripped from description
- `COM.12.3` (row 24): bare numbers stripped from description
- `COM.13.1` (row 28): bare numbers stripped from description
- `COM.14.1` (row 32): bare numbers stripped from description
- `COM.14C` (row 35): bare numbers stripped from description
- `FIN.15.1` (row 37): bare numbers stripped from description
- `FIN.15C` (row 40): bare numbers stripped from description
- `FIN.151` (row 41): bare numbers stripped from description
- `FIN.16.1` (row 42): bare numbers stripped from description
- `FIN.16C` (row 45): bare numbers stripped from description
- `FIN.161` (row 46): bare numbers stripped from description
- `FIN.17.1` (row 47): bare numbers stripped from description
- `FIN.17B` (row 49): bare numbers stripped from description
- `FIN.17C` (row 50): bare numbers stripped from description
- `FIN.171` (row 51): bare numbers stripped from description
- `FIN.18.1` (row 52): bare numbers stripped from description
- `FIN.18C` (row 55): bare numbers stripped from description
- `FIN.181` (row 56): bare numbers stripped from description
- `FIN.19.1` (row 57): bare numbers stripped from description
- `FIN.19B` (row 59): bare numbers stripped from description
- `FIN.19C` (row 60): bare numbers stripped from description
- `FIN.191` (row 61): bare numbers stripped from description
- `FIN.20.1` (row 62): bare numbers stripped from description
- `FIN.20C` (row 65): bare numbers stripped from description
- `FIN.201` (row 66): bare numbers stripped from description
- `FIN.21` (row 67): bare numbers stripped from description
- `FIN.21.1` (row 68): bare numbers stripped from description
- `FIN.21A` (row 69): bare numbers stripped from description
- `FIN.21B` (row 70): bare numbers stripped from description
- `FIN.21C` (row 71): bare numbers stripped from description
- `FIN.22.1` (row 72): bare numbers stripped from description
- `FIN.22C` (row 75): bare numbers stripped from description
- `FIN.221` (row 76): bare numbers stripped from description
- `FIN.23.1` (row 77): bare numbers stripped from description
- `FIN.23C` (row 80): bare numbers stripped from description
- `FIN.24.1` (row 81): bare numbers stripped from description
- `FIN.24A` (row 82): bare numbers stripped from description
- `FIN.24B` (row 83): bare numbers stripped from description
- `FIN.24C` (row 84): bare numbers stripped from description
- `FIN.241` (row 85): bare numbers stripped from description
- `FIN.25.1` (row 86): bare numbers stripped from description
- `FIN.25A` (row 87): bare numbers stripped from description
- `FIRE.26.2` (row 92): bare numbers stripped from description
- `FIRE.26.5` (row 95): bare numbers stripped from description
- `FIRE.26.6` (row 96): bare numbers stripped from description
- `FIRE.26.8` (row 98): bare numbers stripped from description
- `FIRE.9` (row 99): bare numbers stripped from description
- `FIRE.9.140` (row 100): bare numbers stripped from description
- `FIRE.26C` (row 103): bare numbers stripped from description
- `FIRE.27.1` (row 104): bare numbers stripped from description
- `FIRE.27B` (row 106): bare numbers stripped from description
- `FIRE.28C` (row 114): bare numbers stripped from description
- `FIRE.29.1` (row 115): bare numbers stripped from description
- `FIRE.29.2` (row 116): bare numbers stripped from description
- `FIRE.29.3` (row 117): bare numbers stripped from description
- `FIRE.29C` (row 120): bare numbers stripped from description
- `LIB.30C` (row 124): bare numbers stripped from description
- `HLTH.32.1` (row 125): bare numbers stripped from description
- `HLTH.32.2` (row 126): bare numbers stripped from description
- `HLTH.32C` (row 129): bare numbers stripped from description
- `HLTH.33.1` (row 130): bare numbers stripped from description
- `HLTH.34B` (row 135): bare numbers stripped from description
- `MDO.35.2` (row 137): bare numbers stripped from description
- `MDO.35.4` (row 139): bare numbers stripped from description
- `MDO.351` (row 144): bare numbers stripped from description
- `OHS.36.1` (row 145): bare numbers stripped from description
- `OHS.36.2` (row 146): bare numbers stripped from description
- `OHS.36C` (row 150): bare numbers stripped from description
- `SUST.37.1` (row 151): bare numbers stripped from description
- `SUST.37.2` (row 152): bare numbers stripped from description
- `SUST.37.3` (row 153): bare numbers stripped from description
- `SUST.37.4` (row 154): bare numbers stripped from description
- `SUST.37.5` (row 155): bare numbers stripped from description
- `SUST.37C` (row 158): bare numbers stripped from description
- `OIT.38.1` (row 159): bare numbers stripped from description
- `OIT.38.2` (row 160): bare numbers stripped from description
- `OIT.38C` (row 163): bare numbers stripped from description
- `PRK.39.1` (row 164): bare numbers stripped from description
- `PRK.39.2` (row 165): bare numbers stripped from description
- `PRK.39C` (row 169): bare numbers stripped from description
- `PRK.40.1` (row 170): bare numbers stripped from description
- `PRK.40C` (row 173): bare numbers stripped from description
- `PRK.41.1` (row 174): bare numbers stripped from description
- `PRK.41.2` (row 175): bare numbers stripped from description
- `PRK.41.3` (row 176): bare numbers stripped from description
- `PRK.41A` (row 177): bare numbers stripped from description
- `PRK.41B` (row 178): bare numbers stripped from description
- `PRK.42.1` (row 180): bare numbers stripped from description
- `PRK.42.2` (row 181): bare numbers stripped from description
- `PRK.4` (row 183): bare numbers stripped from description
- `PRK.4.5` (row 184): bare numbers stripped from description
- `PRK.4.6` (row 185): bare numbers stripped from description
- `PRK.4.7` (row 186): bare numbers stripped from description
- `PRK.4.8` (row 187): bare numbers stripped from description
- `PRK.43.1` (row 191): bare numbers stripped from description
- `PRK.43.2` (row 192): bare numbers stripped from description
- `PRK.3` (row 193): bare numbers stripped from description
- `PRK.3.5` (row 195): bare numbers stripped from description
- `PRK.43C` (row 198): bare numbers stripped from description
- `PRK.44.1` (row 199): bare numbers stripped from description
- `PRK.44B` (row 201): bare numbers stripped from description
- `PRK.44C` (row 202): bare numbers stripped from description
- `PRK.45.1` (row 203): bare numbers stripped from description
- `PRK.45C` (row 206): bare numbers stripped from description
- `PRK.451` (row 207): bare numbers stripped from description
- `PRK.450` (row 208): bare numbers stripped from description
- `PRK.46.1` (row 209): bare numbers stripped from description
- `PRK.46C` (row 212): bare numbers stripped from description
- `PRK.461` (row 213): bare numbers stripped from description
- `PRK.460` (row 214): bare numbers stripped from description
- `PRK.47.1` (row 215): bare numbers stripped from description
- `PRK.47B` (row 217): bare numbers stripped from description
- `PRK.47C` (row 218): bare numbers stripped from description
- `PRK.48.1` (row 219): bare numbers stripped from description
- `PRK.48C` (row 222): bare numbers stripped from description
- `PRK.481` (row 223): bare numbers stripped from description
- `PRK.49.1` (row 225): bare numbers stripped from description
- `PRK.49C` (row 228): bare numbers stripped from description
- `PRK.491` (row 229): bare numbers stripped from description
- `PRK.50.1` (row 230): bare numbers stripped from description
- `PRK.50C` (row 233): bare numbers stripped from description
- `PRK.501` (row 234): bare numbers stripped from description
- `PRK.500` (row 235): bare numbers stripped from description
- `PRK.51.1` (row 236): bare numbers stripped from description
- `PRK.51A` (row 237): bare numbers stripped from description
- `PRK.51B` (row 238): bare numbers stripped from description
- `PRK.51C` (row 239): bare numbers stripped from description
- `PRK.511` (row 240): bare numbers stripped from description
- `PRK.52.1` (row 241): bare numbers stripped from description
- `PRK.52C` (row 244): bare numbers stripped from description
- `PRK.521` (row 245): bare numbers stripped from description
- `PRK.53.1` (row 247): bare numbers stripped from description
- `PRK.53C` (row 250): bare numbers stripped from description
- `PRK.531` (row 251): bare numbers stripped from description
- `PRK.54.2` (row 253): bare numbers stripped from description
- `PRK.54C` (row 256): bare numbers stripped from description
- `PRK.56C` (row 262): bare numbers stripped from description
- `PRK.57A` (row 263): bare numbers stripped from description
- `PRK.57C` (row 264): bare numbers stripped from description
- `PRK.59A` (row 267): bare numbers stripped from description
- `PRK.59B` (row 268): bare numbers stripped from description
- `PRK.59C` (row 269): bare numbers stripped from description
- `PRK.59C-2` (row 270): bare numbers stripped from description
- `POL.60.1` (row 271): bare numbers stripped from description
- `POL.60.2` (row 272): bare numbers stripped from description
- `POL.4` (row 274): bare numbers stripped from description
- `POL.60C` (row 277): bare numbers stripped from description
- `PRS.61` (row 279): bare numbers stripped from description
- `PRS.61.2` (row 281): bare numbers stripped from description
- `PRS.61.3` (row 282): bare numbers stripped from description
- `PRS.61A` (row 283): bare numbers stripped from description
- `PRS.61B` (row 284): bare numbers stripped from description
- `PRS.61C` (row 285): bare numbers stripped from description
- `PPD.62.1` (row 286): bare numbers stripped from description
- `PPD.62B` (row 288): bare numbers stripped from description
- `PPD.63.1` (row 290): bare numbers stripped from description
- `PPD.63.2` (row 291): bare numbers stripped from description
- `PPD.63.3` (row 292): bare numbers stripped from description
- `REC.64A` (row 297): bare numbers stripped from description
- `STR.65.1` (row 300): bare numbers stripped from description
- `STR.65.2` (row 301): bare numbers stripped from description
- `STR.65.3` (row 302): bare numbers stripped from description
- `STR.65.4` (row 303): bare numbers stripped from description
- `STR.66.1` (row 307): bare numbers stripped from description
- `STR.66.2` (row 308): bare numbers stripped from description
- `STR.66C` (row 311): bare numbers stripped from description
- `STR.68.1` (row 312): bare numbers stripped from description
- `STR.68A` (row 313): bare numbers stripped from description
- `STR.69.1` (row 316): bare numbers stripped from description
- `STR.69.2` (row 317): bare numbers stripped from description
- `STR.69.3` (row 318): bare numbers stripped from description
- `STR.69B` (row 322): bare numbers stripped from description
- `STR.69C` (row 323): bare numbers stripped from description
- `STR.70.1` (row 324): bare numbers stripped from description
- `STR.70.2` (row 325): bare numbers stripped from description
- `STR.70.3` (row 326): bare numbers stripped from description
- `STR.70.4` (row 327): bare numbers stripped from description
- `STR.71.1` (row 331): bare numbers stripped from description
- `STR.71.2` (row 332): bare numbers stripped from description
- `STR.71A` (row 334): bare numbers stripped from description
- `STR.71B` (row 335): bare numbers stripped from description
- `STR.71C` (row 336): bare numbers stripped from description
- `STR.72.1` (row 337): bare numbers stripped from description
- `STR.72.2` (row 338): bare numbers stripped from description
- `STR.72C` (row 342): bare numbers stripped from description
- `STR.73.1` (row 343): bare numbers stripped from description
- `STR.73.2` (row 344): bare numbers stripped from description
- `STR.73.3` (row 345): bare numbers stripped from description
- `STR.73.4` (row 346): bare numbers stripped from description
- `STR.5-2` (row 347): bare numbers stripped from description
- `STR.5.6` (row 348): bare numbers stripped from description
- `STR.5.7` (row 349): bare numbers stripped from description
- `STR.73C` (row 352): bare numbers stripped from description
- `TRN.74.1` (row 353): bare numbers stripped from description
- `TRN.74.2` (row 354): bare numbers stripped from description
- `TRN.74.3` (row 355): bare numbers stripped from description
- `TRN.4` (row 356): bare numbers stripped from description
- `TRN.4.5` (row 357): bare numbers stripped from description
- `TRN.4.6` (row 358): bare numbers stripped from description
- `TRN.75.2` (row 363): bare numbers stripped from description
- `TRN.3.4` (row 365): bare numbers stripped from description
- `TRN.75A` (row 366): bare numbers stripped from description
- `TRN.76.1` (row 367): bare numbers stripped from description
- `TRN.77.1` (row 369): bare numbers stripped from description
- `TRN.78.4` (row 371): bare numbers stripped from description
- `WAT.80.8` (row 383): bare numbers stripped from description
- `WAT.81A` (row 386): bare numbers stripped from description
- `WAT.81B` (row 387): bare numbers stripped from description
- `WAT.81C` (row 388): bare numbers stripped from description
- `WAT.82.1` (row 389): bare numbers stripped from description

## 2024.csv — Description number cleanup (2026-07-16)

Stripped bare numbers from 216 descriptions via clean_descriptions.py.

- `AVN.2.1` (row 0): bare numbers stripped from description
- `AVN.3.1` (row 2): bare numbers stripped from description
- `AVN.4.1` (row 4): bare numbers stripped from description
- `AVN.4A` (row 5): bare numbers stripped from description
- `AVN.5.1` (row 6): bare numbers stripped from description
- `COM.6.1` (row 7): bare numbers stripped from description
- `COM.6B` (row 10): bare numbers stripped from description
- `COM.6C` (row 11): bare numbers stripped from description
- `COM.7.1` (row 12): bare numbers stripped from description
- `COM.7B` (row 14): bare numbers stripped from description
- `COM.7C` (row 15): bare numbers stripped from description
- `COM.8.1` (row 16): bare numbers stripped from description
- `COM.8.2` (row 17): bare numbers stripped from description
- `COM.10.1` (row 20): bare numbers stripped from description
- `COM.12.1` (row 22): bare numbers stripped from description
- `COM.12.2` (row 23): bare numbers stripped from description
- `COM.12.3` (row 24): bare numbers stripped from description
- `COM.12C` (row 26): bare numbers stripped from description
- `COM.13.1` (row 27): bare numbers stripped from description
- `COM.13C` (row 30): bare numbers stripped from description
- `COM.14.1` (row 31): bare numbers stripped from description
- `COM.14C` (row 34): bare numbers stripped from description
- `FIN.15.1` (row 35): bare numbers stripped from description
- `FIN.15C` (row 38): bare numbers stripped from description
- `FIN.151` (row 39): bare numbers stripped from description
- `FIN.16.1` (row 40): bare numbers stripped from description
- `FIN.16C` (row 43): bare numbers stripped from description
- `FIN.161` (row 44): bare numbers stripped from description
- `FIN.17.1` (row 45): bare numbers stripped from description
- `FIN.17C` (row 47): bare numbers stripped from description
- `FIN.18.1` (row 48): bare numbers stripped from description
- `FIN.18C` (row 51): bare numbers stripped from description
- `FIN.181` (row 52): bare numbers stripped from description
- `FIN.19.1` (row 53): bare numbers stripped from description
- `FIN.20.1` (row 58): bare numbers stripped from description
- `FIN.20C` (row 61): bare numbers stripped from description
- `FIN.201` (row 62): bare numbers stripped from description
- `FIN.21` (row 63): bare numbers stripped from description
- `FIN.21.1` (row 64): bare numbers stripped from description
- `FIN.241A` (row 65): bare numbers stripped from description
- `FIN.21B` (row 66): bare numbers stripped from description
- `FIN.21C` (row 67): bare numbers stripped from description
- `FIN.22.1` (row 68): bare numbers stripped from description
- `FIN.22C` (row 71): bare numbers stripped from description
- `FIN.221` (row 72): bare numbers stripped from description
- `FIN.23.1` (row 73): bare numbers stripped from description
- `FIN.23C` (row 76): bare numbers stripped from description
- `FIN.230` (row 77): bare numbers stripped from description
- `FIN.24.1` (row 78): bare numbers stripped from description
- `FIN.24C` (row 81): bare numbers stripped from description
- `FIN.241` (row 82): bare numbers stripped from description
- `FIN.25.1` (row 83): bare numbers stripped from description
- `FIN.251` (row 87): bare numbers stripped from description
- `FIRE.26.1` (row 88): bare numbers stripped from description
- `FIRE.26.4` (row 91): bare numbers stripped from description
- `FIRE.26.5` (row 92): bare numbers stripped from description
- `FIRE.26.6` (row 93): bare numbers stripped from description
- `FIRE.26.7` (row 94): bare numbers stripped from description
- `FIRE.8` (row 95): bare numbers stripped from description
- `FIRE.8.9` (row 96): bare numbers stripped from description
- `FIRE.27C` (row 104): bare numbers stripped from description
- `FIRE.28.2` (row 106): bare numbers stripped from description
- `FIRE.28C` (row 111): bare numbers stripped from description
- `FIRE.29.1` (row 112): bare numbers stripped from description
- `FIRE.2` (row 113): bare numbers stripped from description
- `FIRE.2.3` (row 114): bare numbers stripped from description
- `LIB.30A` (row 119): bare numbers stripped from description
- `LIB.30C` (row 121): bare numbers stripped from description
- `HLTH.31.1` (row 122): bare numbers stripped from description
- `HLTH.31.2` (row 123): bare numbers stripped from description
- `HLTH.31A` (row 124): bare numbers stripped from description
- `HLTH.31C` (row 125): bare numbers stripped from description
- `HLTH.32.2` (row 127): bare numbers stripped from description
- `MDO.33.1` (row 131): bare numbers stripped from description
- `MDO.33.4` (row 134): bare numbers stripped from description
- `MDO.33.5` (row 135): bare numbers stripped from description
- `MDO.6.7` (row 137): bare numbers stripped from description
- `MDO.33C` (row 140): bare numbers stripped from description
- `OHS.34.1` (row 142): bare numbers stripped from description
- `OHS.34.2` (row 143): bare numbers stripped from description
- `OHS.34B` (row 146): bare numbers stripped from description
- `OHS.34C` (row 147): bare numbers stripped from description
- `SUST.35.1` (row 148): bare numbers stripped from description
- `SUST.35.2` (row 149): bare numbers stripped from description
- `SUST.35.3` (row 150): bare numbers stripped from description
- `SUST.35.4` (row 151): bare numbers stripped from description
- `SUST.35.5` (row 152): bare numbers stripped from description
- `SUST.6` (row 153): bare numbers stripped from description
- `SUST.35A` (row 154): bare numbers stripped from description
- `OIT.36.1` (row 157): bare numbers stripped from description
- `OIT.36.2` (row 158): bare numbers stripped from description
- `OIT.36B` (row 160): bare numbers stripped from description
- `OIT.36C` (row 161): bare numbers stripped from description
- `PRK.37.1` (row 163): bare numbers stripped from description
- `PRK.37.2` (row 164): bare numbers stripped from description
- `PRK.37C` (row 168): bare numbers stripped from description
- `PRK.38.4` (row 169): bare numbers stripped from description
- `PRK.38C` (row 172): bare numbers stripped from description
- `PRK.39.1` (row 173): bare numbers stripped from description
- `PRK.39.3` (row 174): bare numbers stripped from description
- `PRK.39C` (row 177): bare numbers stripped from description
- `PRK.40.2` (row 179): bare numbers stripped from description
- `PRK.40.4` (row 181): bare numbers stripped from description
- `PRK.6` (row 183): bare numbers stripped from description
- `PRK.6.7` (row 184): bare numbers stripped from description
- `PRK.6.8` (row 185): bare numbers stripped from description
- `PRK.40C` (row 188): bare numbers stripped from description
- `PRK.401` (row 189): bare numbers stripped from description
- `PRK.401.1` (row 190): bare numbers stripped from description
- `PRK.3` (row 192): bare numbers stripped from description
- `PRK.3.4` (row 193): bare numbers stripped from description
- `PRK.3.5` (row 194): bare numbers stripped from description
- `PRK.41A` (row 195): bare numbers stripped from description
- `PRK.41B` (row 196): bare numbers stripped from description
- `PRK.41C` (row 197): bare numbers stripped from description
- `PRK.42.1` (row 198): bare numbers stripped from description
- `PRK.42C` (row 201): bare numbers stripped from description
- `PRK.421` (row 202): bare numbers stripped from description
- `PRK.43.1` (row 203): bare numbers stripped from description
- `PRK.430` (row 207): bare numbers stripped from description
- `PRK.44.1` (row 208): bare numbers stripped from description
- `PRK.45.1` (row 214): bare numbers stripped from description
- `PRK.46.1` (row 220): bare numbers stripped from description
- `PRK.46B` (row 222): bare numbers stripped from description
- `PRK.46C` (row 223): bare numbers stripped from description
- `PRK.47.1` (row 226): bare numbers stripped from description
- `PRK.47C` (row 229): bare numbers stripped from description
- `PRK.48.1` (row 230): bare numbers stripped from description
- `PRK.48C` (row 233): bare numbers stripped from description
- `PRK.480` (row 234): bare numbers stripped from description
- `PRK.49.1` (row 235): bare numbers stripped from description
- `PRK.49C` (row 238): bare numbers stripped from description
- `PRK.490` (row 239): bare numbers stripped from description
- `PRK.50.1` (row 240): bare numbers stripped from description
- `PRK.50C` (row 243): bare numbers stripped from description
- `PRK.501` (row 244): bare numbers stripped from description
- `PRK.500` (row 245): bare numbers stripped from description
- `PRK.51.1` (row 246): bare numbers stripped from description
- `PRK.51A` (row 247): bare numbers stripped from description
- `PRK.51B` (row 248): bare numbers stripped from description
- `PRK.51C` (row 249): bare numbers stripped from description
- `PRK.511` (row 250): bare numbers stripped from description
- `PRK.510` (row 251): bare numbers stripped from description
- `PRK.52C` (row 256): bare numbers stripped from description
- `PRK.53C` (row 259): bare numbers stripped from description
- `PRK.54B` (row 261): bare numbers stripped from description
- `PRK.54C` (row 262): bare numbers stripped from description
- `PRK.55A` (row 263): bare numbers stripped from description
- `PRK.55B` (row 264): bare numbers stripped from description
- `PRK.57C` (row 268): bare numbers stripped from description
- `POL.58.1` (row 269): bare numbers stripped from description
- `POL.3` (row 271): bare numbers stripped from description
- `POL.3.4` (row 272): bare numbers stripped from description
- `POL.58C` (row 275): bare numbers stripped from description
- `PRS.59.2` (row 278): bare numbers stripped from description
- `PRS.59.4` (row 279): bare numbers stripped from description
- `PRS.59.5` (row 280): bare numbers stripped from description
- `PRS.59C` (row 285): bare numbers stripped from description
- `PPD.60.1` (row 286): bare numbers stripped from description
- `PPD.61.1` (row 290): bare numbers stripped from description
- `PPD.61.2` (row 291): bare numbers stripped from description
- `PPD.4.623` (row 293): bare numbers stripped from description
- `PPD.4.5` (row 294): bare numbers stripped from description
- `PPD.61A` (row 295): bare numbers stripped from description
- `PPD.61B` (row 296): bare numbers stripped from description
- `PPD.61C` (row 297): bare numbers stripped from description
- `REC.62A` (row 298): bare numbers stripped from description
- `STR.63.1` (row 301): bare numbers stripped from description
- `STR.63.2` (row 302): bare numbers stripped from description
- `STR.63.3` (row 303): bare numbers stripped from description
- `STR.4` (row 304): bare numbers stripped from description
- `STR.64C` (row 312): bare numbers stripped from description
- `STR.65.1` (row 313): bare numbers stripped from description
- `STR.65C` (row 316): bare numbers stripped from description
- `STR.66.1` (row 317): bare numbers stripped from description
- `STR.66.2` (row 318): bare numbers stripped from description
- `STR.66.3` (row 319): bare numbers stripped from description
- `STR.4-2` (row 320): bare numbers stripped from description
- `STR.66B` (row 324): bare numbers stripped from description
- `STR.67.1` (row 326): bare numbers stripped from description
- `STR.67.2` (row 327): bare numbers stripped from description
- `STR.67A` (row 328): bare numbers stripped from description
- `STR.68.1` (row 331): bare numbers stripped from description
- `STR.68C` (row 336): bare numbers stripped from description
- `STR.69.1` (row 337): bare numbers stripped from description
- `STR.69.2` (row 338): bare numbers stripped from description
- `STR.69C` (row 342): bare numbers stripped from description
- `STR.70` (row 343): bare numbers stripped from description
- `STR.70.2` (row 344): bare numbers stripped from description
- `STR.3-2` (row 345): bare numbers stripped from description
- `STR.3.4` (row 346): bare numbers stripped from description
- `STR.3.5` (row 347): bare numbers stripped from description
- `STR.3.6` (row 348): bare numbers stripped from description
- `STR.7` (row 349): bare numbers stripped from description
- `STR.70.8` (row 350): bare numbers stripped from description
- `STR.70C` (row 353): bare numbers stripped from description
- `TRN.71.1` (row 354): bare numbers stripped from description
- `TRN.71.2` (row 355): bare numbers stripped from description
- `TRN.71.3` (row 356): bare numbers stripped from description
- `TRN.4` (row 357): bare numbers stripped from description
- `TRN.4.5` (row 358): bare numbers stripped from description
- `TRN.4.6` (row 359): bare numbers stripped from description
- `TRN.71A` (row 360): bare numbers stripped from description
- `TRN.71B` (row 361): bare numbers stripped from description
- `TRN.71C` (row 362): bare numbers stripped from description
- `TRN.72.1` (row 363): bare numbers stripped from description
- `TRN.72.2` (row 364): bare numbers stripped from description
- `TRN.72.4` (row 366): bare numbers stripped from description
- `TRN.73.1` (row 369): bare numbers stripped from description
- `TRN.74.1` (row 372): bare numbers stripped from description
- `TRN.74.2` (row 373): bare numbers stripped from description
- `WAT.75.1` (row 375): bare numbers stripped from description
- `WAT.75C` (row 379): bare numbers stripped from description
- `WAT.76C` (row 385): bare numbers stripped from description
- `WAT.77.2` (row 387): bare numbers stripped from description
- `ZOO.79.1` (row 395): bare numbers stripped from description

## 2025.csv — Description number cleanup (2026-07-16)

Stripped bare numbers from 173 descriptions via clean_descriptions.py.

- `AVN.2.1` (row 2): bare numbers stripped from description
- `AVN.2A` (row 3): bare numbers stripped from description
- `AVN.2B` (row 4): bare numbers stripped from description
- `AVN.3.1` (row 5): bare numbers stripped from description
- `AVN.3B` (row 7): bare numbers stripped from description
- `AVN.4.1` (row 8): bare numbers stripped from description
- `AVN.4B` (row 9): bare numbers stripped from description
- `AVN.5.1` (row 10): bare numbers stripped from description
- `COM.6.1` (row 12): bare numbers stripped from description
- `COM.7.1` (row 16): bare numbers stripped from description
- `COM.8.1` (row 19): bare numbers stripped from description
- `COM.2` (row 20): bare numbers stripped from description
- `COM.10.1` (row 24): bare numbers stripped from description
- `COM.1.1` (row 25): bare numbers stripped from description
- `COM.12.3` (row 28): bare numbers stripped from description
- `COM.12B` (row 30): bare numbers stripped from description
- `COM.13.1` (row 32): bare numbers stripped from description
- `COM.14.1` (row 36): bare numbers stripped from description
- `FIN.15.1` (row 40): bare numbers stripped from description
- `FIN.17.1` (row 50): bare numbers stripped from description
- `FIN.171` (row 54): bare numbers stripped from description
- `FIN.18.1` (row 56): bare numbers stripped from description
- `FIN.19.1` (row 61): bare numbers stripped from description
- `FIN.191` (row 65): bare numbers stripped from description
- `FIN.20.1` (row 66): bare numbers stripped from description
- `FIN.21` (row 72): bare numbers stripped from description
- `FIN.21C` (row 76): bare numbers stripped from description
- `FIN.22.1` (row 78): bare numbers stripped from description
- `FIN.23.1` (row 83): bare numbers stripped from description
- `FIN.25.1` (row 93): bare numbers stripped from description
- `FIRE.26.1` (row 99): bare numbers stripped from description
- `FIRE.26.2` (row 100): bare numbers stripped from description
- `FIRE.26.3` (row 101): bare numbers stripped from description
- `FIRE.26.4` (row 102): bare numbers stripped from description
- `FIRE.26.5` (row 103): bare numbers stripped from description
- `FIRE.26.6` (row 104): bare numbers stripped from description
- `FIRE.26.7` (row 105): bare numbers stripped from description
- `FIRE.26.8` (row 106): bare numbers stripped from description
- `FIRE.26.9` (row 107): bare numbers stripped from description
- `FIRE.26.10` (row 108): bare numbers stripped from description
- `FIRE.26.11` (row 109): bare numbers stripped from description
- `FIRE.27.1` (row 113): bare numbers stripped from description
- `FIRE.28.2` (row 118): bare numbers stripped from description
- `FIRE.29.2` (row 124): bare numbers stripped from description
- `FIRE.3` (row 125): bare numbers stripped from description
- `LIB.30.1` (row 129): bare numbers stripped from description
- `HLTH.31.1` (row 133): bare numbers stripped from description
- `HLTH.31.2` (row 134): bare numbers stripped from description
- `HLTH.32` (row 138): bare numbers stripped from description
- `MDO.33.1` (row 143): bare numbers stripped from description
- `MDO.33.2` (row 144): bare numbers stripped from description
- `MDO.33.5` (row 146): bare numbers stripped from description
- `MDO.33.6` (row 147): bare numbers stripped from description
- `MDO.7` (row 148): bare numbers stripped from description
- `OHS.34.1` (row 152): bare numbers stripped from description
- `OHS.34.2` (row 153): bare numbers stripped from description
- `OHS.34.3` (row 154): bare numbers stripped from description
- `SUST.35.1` (row 158): bare numbers stripped from description
- `SUST.35.3` (row 160): bare numbers stripped from description
- `SUST.35.5` (row 162): bare numbers stripped from description
- `SUST.6` (row 163): bare numbers stripped from description
- `OIT.36.1` (row 166): bare numbers stripped from description
- `OIT.36.2` (row 167): bare numbers stripped from description
- `PRK.37.1` (row 172): bare numbers stripped from description
- `PRK.37.2` (row 173): bare numbers stripped from description
- `PRK.37.4` (row 175): bare numbers stripped from description
- `PRK.37C` (row 178): bare numbers stripped from description
- `PRK.39.1` (row 182): bare numbers stripped from description
- `PRK.39.2` (row 183): bare numbers stripped from description
- `PRK.3` (row 184): bare numbers stripped from description
- `PRK.40.1` (row 188): bare numbers stripped from description
- `PRK.40.2` (row 189): bare numbers stripped from description
- `PRK.40.3` (row 190): bare numbers stripped from description
- `PRK.40.4` (row 191): bare numbers stripped from description
- `PRK.40.5` (row 192): bare numbers stripped from description
- `PRK.6` (row 193): bare numbers stripped from description
- `PRK.6.7` (row 194): bare numbers stripped from description
- `PRK.6.8` (row 195): bare numbers stripped from description
- `PRK.401` (row 199): bare numbers stripped from description
- `PRK.41.1` (row 200): bare numbers stripped from description
- `PRK.3-2` (row 202): bare numbers stripped from description
- `PRK.3.4` (row 203): bare numbers stripped from description
- `PRK.3.5` (row 204): bare numbers stripped from description
- `PRK.3.8` (row 205): bare numbers stripped from description
- `PRK.42.4` (row 210): bare numbers stripped from description
- `PRK.43.1` (row 214): bare numbers stripped from description
- `PRK.44.1` (row 220): bare numbers stripped from description
- `PRK.45.1` (row 223): bare numbers stripped from description
- `PRK.450` (row 228): bare numbers stripped from description
- `PRK.46.1` (row 229): bare numbers stripped from description
- `PRK.46B` (row 231): bare numbers stripped from description
- `PRK.47.1` (row 235): bare numbers stripped from description
- `PRK.47B` (row 237): bare numbers stripped from description
- `PRK.48.1` (row 238): bare numbers stripped from description
- `PRK.49.1` (row 243): bare numbers stripped from description
- `PRK.49B` (row 245): bare numbers stripped from description
- `PRK.50.1` (row 248): bare numbers stripped from description
- `PRK.51.1` (row 253): bare numbers stripped from description
- `PRK.51C` (row 256): bare numbers stripped from description
- `PRK.51C.8` (row 257): bare numbers stripped from description
- `PRK.511` (row 258): bare numbers stripped from description
- `PRK.52.14` (row 260): bare numbers stripped from description
- `PRK.53A` (row 265): bare numbers stripped from description
- `PRK.53C` (row 267): bare numbers stripped from description
- `PRK.54B` (row 269): bare numbers stripped from description
- `PRK.55A` (row 271): bare numbers stripped from description
- `POL.58.1` (row 276): bare numbers stripped from description
- `POL.58.3` (row 278): bare numbers stripped from description
- `POL.58.4` (row 279): bare numbers stripped from description
- `PRS.59.1` (row 284): bare numbers stripped from description
- `PRS.59.2` (row 285): bare numbers stripped from description
- `PRS.59.3` (row 286): bare numbers stripped from description
- `PRS.59.4` (row 287): bare numbers stripped from description
- `PPD.60.1` (row 291): bare numbers stripped from description
- `PPD.61.1` (row 295): bare numbers stripped from description
- `PPD.61.2` (row 296): bare numbers stripped from description
- `PPD.61.3` (row 297): bare numbers stripped from description
- `REC.62.1` (row 301): bare numbers stripped from description
- `REC.63.1` (row 303): bare numbers stripped from description
- `REC.63.2` (row 304): bare numbers stripped from description
- `REC.63.3` (row 305): bare numbers stripped from description
- `STR.64.1` (row 309): bare numbers stripped from description
- `STR.64.2` (row 310): bare numbers stripped from description
- `STR.64.3` (row 311): bare numbers stripped from description
- `STR.4` (row 312): bare numbers stripped from description
- `STR.65.1` (row 315): bare numbers stripped from description
- `STR.65.2` (row 316): bare numbers stripped from description
- `STR.66.1` (row 320): bare numbers stripped from description
- `STR.67.1` (row 323): bare numbers stripped from description
- `STR.67.2` (row 324): bare numbers stripped from description
- `STR.67.3` (row 325): bare numbers stripped from description
- `STR.4-2` (row 326): bare numbers stripped from description
- `STR.4.5` (row 327): bare numbers stripped from description
- `STR.4.6` (row 328): bare numbers stripped from description
- `STR.4.7` (row 329): bare numbers stripped from description
- `STR.68.1` (row 334): bare numbers stripped from description
- `STR.68.3` (row 336): bare numbers stripped from description
- `STR.69.1` (row 339): bare numbers stripped from description
- `STR.69.2` (row 340): bare numbers stripped from description
- `STR.70.1` (row 345): bare numbers stripped from description
- `STR.71.1` (row 346): bare numbers stripped from description
- `STR.2.3` (row 348): bare numbers stripped from description
- `STR.2.4` (row 349): bare numbers stripped from description
- `STR.6` (row 351): bare numbers stripped from description
- `STR.6.7` (row 352): bare numbers stripped from description
- `STR.6.8` (row 353): bare numbers stripped from description
- `TRN.72.1` (row 355): bare numbers stripped from description
- `TRN.72.2` (row 356): bare numbers stripped from description
- `TRN.72.3` (row 357): bare numbers stripped from description
- `TRN.4` (row 358): bare numbers stripped from description
- `TRN.4.5` (row 359): bare numbers stripped from description
- `TRN.4.6` (row 360): bare numbers stripped from description
- `TRN.73.1` (row 363): bare numbers stripped from description
- `TRN.73.2` (row 364): bare numbers stripped from description
- `TRN.3` (row 365): bare numbers stripped from description
- `TRN.3.4` (row 366): bare numbers stripped from description
- `TRN.74.1` (row 369): bare numbers stripped from description
- `TRN.74B` (row 370): bare numbers stripped from description
- `TRN.75.1` (row 371): bare numbers stripped from description
- `TRN.2` (row 372): bare numbers stripped from description
- `WAT.76.1` (row 375): bare numbers stripped from description
- `WAT.76.2` (row 376): bare numbers stripped from description
- `WAT.77.1` (row 380): bare numbers stripped from description
- `WAT.77.2` (row 381): bare numbers stripped from description
- `WAT.77.3` (row 382): bare numbers stripped from description
- `WAT.77C` (row 385): bare numbers stripped from description
- `WAT.78.4` (row 386): bare numbers stripped from description
- `WAT.78.2` (row 387): bare numbers stripped from description
- `WAT.78.3` (row 388): bare numbers stripped from description
- `WAT.79.1` (row 392): bare numbers stripped from description
- `WAT.79B` (row 394): bare numbers stripped from description
- `ZOO.80.1` (row 396): bare numbers stripped from description
- `ZOO.80.3` (row 398): bare numbers stripped from description

## 2024.csv — Description number cleanup (2026-07-16)

Stripped bare numbers from 2 descriptions via clean_descriptions.py.

- `OHS.34C` (row 147): bare numbers stripped from description
- `WAT.76C` (row 385): bare numbers stripped from description
