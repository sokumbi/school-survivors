# 드리미나 괴물 시트(art/monsters/src/mobs.jpeg, bosses.jpeg)를 한 마리씩 잘라요
# 결과: img/mon/<이름>.png (투명 배경, 발이 그림 맨 아래), img/mon/mon.json {이름: [폭, 높이]}
# 실행: /opt/homebrew/bin/python3.10 tools/cut_monsters.py
import json, os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'art/monsters/src')
OUT = os.path.join(ROOT, 'img/mon')
SHEETS = {'mobs': ['paper', 'chalk', 'chair', 'eraser', 'milk', 'clock'], 'bosses': ['podium', 'speaker', 'captain']}
SCALE = 0.5


def dilate(m):
    p = m.copy(); p[1:] |= m[:-1]; p[:-1] |= m[1:]; p[:, 1:] |= m[:, :-1]; p[:, :-1] |= m[:, 1:]; return p


def flood(bglike):
    s = np.zeros_like(bglike)
    s[0], s[-1], s[:, 0], s[:, -1] = bglike[0], bglike[-1], bglike[:, 0], bglike[:, -1]
    while True:
        n = dilate(s) & bglike
        if (n == s).all(): return s
        s = n


def merge_to(segs, n, proj):
    segs = list(segs)
    while len(segs) > n:
        mass = [proj[a:b].sum() for a, b in segs]; i = int(np.argmin(mass))
        if i == 0: j = 1
        elif i == len(segs) - 1: j = i - 1
        else: j = i - 1 if segs[i][0] - segs[i - 1][1] < segs[i + 1][0] - segs[i][1] else i + 1
        a, b = min(i, j), max(i, j); segs[a:b + 1] = [(segs[a][0], segs[b][1])]
    return segs


def main():
    os.makedirs(OUT, exist_ok=True); meta = {}
    for sheet, names in SHEETS.items():
        im = Image.open(os.path.join(SRC, sheet + '.jpeg')).convert('RGB')
        im = im.crop((0, 200, im.width, 1240))           # 위 AI 표시, 아래 워터마크 빼기
        a = np.asarray(im).astype(int)
        mn, mx = a.min(2), a.max(2); sat = mx - mn
        bg = flood((mn >= 200) & (sat <= 24))
        fg = ~bg
        fg &= ~((mn >= 180) & (mx <= 236) & (sat <= 18))  # 발밑 연한 그림자
        nb = sum(np.roll(np.roll(fg, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1))
        fg &= nb >= 4
        xp = fg.sum(0); segs, s0 = [], None
        for x in range(len(xp) + 1):
            on = x < len(xp) and xp[x] > 0
            if on and s0 is None: s0 = x
            if not on and s0 is not None:
                if x - s0 > 6: segs.append((s0, x))
                s0 = None
        segs = merge_to(segs, len(names), xp)
        for name, (x0, x1) in zip(names, segs):
            m = fg[:, x0:x1]; ys = np.flatnonzero(m.any(1)); y0, y1 = ys[0], ys[-1] + 1
            rgb = a[y0:y1, x0:x1].astype(np.uint8); al = (m[y0:y1] * 255).astype(np.uint8)
            img = Image.fromarray(np.dstack([rgb, al]), 'RGBA')
            w, h = round(img.width * SCALE), round(img.height * SCALE)
            col = img.convert('RGB').resize((w, h), Image.LANCZOS)
            col.putalpha(img.getchannel('A').resize((w, h), Image.LANCZOS).point(lambda v: 255 if v > 110 else 0))
            col.save(os.path.join(OUT, name + '.png')); meta[name] = [w, h]
    json.dump(meta, open(os.path.join(OUT, 'mon.json'), 'w'))
    print(meta)


if __name__ == '__main__':
    main()
