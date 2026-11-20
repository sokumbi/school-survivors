# 잘라 낸 픽셀 그림에 남은 바탕색을 지워요 (img 폴더 그림을 그 자리에서 고쳐요)
# 1) 다리 사이처럼 갇힌 바탕 조각: 연회색(완전 흰색보다 어두움)이 뭉친 덩어리
# 2) 가장자리 하얀 테두리: 바깥 가장자리의 연회색 점 (완전 흰색 몸통은 남겨요)
# 실행: /opt/homebrew/bin/python3.10 tools/clean_edges.py
import glob, os
from collections import deque
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATTERNS = ['img/hr/*.png', 'img/yd/*.png', 'img/mon/*.png', 'img/ui/*.png', 'img/props/*.png', 'img/start_ufo.png']
SKIP = ('box_',)
KEEP_GRAY = ('milk', 'note', 'i_coat', 'mannequin', 'shoes', 'i_slipper', 'i_hoodie', 'i_beanie', 'stairs', 'p_cube', 'trash', 'lock')   # 회색이 원래 색인 그림은 갇힌 바탕 지우기를 건너뛰어요


def bgish(rgb):
    mn = rgb.min(2); sat = rgb.max(2) - mn
    return (mn >= 200) & (mn <= 246) & (sat <= 16)   # 바탕 회색 (233,237,241) 근처, 흰 몸통(250+)은 빼요


def pockets(im):
    a = im[..., 3] > 0; cand = a & bgish(im[..., :3].astype(int)); seen = np.zeros_like(cand); H, W = cand.shape; kill = np.zeros_like(cand)
    for y0, x0 in zip(*np.nonzero(cand)):
        if seen[y0, x0]: continue
        q = deque([(y0, x0)]); seen[y0, x0] = True; comp = []
        while q:
            y, x = q.popleft(); comp.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < H and 0 <= nx < W and cand[ny, nx] and not seen[ny, nx]: seen[ny, nx] = True; q.append((ny, nx))
        if len(comp) >= 18:
            ys, xs = zip(*comp); vals = im[ys, xs, :3].astype(int)
            if vals.mean() < 243 and vals.std() < 9: kill[ys, xs] = True   # 고르게 칠해진 연회색 덩어리 = 바탕
    return kill


def clean(path):
    im = np.asarray(Image.open(path).convert('RGBA')).copy()
    k1 = np.zeros(im.shape[:2], bool) if os.path.basename(path)[:-4] in KEEP_GRAY else pockets(im); im[k1, 3] = 0
    rgb = im[..., :3].astype(int); light = bgish(rgb) | ((rgb.min(2) >= 150) & (rgb.max(2) - rgb.min(2) <= 30) & (rgb.min(2) < 246))
    n2 = 0
    for _ in range(2):
        a = im[..., 3] > 0; p = np.pad(a, 1)
        edge = a & ~(p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:])
        kill = edge & light
        if not kill.any(): break
        im[kill, 3] = 0; n2 += int(kill.sum())
    # 3) 스티커처럼 외곽선 바깥에 붙은 흰 테두리: 가장자리의 밝은 점 중 3칸 안에 어두운 외곽선이 있는 것만 (평평하게 잘린 흰 옷은 남아요)
    for _ in range(4):
        rgb = im[..., :3].astype(int); a_ = im[..., 3] > 0
        dark = a_ & (rgb.max(2) < 110)
        near = dark.copy()
        for _r in range(3):
            q = np.pad(near, 1); near = near | q[:-2, 1:-1] | q[2:, 1:-1] | q[1:-1, :-2] | q[1:-1, 2:]
        lt = (rgb.min(2) >= 190) & (rgb.max(2) - rgb.min(2) <= 45)
        p = np.pad(a_, 1); edge = a_ & ~(p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:])
        kill = edge & lt & near
        if not kill.any(): break
        im[kill, 3] = 0; n2 += int(kill.sum())
    Image.fromarray(im).save(path)
    return int(k1.sum()), n2


def main():
    t1 = t2 = 0
    for pat in PATTERNS:
        for f in sorted(glob.glob(os.path.join(ROOT, pat))):
            if os.path.basename(f).startswith(SKIP): continue
            a, b = clean(f); t1 += a; t2 += b
    print('갇힌 바탕', t1, '테두리', t2)


if __name__ == '__main__':
    main()
