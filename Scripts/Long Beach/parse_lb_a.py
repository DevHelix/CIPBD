import csv, os, re, collections
import pdfplumber

PDF_DIR = r"C:\Users\vince\Documents\GitHub\CIPBD\Long Beach\PDF"
OUT_DIR = r"C:\Users\vince\Documents\GitHub\CIPBD\Scripts\Long Beach\outputs"

# layout A = "Program Historical Summary"  (FY12–FY17 books, files 2011–2016)
# layout B = "Funding Source / Beg Balance / FY n / FY n+1 / FY n+2 / 3 Year Total"
FILES = {2011:'A', 2012:'A', 2013:'A', 2014:'A', 2015:'A', 2016:'A',
         2017:'B', 2018:'B', 2019:'B', 2020:'B', 2021:'B', 2022:'B',
         2023:'B', 2024:'B', 2025:'B'}

NUM = re.compile(r'^\(?-?\$?-?[\d,]+\)?$')

def num(s):
    s = str(s or '').strip().replace('$','').replace(',','').replace(' ','')
    neg = s.startswith('(') and s.endswith(')')
    if neg: s = s[1:-1]
    if not s or s in ('-','—','N/A'): return 0
    try: v = int(float(s))
    except: return 0
    return -v if neg else v

def txt(s): return ' '.join(str(s or '').replace('\n',' ').split())

def lines_of(pg, tol=3.0):
    """Cluster words into visual lines using true PDF y-coordinates."""
    ws = pg.extract_words(use_text_flow=False, keep_blank_chars=False)
    out = []
    for w in sorted(ws, key=lambda w:(w['top'], w['x0'])):
        for ln in out:
            if abs(ln['top']-w['top']) <= tol:
                ln['w'].append(w); break
        else:
            out.append({'top':w['top'], 'w':[w]})
    for ln in out:
        ln['w'].sort(key=lambda w:w['x0'])
        ln['text'] = ' '.join(w['text'] for w in ln['w'])
    out.sort(key=lambda l:l['top'])
    return out

def cells(words, gap=7.0):
    """Merge adjacent words into logical header cells; returns [(text, x1)]."""
    out = []
    for w in words:
        if out and w['x0']-out[-1][2] <= gap:
            out[-1][0] += ' '+w['text']; out[-1][2] = w['x1']
        else:
            out.append([w['text'], w['x0'], w['x1']])
    return [(c[0], c[2]) for c in out]

def by_right_edge(nums, cols):
    """Figures are right-aligned under their header, so match on x1."""
    vals = {}
    for w in nums:
        f, _ = min(cols, key=lambda c: abs(c[1]-w['x1']))
        vals[f] = num(w['text'])
    return vals

# ------------------------- LAYOUT A : 2011-2016 -------------------------
A_MAP  = {'Budget':'inception_budget', 'Actuals':'inception_actuals',
          'Expenditures':'fy_expenditures', 'Carryover':'carryover', 'Balance':'carryover'}
A_CONT = re.compile(r'Program Number\s+\S+\s*\(Continued\)')
A_NUM  = re.compile(r'Program Number\s+([A-Z]{2,4}\d{3,5}\*?)')

def famA_totals(pg):
    L = lines_of(pg); hi = None
    for i, ln in enumerate(L):
        t = ln['text']
        if 'Funding Sources' in t and 'Budget' in t and 'Actuals' in t:
            hi = i; break
    if hi is None: return None
    # word-level anchors: 'Expenditures Carryover' can sit <7px apart on some pages
    cols = [(A_MAP[w['text']], w['x1']) for w in L[hi]['w'] if w['text'] in A_MAP]
    if len(cols) < 3: return None

    out = {}
    for ln in L[hi+1:]:
        w, t = ln['w'], ln['text']
        if w[0]['text'] == 'Total' and len(w) > 1 and w[1]['text'] != 'Adopted':
            n = [x for x in w[1:] if NUM.match(x['text'])]
            if n: out.update(by_right_edge(n, cols))
        elif t.startswith('Total Adopted Budget'):
            n = [x for x in w if NUM.match(x['text'])]
            if n: out['total_adopted_budget'] = num(n[-1]['text'])
        elif re.match(r'FY\s?\d{2} New Funding', t):
            n = [x for x in w if NUM.match(x['text'])]
            if n: out['new_funding'] = num(n[-1]['text'])
    return out or None

def famA_meta(t):
    L = [re.sub(r'^\d\)\s*','',l.strip()) for l in t.split('\n') if l.strip()]
    m = A_NUM.search(t)
    d = re.search(r'Program Description\s*(.*?)(?=\n?\s*(?:\d\)\s*)?'
                  r'(?:Work to be initiated|Estimated Schedule))', t, re.S)
    s = re.search(r'Estimated Schedule for FY\s?\d{2}\s*(.*?)'
                  r'(?=\n\s*(?:\d\)\s*)?FY\s?\d{2} New Funding)', t, re.S)
    return {'program_name'  : L[0] if L else '',
            'program_number': m.group(1) if m else '',
            'department'    : next((l.split(':',1)[1].strip() for l in L if l.startswith('Department:')), ''),
            'contact'       : next((l.split(':',1)[1].strip() for l in L if l.startswith('Contact:')), ''),
            'project_description': txt(d.group(1)) if d else '',
            'schedule'      : txt(s.group(1)) if s else ''}

def parse_famA(path, cip_year):
    fy = cip_year + 1
    recs = []
    with pdfplumber.open(path) as pdf:
        P = pdf.pages
        for i, pg in enumerate(P):
            t = pg.extract_text() or ''
            if 'Program Number' not in t or 'Program Historical Summary' not in t:      continue
            if 'SAMPLE' in t or 'Guide to the' in t or A_CONT.search(t):                continue
            # long funding tables spill onto the next page; totals live wherever
            # "Total Adopted Budget" is, and that page owns the header geometry
            fin, src = None, i
            for j in range(i, min(i+4, len(P))):
                if 'Total Adopted Budget' in (P[j].extract_text() or ''):
                    fin, src = famA_totals(P[j]), j; break
            fin = fin or famA_totals(pg) or {}

            prev    = fin.get('inception_actuals',0) + fin.get('fy_expenditures',0)
            adopted = fin.get('total_adopted_budget',0)
            recs.append({'cip_year':cip_year, 'budget_fy':fy, 'layout':'A', 'section':'',
                         'source_page':i+1, 'totals_page':src+1, **famA_meta(t),
                         'operating_maintenance':'',
                         'inception_budget'  : fin.get('inception_budget',0),
                         'inception_actuals' : fin.get('inception_actuals',0),
                         'fy_expenditures'   : fin.get('fy_expenditures',0),
                         'carryover'         : fin.get('carryover',0),
                         'new_funding'       : fin.get('new_funding',0),
                         'total_adopted_budget': adopted,
                         'previous_appropriations': prev,     # Actuals + FY Expenditures
                         f'year_{fy}'        : adopted,       # Total Adopted Budget
                         'project_total'     : prev + adopted})
    return recs

# ------------------------- LAYOUT B : 2017-2025 -------------------------
def famB_totals(pg, fy1):
    L = lines_of(pg); hi = None
    for i, ln in enumerate(L):
        t = ln['text']
        if re.search(r'Funding\s?Source', t) and re.search(r'Bal', t) and 'Total' in t:
            hi = i; break
    if hi is None: return None

    cs = cells(L[hi]['w'])                      # 'FY'+'23' merge; bare 'FY' stays separate
    bi = next((k for k,(c,_) in enumerate(cs) if re.search(r'Bal', c)), None)
    if bi is None: return None
    cols = [('previous_appropriations', cs[bi][1])]
    for k, (_, x1) in enumerate(cs[bi+1:-1][:3]):   # positional: survives 'FY FY FY' pages
        cols.append((f'year_{fy1+k}', x1))
    cols.append(('project_total', cs[-1][1]))

    for ln in L[hi+1:]:
        w = ln['w']
        if w[0]['text'] == 'Total':
            n = [x for x in w[1:] if NUM.match(x['text'])]
            if n: return by_right_edge(n, cols)
    return None

def famB_meta(t):
    L = [l.strip() for l in t.split('\n') if l.strip()]
    title = L[1] if len(L) > 1 else ''
    # trailing token is the program number only if it carries a digit or underscore
    m = re.match(r'^(.*?)\s+((?=[A-Z0-9_]*[\d_])[A-Z0-9_]{4,}\*?)$', title)
    def grab(a, b):
        r = re.search(a + r'\s*(.*?)(?=' + b + r')', t, re.S)
        return txt(r.group(1)) if r else ''
    return {'section'       : L[0] if L else '',
            'program_name'  : (m.group(1) if m else title).strip(),
            'program_number': m.group(2) if m else '',
            'department'    : '',
            'project_description'  : grab(r'Project\s?Description', r'Estimated\s?Operating'),
            'operating_maintenance': grab(r'and\s?Maintenance',     r'Project\s?Timeline'),
            'schedule'      : grab(r'Project\s?Timeline',           r'Department\s?Contact'),
            'contact'       : grab(r'Department\s?Contact',         r'Funding\s?Sources?\b')}

def parse_famB(path, cip_year):
    fy1 = cip_year + 1
    recs = []
    with pdfplumber.open(path) as pdf:
        for i, pg in enumerate(pdf.pages):
            t = pg.extract_text() or ''
            if 'Guide to the CIP' in t or 'SAMPLE PROGRAM' in t: continue
            if not (re.search(r'Funding\s?Source', t) and re.search(r'Beg\w*\.?\s*Bal', t)): continue
            fin = famB_totals(pg, fy1)
            if not fin: continue
            recs.append({'cip_year':cip_year, 'budget_fy':fy1, 'layout':'B',
                         'source_page':i+1, 'totals_page':i+1, **famB_meta(t),
                         'inception_budget':0, 'inception_actuals':0, 'fy_expenditures':0,
                         'carryover':0, 'new_funding':0, 'total_adopted_budget':0,
                         'previous_appropriations': fin.get('previous_appropriations',0),
                         **{f'year_{fy1+k}': fin.get(f'year_{fy1+k}',0) for k in range(3)},
                         'project_total': fin.get('project_total',0)})
    return recs

# ------------------------------- driver -------------------------------
BASE = ['cip_year','source_page','program_number','program_name','department',
        'project_description','inception_budget','inception_actuals',
        'previous_appropriations']
TAIL = ['project_total','start_year','end_year']

RENAME = {'program_number'   : 'project_id',
          'program_name'     : 'project_name',
          'inception_budget' : 'spent',
          'inception_actuals': 'remaining'}

def year_cols(cip_year, fam):
    """A books carry one adopted-budget year; B books carry three forward years."""
    return [cip_year + 1 + k for k in range(1 if fam == 'A' else 3)]

def run():
    os.makedirs(OUT_DIR, exist_ok=True)
    grand = 0
    for year, fam in FILES.items():
        pdf = os.path.join(PDF_DIR, f"{year}.pdf")
        if not os.path.exists(pdf):
            print(f"{year}: MISSING {pdf}"); continue

        rows   = parse_famA(pdf, year) if fam == 'A' else parse_famB(pdf, year)
        ycols  = year_cols(year, fam)
        keys   = BASE + [f'year_{y}' for y in ycols] + TAIL
        fields = [RENAME.get(k, k) for k in keys]

        for r in rows:
            for y in ycols: r.setdefault(f'year_{y}', 0)
            funded = [y for y in ycols if r[f'year_{y}'] != 0]
            r['start_year'] = min(funded) if funded else ''
            r['end_year']   = max(funded) if funded else ''
            # still checked, no longer written
            r['residual'] = (r['previous_appropriations']
                             + sum(r[f'year_{y}'] for y in ycols)
                             - r['project_total'])

        with open(os.path.join(OUT_DIR, f"{year}.csv"), 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
            w.writeheader()
            for r in rows:
                w.writerow({RENAME.get(k, k): r.get(k, '') for k in keys})
        grand += len(rows)

        blank = sum(1 for r in rows if r['start_year'] == '')
        bad   = [r for r in rows if r['residual'] != 0]
        print(f"{year} [{fam}] {len(rows):>3} programs, year col(s) {ycols} -> {year}.csv"
              f"   unfunded: {blank}   residual!=0: {len(bad)}")
        for r in bad:
            print(f"    p{r['source_page']:>3} {r['program_number']:>12} "
                  f"total={r['project_total']:>14,} resid={r['residual']:>13,}  "
                  f"{r['program_name'][:40]}")

    print(f"\nTOTAL {grand} programs across {len(FILES)} files")

run()