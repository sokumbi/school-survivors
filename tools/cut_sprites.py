# 드리미나 픽셀아트 시트(art/yudam/src/*.jpeg)를 동작 장면으로 잘라요
# 결과: art/yudam/frames/<동작>_<번호>.png, img/yd/ 에도 복사, art/yudam/anims.json
# 장면은 220x190 투명 PNG, 발이 (110,178), 서 있는 키 132
# 실행: /opt/homebrew/bin/python3.10 tools/cut_sprites.py
import json, os, shutil
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'art/yudam/src')
OUT = os.path.join(ROOT, 'art/yudam/frames')
GAME = os.path.join(ROOT, 'img/yd')
FW, FH, FX, FY, TALL = 220, 190, 110, 178, 132

# 시트: 줄마다 사람 수, 키를 잴 장면(ref), 크기 보정(k)
SHEETS = {
    'victory':     {'rows': [5], 'ref': [0, 1]},
    'walk':        {'rows': [4, 4]},
    'run':         {'rows': [4, 4]},
    'idle_dash':   {'rows': [4, 4], 'ref': [0, 1, 2, 3]},
    'punch_hurt':  {'rows': [4, 4], 'ref': [0, 1, 3, 4, 7]},
    'trip_ko':     {'rows': [5, 5], 'ref': [0, 5], 'k': 0.87},
    'getup_dizzy': {'rows': [5, 5], 'ref': [6, 8]},
    'tired_joy':   {'rows': [4, 5], 'ref': [1, 2, 7, 8]},
}
# 동작: (시트, 장면 번호들, 빠르기, 반복)
ANIMS = {
    'idle': ('idle_dash', [0, 1, 2, 3], 4, 1), 'dash': ('idle_dash', [4, 5, 6, 7], 14, 0),
    'walk': ('walk', list(range(8)), 10, 1), 'run': ('run', list(range(8)), 12, 1),
    'punch': ('punch_hurt', [0, 1, 2, 3], 12, 0), 'hurt': ('punch_hurt', [4, 5, 6, 7], 10, 0),
    'trip': ('trip_ko', [0, 1, 2, 3, 4], 10, 0), 'ko': ('trip_ko', [5, 6, 7, 8, 9], 8, 0),
    'getup': ('getup_dizzy', [0, 1, 2, 3, 4], 8, 0), 'dizzy': ('getup_dizzy', [5, 6, 7, 8], 5, 1),
    'tired': ('tired_joy', [0, 1, 2, 3], 4, 1), 'joy': ('tired_joy', [4, 5, 6, 7, 8], 8, 0),
    'victory': ('victory', [0, 1, 2, 3, 4], 6, 0),
}


def dilate(m, r=1):
    o = m.copy()
    for _ in range(r):
        p = o.copy()
        p[1:] |= o[:-1]; p[:-1] |= o[1:]; p[:, 1:] |= o[:, :-1]; p[:, :-1] |= o[:, 1:]
        o = p
    return o


def flood_bg(bglike):
    seed = np.zeros_like(bglike)
    seed[0, :] = bglike[0, :]; seed[-1, :] = bglike[-1, :]; seed[:, 0] = bglike[:, 0]; seed[:, -1] = bglike[:, -1]
    while True:
        n = dilate(seed) & bglike
        if (n == seed).all():
            return seed
        seed = n


def runs(v, gap=0):
    """v: bool 1D → [(시작, 끝)] (gap 칸 이하 빈 곳은 이어 붙여요)"""
    out = []; s = p = None
    for x in np.flatnonzero(v):
        if s is None:
            s = p = x
        elif x - p > gap + 1:
            out.append((s, p + 1)); s = x
        p = x
    if s is not None:
        out.append((s, p + 1))
    return out


def merge_to(segs, n, proj):
    segs = list(segs)
    while len(segs) > n:  # 가장 가벼운 조각을 가까운 이웃에 붙여요
        mass = [proj[a:b].sum() for a, b in segs]
        i = int(np.argmin(mass))
        if i == 0: j = 1
        elif i == len(segs) - 1: j = i - 1
        else: j = i - 1 if segs[i][0] - segs[i - 1][1] < segs[i + 1][0] - segs[i][1] else i + 1
        a, b = min(i, j), max(i, j)
        segs[a:b + 1] = [(segs[a][0], segs[b][1])]
    while len(segs) < n:  # 붙은 장면은 가장 넓은 곳을 가운데 쪽 골짜기에서 나눠요
        i = int(np.argmax([b - a for a, b in segs]))
        a, b = segs[i]; w = b - a
        lo, hi = a + w // 4, b - w // 4
        c = lo + int(np.argmin(proj[lo:hi]))
        segs[i:i + 1] = [(a, c), (c, b)]
    return segs


def cut_sheet(name, spec):
    im = Image.open(os.path.join(SRC, name + '.jpeg')).convert('RGB')
    im = im.resize((im.width // 2, im.height // 2), Image.LANCZOS)
    a = np.asarray(im).astype(int)
    H, W = a.shape[:2]
    mn, mx = a.min(2), a.max(2)
    sat = mx - mn
    bg = flood_bg((mn >= 196) & (sat <= 22))
    fg = ~bg
    # 땅 선: 가로로 길게 이어진 줄은 지워요
    for y in range(H):
        r = runs(fg[y])
        if fg[y].sum() > W * 0.3 and r and max(b - a_ for a_, b in r) > W * 0.3:
            fg[max(0, y - 1):y + 2] = False
    # 워터마크(오른쪽 아래)
    wm = np.zeros_like(fg); wm[int(H * 0.86):, int(W * 0.72):] = True
    fg &= ~(wm & (mn >= 150))
    # 위아래로 얇은 찌꺼기 지우기 (세로 열림)
    e = fg.copy()
    for d in (1, 2):
        e[d:] &= fg[:-d]; e[:-d] &= fg[d:]
    o = e.copy()
    for d in (1, 2):
        o[d:] |= e[:-d]; o[:-d] |= e[d:]
    fg &= o
    # 갇힌 바탕색, 연한 회색 그림자
    med = np.median(a[bg], axis=0)
    fg &= ~(np.abs(a - med).max(2) <= 10)
    fg &= ~((mn >= 185) & (mx <= 226) & (sat <= 14))

    rows = spec['rows']
    yp = fg.sum(1)
    if len(rows) == 1:
        rr = [(0, H)]
    else:  # 두 줄: 가운데쯤 가장 빈 곳에서 나눠요
        lo, hi = int(H * 0.35), int(H * 0.65)
        c = lo + int(np.argmin(yp[lo:hi]))
        rr = [(0, c), (c, H)]
    frames = []
    for (y0, y1), n in zip(rr, rows):
        sub = fg[y0:y1]
        xp = sub.sum(0)
        segs = merge_to(runs(xp > 0, gap=2), n, xp)
        for x0, x1 in segs:
            m = sub[:, x0:x1]
            ys = np.flatnonzero(m.any(1)); xs = np.flatnonzero(m.any(0))
            by0, by1 = ys[0], ys[-1] + 1; bx0, bx1 = xs[0], xs[-1] + 1
            rgb = a[y0 + by0:y0 + by1, x0 + bx0:x0 + bx1]
            al = m[by0:by1, bx0:bx1]
            frames.append((rgb, al))
    hs = [f[1].shape[0] for f in frames]
    ref = spec.get('ref', range(len(frames)))
    scale = TALL / float(np.median([hs[i] for i in ref])) * spec.get('k', 1)
    out = []
    for rgb, al in frames:
        h, w = al.shape
        rgba = np.dstack([rgb, al * 255]).astype(np.uint8)
        nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
        img = Image.fromarray(rgba, 'RGBA')
        col = img.convert('RGB').resize((nw, nh), Image.LANCZOS)
        alp = img.getchannel('A').resize((nw, nh), Image.LANCZOS).point(lambda v: 255 if v > 128 else 0)
        A = np.asarray(alp) > 0
        # 발밑에 남은 땅 선: 맨 아래 몇 줄에서 다리 폭 밖으로 삐져나간 점은 지워요
        if nh > 20:
            leg = np.flatnonzero(A[nh - 16:nh - 6].any(0))
            if len(leg):
                A = A.copy(); A[nh - 6:, :max(0, leg[0] - 4)] = False; A[nh - 6:, leg[-1] + 5:] = False
                alp = Image.fromarray((A * 255).astype(np.uint8))
        col.putalpha(alp)
        t0, t1 = int(nh * 0.3), max(int(nh * 0.65), int(nh * 0.3) + 1)
        xs = np.nonzero(A[t0:t1])[1]
        cx = xs.mean() if len(xs) else nw / 2
        canvas = Image.new('RGBA', (FW, FH))
        canvas.paste(col, (int(round(FX - cx)), FY - nh), col)
        out.append(canvas)
    return out


def main():
    os.makedirs(OUT, exist_ok=True); os.makedirs(GAME, exist_ok=True)
    cut = {n: cut_sheet(n, s) for n, s in SHEETS.items()}
    meta = {'w': FW, 'h': FH, 'foot': [FX, FY], 'anims': {}}
    for an, (sh, idx, fps, loop) in ANIMS.items():
        for k, i in enumerate(idx):
            p = os.path.join(OUT, f'{an}_{k}.png')
            cut[sh][i].save(p)
            shutil.copy(p, os.path.join(GAME, f'{an}_{k}.png'))
        meta['anims'][an] = {'frames': len(idx), 'fps': fps, 'loop': loop}
    # 화면용 얼굴 (네모로 꼭 맞게 자른 그림)
    for ui, (an, k) in {'ui_ready': ('idle', 0), 'ui_joy': ('joy', 2), 'ui_tired': ('tired', 0)}.items():
        im = Image.open(os.path.join(OUT, f'{an}_{k}.png'))
        im.crop(im.getbbox()).save(os.path.join(GAME, ui + '.png'))
    json.dump(meta, open(os.path.join(ROOT, 'art/yudam/anims.json'), 'w'), ensure_ascii=False, indent=1)
    print({n: len(v) for n, v in cut.items()})


if __name__ == '__main__':
    main()
