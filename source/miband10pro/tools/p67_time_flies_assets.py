from __future__ import annotations
from dataclasses import dataclass

CANVAS=(336,480)
RGBA=tuple[int,int,int,int]
BG=(8,10,16,255); PANEL=(19,24,34,255); GRID=(39,47,62,255)
WHITE=(244,247,251,255); MUTED=(148,158,178,255); ACCENT=(74,222,188,255); ORANGE=(255,137,80,255)

@dataclass
class Indexed:
    width:int
    height:int
    palette:bytes
    indices:bytes

class Canvas:
    def __init__(self,w:int,h:int,colors:list[RGBA],fill:int=0):
        self.w=w; self.h=h; self.colors=colors[:]
        self.p=bytearray([fill])*(w*h)
    def set(self,x:int,y:int,c:int):
        if 0<=x<self.w and 0<=y<self.h: self.p[y*self.w+x]=c
    def rect(self,x0:int,y0:int,x1:int,y1:int,c:int):
        x0=max(0,x0); y0=max(0,y0); x1=min(self.w,x1); y1=min(self.h,y1)
        row=bytes([c])*(x1-x0)
        for y in range(y0,y1): self.p[y*self.w+x0:y*self.w+x1]=row
    def rounded(self,x0:int,y0:int,x1:int,y1:int,r:int,c:int,border:int|None=None,bw:int=1):
        def fill_round(a,b,d,e,rad,col):
            for y in range(b,e):
                dy=min(y-b,e-1-y)
                inset=0
                if dy<rad:
                    rr=rad-0.5; yy=rad-dy-0.5
                    inset=max(0,int(rad-(max(0,rr*rr-yy*yy))**0.5))
                self.rect(a+inset,y,d-inset,y+1,col)
        if border is not None:
            fill_round(x0,y0,x1,y1,r,border)
            fill_round(x0+bw,y0+bw,x1-bw,y1-bw,max(0,r-bw),c)
        else: fill_round(x0,y0,x1,y1,r,c)
    def line(self,x0:int,y0:int,x1:int,y1:int,c:int,t:int=1):
        dx=abs(x1-x0); sx=1 if x0<x1 else -1; dy=-abs(y1-y0); sy=1 if y0<y1 else -1; err=dx+dy
        while True:
            self.rect(x0-t//2,y0-t//2,x0+(t+1)//2,y0+(t+1)//2,c)
            if x0==x1 and y0==y1: break
            e2=2*err
            if e2>=dy: err+=dy; x0+=sx
            if e2<=dx: err+=dx; y0+=sy
    def paste(self,im:Indexed,x:int,y:int,color_index:int):
        for yy in range(im.height):
            for xx in range(im.width):
                if im.indices[yy*im.width+xx]: self.set(x+xx,y+yy,color_index)
    def indexed(self)->Indexed:
        pal=bytearray()
        for color in self.colors: pal.extend(color)
        pal.extend(b'\0'*(1024-len(pal)))
        return Indexed(self.w,self.h,bytes(pal),bytes(self.p))

FONT={
'A':['01110','10001','10001','11111','10001','10001','10001'],
'B':['11110','10001','10001','11110','10001','10001','11110'],
'C':['01111','10000','10000','10000','10000','10000','01111'],
'D':['11110','10001','10001','10001','10001','10001','11110'],
'E':['11111','10000','10000','11110','10000','10000','11111'],
'F':['11111','10000','10000','11110','10000','10000','10000'],
'H':['10001','10001','10001','11111','10001','10001','10001'],
'I':['11111','00100','00100','00100','00100','00100','11111'],
'K':['10001','10010','10100','11000','10100','10010','10001'],
'L':['10000','10000','10000','10000','10000','10000','11111'],
'M':['10001','11011','10101','10101','10001','10001','10001'],
'N':['10001','11001','10101','10011','10001','10001','10001'],
'O':['01110','10001','10001','10001','10001','10001','01110'],
'P':['11110','10001','10001','11110','10000','10000','10000'],
'R':['11110','10001','10001','11110','10100','10010','10001'],
'S':['01111','10000','10000','01110','00001','00001','11110'],
'T':['11111','00100','00100','00100','00100','00100','00100'],
'U':['10001','10001','10001','10001','10001','10001','01110'],
'W':['10001','10001','10001','10101','10101','11011','10001'],
'Y':['10001','10001','01010','00100','00100','00100','00100'],
' ':['00000']*7,
}

def text(c:Canvas,s:str,x:int,y:int,scale:int,color:int,spacing:int=1):
    for ch in s:
        glyph=FONT.get(ch,FONT[' '])
        for gy,row in enumerate(glyph):
            for gx,v in enumerate(row):
                if v=='1': c.rect(x+gx*scale,y+gy*scale,x+(gx+1)*scale,y+(gy+1)*scale,color)
        x+=(5+spacing)*scale

SEGMENTS={'0':'abcdef','1':'bc','2':'abdeg','3':'abcdg','4':'bcfg','5':'acdfg','6':'acdefg','7':'abc','8':'abcdefg','9':'abcdfg'}

def seven_digit(w:int,h:int,t:int,digit:str)->Indexed:
    c=Canvas(w,h,[(0,0,0,0),WHITE],0); m=max(2,t//2); mid=h//2
    seg={'a':(m+t,m,w-m-t,m+t),'g':(m+t,mid-t//2,w-m-t,mid+(t+1)//2),'d':(m+t,h-m-t,w-m-t,h-m),'f':(m,m+t,m+t,mid-t//2),'b':(w-m-t,m+t,w-m,mid-t//2),'e':(m,mid+t//2,m+t,h-m-t),'c':(w-m-t,mid+t//2,w-m,h-m-t)}
    for key in SEGMENTS[digit]: c.rounded(*seg[key],max(1,t//3),1)
    return c.indexed()

def digit_set(w:int,h:int,t:int)->list[Indexed]: return [seven_digit(w,h,t,str(i)) for i in range(10)]

def colon()->Indexed:
    c=Canvas(24,96,[(0,0,0,0),WHITE],0); c.rounded(8,25,16,33,4,1); c.rounded(8,63,16,71,4,1); return c.indexed()

def slash()->Indexed:
    c=Canvas(24,40,[(0,0,0,0),WHITE],0); c.line(17,4,7,35,1,4); return c.indexed()

def percent()->Indexed:
    c=Canvas(14,36,[(0,0,0,0),WHITE],0); c.rounded(1,4,6,9,2,1); c.rounded(8,27,13,32,2,1); c.line(11,4,3,32,1,2); return c.indexed()

def weekday_set()->list[Indexed]:
    result=[]
    for label in ('MON','TUE','WED','THU','FRI','SAT','SUN'):
        c=Canvas(48,16,[(0,0,0,0),WHITE],0); text(c,label,2,4,1,1,1); result.append(c.indexed())
    return result

def background()->Indexed:
    colors=[BG,PANEL,GRID,WHITE,MUTED,ACCENT,ORANGE]; c=Canvas(*CANVAS,colors,0)
    for x in range(0,337,24): c.rect(x,0,x+1,480,1)
    c.rounded(14,22,322,226,22,1,2,2); c.rounded(14,244,322,326,20,1,2,2); c.rounded(14,344,322,456,20,1,2,2)
    text(c,'TIME FLIES',28,38,2,5,1); text(c,'MAKE TODAY COUNT',28,207,1,4,1); text(c,'DATE',28,258,1,4,1); text(c,'STEPS',28,358,1,4,1); text(c,'BATTERY',212,358,1,4,1)
    c.rect(28,390,308,392,2); c.rect(190,356,192,442,2); c.rounded(283,38,301,56,9,6)
    return c.indexed()

def preview(hour='10',minute='09',month='07',day='11',steps='7812',battery='87',weekday=4)->Indexed:
    bg=background(); c=Canvas(bg.width,bg.height,[BG,PANEL,GRID,WHITE,MUTED,ACCENT,ORANGE],0); c.p[:]=bg.indices
    big=digit_set(60,96,10); small=digit_set(26,40,4); numbers=digit_set(24,36,4)
    def add(chars,images,x,y,gap=0):
        for ch in chars: c.paste(images[int(ch)],x,y,3); x+=images[0].width+gap
    add(hour,big,28,84); c.paste(colon(),151,84,3); add(minute,big,184,84)
    add(month,small,58,264); c.paste(slash(),116,264,3); add(day,small,142,264); c.paste(weekday_set()[weekday],244,276,3)
    add(steps,numbers,38,399,2); add(battery,numbers,242,399); c.paste(percent(),294,399,3)
    return c.indexed()

def build_assets():
    return {'background':background(),'colon':colon(),'slash':slash(),'percent':percent(),'time_digits':digit_set(60,96,10),'date_digits':digit_set(26,40,4),'step_digits':digit_set(24,36,4),'weekdays':weekday_set(),'preview':preview()}
