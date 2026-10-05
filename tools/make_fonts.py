# 한글 글꼴(IBM Plex Sans KR)을 앱에 필요한 글자만 담아 작게 만듭니다.
# 실행: 원어성경앱 폴더에서  python3 tools/make_fonts.py   (먼저 pip install fonttools brotli)
import os,glob
from fontTools import subset
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
chars=set(chr(c) for c in range(0x20,0x7f))|set('·…‘’“”–—‹›×←→↑↓○●')
# 자주 쓰는 한글 2,350자 (KS X 1001)
for hi in range(0xB0,0xC9):
    for lo in range(0xA1,0xFF):
        try: chars.add(bytes([hi,lo]).decode('euc-kr'))
        except UnicodeDecodeError: pass
# 앱 화면과 데이터에 실제로 나오는 한글
for f in [os.path.join(ROOT,'index.html'),os.path.join(ROOT,'data','pt.json')]:
    if os.path.exists(f): chars|={c for c in open(f,encoding='utf-8').read() if '가'<=c<='힣' or 'ㄱ'<=c<='ㆎ'}
text=''.join(sorted(chars))
css=[]
for w,name in [(400,'Regular'),(500,'Medium'),(600,'SemiBold')]:
    out='plexkr-%d.woff2'%w
    opt=subset.Options(); opt.flavor='woff2'; opt.layout_features=['*']
    f=subset.load_font(os.path.join(ROOT,'_원자료','Plex-%s.ttf'%name),opt)
    s=subset.Subsetter(opt); s.populate(text=text); s.subset(f)
    subset.save_font(f,os.path.join(ROOT,'fonts',out),opt)
    css.append("@font-face {\n  font-family: 'IBM Plex Sans KR';\n  font-style: normal;\n  font-weight: %d;\n  font-display: swap;\n  src: url(%s) format('woff2');\n}"%(w,out))
p=os.path.join(ROOT,'fonts','fonts.css'); old=open(p,encoding='utf-8').read()
old=old.split('/* IBM Plex Sans KR */')[0].rstrip()
open(p,'w',encoding='utf-8').write(old+'\n/* IBM Plex Sans KR */\n'+'\n'.join(css)+'\n')
print(len(text),'chars')
