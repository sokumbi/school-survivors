# 드리미나 교실 소품 시트(art/props/src/props1.jpeg)를 하나씩 잘라요
# 결과: img/props/<이름>.png (투명 배경), img/props/props.json {이름: [폭, 높이]}
# 실행: /opt/homebrew/bin/python3.10 tools/cut_props.py
import json, os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'art/props/src/props1.jpeg')
OUT = os.path.join(ROOT, 'img/props')
NAMES = ['desk', 'tdesk', 'lockers', 'shelf', 'plant', 'trash', 'water']
SCALE = 0.5   # 원본 2560 기준 절반으로 저장 (게임에서 다시 맞춰요)


def dilate(m):
    p = m.copy(); p[1:] |= m[:-1]; p[:-1] |= m[1:]; p[:, 1:] |= m[:, :-1]; p[:, :-1] |= m[:, 1:]; return p


def flood(bglike):
    s = np.zeros_like(bglike)
    s[0], s[-1], s[:, 0], s[:, -1] = bglike[0], bglike[-1], bglike[:, 0], bglike[:, -1]
    while True:
        n = dilate(s) & bglike
        if (n == s).all(): return s
        s = n


def main():
    os.makedirs(OUT, exist_ok=True)
    im = Image.open(SRC).convert('RGB')
    im = im.crop((0, 250, im.width, 1150))      # 위 AI 표시와 아래 워터마크를 빼요
    a = np.asarray(im).astype(int)
    mn, mx = a.min(2), a.max(2); sat = mx - mn
    bg = flood((mn >= 200) & (sat <= 24))
    fg = ~bg
    fg &= ~((mn >= 196) & (mx <= 232) & (sat <= 16))   # 바닥 그림자
    # 작은 점 지우기: 이웃이 적은 점
    nb = sum(np.roll(np.roll(fg, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1))
    fg &= nb >= 4
    xp = fg.sum(0)
    segs, s0 = [], None
    for x in range(len(xp) + 1):
        on = x < len(xp) and xp[x] > 0
        if on and s0 is None: s0 = x
        if not on and s0 is not None:
            if x - s0 > 20: segs.append((s0, x))
            s0 = None
    # 가까운 조각은 합쳐요 (간격 25 이하)
    merged = []
    for sg in segs:
        if merged and sg[0] - merged[-1][1] <= 25: merged[-1] = (merged[-1][0], sg[1])
        else: merged.append(sg)
    assert len(merged) == len(NAMES), merged
    meta = {}
    for name, (x0, x1) in zip(NAMES, merged):
        m = fg[:, x0:x1]
        ys = np.flatnonzero(m.any(1)); y0, y1 = ys[0], ys[-1] + 1
        rgb = a[y0:y1, x0:x1].astype(np.uint8); al = (m[y0:y1] * 255).astype(np.uint8)
        img = Image.fromarray(np.dstack([rgb, al]), 'RGBA')
        w, h = round(img.width * SCALE), round(img.height * SCALE)
        col = img.convert('RGB').resize((w, h), Image.LANCZOS)
        col.putalpha(img.getchannel('A').resize((w, h), Image.LANCZOS).point(lambda v: 255 if v > 110 else 0))
        col.save(os.path.join(OUT, name + '.png')); meta[name] = [w, h]
    json.dump(meta, open(os.path.join(OUT, 'props.json'), 'w'))
    print(meta)


if __name__ == '__main__':
    main()
