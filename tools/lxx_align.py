# CATSS 대조 본문(히브리어 ↔ 70인경, E. Tov)으로 70인경 낱말마다 짝이 되는 히브리어 낱말을 찾습니다.
# 히브리어 낱말은 data/books 안의 위치 [영어 장, 절 순서, 단어 순서]로 돌려주며,
# 앱은 이 히브리어 낱말의 영어 짝(Clear Bible 정렬)을 이어서 영어 단어를 강조합니다.
# 원자료: CCAT parallel (_원자료/lxx/par/*.par) — CCAT 이용 동의 필요, 공개 금지
import os,re,json,glob,unicodedata,difflib,collections
PARFILE={1:'01.Genesis',2:'02.Exodus',3:'03.Lev',4:'04.Num',5:'05.Deut',6:'06.JoshB',7:'08.JudgesB',8:'10.Ruth',9:'11.1Sam',10:'12.2Sam',
 11:'13.1Kings',12:'14.2Kings',13:'15.1Chron',14:'16.2Chron',15:'18.Ezra',16:'19.Neh',17:'18.Esther',18:'26.Job',19:'20.Psalms',20:'23.Prov',
 21:'24.Qoh',22:'25.Cant',23:'40.Isaiah',24:'41.Jer',25:'43.Lam',26:'44.Ezekiel',27:'46.DanielTh',28:'28.Hosea',29:'31.Joel',30:'30.Amos',
 31:'33.Obadiah',32:'32.Jonah',33:'29.Micah',34:'34.Nahum',35:'35.Hab',36:'36.Zeph',37:'37.Haggai',38:'38.Zech',39:'39.Malachi'}
HB=dict(zip(')BGDHWZX+YKLMNS(PCQR#&$T','אבגדהוזחטיכלמנסעפצקרשששת'))
GB=dict(zip('ABGDEZHQIKLMNCOPRSJTUFXYW','αβγδεζηθικλμνξοπρσστυφχψω'))
FIN=str.maketrans('ךםןףץ','כמנפצ')
def nh(s):  # 히브리어: 자음만
    s=re.sub(r'[֑-ׇ־׀׃/\\\s־׀]','',s); return s.translate(FIN)
def nhb(tok): return ''.join(HB.get(c,'') for c in tok)
def ng(s):  # 헬라어: 악센트 없는 소문자
    s=unicodedata.normalize('NFD',s.lower()); s=''.join(c for c in s if not unicodedata.combining(c)).replace('ς','σ')
    return re.sub(r'[^α-ω]','',s)
def ngb(tok): return ''.join(GB.get(c,'') for c in tok.upper())
def clean_cols(line):
    p=line.rstrip('\r\n').split('\t')
    if len(p)<2: return None
    h,g=p[0],p[1]
    h=re.sub(r'\{[^}]*\}|<[^>]*>',' ',h); h=re.sub(r'\s=.*$','',h)   # 둘째 칸(재구성 읽기)은 버림
    g=re.sub(r'\{[^}]*\}',' ',g)
    m=re.findall(r'\[(\d+)(?:\.(\w+))?\]',g)
    g=re.sub(r'\[[^\]]*\]',' ',g)
    ht=[] if h.strip().startswith('--+') else [nhb(t) for t in h.split() if nhb(t)]
    gt=[] if g.strip().startswith('---') else [ngb(t) for t in g.split() if ngb(t)]
    lref=None
    if m:
        a,b=m[0]; lref=(int(a),b) if b else (None,a)
    return ht,gt,lref
def sim(a,b):
    if a==b: return 1.0
    if not a or not b: return 0.0
    return difflib.SequenceMatcher(None,a,b).ratio()
def seqmatch(src,dst,win=4,th=0.75):
    """src 토큰 목록을 dst 낱말 목록에 차례대로 맞춤 -> {src 순번: dst 순번}"""
    out={};j=0
    for i,s in enumerate(src):
        best=None
        for k in range(j,min(len(dst),j+win)):
            r=sim(s,dst[k])
            if r>=th and (best is None or r>best[0]+0.05): best=(r,k)
            if r==1.0: break
        if best: out[i]=best[1]; j=best[1]+1
    return out
def build(root,lxx_books):
    """lxx_books: {b:{'c':[[c,[[label,er,words],...]],...]}} -> 각 낱말에 links 목록을 덧붙임"""
    src=os.path.join(root,'_원자료','lxx','par'); stats=collections.Counter()
    for b,bk in lxx_books.items():
        heb=json.load(open(os.path.join(root,'data','books','%02d.json'%b),encoding='utf-8'))
        MT={};HC=dict((c,vs) for c,vs in heb['c'])   # 히브리어(MT) 장·절 -> (영어 장, 절 순서)
        for c,vs in heb['c']:
            for vi,v in enumerate(vs):
                if v[1]: hc,hv=map(int,v[1].split(':'))
                else: hc,hv=c,(v[0][0] if isinstance(v[0],list) else v[0])
                MT[(hc,hv)]=(c,vi)
        LX={}   # 70인경 (장, 절 이름) -> 낱말 목록
        for c,vs in bk['c']:
            for v in vs: LX[(c,v[0])]=v[2]
        # 대조 본문 읽기
        verses=[];cur=None
        for line in open(os.path.join(src,PARFILE[b]+'.par'),encoding='latin-1'):
            m=re.match(r'^[1-3]?[A-Za-z]+\s+(\d+):(\d+)\s*$',line.strip())
            if m: cur=[(int(m.group(1)),int(m.group(2))),[]]; verses.append(cur); continue
            if cur is None or not line.strip(): continue
            r=clean_cols(line)
            if r: cur[1].append(r)
        # 1단계: 히브리어 토큰 -> 히브리어 낱말 위치
        byL=collections.defaultdict(list)   # 70인경 절 -> [(헬라어 토큰 목록, 히브리어 위치 목록)]
        for (hc,hv),lines in verses:
            loc=MT.get((hc,hv)); hlinks=[[] for _ in lines]
            if loc:
                c,vi=loc;words=HC[c][vi][2]
                dst=[nh(w[0]) for w in words];src_t=[];own=[]
                for li,(ht,gt,lr) in enumerate(lines):
                    for t in ht: src_t.append(t);own.append(li)
                mm=seqmatch(src_t,dst)
                for i,k in mm.items(): hlinks[own[i]].append([c,vi,k])
                stats['heb_tok']+=len(src_t);stats['heb_hit']+=len(mm)
            for li,(ht,gt,lr) in enumerate(lines):
                if lr is None: key=(hc,str(hv))
                elif lr[0] is None: key=(hc,lr[1])
                else: key=(lr[0],lr[1])
                if b==16 and key[0]>=11: key=(key[0]-10,key[1])   # 느헤미야 = 에스드라 2서 11장~
                byL[key].append((gt,hlinks[li]))
        # 2단계: 헬라어 토큰 -> 70인경 낱말
        for key,items in byL.items():
            words=LX.get(key)
            if not words: stats['lxx_miss']+=1; continue
            dst=[ng(w[0]) for w in words];src_t=[];own=[]
            for ii,(gt,hl) in enumerate(items):
                for t in gt: src_t.append(t);own.append(ii)
            mm=seqmatch(src_t,dst)
            stats['grk_tok']+=len(src_t);stats['grk_hit']+=len(mm)
            for i,k in mm.items():
                hl=items[own[i]][1]
                if hl:
                    w=words[k]
                    if len(w)<5: w.append([])
                    for x in hl:
                        if x not in w[4]: w[4].append(x)
    return stats
