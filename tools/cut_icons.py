# 드리미나 픽셀 아이콘 시트(art/ui/src/*.jpeg)를 하나씩 잘라 img/ui/<이름>.png 로 저장해요
# 줄(가로 빈 띠)로 먼저 나누고, 줄마다 칸(세로 빈 띠)으로 나눠요. 칸 수가 안 맞으면 가까운 조각끼리 합쳐요
# 실행: /opt/homebrew/bin/python3.10 tools/cut_icons.py
import json, os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'art/ui/src')
OUT = os.path.join(ROOT, 'img/ui')
SHEETS = {
    'skills1': [['punch', 'shoes', 'magnet', 'note'], ['bat', 'power', 'ball', 'guard'], ['boom', 'alarm', 'eraser', 'aim']],
    'skills2': [['recorder', 'milk', 'bandage', 'vitamin'], ['plane', 'ink', 'book', 'quick'], ['paint', 'crayon', 'bolt', 'palette']],
    'ui':      [['club_war', 'club_arch', 'club_heal', 'club_sum'], ['club_mag', 'gem', 'coin', 'heart'], ['radio', 'dash', 'star', 'lock']],
    'teachers': [['t_pe', 't_math', 't_nurse'], ['t_kor', 't_art', 't_home']],
    'items':   [['i_cap', 'i_ribbon', 'i_helmet', 'i_beanie'], ['i_blazer', 'i_gym', 'i_hoodie', 'i_coat'],
                ['i_slipper', 'i_sneaker', 'i_boot', 'i_roller'], ['i_pencil', 'i_tag', 'i_watch', 'i_key']],
    'kids':    [['k_haram', 'k_minjun', 'k_seoyeon', 'k_jiho', 'k_haeun', 'k_doyun', 'k_sua']],
    'props2':  [['p_eraser', 'p_ball', 'p_ruler', 'p_plane'], ['p_book', 'p_chalk', 'p_cube', 'locker'], ['locker_open', 'stairs', 'p_burst', 'p_spark']],
    'portraits2': [['t_sci', 't_music', 't_food'], ['t_fake', 't_principal', 't_captain']],
    'title_ufo': [['ufo']],
    'equip2':  [['i_glove', 'i_mitt', 'i_workglove', 'i_mitten'], ['i_backpack', 'i_crossbag', 'i_duffel', 'i_lunchbag'], ['ult', 'bagicon', 'pouch', 'mannequin']],
}
MAXW = {'teachers': 220, 'kids': 220, 'portraits2': 220, 'title_ufo': 420, 'props2': 160}
BGMIN = {'items': 160, 'props2': 160}   # 저장 크기(긴 변). 나머지 아이콘은 128


def dilate(m):
    p = m.copy(); p[1:] |= m[:-1]; p[:-1] |= m[1:]; p[:, 1:] |= m[:, :-1]; p[:, :-1] |= m[:, 1:]; return p


def flood(bglike):
    s = np.zeros_like(bglike)
    s[0], s[-1], s[:, 0], s[:, -1] = bglike[0], bglike[-1], bglike[:, 0], bglike[:, -1]
    while True:
        n = dilate(s) & bglike
        if (n == s).all(): return s
        s = n


def runs(v, min_len=4):
    out, s0 = [], None
    for i in range(len(v) + 1):
        on = i < len(v) and v[i]
        if on and s0 is None: s0 = i
        if not on and s0 is not None:
            if i - s0 >= min_len: out.append((s0, i))
            s0 = None
    return out


def fit(segs, n, proj):
    segs = list(segs)
    while len(segs) > n:   # 가장 가벼운 조각을 가까운 이웃과 합쳐요
        mass = [proj[a:b].sum() for a, b in segs]; i = int(np.argmin(mass))
        j = 1 if i == 0 else i - 1 if i == len(segs) - 1 else (i - 1 if segs[i][0] - segs[i - 1][1] < segs[i + 1][0] - segs[i][1] else i + 1)
        a, b = min(i, j), max(i, j); segs[a:b + 1] = [(segs[a][0], segs[b][1])]
    return segs


def cut(sheet, rows):
    f = [x for x in os.listdir(SRC) if x.startswith(sheet + '.')][0]
    im = Image.open(os.path.join(SRC, f)).convert('RGB')
    im = im.crop((0, int(im.height * 0.05), im.width, int(im.height * 0.97)))     # 위 AI 표시 빼기
    a = np.asarray(im).astype(int); mn, mx = a.min(2), a.max(2); sat = mx - mn
    bg = flood((mn >= BGMIN.get(sheet, 196)) & (sat <= 26))   # 아이템 시트는 회색 칸 줄도 바탕으로
    fg = ~bg
    fg &= ~((mn >= 180) & (mx <= 238) & (sat <= 18))       # 연한 그림자
    nb = sum(np.roll(np.roll(fg, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1)); fg &= nb >= 4
    yp = fg.sum(1)
    rsegs = fit(runs(yp > 0, 8), len(rows), yp)
    if len(rsegs) < len(rows): raise SystemExit(f'{sheet}: 줄이 {len(rsegs)}개뿐이에요')
    meta = {}
    for (y0, y1), names in zip(rsegs, rows):
        sub = fg[y0:y1]; xp = sub.sum(0)
        # 칸은 고르게 놓여 있어요: 줄 전체 폭을 칸 수로 나눈 가운데에 가까운 조각끼리 묶어요
        raw = runs(xp > 0, 3); n = len(names)
        lo, hi = raw[0][0], raw[-1][1]; cw = (hi - lo) / n
        groups = [[] for _ in range(n)]
        for a_, b_ in raw: groups[min(n - 1, max(0, int(((a_ + b_) / 2 - lo) / cw)))].append((a_, b_))
        csegs = [(min(g)[0], max(b for _, b in g)) if g else None for g in groups]
        if None in csegs: csegs = fit(raw, n, xp)
        if len(csegs) < len(names): raise SystemExit(f'{sheet}: {names} 칸이 {len(csegs)}개뿐이에요')
        for name, (x0, x1) in zip(names, csegs):
            m = sub[:, x0:x1]
            # 테두리에 틈이 있어 안쪽 흰 면이 바탕으로 빠진 곳을 메워요 (테두리를 2칸 넓혀 막고 바깥만 바탕으로)
            mm = np.pad(m, 3); cl = dilate(dilate(mm)); out = flood(~cl)
            mm = mm | (~out & ~dilate(out)); m = mm[3:-3, 3:-3]
            ys = np.flatnonzero(m.any(1)); by0, by1 = ys[0], ys[-1] + 1
            rgb = a[y0 + by0:y0 + by1, x0:x1].astype(np.uint8); al = (m[by0:by1] * 255).astype(np.uint8)
            img = Image.fromarray(np.dstack([rgb, al]), 'RGBA')
            L = MAXW.get(sheet, 128); k = L / max(img.size)
            w, h = max(1, round(img.width * k)), max(1, round(img.height * k))
            col = img.convert('RGB').resize((w, h), Image.LANCZOS)
            col.putalpha(img.getchannel('A').resize((w, h), Image.LANCZOS).point(lambda v: 255 if v > 110 else 0))
            col.save(os.path.join(OUT, name + '.png')); meta[name] = [w, h]
    return meta


def main():
    os.makedirs(OUT, exist_ok=True); meta = {}
    for sheet, rows in SHEETS.items():
        if not any(x.startswith(sheet + '.') for x in os.listdir(SRC)): print('없음', sheet); continue
        meta.update(cut(sheet, rows)); print('ok', sheet)
    json.dump(meta, open(os.path.join(OUT, 'ui.json'), 'w'))


if __name__ == '__main__':
    main()
