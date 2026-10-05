# 앱 아이콘(PNG)을 만듭니다. 실행: python3 tools/make_icons.py  (pip install pillow fonttools brotli)
import os,io
from fontTools.ttLib import TTFont
from PIL import Image,ImageDraw,ImageFont
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); F=os.path.join(ROOT,'fonts')
def font(name,size):
    t=TTFont(os.path.join(F,name)); t.flavor=None; b=io.BytesIO(); t.save(b); b.seek(0)
    return ImageFont.truetype(b,size)
LAPIS=(44,74,154); PAPER=(246,247,244)
def draw(S,inset,radius):
    im=Image.new('RGBA',(S,S),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([inset,inset,S-inset-1,S-inset-1],radius=radius,fill=LAPIS)
    inner=S-2*inset; c=S/2
    he=font('noto-600-hebrew.woff2',int(inner*0.46)); gk=font('gentium-400-greek.woff2',int(inner*0.50))
    d.text((c-inner*0.15,c+inner*0.02),'א',font=he,fill=PAPER,anchor='mm')
    d.text((c+inner*0.17,c+inner*0.02),'α',font=gk,fill=PAPER,anchor='mm')
    d.line([c-inner*0.30,c+inner*0.27,c+inner*0.30,c+inner*0.27],fill=PAPER+(150,),width=max(2,int(inner*0.012)))
    return im
def maskable(S):  # 전체를 채우고 글자는 가운데 안전 영역에
    im=Image.new('RGB',(S,S),LAPIS); sm=draw(int(S*0.8),0,0).convert('RGBA'); im.paste(sm,(int(S*0.1),)*2,sm); return im
for S in (192,512): draw(S,int(S*0.06),int(S*0.2)).save(os.path.join(ROOT,'icons','icon-%d.png'%S))
maskable(512).save(os.path.join(ROOT,'icons','maskable-512.png'))
draw(180,0,0).convert('RGB').save(os.path.join(ROOT,'icons','apple-touch-icon.png'))
print('icons ok')
