# 미드저니 교실 소품 시트(여러 물건이 흩어진 그림)에서 물건을 하나씩 오려 내요
# 1) 가장자리에서 이어진 바탕(+옅은 그림자)을 지우기 2) 붙어 있는 덩어리로 나누기 3) 번호 붙인 모아보기 그림
# 실행: python3.10 tools/cut_room_props.py art/roomprops/rp_sci_1.png  → art/roomprops/cut/sci_1/<번호>.png + sheet.png
import os, sys
from collections import deque
import numpy as np
from PIL import Image, ImageDraw


def bg_mask(a):
    h, w, _ = a.shape
    edge = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    bg = np.median(edge, axis=0)
    d = np.abs(a - bg).sum(2)
    lum = a @ [0.3, 0.59, 0.11]
    blg = bg @ [0.3, 0.59, 0.11]
    mx, mn = a.max(2), a.min(2)
    sat = (mx - mn) / np.maximum(mx, 1)
    # 그림자: 바탕보다 조금 어둡고, 색이 옅으며 푸르스름하거나 바탕 색 쪽
    shadow = (lum > blg * 0.6) & (lum < blg * 1.02) & (sat < 0.42) & (d < 175)
    near = (d < 48) | shadow
    seen = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if near[y, x] and not seen[y, x]: seen[y, x] = True; q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if near[y, x] and not seen[y, x]: seen[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not seen[ny, nx] and near[ny, nx]:
                seen[ny, nx] = True; q.append((ny, nx))
    # 물건 속 갇힌 바탕(의자 다리 사이 등): 바탕과 아주 같은 색이면 지워요
    inner = np.zeros_like(seen)   # (갇힌 바탕 지우기는 북 가죽·종이까지 지워서 끔)
    return seen | inner


def label(mask):
    h, w = mask.shape
    lab = np.zeros((h, w), np.int32); n = 0
    for sy, sx in zip(*np.where(mask)):
        if lab[sy, sx]: continue
        n += 1; lab[sy, sx] = n; q = deque([(sy, sx)])
        while q:
            y, x = q.popleft()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = n; q.append((ny, nx))
    return lab, n


def dilate(m, r):
    out = m.copy()
    for _ in range(r):
        o = out.copy()
        o[1:] |= out[:-1]; o[:-1] |= out[1:]; o[:, 1:] |= out[:, :-1]; o[:, :-1] |= out[:, 1:]
        out = o
    return out


def cut(src, outdir, min_area=1800, gap=3):
    a = np.asarray(Image.open(src).convert('RGB')).astype(int)
    fg = ~bg_mask(a)
    # 작은 부스러기 지우고, 가까운 조각은 한 물건으로 묶어요
    lab, n = label(dilate(fg, gap))
    os.makedirs(outdir, exist_ok=True)
    objs = []
    for i in range(1, n + 1):
        m = (lab == i) & fg
        area = m.sum()
        if area < min_area: continue
        ys, xs = np.where(m)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        rgba = np.dstack([a[y0:y1, x0:x1], m[y0:y1, x0:x1] * 255]).astype(np.uint8)
        k = len(objs)
        Image.fromarray(rgba, 'RGBA').save(os.path.join(outdir, f'{k}.png'))
        objs.append((k, x0, y0, x1, y1))
    # 번호 붙인 모아보기
    sheet = Image.new('RGB', (a.shape[1], a.shape[0]), (60, 64, 72))
    sheet.paste(Image.fromarray(a.astype(np.uint8)).point(lambda v: v // 3))
    d = ImageDraw.Draw(sheet)
    for k, x0, y0, x1, y1 in objs:
        im = Image.open(os.path.join(outdir, f'{k}.png')); sheet.paste(im, (x0, y0), im)
        d.rectangle([x0, y0, x1, y1], outline=(255, 220, 0), width=2)
        d.rectangle([x0, y0, x0 + 34, y0 + 24], fill=(0, 0, 0)); d.text((x0 + 4, y0 + 4), str(k), fill=(255, 255, 0))
    sheet.save(os.path.join(outdir, 'sheet.png'))
    return len(objs)


if __name__ == '__main__':
    for s in sys.argv[1:]:
        name = os.path.splitext(os.path.basename(s))[0].replace('rp_', '')
        print(name, cut(s, os.path.join(os.path.dirname(s), 'cut', name)))
