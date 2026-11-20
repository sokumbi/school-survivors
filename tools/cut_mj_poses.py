# 미드저니로 뽑은 자세 그림(1024 정사각, 흰 바탕)을 게임 프레임(220×190, 발끝 110,178)으로 바꿔요
# 1) 가장자리에서 이어진 바탕색을 지우기 2) 발밑 그림자 지우기 3) 키를 맞춰 반으로 줄인 뒤 2배 최근접으로 키우기(픽셀 한 칸 = 2px)
# 실행: /opt/homebrew/bin/python3.10 tools/cut_mj_poses.py 입력.png 출력.png 키(px) [x중심 보정]
import sys
from collections import deque
import numpy as np
from PIL import Image


def cutout(im):
    a = np.asarray(im.convert('RGB')).astype(int)
    h, w, _ = a.shape
    bg = np.median(np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]]), axis=0)
    near = np.abs(a - bg).sum(2) < 60
    seen = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if near[y, x]: seen[y, x] = True; q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if near[y, x] and not seen[y, x]: seen[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not seen[ny, nx] and near[ny, nx]:
                seen[ny, nx] = True; q.append((ny, nx))
    alpha = ~seen
    # 갇힌 바탕(다리 사이·팔 사이): 바탕색에 아주 가까운 덩어리가 어느 정도 크면 지워요
    inner = (np.abs(a - bg).sum(2) < 18) & alpha   # 바탕과 거의 똑같은 색만 (흰 셔츠는 그늘이 있어 남아요)
    done = np.zeros((h, w), bool)
    for sy, sx in zip(*np.where(inner)):
        if done[sy, sx]: continue
        comp = [(sy, sx)]; done[sy, sx] = True; k = 0
        while k < len(comp):
            y, x = comp[k]; k += 1
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and inner[ny, nx] and not done[ny, nx]:
                    done[ny, nx] = True; comp.append((ny, nx))
        if len(comp) > 400:
            ys_, xs_ = zip(*comp); alpha[list(ys_), list(xs_)] = False
    # 발밑 그림자: 파르스름하고 옅은 가로 띠 → 지워요 (몸 아래쪽 6%에서만)
    ys = np.where(alpha.any(1))[0]
    top, bot = ys[0], ys[-1]
    zone = int(bot - (bot - top) * 0.06)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    shadowy = (b > r + 25) & (b > g + 5) & ((r + g + b) / 3 > 90)
    alpha[zone:] &= ~shadowy[zone:]
    # 남은 작은 조각(먼지) 지우기: 가장 큰 덩어리와 그 근처만 남겨요
    return a, alpha


def to_frame(src, dst, height, dx=0, px=2):
    im = Image.open(src)
    a, alpha = cutout(im)
    ys, xs = np.where(alpha)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rgba = np.dstack([a, alpha * 255]).astype(np.uint8)[y0:y1, x0:x1]
    crop = Image.fromarray(rgba, 'RGBA')
    k = (height / px) / crop.height
    sw, sh = max(1, round(crop.width * k)), max(1, round(crop.height * k))
    # 미리 곱한 알파로 줄여야 테두리에 흰 띠가 안 생겨요
    pm = np.asarray(crop).astype(float)
    pm[..., :3] *= pm[..., 3:4] / 255
    small = np.asarray(Image.fromarray(pm.astype(np.uint8), 'RGBA').resize((sw, sh), Image.BOX)).astype(float)
    al = small[..., 3]
    rgb = small[..., :3] / np.maximum(al[..., None] / 255, 1e-3)
    keep = al > 110
    out = np.zeros((sh, sw, 4), np.uint8)
    out[..., :3] = np.clip(rgb, 0, 255)
    out[..., 3] = keep * 255
    # 색을 조금 진하게: 작게 줄이면 색이 바래 보여요
    from PIL import ImageEnhance
    rgbim = ImageEnhance.Contrast(ImageEnhance.Color(Image.fromarray(out[..., :3])).enhance(1.45)).enhance(1.12)
    out[..., :3] = np.asarray(rgbim)
    sm = Image.fromarray(out, 'RGBA')
    # 색 수 줄이기 (투명은 그대로)
    q = sm.convert('RGB').quantize(colors=40, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGB')
    qa = np.dstack([np.asarray(q), out[..., 3]])
    # 바깥 테두리 1칸을 진하게 (게임 바닥 위에서 또렷하게)
    m = qa[..., 3] > 0
    edge = m & ~(np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1))
    qa[edge, :3] = (qa[edge, :3] * 0.45).astype(np.uint8)
    big = Image.fromarray(qa.astype(np.uint8), 'RGBA').resize((sw * px, sh * px), Image.NEAREST)
    frame = Image.new('RGBA', (220, 190))
    frame.paste(big, (110 - big.width // 2 + dx, 178 - big.height), big)
    frame.save(dst)


if __name__ == '__main__':
    to_frame(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else 0, int(sys.argv[5]) if len(sys.argv) > 5 else 2)
