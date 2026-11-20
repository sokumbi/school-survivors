# Draw Things 괴물 그림(art/drawthings/mon)을 오려 게임 그림(img/mon/<key>.png)으로 바꿔요
import os, sys, shutil
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cut_room_props import cut
from make_room_props import pixel_art
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, TMP, OUT = [os.path.join(ROOT, p) for p in ('art/drawthings/mon', 'art/drawthings/mon_cut', 'img/mon')]
WIDTH = {'pencil': 170, 'globe': 190, 'textbook': 190, 'tray': 190, 'bell': 180, 'mop': 170, 'locker': 300, 'piano': 330, 'vending': 300, 'mother': 380}
for k, w in WIDTH.items():
    src = os.path.join(SRC, k + '.png')
    if not os.path.exists(src): print('없음', k); continue
    d = os.path.join(TMP, k); shutil.rmtree(d, ignore_errors=True)
    n = cut(src, d, min_area=1500, gap=6)
    big = max((Image.open(os.path.join(d, f'{i}.png')) for i in range(n)), key=lambda im: im.width * im.height)
    pixel_art(big, w, px=1, sat=1.05).save(os.path.join(OUT, k + '.png')); print(k, 'ok')
