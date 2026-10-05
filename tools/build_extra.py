# 검색 색인과 한국어 성경(개역한글) 파일을 만듭니다.
# 실행: 원어성경앱 폴더에서  python3 tools/build_extra.py   (먼저 build_all.py로 data/books를 만들어 둘 것)
#
# data/search/ot.json, nt.json  (구약/신약 색인)
#   lem : 어근 키 목록 (예: "G3056", "H0430G")
#   v   : 절마다 [책, 장, 장 안의 절 순서, 이 절의 단어 조각 수] 를 이어 붙인 숫자 목록
#   l   : 단어 조각마다 어근 번호 (lem 안의 순서, 없으면 -1)
#   m   : 단어 조각마다 파싱 표 번호 (pt.json 안의 순서)
#   w   : 단어 조각마다 단어 순서*8 + 조각 순서
#   en  : 어근 번호 -> BSB가 옮긴 영어 표현과 횟수 (많은 순서로 최대 12개)
# data/krv/NN.json : {"장": {"절": "본문"}}
import os,json,collections,re
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D=os.path.join(ROOT,'data')
def save(name,obj):
    p=os.path.join(D,name); os.makedirs(os.path.dirname(p),exist_ok=True)
    with open(p,'w',encoding='utf-8') as f: json.dump(obj,f,ensure_ascii=False,separators=(',',':'))
def eng_join(toks):
    s=' '.join(toks)
    s=re.sub(r' ([,.;:!?’”)])',r'\1',s)
    ws=s.strip(' ,.;:!?“”‘’()').lower().split()
    # 앞에 붙은 관사, 소유격, 전치사 등은 떼어 내어 같은 번역끼리 묶음 (예: "your god" -> "god", "you love" -> "love")
    while len(ws)>1 and ws[0] in LEAD: ws=ws[1:]
    return ' '.join(ws)
LEAD={'the','a','an','of','and','to','your','my','his','her','our','their','its','this','that','these','those',
      'i','you','he','she','we','they','it','who'}
for name,books in [('ot',range(1,40)),('nt',range(40,67))]:
    lem=[];lid={};V=[];L=[];M=[];Wn=[];EN=collections.defaultdict(collections.Counter)
    for b in books:
        bk=json.load(open(os.path.join(D,'books','%02d.json'%b),encoding='utf-8'))
        for c,verses in bk['c']:
            for vi,(vn,hl,words,et) in enumerate(verses):
                g2e=collections.defaultdict(list)
                for t in et:
                    if t[2]>=0 and not t[1]&2: g2e[t[2]].append(t[0])
                n=0
                for wi,w in enumerate(words):
                    for pi,p in enumerate(w[3]):
                        k=p[1]
                        if k:
                            if k not in lid: lid[k]=len(lem); lem.append(k)
                            i=lid[k]
                            if p[4]>=0 and g2e.get(p[4]):
                                e=eng_join(g2e[p[4]])
                                if e: EN[i][e]+=1
                        else: i=-1
                        L.append(i); M.append(p[2]); Wn.append(wi*8+min(pi,7)); n+=1
                V+= [b,c,vi,n]
    en={str(i):[[e,n] for e,n in cnt.most_common(12)] for i,cnt in EN.items()}
    save('search/%s.json'%name,{'lem':lem,'v':V,'l':L,'m':M,'w':Wn,'en':en})
    print(name,'lemmas',len(lem),'parts',len(L),'verses',len(V)//4)
# ----- 개역한글
krv=json.load(open(os.path.join(ROOT,'_원자료','krv','KRV.json'),encoding='utf-8'))
K=collections.defaultdict(lambda:collections.defaultdict(dict))
for x in krv: K[x['book']][str(x['chapter'])][str(x['verse'])]=x['text'].strip()
for b in range(1,67): save('krv/%02d.json'%b,K[b])
print('krv books',len(K))
