# 새 주인공 UI 그림: 게임 프레임(img/h2)을 딱 맞게 잘라 화면용 그림으로 → img/h2/ui_<who>_<ready|joy|tired>.png
# 여자 맞는 그림(girl_hurt)도 여기서 만들어요.  실행: /opt/homebrew/bin/python3.10 tools/make_h2_ui.py
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
from cut_mj_poses import cutout
from make_room_props import pixel_art
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
a, al = cutout(Image.open(f'{R}/art/hero2/poses/hp_girl_hurt_0.png'))
ys, xs = np.where(al); c = Image.fromarray(np.dstack([a, al * 255]).astype(np.uint8)[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 'RGBA')
pa = pixel_art(c, round(c.width * 128 / c.height), px=1, colors=48, sat=1.08)
from scipy import ndimage
m = np.asarray(pa)[..., 3] > 0; lab, k = ndimage.label(m, structure=np.ones((3, 3)))
if k > 1:
    sz = ndimage.sum(np.ones_like(lab), lab, range(1, k + 1)); arr = np.asarray(pa).copy(); arr[lab != 1 + int(np.argmax(sz)), 3] = 0; pa = Image.fromarray(arr)
pa = pa.crop(pa.getbbox()); fr = Image.new('RGBA', (220, 190)); fr.paste(pa, (110 - pa.width // 2, 178 - pa.height), pa); fr.save(f'{R}/img/h2/girl_hurt.png')
for who in ('boy', 'girl'):
    for f, src in (('ready', 'idle'), ('joy', 'joy'), ('tired', 'hurt')):
        im = Image.open(f'{R}/img/h2/{who}_{src}.png'); im.crop(im.getbbox()).save(f'{R}/img/h2/ui_{who}_{f}.png')
print('ok')
