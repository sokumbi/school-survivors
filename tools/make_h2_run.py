# 새 주인공 달리기 프레임: 미드저니 달리기 그림 여러 장을 같은 크기 픽셀 그림으로 → img/h2/<who>_r<n>.png
# 실행: /opt/homebrew/bin/python3.10 tools/make_h2_run.py
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
from cut_mj_poses import cutout
from make_room_props import pixel_art
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'art/hero2/poses/')
# (파일, 키, 뒤집기) — 모두 오른쪽 보기, 달리는 차례대로
RUN = {
    'boy': [('runA_2', 128, 0), ('air_1', 128, 0), ('runB_0', 130, 0), ('con_2', 128, 0), ('air_2', 128, 0), ('pass_2', 130, 0)],
    'girl': [('runA_2', 128, 0), ('runB_1', 130, 0), ('runA_0', 128, 0), ('runA_3', 128, 0), ('runB_0', 130, 0), ('runB_3', 130, 0)],
}


def no_floor_shadow(pa):
    a = np.asarray(pa).copy(); h = a.shape[0]
    rgb = a[..., :3].astype(int); lum = rgb @ [.3, .59, .11]; sat = (rgb.max(2) - rgb.min(2)) / np.maximum(rgb.max(2), 1)
    zone = np.zeros(a.shape[:2], bool); zone[h - 8:] = True
    a[zone & (lum > 95) & (sat < .3), 3] = 0
    m = a[..., 3] > 0   # 남은 외톨이 점 지우기
    n = sum(np.roll(np.roll(m, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1)) - m
    a[zone & m & (n < 2), 3] = 0
    from scipy import ndimage   # 가장 큰 덩어리만 남겨요 (바닥 줄·느낌표 같은 떨어진 점 지우기)
    lab, k = ndimage.label(a[..., 3] > 0, structure=np.ones((3, 3)))
    if k > 1:
        sz = ndimage.sum(np.ones_like(lab), lab, range(1, k + 1)); a[(lab != 1 + int(np.argmax(sz))), 3] = 0
    return Image.fromarray(a, 'RGBA')


for who, lst in RUN.items():
    for i, (f, H, flip) in enumerate(lst):
        a, al = cutout(Image.open(f'{P}hp_{who}_{f}.png'))
        ys, xs = np.where(al); c = Image.fromarray(np.dstack([a, al * 255]).astype(np.uint8)[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 'RGBA')
        if flip: c = c.transpose(Image.FLIP_LEFT_RIGHT)
        pa = no_floor_shadow(pixel_art(c, round(c.width * H / c.height), px=1, colors=48, sat=1.08))
        bb = pa.getbbox(); pa = pa.crop(bb)
        fr = Image.new('RGBA', (220, 190)); fr.paste(pa, (110 - pa.width // 2, 178 - pa.height), pa)
        fr.save(os.path.join(ROOT, f'img/h2/{who}_r{i}.png'))
    print(who, len(lst))
