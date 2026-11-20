# 바닥 칸에 딱 맞는 상자 모양 소품의 면 그림(픽셀아트)을 만들어요
# 게임이 이 네모 그림을 비스듬히 기울여 상자의 앞면(_f)·옆면(_s)으로 붙여요. 윗면은 게임이 색으로 칠해요
# 한 점 = 세계 4칸, 타일 한 칸 폭 = 16점
# 실행: /opt/homebrew/bin/python3.10 tools/make_props.py
import os, random
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'img/props')
random.seed(7)


def hexc(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def canvas(w, h, col=None): return Image.new('RGBA', (w, h), hexc(col) if col else (0, 0, 0, 0))


def rect(im, x0, y0, x1, y1, col):
    c = hexc(col)
    for y in range(max(0, y0), min(im.height, y1)):
        for x in range(max(0, x0), min(im.width, x1)): im.putpixel((x, y), c)


def border(im, col):
    w, h = im.size; rect(im, 0, 0, w, 1, col); rect(im, 0, h - 1, w, h, col); rect(im, 0, 0, 1, h, col); rect(im, w - 1, 0, w, h, col)


def lockers(n=3, h=25):
    f = canvas(16 * n, h, '#1fa39d'); OL, DK, HI = '#0b4446', '#157a76', '#5fd3c9'
    doors = 4 if n == 3 else n
    dw = f.width // doors
    for i in range(doors):
        x0 = i * dw
        rect(f, x0, 0, x0 + 1, h, OL)
        rect(f, x0 + 1, 1, x0 + dw, 2, HI)                     # 위 반짝
        for vy in (4, 6, h - 7, h - 5): rect(f, x0 + 3, vy, x0 + dw - 3, vy + 1, DK)   # 숨구멍
        rect(f, x0 + dw - 3, h // 2 - 1, x0 + dw - 2, h // 2 + 2, '#d8e4e4')        # 손잡이
    rect(f, 0, h - 2, f.width, h, DK); border(f, OL)
    s = canvas(16, h, '#16827d'); rect(s, 0, h - 2, 16, h, '#0f5f5b'); border(s, OL)
    return f, s


def shelf(n=2, h=31):
    FR, OL, IN = '#b8693a', '#4a2a14', '#6b3b1e'
    f = canvas(16 * n, h, FR); rect(f, 2, 2, f.width - 2, h - 2, IN)
    books = ['#e53935', '#1e88e5', '#fdd835', '#43a047', '#8e24aa', '#fb8c00', '#00acc1', '#f06292']
    rows = list(range(2, h - 3, 6))
    for y0 in rows:
        rect(f, 2, y0 + 5, f.width - 2, y0 + 6, FR)            # 선반
        x = 3
        while x < f.width - 3:
            bh = random.choice([3, 4, 4, 5]); c = random.choice(books)
            if random.random() < 0.12: x += 2; continue
            rect(f, x, y0 + 5 - bh, x + 1, y0 + 5, c); x += 1
    border(f, OL)
    s = canvas(16, h, '#9c5630'); rect(s, 0, 0, 16, 1, '#c97b45'); border(s, OL)
    return f, s


def tdesk(n=2, h=9):
    OL = '#5a2f12'
    f = canvas(16 * n, h, '#e08a45'); rect(f, 0, 0, f.width, 2, '#f2a35e'); rect(f, 0, h - 2, f.width, h, '#b86a30')
    rect(f, 3, 3, f.width // 2 - 1, h - 3, '#c8763a'); rect(f, f.width // 2 + 1, 3, f.width - 3, h - 3, '#c8763a')
    border(f, OL)
    s = canvas(16, h, '#c8763a'); rect(s, 0, 0, 16, 2, '#e08a45'); border(s, OL)
    return f, s


def desk(n=2, h=8):
    OL, TOP, LEG = '#5a2f12', '#e8924c', '#7d8591'
    f = canvas(16 * n, h)
    rect(f, 0, 0, f.width, 2, TOP); rect(f, 0, 1, f.width, 2, '#c4733a'); rect(f, 0, 0, f.width, 1, OL)
    rect(f, 0, 0, 1, 2, OL); rect(f, f.width - 1, 0, f.width, 2, OL); rect(f, 0, 2, f.width, 3, OL)
    for lx in (1, f.width - 3, f.width // 2 - 1): rect(f, lx, 3, lx + 2, h, LEG); rect(f, lx, h - 1, lx + 2, h, '#3c4048')
    rect(f, 3, 4, f.width - 3, 5, '#5b616b')                    # 책 받침대
    s = canvas(16, h)
    rect(s, 0, 0, 16, 2, '#c4733a'); rect(s, 0, 0, 16, 1, OL); rect(s, 0, 2, 16, 3, OL)
    for lx in (1, 13): rect(s, lx, 3, lx + 2, h, '#6b727d'); rect(s, lx, h - 1, lx + 2, h, '#3c4048')
    return f, s


def main():
    for k, fn in {'lockers': lockers, 'shelf': shelf, 'tdesk': tdesk, 'desk': desk}.items():
        f, s = fn(); f.save(os.path.join(OUT, f'box_{k}_f.png')); s.save(os.path.join(OUT, f'box_{k}_s.png'))
    print('ok')


if __name__ == '__main__':
    main()
