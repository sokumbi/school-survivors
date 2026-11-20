# 미드저니 학교 타일 그림(art/tiles/mj/mj_tiles_0.png)에서 바닥·벽 그림을 뽑아 픽셀아트로 만들어요
# 결과: img/tiles/*.png
#   floor_room, floor_room2, floor_hall, floor_hall2 : 바닥 마름모 (128x64 세계 크기 → 픽셀 PX마다 한 점)
#   wall_<종류>, wall_<종류>_r : 벽 앞면 (가로 64 x 세로 WALL_H, 게임이 비스듬히 기울여 그려요). _r은 오른쪽 면(뒤집고 어둡게)
# 실행: /opt/homebrew/bin/python3.10 tools/cut_tiles.py
import os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'art/tiles/mj/mj_tiles_0.png')
OUT = os.path.join(ROOT, 'img/tiles')
PX = 4                 # 픽셀 한 점 = 세계 4칸
TS, WALL_H = 64, 76    # 게임과 같아야 해요
FW, FH = TS // PX, WALL_H // PX     # 벽 면 16 x 19 점
DW, DH = 2 * TS // PX, TS // PX     # 바닥 마름모 32 x 16 점

a = np.asarray(Image.open(SRC).convert('RGB')).astype(float)


def unshear(xl, xr, ytl, slope, hh):
    """비스듬한 벽 앞면을 반듯한 네모로 펴요"""
    out = np.zeros((hh, xr - xl, 3))
    for i, x in enumerate(range(xl, xr)):
        y0 = ytl + (x - xl) * slope
        out[:, i] = a[np.round(y0 + np.arange(hh)).astype(int), x]
    return out


def shrink(img, w, h):
    """큰 그림 → w x h 점. 칸마다 중간값 색, 가는 어두운 선은 살려요"""
    im = Image.fromarray(img.clip(0, 255).astype(np.uint8)).resize((w * 10, h * 10), Image.LANCZOS)
    b = np.asarray(im).astype(float).reshape(h, 10, w, 10, 3).transpose(0, 2, 1, 3, 4).reshape(h, w, 100, 3)
    out = np.median(b, axis=2)
    lum = b @ [0.3, 0.59, 0.11]
    dk = lum < 90
    dark = dk.mean(2) >= 0.3
    dmean = np.where(dk[..., None], b, 0).sum(2) / np.maximum(dk.sum(2), 1)[..., None]
    out[dark] = dmean[dark]
    return out


def save(arr, name, alpha=None):
    rgb = arr.clip(0, 255).astype(np.uint8)
    im = Image.fromarray(rgb)
    if alpha is not None: im.putalpha(Image.fromarray((alpha * 255).astype(np.uint8)))
    im.save(os.path.join(OUT, name + '.png'))


def walls():
    # 창문·미닫이문 벽 앞면 (361 x 187)
    R = unshear(981, 1342, 234, 0.465, 187)
    # 칠판 벽 앞면: 높이가 조금 달라서 187로 맞춰요
    B = unshear(607, 875, 87, 0.46, 178)
    B = np.asarray(Image.fromarray(B.astype(np.uint8)).resize((B.shape[1], 187), Image.LANCZOS)).astype(float)
    TW = round(TS * 187 / WALL_H)          # 타일 한 칸 폭(그림 픽셀) ≈ 157
    plain = np.repeat(R[:, 118:119], TW, axis=1)
    def patch(src, u0, u1, v0, v1):
        p = plain.copy(); w = u1 - u0; x = (TW - w) // 2
        p[v0:v1, x:x + w] = src[v0:v1, u0:u1]; return p
    kinds = {
        'plain': plain,
        'window': patch(R, 6, 88, 8, 130),
        'door': np.asarray(Image.fromarray(R[:, 183:351].astype(np.uint8)).resize((TW, 187), Image.LANCZOS)).astype(float),
        'board': patch(B, 110, 266, 12, 142),
    }
    for k, img in kinds.items():
        s = shrink(img, FW, FH)
        save(s, 'wall_' + k)
        save(s[:, ::-1] * 0.78, 'wall_' + k + '_r')   # 오른쪽 면: 뒤집고 어둡게


def floor(top, right, left, name, inset, line):
    T, Rr, L = map(np.array, (top, right, left))
    rgb = np.zeros((DH, DW, 3)); al = np.zeros((DH, DW))
    for sy in range(DH):
        for sx in range(DW):
            X = (sx + .5) * PX - TS; Y = (sy + .5) * PX
            u = (Y / (TS / 2) + X / TS) / 2; v = (Y / (TS / 2) - X / TS) / 2
            if not (0 <= u < 1 and 0 <= v < 1): continue
            uu, vv = inset + u * (1 - 2 * inset), inset + v * (1 - 2 * inset)
            p = T + uu * (Rr - T) + vv * (L - T)
            x0, y0 = int(p[0]), int(p[1])
            rgb[sy, sx] = np.median(a[y0 - 3:y0 + 4, x0 - 3:x0 + 4].reshape(-1, 3), axis=0); al[sy, sx] = 1
            # 칸 줄: 위쪽 두 변 첫 줄을 살짝 어둡게
            if line and (u < PX / TS * 1.0 or v < PX / TS * 1.0): rgb[sy, sx] *= line
    save(rgb, name, al)
    save(np.minimum(rgb * 1.04 + 2, 255), name + '2', al)


def main():
    os.makedirs(OUT, exist_ok=True)
    walls()
    floor((257, 285), (426, 366), (87, 368), 'floor_room', 0.05, 0.9)
    floor((261, 531), (436, 613), (88, 614), 'floor_hall', 0.04, 0.93)
    print(sorted(os.listdir(OUT)))


if __name__ == '__main__':
    main()
