# 시트 이미지에서 회색 배경을 지우고 칸마다 잘라 img/에 저장 + 기준점(발 위치) 기록
from PIL import Image
from collections import deque
import json
SCALE=0.4
def cutout(path, tol=14):
    im=Image.open(path).convert('RGBA'); W,H=im.size; px=im.load()
    bg=px[3,3][:3]
    def isbg(c): return all(abs(c[i]-bg[i])<=tol for i in range(3))
    seen=bytearray(W*H); q=deque()
    for x in range(W): q.append((x,0)); q.append((x,H-1))
    for y in range(H): q.append((0,y)); q.append((W-1,y))
    while q:
        x,y=q.popleft(); i=y*W+x
        if seen[i]: continue
        seen[i]=1
        if not isbg(px[x,y]): continue
        px[x,y]=(0,0,0,0)
        for dx,dy in((1,0),(-1,0),(0,1),(0,-1)):
            nx,ny=x+dx,y+dy
            if 0<=nx<W and 0<=ny<H and not seen[ny*W+nx]: q.append((nx,ny))
    return im
def cells(im, cols, rows, names, prefix, meta):
    W,H=im.size; cw,ch=W//cols,H//rows
    for k,n in enumerate(names):
        c,r=k%cols,k//cols
        cell=im.crop((c*cw,r*ch,(c+1)*cw,(r+1)*ch))
        bb=cell.getbbox(); cell=cell.crop(bb); a=cell.load(); w,h=cell.size
        # 발 기준점: 아래쪽 15% 줄의 불투명 픽셀 가로 중앙값
        xs=[x for y in range(int(h*0.85),h) for x in range(w) if a[x,y][3]>0]
        xs.sort(); fx=xs[len(xs)//2] if xs else w//2
        cell=cell.resize((max(1,int(w*SCALE)),max(1,int(h*SCALE))),Image.LANCZOS)
        cell.save(f'img/{prefix}_{n}.png')
        meta[f'{prefix}_{n}']={'ax':round(fx*SCALE),'ay':cell.size[1]}
meta={}
cells(cutout('src_img/hero.webp'),3,2,['idle','walk1','walk2','attack','hurt','down'],'hero',meta)
cells(cutout('src_img/paper.webp'),2,2,['idle','walk1','walk2','attack'],'paper',meta)
Image.open('src_img/classroom.webp').convert('RGB').save('img/classroom.jpg',quality=90)
json.dump(meta,open('img/sprites.json','w'),indent=1); print(meta)
