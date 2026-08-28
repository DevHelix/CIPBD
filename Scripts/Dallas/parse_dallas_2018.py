#!/usr/bin/env python3
"""
Dallas CIP 2018 PDF parser.
Uses PyMuPDF (pymupdf) to handle landscape (rotation=270) pages correctly.
"""

import pymupdf as fitz
import csv, re, os

PDF_PATH = r"C:\Users\vince\Documents\GitHub\CIPBD\Dallas\PDF\2018.pdf"
CSV_PATH = r"C:\Users\vince\Documents\GitHub\CIPBD\Scripts\Dallas\outputs\2018.csv"

FIELDNAMES = [
    'cip_year', 'project_type', 'source_page', 'department', 'project_name', 'council_district', 'start_year', 'end_year',
    'previous_appropriations', 'project_total',
    'year_2019', 'year_2020', 'year_2021', 'year_2022', 'year_2023',
]


def clean_num(s):
    s = str(s).strip().lstrip('$').replace(',', '').replace('(', '-').replace(')', '')
    try:
        return int(float(s)) if s else 0
    except ValueError:
        return 0


def is_unit(s):
    return bool(re.match(r'^U_', s))


def is_fund(s):
    return bool(re.match(r'^F_', s))


def is_number_str(s):
    return bool(re.match(r'^\$?-?[\d,]+$', s.strip()))


def is_amount(s):
    s = s.strip()
    if s == '0':
        return True
    if re.match(r'^\$', s):
        return True
    if not re.match(r'^[\d,]+$', s):
        return False
    return ',' in s or len(re.sub(r'\D', '', s)) >= 4


def is_district(s):
    """Council district: text like 'Citywide'/'CW', small int 1-20, or comma-list like '1, 2, 6'."""
    s = s.strip()
    if not s:
        return False
    if re.match(r'^[A-Za-z]', s):
        return True
    # Single integer
    try:
        return 0 < int(s) <= 20
    except ValueError:
        pass
    # Comma-separated list of district numbers e.g. "1, 2, 6"
    parts = re.split(r'[\s,]+', s)
    try:
        return bool(parts) and all(0 < int(p) <= 20 for p in parts if p)
    except ValueError:
        return False


def is_total_row(s):
    """'Total X' subtotal rows (but not 'Total Budget' header)."""
    return bool(re.match(r'^Total\b', s.strip(), re.I)) and s.strip() != 'Total Budget'


def expand_lines(lines):
    """Split lines that contain multiple space-separated numbers into individual entries."""
    result = []
    for line in lines:
        parts = line.split()
        if (len(parts) >= 2 and all(re.match(r'^\$?[\d,]+$', p) for p in parts) and all(not p.endswith(',') for p in parts)):
            result.extend(parts)
        else:
            result.append(line)
    return result


def find_header_end(lines):
    """Return index of first data line after column headers."""
    for i, l in enumerate(lines):
        if l == 'Total Budget':
            return i + 1
        if l == 'Total' and i + 1 < len(lines) and lines[i + 1] == 'Budget':
            return i + 2
    return 0


def dept_name_from_page(txt):
    """
    Extract department name from a rot=0 page.
    Returns '' if the page is not a department section header.
    """
    lines = [l.strip() for l in txt.split('\n') if l.strip()]
    if not lines:
        return ''
    first = lines[0]
    # Page-number-only pages (e.g. "398")
    if re.match(r'^\d{3,4}$', first):
        return ''
    # Introductory pages like "FY 2018-19 CAPITAL BUDGET"
    if re.search(r'\d{4}', first):
        return ''
    # Operating & maintenance pages — skip
    if 'OPERATING AND MAINTENANCE' in txt:
        return ''
    # Must look like an all-caps department name
    if re.match(r'^[A-Z][A-Z\s&/()\-]+$', first):
        return first.title()
    return ''


def parse_project_page(lines, department, page_num, current_category):
    """
    Parse data lines from a rot=270 page.
    Returns (records, current_category) so category carries across pages.
    """
    records = []
    after_total = True   # treat page start like after a Total row
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        # Stop at "Total by Department" footer
        if re.match(r'^Total\s+by\s+Department', line, re.I):
            break

        # Skip page-number lines and stray department-name echoes at page footer
        if re.match(r'^\d{3,4}$', line):
            i += 1
            continue

        # Skip "Total X" rows and consume their trailing numbers
        if is_total_row(line):
            i += 1
            while i < n and is_number_str(lines[i]):
                i += 1
            after_total = True
            continue

        # Accumulate non-unit, non-amount lines as potential name parts.
        # Small bare integers (e.g. "12" in "Loop 12") are allowed.
        name_parts = []
        while i < n:
            l = lines[i]
            if is_unit(l) or is_amount(l) or is_total_row(l):
                break
            if re.match(r'^Total\s+by\s+Department', l, re.I):
                break
            if re.match(r'^\d{3,4}$', l):
                break
            name_parts.append(l)
            i += 1

        if not name_parts:
            i += 1
            continue

        # If not followed by a unit number, treat accumulated lines as category/section header.
        # Also consume any stray numbers that follow (from non-standard format records).
        if i >= n or not is_unit(lines[i]):
            if name_parts:
                joined = ' / '.join(name_parts)
                # Only update category if it looks like real descriptive text:
                # - not purely numeric/slash garbage
                # - not a fund-code + district block (continuation funds from previous page)
                all_fund_or_district = all(
                    re.match(r'^F_', p) or is_district(p) for p in name_parts
                )
                if not re.match(r'^[\d\s/]+$', joined) and not all_fund_or_district:
                    current_category = joined
            # Consume stray numbers (from non-standard or cross-page continuation records)
            while i < n and is_number_str(lines[i]):
                i += 1
            after_total = False
            continue

        # Separate category header from project name
        if after_total and len(name_parts) >= 2:
            current_category = name_parts[0]
            project_name = ' '.join(name_parts[1:])
        else:
            project_name = ' '.join(name_parts)

        # Unit number (strip "U_")
        i += 1

        # Fund number (possibly district on same line)
        if i >= n or not is_fund(lines[i]):
            after_total = False
            continue

        fund_line = lines[i]; i += 1
        if ' ' in fund_line:
            parts = fund_line.split(None, 1)
            district = parts[1]
        else:
            # District on next line — may be text ("Citywide") or small int ("14")
            if i < n and is_district(lines[i]):
                district = lines[i]; i += 1
            else:
                district = ''

        def collect_9(start_i):
            ns = []
            j = start_i
            while j < n and len(ns) < 9:
                if is_number_str(lines[j]):
                    ns.append(clean_num(lines[j]))
                    j += 1
                else:
                    break
            return ns, j

        def consume_fund_block(start_i):
            """Consume an F_xxx [district] + 9 numbers block. Returns (9 nums or [], new_i)."""
            j = start_i
            if j >= n or not is_fund(lines[j]):
                return [], j
            j += 1  # skip F_xxx
            if j < n and is_district(lines[j]):
                j += 1  # skip district
            return collect_9(j)

        # Collect first fund's 9 numbers: Capital, Expenditure, Remaining, FY19-FY23, Total
        nums, i = collect_9(i)
        if len(nums) < 9:
            after_total = False
            continue

        capital_adopted = nums[0]
        yr_2019 = nums[3]
        yr_2020 = nums[4]
        yr_2021 = nums[5]
        yr_2022 = nums[6]
        yr_2023 = nums[7]
        project_total = nums[8]

        def aggregate(extra):
            nonlocal capital_adopted, yr_2019, yr_2020, yr_2021, yr_2022, yr_2023, project_total
            capital_adopted += extra[0]
            yr_2019 += extra[3]; yr_2020 += extra[4]; yr_2021 += extra[5]
            yr_2022 += extra[6]; yr_2023 += extra[7]; project_total += extra[8]

        # Aggregate additional fund rows (same project, different fund source).
        # Patterns:
        #   (a) bare F_xxx [district] + 9 numbers
        #   (b) repeated U_xxx (same id) + F_xxx [district] + 9 numbers
        #   (c) repeated project name + F_xxx [district] + 9 numbers (no U_ between)
        while i < n:
            if is_fund(lines[i]):
                # (a) bare F_
                extra, i = consume_fund_block(i)
                if len(extra) == 9:
                    aggregate(extra)
            elif not is_unit(lines[i]) and not is_amount(lines[i]) and not is_total_row(lines[i]):
                # (c) possibly repeated name lines before a bare F_; scan ahead
                j = i
                while j < n and not is_unit(lines[j]) and not is_fund(lines[j]) \
                        and not is_amount(lines[j]) and not is_total_row(lines[j]):
                    if re.match(r'^Total\s+by\s+Department', lines[j], re.I):
                        break
                    j += 1
                if j < n and is_fund(lines[j]):
                    # Confirmed: text lines followed by F_ (no U_ in between) → additional fund
                    i = j  # skip the repeated name lines
                    extra, i = consume_fund_block(i)
                    if len(extra) == 9:
                        aggregate(extra)
                else:
                    break  # not an additional fund — next project starts here
            else:
                break

        year_vals = [('2019', yr_2019), ('2020', yr_2020), ('2021', yr_2021),
                     ('2022', yr_2022), ('2023', yr_2023)]
        funded = [yr for yr, val in year_vals if val != 0]
        start_year = funded[0] if funded else ''
        end_year = funded[-1] if funded else ''

        records.append({
            'cip_year': 2018,
            'project_type': current_category,
            'source_page': page_num,
            'department': department,
            'project_name': project_name,
            'council_district': district,
            'start_year': start_year,
            'end_year': end_year,
            'previous_appropriations': capital_adopted,
            'project_total': project_total,
            'year_2019': yr_2019,
            'year_2020': yr_2020,
            'year_2021': yr_2021,
            'year_2022': yr_2022,
            'year_2023': yr_2023,
        })
        after_total = False

    return records, current_category


def main():
    pdf = fitz.open(PDF_PATH)
    current_dept = ''
    current_category = ''
    all_records = []

    for pg_idx in range(len(pdf)):
        pg = pdf[pg_idx]
        txt = pg.get_text("text")

        if pg.rotation == 0:
            dept = dept_name_from_page(txt)
            if dept:
                current_dept = dept
                current_category = ''   # reset category at department boundary
        else:
            # Landscape project-data page
            lines = [l.strip() for l in txt.split('\n') if l.strip()]
            header_end = find_header_end(lines)
            data_lines = expand_lines(lines[header_end:])
            recs, current_category = parse_project_page(
                data_lines, current_dept, pg_idx + 1, current_category
            )
            all_records.extend(recs)

    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_records)

    print(f"Wrote {len(all_records)} records to {CSV_PATH}")


if __name__ == '__main__':
    main()
