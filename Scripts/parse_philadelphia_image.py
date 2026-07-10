"""
Philadelphia CIP – image-based PDF parser (2021–2025)
Converts each project-data page to a grayscale image, runs Tesseract OCR,
then parses the line output into the 13+N CSV schema.

Run directly:  python parse_philadelphia_image.py
Or from notebook via %run or exec(open(...).read())
"""
import re, warnings
from pathlib import Path
from collections import defaultdict

import cv2
import numpy as np
import pdfplumber
import fitz          # pymupdf
import pytesseract
import pandas as pd
from PIL import Image

warnings.filterwarnings('ignore')

# ── Paths ──────────────────────────────────────────────────────────────────
SCRIPTS_DIR = Path(__file__).resolve().parent
CITY_DIR    = SCRIPTS_DIR.parent / 'Philadelphia'
PDF_DIR     = CITY_DIR / 'PDF'
CSV_DIR     = CITY_DIR / 'CSV'
CSV_DIR.mkdir(exist_ok=True)

# PDFs to skip (text-based, already handled)
SKIP_STEMS = {'2019', '2020'}

REQUIRED_COLS = [
    'cip_year', 'project_type', 'source_page', 'department',
    'project_name', 'project_id', 'address_location',
    'start_year', 'end_year',
    'project_description', 'project_justification',
    'previous_appropriations', 'project_total',
]

# Philadelphia funding-source codes
SRC_CODES = {
    'CN','CT','CR','CA','A',
    'XN','XT','XR',
    'Z',
    'FB','FO','FT',
    'PB','PT',
    'SB','SO','ST',
    'TB','TO','TT',
    'GO','GR','GN','GP',
}

YEAR_RE    = re.compile(r'^(\d{4})$')
NUM_RE     = re.compile(r'^-?[\d,]+$')
COMBINED   = re.compile(r'^[\d,]+[A-Z]{1,3}$')
PROJ_RE    = re.compile(r'^(\d+[A-Z]?)\.?\s+(.+)$')
DEPT_RE    = re.compile(r'^[A-Z][A-Z &\-/()–]+$')
RANGE_YR_RE = re.compile(r'\b(\d{4})\s*[-–]\s*(\d{4})\b')

TESS_CFG = '--psm 6 --oem 1'

# ── Helpers ────────────────────────────────────────────────────────────────

def is_src(tok):
    return tok.upper() in SRC_CODES

def parse_num(s):
    try:
        return float(str(s).replace(',', '').strip())
    except Exception:
        return None

def is_data_page(text):
    """True if page contains a year-column header + units marker."""
    years_found = len(re.findall(r'\b20\d{2}\b', text))
    has_unit    = bool(re.search(r'x000|\$x|x 000', text, re.I))
    return years_found >= 4 and has_unit

# ── OCR ────────────────────────────────────────────────────────────────────

def ocr_page(pdf_path, pg_1idx, dpi=300):
    """
    Render PDF page to grayscale image with CLAHE + Otsu binarisation,
    then return Tesseract OCR string.
    """
    doc  = fitz.open(str(pdf_path))
    mat  = fitz.Matrix(dpi / 72, dpi / 72)
    pix  = doc[pg_1idx - 1].get_pixmap(matrix=mat, colorspace=fitz.csGRAY)
    doc.close()
    arr   = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    arr   = clahe.apply(arr)
    _, arr = cv2.threshold(arr, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    img  = Image.fromarray(arr)
    return pytesseract.image_to_string(img, config=TESS_CFG)

# ── Line classifier ────────────────────────────────────────────────────────

def classify_line(line, plan_years):
    """
    Returns a tuple (tag, *data):
      ('year_hdr', [years])       – column header row with >=4 4-digit years
      ('unit',)                   – "$x000" units row → skip
      ('totals_hdr',)             – section totals header
      ('dept', text)              – ALL-CAPS department / project-type header
      ('src_row', nums, left)     – source-code row (e.g. "1,500 CN 1,000CN")
      ('total_row', yr_vals, tot, left) – numeric total row
      ('project', num, name)      – numbered project line
      ('text', text)              – free text (description / continuation)
      ('skip',)                   – bare page number, empty, etc.
    """
    line = line.strip()
    if not line:
        return ('skip',)
    # Bare page number
    if re.match(r'^\d{1,3}$', line):
        return ('skip',)
    # Units row
    if re.search(r'x000|\$x|x 000', line, re.I):
        return ('unit',)

    tokens = line.split()

    # Year-header row (>=4 4-digit years in range)
    yrs = [int(t) for t in tokens
           if YEAR_RE.match(t) and 2018 <= int(t) <= 2040]
    if len(yrs) >= 4:
        uniq = list(dict.fromkeys(yrs))  # preserve order, deduplicate
        return ('year_hdr', uniq)

    # Totals section header
    if re.match(r'^TOTALS?\s*[-–]', line, re.I):
        return ('totals_hdr',)

    # Find where the numeric block starts (first token that is number/src/combined)
    nb_start = None
    for i, tok in enumerate(tokens):
        if NUM_RE.match(tok.replace(',', '')) or is_src(tok) or COMBINED.match(tok):
            nb_start = i
            break

    if nb_start is not None:
        left_text = ' '.join(tokens[:nb_start]).strip()
        right     = tokens[nb_start:]
        has_sc    = any(is_src(t) or COMBINED.match(t) for t in right)

        nums = []
        for t in right:
            if COMBINED.match(t):
                nums.append(parse_num(re.sub(r'[A-Z]+$', '', t)))
            elif NUM_RE.match(t.replace(',', '')):
                nums.append(parse_num(t))
        nums = [n for n in nums if n is not None]

        if not nums:
            return ('text', line)

        if has_sc:
            return ('src_row', nums, left_text)

        # Pure-number row → total row
        # Map left-to-right to plan_years; last value is the range total
        yr_vals = {}
        for j, v in enumerate(nums[:-1]):
            if j < len(plan_years):
                yr_vals[plan_years[j]] = v
        range_total = nums[-1] if len(nums) > 1 else (nums[0] if nums else None)
        return ('total_row', yr_vals, range_total, left_text)

    # Numbered project line
    m = PROJ_RE.match(line)
    if m:
        name = m.group(2).strip()
        if not re.search(r'\btotal\b', name, re.I):
            return ('project', m.group(1).rstrip('.'), name)

    # ALL-CAPS department / project-type header
    if DEPT_RE.match(line) and len(line.replace(' ', '')) > 3 and 'TOTAL' not in line.upper():
        return ('dept', line)

    return ('text', line)

# ── Page-level parser ──────────────────────────────────────────────────────

def parse_page(ocr_text, pg_num, cip_year, ctx, projects):
    """
    Parse OCR output from one data page.
    Appends completed project dicts to `projects`.
    Mutates `ctx` dict to carry dept/type/plan_years across pages.
    """
    plan_years = ctx.get('plan_years', [])
    pending    = ctx.get('pending')
    pending_yr = ctx.get('pending_yr')
    pending_tot= ctx.get('pending_tot')
    desc_buf   = ctx.get('desc_buf', [])

    def _flush():
        nonlocal pending, pending_yr, pending_tot, desc_buf
        if pending is None or not pending_yr:
            if pending is not None:
                pending = None; pending_yr = None; pending_tot = None; desc_buf = []
            return
        name = pending.get('project_name', '').strip()
        if name and len(name) >= 3 and name[0] not in ("'", '|', '"', '.', ','):
            for yr, v in pending_yr.items():
                pending[f'year_{yr}'] = v
            pending['project_total']        = pending_tot if pending_tot else sum(pending_yr.values())
            pending['project_description']  = ' '.join(desc_buf).strip()
            pending['project_justification'] = pending['project_description']
            projects.append(pending)
        pending = None; pending_yr = None; pending_tot = None; desc_buf = []

    for raw_line in ocr_text.split('\n'):
        cat = classify_line(raw_line, plan_years if plan_years else list(range(2022, 2028)))

        if cat[0] == 'year_hdr':
            # Keep at most 6 fiscal-year columns (exclude range-total column)
            plan_years = cat[1][:6]
            ctx['plan_years'] = plan_years

        elif cat[0] in ('unit', 'skip'):
            pass

        elif cat[0] == 'totals_hdr':
            _flush()

        elif cat[0] == 'dept':
            _flush()
            txt = cat[1].upper()
            # Distinguish dept names from sub-type labels heuristically:
            # known dept names are recorded; everything else is proj_type
            if any(kw in txt for kw in (
                'MUSEUM', 'AVIATION', 'COMMERCE', 'FINANCE', 'FIRE', 'FLEET',
                'LIBRARY', 'HEALTH', 'HOMELESS', 'HOUSING', 'SERVICES',
                'LICENSES', 'MANAGING', 'MURAL', 'PARKS', 'PLANNING', 'POLICE',
                'PRISONS', 'PROPERTY', 'RECORDS', 'REVENUE', 'SCHOOLS',
                'SEPTA', 'STREETS', 'TRANSIT', 'WATER', 'ZOO', 'OIT',
                'SUSTAINABILITY', 'MDO', 'OHS',
            )):
                ctx['dept']      = txt
                ctx['proj_type'] = ''
                ctx['main_num']  = ''
            else:
                ctx['proj_type'] = txt

        elif cat[0] == 'src_row':
            _, nums, left_text = cat
            if left_text and pending is not None:
                desc_buf.append(left_text)

        elif cat[0] == 'total_row':
            _, yr_vals, range_total, left_text = cat
            if pending is not None and yr_vals and pending_yr is None:
                pending_yr  = yr_vals
                pending_tot = range_total
                _flush()

        elif cat[0] == 'project':
            _flush()
            _, num, name = cat
            dept    = ctx.get('dept', '')
            pid     = f"{dept[:4].replace(' ','')}.{num}" if dept else num
            pending = {
                'cip_year': cip_year, 'project_type': ctx.get('proj_type', ''),
                'source_page': pg_num, 'department': dept,
                'project_name': name, 'project_id': pid,
                'address_location': '', 'start_year': '', 'end_year': '',
                'project_description': '', 'project_justification': '',
                'previous_appropriations': '', 'project_total': '',
            }
            pending_yr = None; pending_tot = None; desc_buf = []

        elif cat[0] == 'text':
            if pending is not None and cat[1]:
                desc_buf.append(cat[1])

    # Store state back in ctx (projects may continue on next page)
    ctx['pending']     = pending
    ctx['pending_yr']  = pending_yr
    ctx['pending_tot'] = pending_tot
    ctx['desc_buf']    = desc_buf

# ── PDF-level parser ───────────────────────────────────────────────────────

def parse_pdf(pdf_path):
    """
    Parse one image-based Philadelphia CIP PDF.
    Returns (cip_year, plan_years, projects_list).
    """
    pdf_path = Path(pdf_path)
    stem     = pdf_path.stem
    cip_year = int(stem) if stem.isdigit() else None

    # Pull plan years from intro text
    plan_years = []
    with pdfplumber.open(pdf_path) as pdf:
        for pg in pdf.pages[:30]:
            txt = pg.extract_text() or ''
            m   = re.search(r'(?:FY|FISCAL YEARS?)\s*(\d{4})\s*[-–]\s*(\d{4})', txt, re.I)
            if m:
                y1 = int(m.group(1)); y2 = int(m.group(2))
                plan_years = list(range(y1, min(y2 + 1, y1 + 7)))[:6]
                if cip_year is None:
                    cip_year = y1 - 1  # publication year
                break

    if not plan_years and cip_year:
        plan_years = list(range(cip_year + 1, cip_year + 7))

    print(f'  cip_year={cip_year}  plan_years={plan_years}')

    # Identify image pages worth OCR-ing (skip intro/photo pages)
    image_pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, pg in enumerate(pdf.pages):
            pg_num  = i + 1
            n_chars = len(pg.chars)
            n_imgs  = len(pg.images)
            # Data pages: have an embedded image and very few text chars
            # (the few chars are just the header/footer overlay)
            if n_imgs >= 1 and n_chars < 300 and pg_num >= 15:
                image_pages.append(pg_num)

    print(f'  image pages to OCR: {len(image_pages)}')

    ctx = {
        'plan_years': plan_years,
        'dept': '', 'proj_type': '', 'main_num': '',
        'pending': None, 'pending_yr': None, 'pending_tot': None, 'desc_buf': [],
    }
    projects = []
    total    = len(image_pages)

    for i, pg_num in enumerate(image_pages, 1):
        if i % 20 == 0 or i == 1:
            print(f'  OCR {i}/{total} (page {pg_num})…', flush=True)
        try:
            text = ocr_page(pdf_path, pg_num)
        except Exception as exc:
            print(f'  OCR error page {pg_num}: {exc}')
            continue
        if not is_data_page(text):
            continue
        parse_page(text, pg_num, cip_year, ctx, projects)

    # Flush anything still pending after the last page
    if ctx.get('pending') and ctx.get('pending_yr'):
        p = ctx['pending']
        for yr, v in ctx['pending_yr'].items():
            p[f'year_{yr}'] = v
        p['project_total']        = ctx['pending_tot'] or sum(ctx['pending_yr'].values())
        p['project_description']  = ' '.join(ctx['desc_buf']).strip()
        p['project_justification'] = p['project_description']
        projects.append(p)

    return cip_year, plan_years, projects

# ── DataFrame builder ──────────────────────────────────────────────────────

def build_dataframe(projects, plan_years):
    """
    Assemble a tidy DataFrame with all required columns + year_YYYY columns.
    Fills start_year / end_year from non-zero year_YYYY columns.
    """
    if not projects:
        return pd.DataFrame(columns=REQUIRED_COLS)

    year_cols = [f'year_{y}' for y in sorted(plan_years)]
    all_cols  = REQUIRED_COLS + year_cols

    df = pd.DataFrame(projects)
    for col in all_cols:
        if col not in df.columns:
            df[col] = ''

    # Derive start_year / end_year
    for idx, row in df.iterrows():
        vals = {y: row.get(f'year_{y}') for y in plan_years
                if pd.notna(row.get(f'year_{y}')) and row.get(f'year_{y}', 0) != 0}
        if vals:
            df.at[idx, 'start_year'] = min(vals)
            df.at[idx, 'end_year']   = max(vals)

    return df[all_cols].fillna('')

# ── Main loop ──────────────────────────────────────────────────────────────

def main():
    pdfs = sorted(p for p in PDF_DIR.glob('*.pdf') if p.stem not in SKIP_STEMS)
    print(f'PDFs to process: {[p.name for p in pdfs]}\n')

    for pdf_path in pdfs:
        print(f'\n══ {pdf_path.name} ══')
        cip_year, plan_years, projects = parse_pdf(pdf_path)
        print(f'  rows extracted: {len(projects)}')

        df       = build_dataframe(projects, plan_years)
        csv_path = CSV_DIR / f'{pdf_path.stem}.csv'
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f'  → {csv_path}')

        # Null-rate summary
        for col in REQUIRED_COLS:
            if col in df.columns:
                null_pct = (df[col] == '').mean() * 100
                if null_pct > 50:
                    print(f'    WARN {col}: {null_pct:.0f}% empty')

    print('\n══ DONE ══')


if __name__ == '__main__':
    main()
