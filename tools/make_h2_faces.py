# 상태창 얼굴(머리+어깨) 그림: 미드저니 원본 서 있는 그림 윗부분 → img/h2/face_<who>.png (키 110px 픽셀 그림)
# 실행: /opt/homebrew/bin/python3.10 tools/make_h2_faces.py
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
from scipy import ndimage
from cut_mj_poses import cutout
from make_room_props import pixel_art
from make_friends2 import PICKS
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = {'boy': ('art/hero2/poses/hp_boy_idle_0.png', 0), 'girl': ('art/hero2/poses/hp_girl_idle_1.png', 0)}
for w, p in PICKS.items():
    sp = p['idle']; SRC[w] = (f"art/friends2/fp_{w}_{sp.rstrip('F').rsplit('_', 1)[0]}_{sp.rstrip('F').rsplit('_', 1)[1]}.png", sp.endswith('F'))
for who, (f, flip) in SRC.items():
    a, al = cutout(Image.open(f'{R}/{f}'))
    lab, k = ndimage.label(al, structure=np.ones((3, 3)))
    if k > 1:
        sz = ndimage.sum(np.ones_like(lab), lab, range(1, k + 1)); al = al & (lab == 1 + int(np.argmax(sz)))
    al = ndimage.binary_fill_holes(al)   # 이·눈 흰자처럼 안쪽 구멍 메우기
    ys, xs = np.where(al); y0, y1 = ys.min(), ys.max()
    cut = y0 + int((y1 - y0) * 0.5)                       # 위쪽 절반 = 머리와 어깨
    m = al[y0:cut]; cols = np.where(m.any(0))[0]
    c = Image.fromarray(np.dstack([a, al * 255]).astype(np.uint8)[y0:cut, cols.min():cols.max() + 1], 'RGBA')
    if flip: c = c.transpose(Image.FLIP_LEFT_RIGHT)
    pa = pixel_art(c, round(c.width * 110 / c.height), px=1, colors=56, sat=1.08, peel=False)   # 키 110으로 맞춤
    pa.crop(pa.getbbox()).save(f'{R}/img/h2/face_{who}.png'); print(who, pa.size)
