import csv, os, re
import pdfplumber

PDF_DIR = r"C:\Users\vince\Documents\GitHub\CIPBD\San-Diego\PDF"
OUT_DIR = r"C:\Users\vince\Documents\GitHub\CIPBD\Scripts\San-Diego\outputs"
CIP_YEARS = [2009]
NA = 'NA'

NUM_RE = re.compile(r'^\(?-?[\d,]+\)?$')
FY_RE  = re.compile(r'^FY(\d{4})$')
PROJECT_ID_RE = re.compile(r'\b(\d{2,}-\d{3,4}\.\d+)(?:\s*/\s*(\S+))?\s*$')
LABEL_TOKENS  = {'Revenue','Source/Tag','Fund','Source','Tag','/Tag'}

def clean_num(s):
    s = str(s or '').strip().replace(',', '').replace(' ', '')
    if s.startswith('(') and s.endswith(')'): s = '-' + s[1:-1]
    if not s or s in ('-', '—', 'N/A', 'n/a', 'TBD'): return 0
    try: return int(float(s))
    except: return 0

def clean_text(s): return ' '.join(str(s or '').replace('\n', ' ').split())

# ---------- geometry ----------
def group_lines(words, tol=2.5):
    lines = []
    for w in sorted(words, key=lambda w: (w['top'], w['x0'])):
        for ln in lines:
            if abs(ln['top'] - w['top']) <= tol:
                ln['words'].append(w); break
        else:
            lines.append({'top': w['top'], 'words': [w]})
    for ln in lines:
        ln['words'].sort(key=lambda w: w['x0'])
        ln['text'] = ' '.join(w['text'] for w in ln['words'])
    lines.sort(key=lambda l: l['top'])
    return lines

def centre(w): return (w['x0'] + w['x1']) / 2.0

def is_header_line(ln):
    return sum(1 for w in ln['words'] if FY_RE.match(w['text'])) >= 2

def header_band(lines, hi):
    """Header line plus its stacked upper line (2009: 'FY2016   Unidentified')."""
    band = list(lines[hi]['words'])
    if hi > 0:
        prev = lines[hi-1]
        if ((lines[hi]['top'] - prev['top']) < 16
                and not any(NUM_RE.match(w['text']) for w in prev['words'])
                and any(FY_RE.match(w['text']) or w['text'] in ('Unidentified','Total')
                        for w in prev['words'])):
            band += list(prev['words'])
    return band

def header_columns(lines, hi):
    """Cluster header-band tokens into columns by x-overlap, then name them."""
    # drop row-label tokens by NAME, never by a fixed x cutoff: the table shifts
    # left/right between pages and a cutoff silently swallows the first FY column
    toks = [w for w in header_band(lines, hi) if w['text'] not in LABEL_TOKENS]
    if not toks: return None
    toks.sort(key=lambda w: w['x0'])

    clusters = []
    for w in toks:
        if clusters and w['x0'] <= clusters[-1]['x1'] + 4:
            clusters[-1]['w'].append(w)
            clusters[-1]['x1'] = max(clusters[-1]['x1'], w['x1'])
        else:
            clusters.append({'w': [w], 'x0': w['x0'], 'x1': w['x1']})

    cols = []
    for c in clusters:
        c['w'].sort(key=lambda w: (w['top'], w['x0']))
        name = ' '.join(w['text'] for w in c['w'])
        fys  = [m.group(1) for m in (FY_RE.match(w['text']) for w in c['w']) if m]
        cx   = (c['x0'] + c['x1']) / 2.0
        if   'Exp/Enc' in name:        f = 'exp_enc'
        elif 'Appn' in name:           f = 'con_appn'
        elif 'Unidentified' in name:   f = 'unidentified_funding'
        elif name.strip() == 'Total':  f = 'project_total'
        elif len(fys) >= 2:            f = f'year_{min(fys)}_{max(fys)}'   # FY2016-FY2020 bucket
        elif len(fys) == 1:            f = f'year_{fys[0]}'
        else:                          continue
        cols.append((f, cx))
    return cols or None

def money(v, w=13):
    """previous_appropriations may be the string NA once the rule fires."""
    return f"{v:>{w},}" if isinstance(v, (int, float)) else f"{str(v):>{w}}"

def assign_by_x(nums, cols):
    vals = {}
    for w in nums:
        cx = centre(w)
        f, _ = min(cols, key=lambda c: abs(c[1] - cx))
        vals[f] = clean_num(w['text'])
    return vals

# ---------- page parsing ----------
def parse_text(txt):
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    department   = lines[0] if len(lines) >= 1 else ''
    project_type = lines[1] if len(lines) >= 2 else ''
    project_name = project_id = ''
    if len(lines) >= 3:
        m = PROJECT_ID_RE.search(lines[2])
        if m: project_id, project_name = m.group(1), lines[2][:m.start()].strip()
        else: project_name = lines[2]
    council = []
    for l in lines[3:]:
        if l.startswith('Council District'): council.append(l)
        elif council and not l.startswith('Description'): council.append(l)
        elif council: break
    address = ''
    if council:
        address = clean_text(re.sub(r'(?<=\S)\s+(Community Plan:)', r'; \1', ' '.join(council)))
    d = re.search(r'Description:\s*', txt)
    j = re.search(r'Justification:\s*', txt)
    o = re.search(r'Operating Budget Effect:\s*', txt)
    return {'department':department, 'project_type':project_type,
            'project_name':project_name, 'project_id':project_id,
            'address_location':address,
            'project_description'  : clean_text(txt[d.end():j.start()]) if d and j else '',
            'project_justification': clean_text(txt[j.end():o.start()]) if j and o else ''}

def get_financial(pg):
    words = pg.extract_words(use_text_flow=False, keep_blank_chars=False)
    if not words: return None
    lines = group_lines(words)
    start = next((i for i, ln in enumerate(lines)
                  if 'Expenditures by Revenue Source' in ln['text']), None)
    if start is None: return None

    result, found = {}, False
    hdr = [i for i in range(start, len(lines)) if is_header_line(lines[i])]
    for n, hi in enumerate(hdr):
        cols = header_columns(lines, hi)
        if not cols: continue
        # -1 keeps the next header's stacked upper line out of this block
        stop = hdr[n+1] - 1 if n + 1 < len(hdr) else len(lines)
        for j in range(hi + 1, stop):
            ws = lines[j]['words']
            if not ws or ws[0]['text'] != 'Total': continue
            nums = [w for w in ws[1:] if NUM_RE.match(w['text'])]
            if nums:
                result.update(assign_by_x(nums, cols)); found = True
            break
    if not found: return None
    result['previous_appropriations'] = result.pop('exp_enc', 0) + result.pop('con_appn', 0)
    return result

def is_project_page(txt):
    return ('Description:' in txt and 'Justification:' in txt
            and 'Expenditures by Revenue Source' in txt)

# ---------- driver ----------
def col_sort(c):
    yrs = re.findall(r'\d{4}', c)
    return (int(yrs[0]) if yrs else 9999, c)

def years_in(col):
    return [int(y) for y in re.findall(r'\d{4}', col)]

def parse_year(cip_year):
    pdf_path = os.path.join(PDF_DIR, f"{cip_year}.pdf")
    if not os.path.exists(pdf_path):
        print(f"{cip_year}: MISSING {pdf_path}"); return

    recs = []
    with pdfplumber.open(pdf_path) as pdf:
        for pg in pdf.pages:
            txt = pg.extract_text() or ''
            if not is_project_page(txt): continue
            fin = get_financial(pg)
            if fin is None: continue
            recs.append({'cip_year':cip_year, 'source_page':pg.page_number,
                         **parse_text(txt), '_fin':fin})
    if not recs:
        print(f"{cip_year}: no projects"); return

    # column set is discovered, not hardcoded: FY range shifts each book and 2009
    # adds a FY2016-FY2020 bucket plus an Unidentified Funding column
    ycols = sorted({k for r in recs for k in r['_fin'] if k.startswith('year_')}, key=col_sort)
    extra = ['unidentified_funding'] if any('unidentified_funding' in r['_fin'] for r in recs) else []
    funding = ycols + extra
    keep    = f'year_{cip_year + 1}'          # the one column the rule preserves

    fired = 0
    for r in recs:
        fin = r.pop('_fin')
        for c in funding: r[c] = fin.get(c, 0)
        r['previous_appropriations'] = fin['previous_appropriations']
        r['project_total']           = fin.get('project_total', 0)

        computed = r['previous_appropriations'] + sum(r[c] for c in funding)
        # WORK CODES: only funding tagged with a work code rolls into the project
        # total. Detecting the tags on the page is too fragile, so an overcount is
        # taken as the signal and every other money column is voided -- previous
        # appropriations included, since it carries no work-code tag either.
        if computed > r['project_total']:
            fired += 1
            for c in funding:
                if c != keep: r[c] = NA
            r['previous_appropriations'] = NA
            computed = r[keep] if r.get(keep, NA) != NA else 0

        funded = [y for c in funding if r[c] != NA and r[c] != 0 for y in years_in(c)]
        r['start_year']     = min(funded) if funded else ''
        r['end_year']       = max(funded) if funded else ''
        r['computed_total'] = computed
        r['residual']       = computed - r['project_total']

    fields = ['cip_year','source_page','department','project_type','project_name',
              'project_id','address_location','previous_appropriations','project_total',
              'project_description','project_justification', *funding,
              'start_year','end_year','computed_total','residual']
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, f"{cip_year}.csv"), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader(); w.writerows(recs)

    bad = [r for r in recs if r['residual'] != 0]
    print(f"{cip_year}: {len(recs)} projects -> {cip_year}.csv | {len(funding)} funding cols "
          f"| work-code rule fired {fired} ({100*fired/len(recs):.0f}%) "
          f"| residual!=0 {len(bad)}")
    for r in bad[:15]:
        print(f"    p{r['source_page']:>4} prev={money(r['previous_appropriations'])} "
              f"comp={money(r['computed_total'])} tot={money(r['project_total'])} "
              f"resid={money(r['residual'])}  {r['project_name'][:38]}")

for y in CIP_YEARS:
    parse_year(y)