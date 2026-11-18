# 두 번째 주인공 시트(5×3, 칸 아래에 글자 이름표)를 잘라요. 이름표 줄은 버려요.
from PIL import Image
import json
from cut import cutout, SCALE
im = cutout('src_img/hero2.webp')
W, H = im.size
names = ['walk0','walk1','walk2','walk3','walk4',
         'ready','punch1','punch2','guard','swing',
         'stagger','fall','down','joy','tired']
rowsY = [(0, 270), (270, 518), (518, H)]
meta = json.load(open('img/sprites.json'))
for k, n in enumerate(names):
    c, r = k % 5, k // 5
    x0, x1 = c * W // 5, (c + 1) * W // 5
    cell = im.crop((x0, rowsY[r][0], x1, rowsY[r][1]))
    a = cell.load(); w, h = cell.size
    occ = [any(a[x, y][3] > 0 for x in range(w)) for y in range(h)]
    runs = []; s = None
    for y, o in enumerate(occ + [False]):
        if o and s is None: s = y
        if not o and s is not None: runs.append((s, y)); s = None
    # 맨 아래 짧은 덩어리 = 글자 이름표
    if len(runs) > 1 and runs[-1][1] - runs[-1][0] < 40 and runs[-1][0] > h * 0.7:
        cut_y = runs[-1][0]
    else:
        cut_y = h; print('no label gap', n, runs[-3:])
    cell = cell.crop((0, 0, w, cut_y)); cell = cell.crop(cell.getbbox())
    a = cell.load(); w, h = cell.size
    xs = sorted(x for y in range(int(h * 0.85), h) for x in range(w) if a[x, y][3] > 0)
    fx = xs[len(xs) // 2] if xs else w // 2
    cell = cell.resize((max(1, int(w * SCALE)), max(1, int(h * SCALE))), Image.LANCZOS)
    cell.save(f'img/h2_{n}.png')
    meta[f'h2_{n}'] = {'ax': round(fx * SCALE), 'ay': cell.size[1]}
json.dump(meta, open('img/sprites.json', 'w'), indent=1)
print({k: v for k, v in meta.items() if k.startswith('h2_')})
