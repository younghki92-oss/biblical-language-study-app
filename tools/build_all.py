# 실행: 원어성경앱 폴더에서  python3 tools/build_all.py
# 원자료는 _원자료/ 폴더에서 읽고, 결과는 data/ 폴더에 책별로 저장합니다.
import csv,re,json,collections,unicodedata,glob,gzip,base64,sys,os
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
OUT=os.path.join(ROOT,'data'); os.chdir(os.path.join(ROOT,'_원자료'))
csv.field_size_limit(10**9)
exec(open(os.path.join(HERE,'hebmap.py'),encoding='utf-8').read().split('# WLCM')[0])  # loads T (tahot by heb verse), BK, bi
# ---------- shared helpers
def N(t): return unicodedata.normalize('NFC',t).strip()
def B(t): return ''.join(c for c in unicodedata.normalize('NFD',t) if not unicodedata.combining(c)).lower().strip()
def clean_def(h):
    h=re.sub(r"<ref='[^']*'>(.*?)</ref>",r'<span class="ref">\1</span>',h)
    h=re.sub(r'<BR\s*/?>','<br>',h,flags=re.I)
    h=h.replace('__','')
    h=re.sub(r'<(?!/?(b|i|br|span)\b)[^>]*>','',h)
    h=re.sub(r'\((AS|BDB)\)\s*$','',h.strip())
    h=re.sub(r'(<br>\s*)+$','',h)
    return h.strip()
PT={}; PTL=[]  # parse table
def pidx(rows):
    k=json.dumps(rows,ensure_ascii=False)
    if k not in PT: PT[k]=len(PTL); PTL.append(rows)
    return PT[k]
# ---------- Greek translit
GM={'α':'a','β':'b','γ':'g','δ':'d','ε':'e','ζ':'z','η':'ē','θ':'th','ι':'i','κ':'k','λ':'l','μ':'m','ν':'n','ξ':'x','ο':'o','π':'p','ρ':'r','σ':'s','ς':'s','τ':'t','υ':'y','φ':'ph','χ':'ch','ψ':'ps','ω':'ō'}
def gtr(w):
    letters=[]
    for ch in unicodedata.normalize('NFD',w):
        if unicodedata.combining(ch):
            if letters: letters[-1][1].add(ch)
        else: letters.append([ch,set()])
    L=[(b.lower(),mk) for b,mk in letters if b.lower() in GM]
    if not L: return w
    rough=any('\u0314' in mk for _,mk in L[:3]); cap=letters[0][0].isupper()
    s='';i=0
    while i<len(L):
        b,mk=L[i]; nb=L[i+1][0] if i+1<len(L) else ''
        if b=='γ' and nb and nb in 'γκξχ': s+='n';i+=1;continue
        if b in 'αεηο' and nb=='υ' and '\u0308' not in L[i+1][1]: s+=GM[b]+'u';i+=2;continue
        if b=='υ' and nb=='ι': s+='ui';i+=2;continue
        s+=GM[b];i+=1
    if rough: s=('rh'+s[1:]) if s.startswith('r') else 'h'+s
    return s[0].upper()+s[1:] if cap else s
# ---------- Greek lexicon
GLX={}; g_by_s={}; g_by_l={}; g_by_b={}
for line in open(glob.glob('STEPBible-Data-master/Lexicons/TBESG*')[0],encoding='utf-8'):
    p=line.rstrip('\n').split('\t')
    if len(p)<8 or not re.match(r'^G\d{4}',p[0]): continue
    e=(p[0],p[3],p[4],p[6],p[7])
    g_by_s.setdefault(p[0][:5],e); g_by_l.setdefault(N(p[3]),e); g_by_b.setdefault(B(p[3]),e)
KO={'noun':'명사','verb':'동사','pron':'대명사','det':'관사','conj':'접속사','prep':'전치사','adj':'형용사','adv':'부사','ptcl':'불변화사','num':'수사','intj':'감탄사',
'common':'보통','personal':'인칭','proper':'고유','demonstrative':'지시','relative':'관계','interrogative':'의문','indefinite':'부정','reflexive':'재귀','reciprocal':'상호','possessive':'소유','correlative':'상관',
'third':'3인칭','second':'2인칭','first':'1인칭','singular':'단수','plural':'복수','masculine':'남성','neuter':'중성','feminine':'여성',
'nominative':'주격','accusative':'대격(목적격)','genitive':'속격(소유격)','dative':'여격','vocative':'호격',
'aorist':'부정과거','present':'현재','imperfect':'미완료','perfect':'현재완료','future':'미래','pluperfect':'과거완료',
'active':'능동태','middle':'중간태','passive':'수동태','middlepassive':'중간/수동태',
'indicative':'직설법','participle':'분사','subjunctive':'가정법','imperative':'명령법','infinitive':'부정사','optative':'희구법',
'superlative':'최상급','comparative':'비교급'}
def gparse(x):
    pos=KO.get(x['class'],x['class'] or '기타')
    t=x['type']
    if t and t!='substantive' and x['class'] in('noun','pron','adj'): pos=KO.get(t,t)+' '+pos
    if t=='substantive': pos+=' (명사적 용법)'
    rows=[['품사',pos,'']]
    for k,lab in [('case','격'),('number','수'),('gender','성'),('person','인칭'),('tense','시제'),('voice','태'),('mood','법'),('degree','급')]:
        if x[k]: rows.append([lab,KO.get(x[k],x[k]),x[k]])
    return pidx(rows)
GB=['Mat','Mrk','Luk','Jhn','Act','Rom','1Co','2Co','Gal','Eph','Php','Col','1Th','2Th','1Ti','2Ti','Tit','Phm','Heb','Jas','1Pe','2Pe','1Jn','2Jn','3Jn','Jud','Rev']
# ---------- English tokens
def load_eng(fn):
    E=collections.defaultdict(list)
    for x in csv.DictReader(open(fn,encoding='utf-8'),delimiter='\t'):
        E[x['source_verse']].append(x)
    return E
def build_book_struct(verses, eng, groups_src, groups_tgt):
    pass
# ---------- Hebrew
HLX={}; h_by_k={}; h_by_5={}
for line in open(glob.glob('STEPBible-Data-master/Lexicons/TBESH*')[0],encoding='utf-8'):
    p=line.rstrip('\n').split('\t')
    if len(p)<8 or not re.match(r'^H\d{4}',p[0]): continue
    k=p[1].split(' ')[0]
    e=(k,p[3],p[4],p[6],p[7])
    h_by_k.setdefault(k,e); h_by_5.setdefault(k[:5],e)
def hlex(k):
    k=k.strip('{}').strip()
    m=re.match(r'^(H\d{4})([A-Za-z]?)',k)
    if not m: return None
    return h_by_k.get(m.group(1)+m.group(2).upper()) or h_by_k.get(k) or h_by_5.get(m.group(1))
HK={'c':'보통','g':'족속명','p':'고유'}
GEN={'m':('남성','masculine'),'f':('여성','feminine'),'c':('통성','common'),'b':('양성','both')}
NUM={'s':('단수','singular'),'p':('복수','plural'),'d':('쌍수','dual')}
ST={'a':('절대형','absolute'),'c':('연계형','construct'),'d':('한정형','determined')}
PER={'1':('1인칭','1st'),'2':('2인칭','2nd'),'3':('3인칭','3rd')}
HSTEM={'q':'칼 Qal','N':'니팔 Niphal','p':'피엘 Piel','P':'푸알 Pual','h':'히필 Hiphil','H':'호팔 Hophal','t':'히트파엘 Hithpael','o':'폴렐 Polel','O':'폴랄 Polal','r':'히트폴렐 Hithpolel','m':'포엘 Poel','M':'포알 Poal','k':'팔렐 Palel','K':'풀랄 Pulal','Q':'칼 수동 Qal passive','l':'필펠 Pilpel','L':'폴팔 Polpal','f':'히트팔펠 Hithpalpel','D':'니트파엘 Nithpael','j':'페알랄 Pealal','i':'필렐 Pilel','u':'호트파알 Hothpaal','c':'티필 Tiphil','v':'히쉬타펠 Hishtaphel','w':'니트팔렐 Nithpalel','y':'니트포엘 Nithpoel','z':'히트포엘 Hithpoel'}
ASTEM={'q':'페알 Peal','Q':'페일 Peil','u':'히트페엘 Hithpeel','p':'파엘 Pael','P':'이트파알 Ithpaal','M':'히트파알 Hithpaal','a':'아펠 Aphel','h':'하펠 Haphel','s':'사펠 Saphel','e':'샤펠 Shaphel','H':'호팔 Hophal','i':'이트페엘 Ithpeel','t':'히쉬타펠 Hishtaphel','v':'이쉬타펠 Ishtaphel','w':'히트아펠 Hithaphel','o':'폴렐 Polel','z':'이트포엘 Ithpoel','r':'히트폴렐 Hithpolel','f':'히트팔펠 Hithpalpel','b':'헤팔 Hephal','c':'티펠 Tiphel','m':'포엘 Poel','l':'팔펠 Palpel','L':'이트팔펠 Ithpalpel','O':'이트폴렐 Ithpolel','G':'이타팔 Ittaphal'}
VT={'p':('완료','perfect'),'q':('연속 완료 (와우 완료)','sequential perfect'),'i':('미완료','imperfect'),'w':('연속 미완료 (와우 연속법)','sequential imperfect'),'h':('권유형','cohortative'),'j':('지시형','jussive'),'v':('명령형','imperative'),'r':('능동 분사','participle active'),'s':('수동 분사','participle passive'),'a':('부정사 절대형','infinitive absolute'),'c':('부정사 연계형','infinitive construct')}
PRT={'d':'지시','f':'부정','i':'의문','p':'인칭','r':'관계'}
SUF={'d':('방향 접미어 ה','directional he'),'h':('첨가 ה','paragogic he'),'n':('첨가 ן','paragogic nun'),'p':('대명 접미어','pronominal suffix')}
TT={'a':'긍정','d':'정관사','e':'권유','i':'의문','j':'감탄사','m':'지시','n':'부정어','o':'목적격 표지','r':'관계사'}
AT={'a':'형용사','c':'기수','g':'족속명','o':'서수'}
def hdec(code,lang):
    if not code: return None
    c=code[0]; r=code[1:]; rows=[]
    def add(lab,d,ch):
        if ch in d: v=d[ch]; rows.append([lab,v[0],v[1]] if isinstance(v,tuple) else [lab,v,''])
    if c=='N':
        pos=HK.get(r[:1],'')+' 명사'; rows.append(['품사',pos.strip(),'noun'])
        add('성',GEN,r[1:2]); add('수',NUM,r[2:3]); add('상태',ST,r[3:4])
    elif c=='A':
        rows.append(['품사',AT.get(r[:1],'형용사'),'adjective'])
        add('성',GEN,r[1:2]); add('수',NUM,r[2:3]); add('상태',ST,r[3:4])
    elif c=='V':
        rows.append(['품사','동사','verb'])
        st=(ASTEM if lang=='A' else HSTEM).get(r[:1])
        if st: ko,en=st.split(' ',1); rows.append(['어간',ko,en])
        t=r[1:2]; add('형태',VT,t)
        if t in 'rs' and t: add('성',GEN,r[2:3]); add('수',NUM,r[3:4]); add('상태',ST,r[4:5])
        elif t in 'ac' and t: pass
        else: add('인칭',PER,r[2:3]); add('성',GEN,r[3:4]); add('수',NUM,r[4:5])
    elif c=='P':
        rows.append(['품사',PRT.get(r[:1],'')+' 대명사','pronoun'])
        add('인칭',PER,r[1:2]); add('성',GEN,r[2:3]); add('수',NUM,r[3:4])
    elif c=='S':
        s=SUF.get(r[:1],('접미어','suffix')); rows.append(['품사',s[0],s[1]])
        if r[:1]=='p': add('인칭',PER,r[1:2]); add('성',GEN,r[2:3]); add('수',NUM,r[3:4])
    elif c=='T': rows.append(['품사',TT.get(r[:1],'불변화사'),'particle'])
    elif c=='R': rows.append(['품사','전치사'+(' + 정관사' if r[:1]=='d' else ''),'preposition'])
    elif c=='C': rows.append(['품사','접속사','conjunction'])
    elif c=='D': rows.append(['품사','부사','adverb'])
    else: return None
    if lang=='A': rows.append(['언어','아람어','Aramaic'])
    return pidx(rows)
POSKO={'noun':'명사','verb':'동사','preposition':'전치사','particle':'불변화사','conjunction':'접속사','adjective':'형용사','adverb':'부사','pronoun':'대명사','suffix':'접미어'}
KOB=['창세기','출애굽기','레위기','민수기','신명기','여호수아','사사기','룻기','사무엘상','사무엘하','열왕기상','열왕기하','역대상','역대하','에스라','느헤미야','에스더','욥기','시편','잠언','전도서','아가','이사야','예레미야','예레미야애가','에스겔','다니엘','호세아','요엘','아모스','오바댜','요나','미가','나훔','하박국','스바냐','학개','스가랴','말라기',
'마태복음','마가복음','누가복음','요한복음','사도행전','로마서','고린도전서','고린도후서','갈라디아서','에베소서','빌립보서','골로새서','데살로니가전서','데살로니가후서','디모데전서','디모데후서','디도서','빌레몬서','히브리서','야고보서','베드로전서','베드로후서','요한일서','요한이서','요한삼서','유다서','요한계시록']
def assemble(bookno, verses_src, ENG, s2g, t2g):
    """verses_src: ordered list of (srcVerseKey8, words) ; words already built with gid"""
    chapters=collections.OrderedDict(); last=(1,0)
    for key,words in verses_src:
        toks=ENG.get(key,[])
        ev=None
        for t in toks:
            if t['exclude']!='y': ev=(int(t['id'][2:5]),int(t['id'][5:8])); break
        if ev is None and toks: ev=(int(toks[0]['id'][2:5]),int(toks[0]['id'][5:8]))
        if ev is None: ev=(last[0],last[1])
        last=ev
        evs=[]
        for t in toks:
            if t['exclude']=='y': continue
            q=(int(t['id'][2:5]),int(t['id'][5:8]))
            if q[0]==ev[0] and q[1] not in evs: evs.append(q[1])
        if not evs: evs=[ev[1]]
        hc,hv=int(key[2:5]),int(key[5:8])
        hl=f'{hc}:{hv}' if (hc,hv)!=ev else 0
        et=[]
        for t in toks:
            fl=(1 if t['skip_space_after']=='y' else 0)|(2 if t['exclude']=='y' else 0)
            et.append([t['text'],fl,t2g.get(t['id'],-1)])
        chapters.setdefault(ev[0],[]).append([evs if len(evs)>1 else evs[0],hl,words,et])
    return {'b':bookno,'c':[[c,v] for c,v in chapters.items()]}

def groups_from(fn):
    s2g={};t2g={}
    for i,r in enumerate(json.load(open(fn))['records']):
        for s in r['source']: s2g.setdefault(s,i)
        for t in r['target']: t2g.setdefault(t,i)
    return s2g,t2g
books={}
# ===== NT
s2g,t2g=groups_from('sbl-bsb.json'); ENG=load_eng('nt_BSB.tsv')
byv=collections.OrderedDict()
for x in csv.DictReader(open('mg.tsv',encoding='utf-8'),delimiter='\t'):
    i=x['xml:id']
    if not i.startswith('n'): continue
    key=i[1:9]
    e=g_by_l.get(N(x['lemma'])) or (g_by_s.get('G%04d'%int(re.sub(r'\D','',x['strong']))) if re.sub(r'\D','',x['strong']) else None) or g_by_b.get(B(x['lemma']))
    lk=''
    if e: lk=e[0]; GLX.setdefault(lk,[e[1],gtr(e[1].split(',')[0]),e[3],clean_def(e[4])])
    a=x['after'];a=a if (a.endswith(' ') or a=='') else a+' '
    if a=='': a=' '
    w=[x['text'],a if a!=' ' else '',gtr(x['text']),[[x['text'],lk,gparse(x),x['english'] or x['gloss'],s2g.get(i,-1)]]]
    if lk=='': w[3][0][1]=''
    w[3][0][3]= w[3][0][3] if not e or (x['english'] or x['gloss']) else ''
    byv.setdefault(key,[]).append(w)
bybook=collections.defaultdict(list)
for k,ws in byv.items(): bybook[int(k[:2])].append((k,ws))
for b,vs in bybook.items(): books[b]=assemble(b,vs,ENG,s2g,t2g)
print('NT books',len(books),'GLX',len(GLX))
# ===== OT
s2g,t2g=groups_from('wlc-bsb.json'); ENG=load_eng('ot_BSB.tsv')
W=collections.OrderedDict()
for r in csv.DictReader(open('WLCM.tsv',encoding='utf-8'),delimiter='\t'):
    i=r['id']; k=i[1:9]
    W.setdefault(k,collections.OrderedDict()).setdefault(int(i[9:12]),[]).append(r)
CANT=re.compile('[\u0591-\u05AF]')
stats=collections.Counter()
bybook=collections.defaultdict(list)
for k,wd in W.items():
    tk=(int(k[:2]),int(k[2:5]),int(k[5:8])); tl=T.get(tk,[])
    match=len(tl)==len(wd)
    ws=[]
    for n,(wn,parts) in enumerate(wd.items()):
        t=tl[n] if match else None
        ptxt=[re.sub(r'-\d+$','',p['altId']) for p in parts]
        lang='H'; mparts=None; dparts=None
        if t:
            mo=t['mo']; lang=mo[:1] if mo[:1] in 'HA' else 'H'
            mp=mo[1:].split('/') if mo[:1] in 'HA' else mo.split('/')
            dp=t['ds'].split('/')
            if len(mp)==len(parts): mparts=mp
            if len(dp)==len(parts): dparts=dp
            disp=t['heb'].replace('/','').replace('\\','')
            tr=t['tr'].replace('/','')
        else:
            disp=''.join(ptxt); tr=''
        stats['m' if mparts else 'nm']+=1
        P=[]
        for j,p in enumerate(parts):
            e=None
            if dparts: e=hlex(dparts[j])
            if not e:
                s=p['strongs']; m=re.match(r'(\d+)([a-z]?)',s)
                if m: e=hlex('H%04d%s'%(int(m.group(1)),m.group(2).upper()))
            lk=''
            if e: lk=e[0]; HLX.setdefault(lk,[e[1],e[2],e[3],re.sub(r'^:\s*[^<]*<br>','',clean_def(e[4]))])
            pi=hdec(mparts[j],lang) if mparts else None
            if pi is None:
                pos=POSKO.get(p['pos'],p['pos']); pi=pidx([['품사',pos,p['pos']]]) if pos else -1
            P.append([ptxt[j],lk,pi,p['gloss'] or p['gloss2'],s2g.get(p['id'],-1)])
        after='' if disp.endswith('־') else ' '
        ws.append([disp,after,tr,P])
    bybook[tk[0]].append((k,ws))
for b,vs in bybook.items(): books[b]=assemble(b,vs,ENG,s2g,t2g)
print('books',len(books),'HLX',len(HLX),stats,'PT',len(PTL))
# ===== 저장: 책별 파일 + 사전 + 파싱 표
def save(name,obj):
    with open(os.path.join(OUT,name),'w',encoding='utf-8') as f: json.dump(obj,f,ensure_ascii=False,separators=(',',':'))
os.makedirs(os.path.join(OUT,'books'),exist_ok=True)
for b,bk in books.items(): save('books/%02d.json'%b,bk)
save('glx.json',GLX); save('hlx.json',HLX); save('pt.json',PTL)
print('saved to',OUT)
