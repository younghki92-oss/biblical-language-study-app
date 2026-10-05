# STEPBible TVTMS 표에서 "70인경(Greek) 절 -> 영어(KJV) 절" 대응을 읽습니다.
# 결과: {(책번호, 70인경 장, 70인경 절): [(영어 장, 영어 절), ...]}  (표에 없는 절은 번호가 같다고 봄)
# 영어 절 0 = 시편 표제
# 한 구간에 Greek, Greek2 등 여러 방식이 있으면, test(조건) 함수로 랄프스판에 맞는 방식을 고릅니다.
import re,collections
BK=['Gen','Exo','Lev','Num','Deu','Jos','Jdg','Rut','1Sa','2Sa','1Ki','2Ki','1Ch','2Ch','Ezr','Neh','Est','Job','Psa','Pro','Ecc','Sng','Isa','Jer','Lam','Ezk','Dan','Hos','Jol','Amo','Oba','Jon','Mic','Nam','Hab','Zep','Hag','Zec','Mal']
BI={b:i+1 for i,b in enumerate(BK)}
REF=re.compile(r'([1-3]?[A-Z][a-z]{1,2})\.(\d+):(Title|\d+)(?:\.\d+)?(?:-(\d+))?(?:\.\d+)?')
COND=re.compile(r'([1-3]?[A-Z][a-z]{1,2})\.(\d+):(\d+)=(Last|Exist|NotExist)$')
def refs(cell):
    if not cell or cell.strip().startswith('Absent'): return None
    m=REF.search(cell)
    if not m: return None
    b,c,v1,v2=m.group(1),int(m.group(2)),m.group(3),m.group(4)
    if b not in BI: return None
    if v1=='Title': return [(BI[b],c,0)]
    v1=int(v1); v2=int(v2) if v2 else v1
    return [(BI[b],c,v) for v in range(v1,v2+1)]
def cond_ok(cell,test):
    """평가할 수 있는 조건이 하나라도 틀리면 False"""
    for part in re.split(r'\s*&\s*',cell or ''):
        m=COND.match(part.strip())
        if m and m.group(1) in BI:
            r=test(BI[m.group(1)],int(m.group(2)),int(m.group(3)),m.group(4))
            if r is False: return False
    return True
def load(path,test=lambda b,c,v,k:None):
    M=collections.defaultdict(list); cols=None; on=False; tests={}; pick=None
    for line in open(path,encoding='utf-8-sig'):
        p=[x.strip() for x in line.rstrip('\r\n').split('\t')]
        if p[0].startswith('#DataStart(Condensed)'): on=True; continue
        if on and p[0].startswith('#DataEnd'): break
        if p[0].startswith('#'):          # 주석 처리된 줄(쓰지 않는 구간)은 건너뜀
            if p[0].startswith('#$'): cols=None
            continue
        if not on: continue
        if p[0].startswith('$'):
            cols=p[1:] if len(p)>2 and p[1] else None; tests={}; pick=None; continue
        if p[0]=='BIBLES': cols=p[1:]; pick=None; continue
        if not cols: continue
        if p[0].startswith('TEST'):
            for i,c in enumerate(cols):
                if i+1<len(p): tests.setdefault(i,[]).append(p[i+1])
            continue
        if not re.match(r'^[A-Z][A-Za-z]+$',p[0]): continue
        if pick is None:
            cand=[i for i,c in enumerate(cols) if c.startswith('Greek')]
            ok=[i for i in cand if all(cond_ok(t,test) for t in tests.get(i,[]))]
            pick=(ok or cand or [-1])[0]
            try: ie=cols.index('English KJV')
            except ValueError: ie=-1
            pick=(pick,ie)
        ig,ie=pick
        if ig<0 or ie<0 or ig+1>=len(p) or ie+1>=len(p): continue
        E=refs(p[ie+1]); G=refs(p[ig+1])
        if not E or not G: continue
        if len(E)==len(G): pairs=zip(G,E)
        elif len(G)==1: pairs=[(G[0],e) for e in E]
        elif len(E)==1: pairs=[(g,E[0]) for g in G]
        else: continue
        for g,e in pairs:
            if e[0]!=g[0]: continue
            if (e[1],e[2]) not in M[g]: M[g].append((e[1],e[2]))
    return M
