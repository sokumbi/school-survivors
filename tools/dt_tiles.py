# Draw Things로 만든 바닥·벽 그림(art/drawthings/tiles/*_raw.png)을 게임 타일(img/tiles)로 맞춰요
#   바닥: 네모 타일 그림 → 마름모(가로 2*TS, 세로 TS)  /  벽: 정면 그림 → 가로 TS, 세로 WALL_H 면 (+ 뒤집고 어둡게 _r)
# 픽셀 한 점 = 세계 PX칸 (예전 타일은 4, 이번엔 2로 더 촘촘하게)
# 실행: /opt/homebrew/bin/python3.10 tools/dt_tiles.py floor_room wall_board
import os, sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'art/drawthings/tiles')
OUT = os.path.join(ROOT, 'img/tiles')
PX, TS, WALL_H = 1, 64, 76   # 픽셀 한 점 = 세계 1칸 (2026-11-21: 해상도 2배)


def content_box(a, thr=235):
    """흰 여백을 뺀 그림 상자"""
    m = (a < thr).any(2)
    ys, xs = np.where(m)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def floor(name):
    a = np.asarray(Image.open(os.path.join(SRC, name + '_raw.png')).convert('RGB'))
    x0, y0, x1, y1 = content_box(a)
    N = 2 * TS // PX
    tex = np.asarray(Image.fromarray(a[y0:y1, x0:x1]).resize((N, N), Image.BOX)).astype(float)
    DW, DH = 2 * TS // PX, TS // PX
    rgb = np.zeros((DH, DW, 3)); al = np.zeros((DH, DW))
    for sy in range(DH):
        for sx in range(DW):
            X = (sx + .5) * PX - TS; Y = (sy + .5) * PX
            u = (Y / (TS / 2) + X / TS) / 2; v = (Y / (TS / 2) - X / TS) / 2
            if not (0 <= u < 1 and 0 <= v < 1): continue
            rgb[sy, sx] = tex[int(v * N), int(u * N)]; al[sy, sx] = 1
    im = Image.fromarray(rgb.clip(0, 255).astype(np.uint8)); im.putalpha(Image.fromarray((al * 255).astype(np.uint8)))
    im.save(os.path.join(OUT, name + '.png'))


def wall(name, cut_bottom=None):
    a = np.asarray(Image.open(os.path.join(SRC, name + '_raw.png')).convert('RGB'))
    h = a.shape[0]
    if cut_bottom is None:
        # 바닥(갈색 나무) 줄이 시작되는 곳 위까지만: 아래에서부터 가장 어두운 띠(걸레받이) 찾기
        lum = a.mean(2).mean(1)
        lo = int(h * 0.7) + int(np.argmin(lum[int(h * 0.7):]))
        while lo + 1 < h and lum[lo + 1] < lum[lo] + 25: lo += 1
        cut_bottom = lo + 1
    a = a[:cut_bottom]
    FW, FH = TS // PX, WALL_H // PX
    s = np.asarray(Image.fromarray(a).resize((FW, FH), Image.BOX))
    Image.fromarray(s).save(os.path.join(OUT, name + '.png'))
    Image.fromarray((s[:, ::-1] * 0.78).astype(np.uint8)).save(os.path.join(OUT, name + '_r.png'))
    return cut_bottom


def feature(name):
    """흰 바탕 위 물건(창문·문)만 오려 RGBA로"""
    a = np.asarray(Image.open(os.path.join(SRC, name + '_raw.png')).convert('RGB'))
    x0, y0, x1, y1 = content_box(a, 228)
    c = a[y0:y1, x0:x1]
    al = ((c < 228).any(2)) * 255
    return Image.fromarray(np.dstack([c, al]).astype(np.uint8), 'RGBA')


def wall_set():
    """칠판 벽 그림 하나에서 맨 벽(띠 위치 같음)을 뽑고, 창문·문을 얹어 네 종류를 한 벌로 맞춰요"""
    a = np.asarray(Image.open(os.path.join(SRC, 'wall_board_raw.png')).convert('RGB'))
    cut = wall('wall_board')
    a = a[:cut]
    H = a.shape[0]; TW = round(H * TS / WALL_H)
    col = a[:, 25:26]
    plain = np.repeat(col, TW, axis=1)
    g, r = col[:, 0, 1].astype(int), col[:, 0, 0].astype(int)
    band = int(np.argmax(g - r > 25))            # 청록 띠가 시작되는 줄
    FW, FH = TS // PX, WALL_H // PX
    def save(img, k):
        s = np.asarray(Image.fromarray(img).resize((FW, FH), Image.BOX))
        Image.fromarray(s).save(os.path.join(OUT, f'wall_{k}.png'))
        Image.fromarray((s[:, ::-1] * 0.78).astype(np.uint8)).save(os.path.join(OUT, f'wall_{k}_r.png'))
    save(plain, 'plain')
    base = Image.fromarray(plain)
    win = feature('feat_window'); top = int(H * 0.1); hh = band - top - int(H * 0.06)
    w = int(win.width * hh / win.height); w = min(w, int(TW * 0.82)); hh = int(win.height * w / win.width)
    b = base.copy(); b.paste(win.resize((w, hh), Image.LANCZOS), ((TW - w) // 2, top + (band - top - hh) // 2 - int(H * 0.02)), win.resize((w, hh), Image.LANCZOS))
    save(np.asarray(b.convert('RGB')), 'window')
    door = feature('feat_door'); top = int(H * 0.08); hh = H - top
    w = int(door.width * hh / door.height); w = min(w, int(TW * 0.78))
    d = door.resize((w, hh), Image.LANCZOS)
    b = base.copy(); b.paste(d, ((TW - w) // 2, top), d)
    save(np.asarray(b.convert('RGB')), 'door')
    print('band', band, 'H', H, 'TW', TW)


if __name__ == '__main__':
    for n in sys.argv[1:]:
        if n.startswith('floor'): floor(n)
        elif n == "walls": wall_set()
        else: print(n, "cut at", wall(n))
