# 70인경(랄프스판) 개인용 자료 파일을 만듭니다.  ※ 이 파일은 공개 사이트에 올리지 않습니다.
# 원자료: github.com/eliranwong/LXX-Rahlfs-1935 (CC BY-NC-SA 4.0, CCAT/CATSS 이용 동의 필요)
#         STEPBible TVTMS (절 번호 대응, CC BY)
# 실행: 원어성경앱 폴더에서  python3 tools/build_lxx.py
# 결과: _개인자료/원어성경_70인경.json.gz  (앱의 "70인경 자료 불러오기"로 각 기기에 넣음)
import os,re,json,gzip,collections,sys
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
SRC=os.path.join(ROOT,'_원자료','lxx'); OUT=os.path.join(ROOT,'_개인자료')
sys.path.insert(0,HERE); import lxx_versemap
def col(name):
    return [l.rstrip('\r\n').split('\t')[-1] for l in open(os.path.join(SRC,name),encoding='utf-8-sig')]
TXT=col('text_accented.csv'); MOR=col('patched_623693.csv'); LEXNO=col('Lex_LXXno.csv'); TRN=col('final_transliteration_SBL.csv'); SN=col('final_Strongs.csv')
N=len(TXT); assert N==len(MOR)==len(LEXNO)==len(TRN)==len(SN)
# ---------- 사전 (01-04.csv)
GLX=json.load(open(os.path.join(ROOT,'data','glx.json'),encoding='utf-8'))
def glx_key(s):
    m=re.match(r'G(\d+)$',s or '')
    if not m: return ''
    k='G%04d'%int(m.group(1))
    if k in GLX: return k
    for x in (k+'A',k+'G',k+'B'):
        if x in GLX: return x
    return ''
LXL={}
for line in open(os.path.join(SRC,'01-04.csv'),encoding='utf-8-sig'):
    i,h=line.rstrip('\r\n').split('\t',1)
    lem=re.search(r"href='S:([^']+)'",h); pos=re.search(r'【<font[^>]*>([^<]*)</font>】',h)
    tr=re.search(r"<font color='5'>([^<]*)</font>",h); gl=re.search(r"<font color='1'><b>(.*?)</b>",h)
    sn=re.search(r"<a href='S:(G\d{1,4})'><grk>",h)
    LXL[i]=(lem.group(1) if lem else '',pos.group(1) if pos else '',tr.group(1) if tr else '',re.sub('<[^>]+>','',gl.group(1)) if gl else '',sn.group(1) if sn else '')
# ---------- 문법 부호 -> 한국어 파싱 표
POS={'N':'명사','V':'동사','A':'형용사','RA':'관사','RP':'인칭 대명사','RD':'지시 대명사','RR':'관계 대명사','RI':'의문/부정 대명사','RX':'부정 관계 대명사','C':'접속사','P':'전치사','D':'부사','X':'불변화사','I':'감탄사','M':'수사'}
CASE={'N':('주격','nominative'),'G':('속격(소유격)','genitive'),'D':('여격','dative'),'A':('대격(목적격)','accusative'),'V':('호격','vocative')}
NUM={'S':('단수','singular'),'P':('복수','plural'),'D':('쌍수','dual')}
GEN={'M':('남성','masculine'),'F':('여성','feminine'),'N':('중성','neuter')}
TEN={'P':('현재','present'),'I':('미완료','imperfect'),'F':('미래','future'),'A':('부정과거','aorist'),'X':('현재완료','perfect'),'Y':('과거완료','pluperfect')}
VOI={'A':('능동태','active'),'M':('중간태','middle'),'P':('수동태','passive')}
MOO={'I':('직설법','indicative'),'D':('명령법','imperative'),'S':('가정법','subjunctive'),'O':('희구법','optative'),'N':('부정사','infinitive'),'P':('분사','participle')}
PER={'1':('1인칭','first'),'2':('2인칭','second'),'3':('3인칭','third')}
DEG={'C':('비교급','comparative'),'S':('최상급','superlative')}
PT=[];PTI={}
def pidx(rows):
    k=json.dumps(rows,ensure_ascii=False)
    if k not in PTI: PTI[k]=len(PT); PT.append(rows)
    return PTI[k]
def cng(s,rows):
    if len(s)>0 and s[0] in CASE: rows.append(['격',*CASE[s[0]]])
    if len(s)>1 and s[1] in NUM: rows.append(['수',*NUM[s[1]]])
    if len(s)>2 and s[2] in GEN: rows.append(['성',*GEN[s[2]]])
    if len(s)>3 and s[3] in DEG: rows.append(['급',*DEG[s[3]]])
def parse(code,lexpos):
    parts=code.split('+'); names=[];rows=[]
    for j,pc in enumerate(parts):
        m=re.match(r'^([A-Z]{1,2}?)(\d?)(?:\.(.*))?$',pc) or re.match(r'^([A-Z]+)(\d?)(?:\.(.*))?$',pc)
        if not m: continue
        p,rest=m.group(1),m.group(3) or ''
        if p not in POS and p[:1] in POS: p=p[:1]
        nm=POS.get(p,p)
        if p=='N' and lexpos=='Np': nm='고유 명사'
        names.append(nm)
        if j!=len(parts)-1: continue   # 겹친 말(예: κἀγώ)은 마지막 부분의 문법만 표시
        if p=='V' and len(rest)>=3:
            t,v,mo=rest[0],rest[1],rest[2]
            if t in TEN: rows.append(['시제',*TEN[t]])
            if v in VOI: rows.append(['태',*VOI[v]])
            if mo in MOO: rows.append(['법',*MOO[mo]])
            r=rest[3:]
            if mo=='P': cng(r,rows)
            elif mo!='N' and r:
                if r[0] in PER: rows.append(['인칭',*PER[r[0]]])
                if len(r)>1 and r[1] in NUM: rows.append(['수',*NUM[r[1]]])
        elif rest: cng(rest,rows)
    order=['격','수','성','인칭','시제','태','법','급']
    rows.sort(key=lambda r:order.index(r[0]))
    return pidx([['품사',' + '.join(names) or '기타','']]+rows)
# ---------- 책 구성 (70인경 -> 히브리어 성경 39권 순서)
BOOK={'Gen':1,'Exod':2,'Lev':3,'Num':4,'Deut':5,'JoshB':6,'JudgB':7,'Ruth':8,'1Sam/K':9,'2Sam/K':10,'1/3Kgs':11,'2/4Kgs':12,'1Chr':13,'2Chr':14,'2Esdr':15,'Esth':17,'Job':18,'Ps':19,'Prov':20,'Qoh':21,'Cant':22,'Isa':23,'Jer':24,'Lam':25,'Ezek':26,'DanTh':27,'Hos':28,'Joel':29,'Amos':30,'Obad':31,'Jonah':32,'Mic':33,'Nah':34,'Hab':35,'Zeph':36,'Hag':37,'Zech':38,'Mal':39}
VERSES=[]  # (start_word_index, book, chapter, label)
for l in open(os.path.join(SRC,'E-verse.csv'),encoding='utf-8-sig'):
    wid,_,ref=l.rstrip('\r\n').split('\t')
    m=re.match(r'「(\S+)\s*(?:(\d+):)?([^」]*)」',ref)
    bn,c,v=m.group(1),m.group(2),m.group(3).strip()
    if bn=='Obad': c,v='1',v
    if bn=='Lam' and not v and not c: c,v='1','0'
    VERSES.append((int(wid)-1,bn,int(c) if c else 0,v))
def ours(bn,c):
    b=BOOK.get(bn)
    if b==15 and c>10: return 16,c-10
    return b,c
# 랄프스판에 있는 절 (대응표 방식 고르기용)
EXIST=set(); LAST=collections.defaultdict(int)
for _,bn,c,v in VERSES:
    b,cc=ours(bn,c)
    if not b: continue
    m=re.match(r'\d+',v)
    if m: n=int(m.group()); EXIST.add((b,cc,n)); LAST[(b,cc)]=max(LAST[(b,cc)],n)
def test(b,c,v,kind):
    if kind=='Last': return LAST.get((b,c))==v
    if kind=='Exist': return (b,c,v) in EXIST
    if kind=='NotExist': return (b,c,v) not in EXIST
VMAP=lxx_versemap.load(os.path.join(SRC,'TVTMS.txt'),test)
# 영어(BSB)에 실제로 있는 절
ENGV={}
for b in range(1,40):
    bk=json.load(open(os.path.join(ROOT,'data','books','%02d.json'%b),encoding='utf-8'))
    s=set()
    for c,vs in bk['c']:
        for v in vs:
            for x in (v[0] if isinstance(v[0],list) else [v[0]]): s.add((c,x))
    ENGV[b]=s
# ---------- 본문 조립
LEX={}; books={}
stats=collections.Counter()
for i,(start,bn,c,v) in enumerate(VERSES):
    b,cc=ours(bn,c)
    if not b: continue
    end=VERSES[i+1][0] if i+1<len(VERSES) else N
    words=[]
    for w in range(start,end):
        ln=LEXNO[w]; e=LXL.get(ln); key=''
        if e and e[0]:
            key='L'+ln
            if key not in LEX: LEX[key]=[e[0],e[2],e[3],glx_key(e[4] or SN[w])]
        words.append([TXT[w],' ',TRN[w],[['',key,parse(MOR[w],e[1] if e else ''),'',-1]]])
    m=re.match(r'\d+',v); n=int(m.group()) if m else None
    # 영어·한국어 절: 대응표에 있으면 그 절, 없으면 같은 번호. "1a"처럼 덧붙은 절은 영어에 없음
    er=VMAP.get((b,cc,n),[(cc,n)]) if v.isdigit() else []
    er=[x for x in er if x in ENGV[b]]
    stats['eng' if er else 'noeng']+=1
    ch=books.setdefault(b,collections.OrderedDict()).setdefault(cc,[])
    ch.append([v,er if er!=[(cc,n)] else 0,words])
out={b:{'b':b,'c':[[c,vs] for c,vs in chs.items()]} for b,chs in books.items()}
print('books',len(out),'lex',len(LEX),'pt',len(PT),dict(stats))
# ---------- 검색 색인 (build_extra.py와 같은 구조)
lem=[];lid={};V=[];L=[];M=[];Wn=[]
for b in sorted(out):
    for c,vs in out[b]['c']:
        for vi,(lab,er,words) in enumerate(vs):
            for wi,w in enumerate(words):
                k=w[3][0][1]
                if k and k not in lid: lid[k]=len(lem); lem.append(k)
                L.append(lid[k] if k else -1); M.append(w[3][0][2]); Wn.append(wi*8)
            V+=[b,c,vi,len(words)]
idx={'lem':lem,'v':V,'l':L,'m':M,'w':Wn,'en':{}}
os.makedirs(OUT,exist_ok=True)
data={'kind':'ob-lxx','ver':1,'name':'Rahlfs 1935 (CCAT/CATSS, eliranwong/LXX-Rahlfs-1935)',
      'credit':'70인경 본문 Rahlfs 1935, 형태 분석 CATSS LXXM (CCAT, University of Pennsylvania), 자료 정리 eliranwong/LXX-Rahlfs-1935 (CC BY-NC-SA 4.0), 절 대응 STEPBible TVTMS (CC BY). 개인 공부용으로만 쓰고 다른 사람에게 나누지 않습니다.','pt':PT,'lex':LEX,'books':out,'idx':idx}
raw=json.dumps(data,ensure_ascii=False,separators=(',',':')).encode('utf-8')
p=os.path.join(OUT,'원어성경_70인경.json.gz')
with gzip.open(p,'wb',compresslevel=9) as f: f.write(raw)
print('raw %.1fMB  gz %.1fMB -> %s'%(len(raw)/1e6,os.path.getsize(p)/1e6,p))
