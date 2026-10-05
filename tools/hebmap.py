import csv,re,collections,json
BK=['Gen','Exo','Lev','Num','Deu','Jos','Jdg','Rut','1Sa','2Sa','1Ki','2Ki','1Ch','2Ch','Ezr','Neh','Est','Job','Psa','Pro','Ecc','Sng','Isa','Jer','Lam','Ezk','Dan','Hos','Jol','Amo','Oba','Jon','Mic','Nam','Hab','Zep','Hag','Zec','Mal']
bi={b:i+1 for i,b in enumerate(BK)}
# TAHOT
T=collections.defaultdict(list); bad=set()
for line in open('tahot.txt',encoding='utf-8'):
    m=re.match(r'^(\w+)\.(\d+)\.(\d+)(?:\((\d+)\.(\d+)\))?#(\d+)=(\S+)\t',line)
    if not m: continue
    b,c,v,hc,hv,w,ty=m.groups()
    if b not in bi: bad.add(b);continue
    if ty.startswith('X'): continue
    hc=int(hc or c); hv=int(hv or v)
    p=line.rstrip('\n').split('\t')
    T[(bi[b],hc,hv)].append(dict(eng=(int(c),int(v)),heb=p[1],tr=p[2],en=p[3],ds=p[4],mo=p[5],ty=ty))
# WLCM
W=collections.defaultdict(lambda:collections.OrderedDict())
for r in csv.DictReader(open('WLCM.tsv',encoding='utf-8'),delimiter='\t'):
    i=r['id']; k=(int(i[1:3]),int(i[3:6]),int(i[6:9])); wn=int(i[9:12])
    W[k].setdefault(wn,[]).append(r)
mis=0;tot=0;pm=0;ex=[]
for k in W:
    tot+=1
    a=len(W[k]); b=len(T.get(k,[]))
    if a!=b:
        mis+=1
        if len(ex)<8: ex.append((k,a,b))
    else:
        for (wn,parts),t in zip(W[k].items(),T[k]):
            if len(parts)!=len(t['heb'].replace('\\','').split('/')): pm+=1
print('bad',bad,'verses',tot,'mismatch',mis,ex,'partmismatch',pm)
