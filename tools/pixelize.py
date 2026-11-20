# 매끈한 그림(미드저니 등)을 16비트 픽셀아트처럼 바꿔요
# 1) 작게 줄이기(픽셀 크기 = px) 2) 색 수 줄이기(팔레트) 3) 어두운 테두리 진하게 4) 최근접으로 다시 키우기
# 실행: /opt/homebrew/bin/python3.10 tools/pixelize.py 입력.png 출력.png [px=6] [colors=24]
import sys
import numpy as np
from PIL import Image, ImageFilter


def pixelize(src, dst, px=6, colors=24):
    im = Image.open(src).convert('RGB')
    w, h = im.width // px, im.height // px
    # 가장자리가 흐려지지 않도록: 살짝 선명하게 한 뒤, 칸마다 중간값 색(평균보다 덜 뭉개져요)
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=120, threshold=2))
    a = np.asarray(im.resize((w * px, h * px), Image.LANCZOS)).reshape(h, px, w, px, 3)
    blk = a.transpose(0, 2, 1, 3, 4).reshape(h, w, px * px, 3).astype(int)
    small = np.median(blk, axis=2)
    # 가는 검은 선 살리기: 칸 안에 어두운 점이 꽤 있으면 그 칸은 선 색으로
    bl = blk @ [0.3, 0.59, 0.11]
    dark = (bl < 80).mean(2) >= 0.18
    dsum = np.where((bl < 80)[..., None], blk, 0).sum(2) / np.maximum((bl < 80).sum(2), 1)[..., None]
    small[dark] = dsum[dark]
    sm = Image.fromarray(small.astype(np.uint8))
    # 팔레트: 색 수를 줄여요 (k-평균으로 다듬어 작은 면 색도 남게, 디더링 없이)
    q = sm.quantize(colors=colors, method=Image.Quantize.FASTOCTREE, kmeans=3, dither=Image.Dither.NONE).convert('RGB')
    arr = np.asarray(q).astype(int)
    # 테두리: 밝기가 확 바뀌는 곳의 어두운 쪽 칸을 더 어둡게 (1픽셀 외곽선 느낌)
    lum = arr @ [0.3, 0.59, 0.11]
    edge = np.zeros(lum.shape, bool)
    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        nb = np.roll(np.roll(lum, dy, 0), dx, 1)
        edge |= (nb - lum) > 55
    out = arr.copy()
    out[edge] = (arr[edge] * 0.55).astype(int)
    Image.fromarray(out.astype(np.uint8)).resize((w * px, h * px), Image.NEAREST).save(dst)
    return w, h


if __name__ == '__main__':
    px = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    c = int(sys.argv[4]) if len(sys.argv) > 4 else 24
    print(pixelize(sys.argv[1], sys.argv[2], px, c))
