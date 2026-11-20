# 교실별 소품: 오려 낸 미드저니 물건(art/roomprops/cut)을 게임 크기 픽셀 그림(img/rprops)으로 바꿔요
# 표 ROOM_PROPS: 방 → [(오린 그림, 칸 수 n(정사각 n×n), 폭 비율, 벽에 붙이기)]
# 실행: /opt/homebrew/bin/python3.10 tools/make_room_props.py  → img/rprops/*.png + img/rprops/props.js(게임에 붙일 표)
import os, json
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUT = os.path.join(ROOT, 'art/roomprops/cut')
OUT = os.path.join(ROOT, 'img/rprops')
TS = 64
F, W = 'floor', 'wall'
ROOM_PROPS = {
    '과학실': [('sci_2/9', 2, .9, F), ('sci_2/4', 2, .78, F), ('sci_2/16', 1, .85, W), ('sci_2/14', 1, .7, W), ('sci_2/2', 1, .62, F),
              ('sci_2/12', 1, .6, F), ('sci_2/1', 1, .32, F), ('sci_1/0', 1, .62, F), ('sci_2/15', 1, .8, F)],
    '음악실': [('mus_2/2', 2, .95, F), ('mus_2/0', 2, .8, F), ('mus_2/6', 2, .8, F), ('mus_2/7', 2, .75, F), ('mus_2/1', 1, .42, W),
              ('mus_2/4', 1, .5, F), ('mus_2/3', 1, .42, W), ('mus_2/9', 1, .75, W), ('mus_1/9', 1, .72, F)],
    '미술실': [('art_3/6', 1, .8, F), ('art_3/7', 1, .62, F), ('art_0/0', 1, .7, F), ('art_3/17', 1, .55, F), ('art_3/1', 1, .55, F),
              ('art_0/4', 1, .7, F), ('art_3/2', 2, .75, F), ('art_0/9', 2, .8, F), ('art_3/20', 1, .6, F), ('art_3/9', 1, .4, F)],
    '도서실': [('lib_2/1', 1, .95, W), ('lib_2/0', 2, .9, F), ('lib_1/0', 2, .85, F), ('lib_1/12', 2, .8, F), ('lib_1/8', 2, .8, F),
              ('lib_1/1', 2, .8, F), ('lib_1/15', 1, .7, F), ('lib_2/10', 1, .7, F), ('lib_1/13', 1, .5, F), ('lib_1/11', 1, .6, W)],
    '컴퓨터실': [('com_2/0', 2, .9, F), ('com_2/1', 2, .85, F), ('com_2/2', 2, .9, F), ('com_2/3', 2, .9, F), ('com_2/4', 2, .9, F),
               ('com_2/5', 1, .85, W), ('com_2/6', 1, .5, F)],
    '방송실': [('bro_2/15', 2, .75, W), ('bro_2/16', 2, .7, F), ('bro_2/17', 2, .8, F), ('bro_2/7', 1, .62, F), ('bro_2/11', 1, .62, F),
              ('bro_2/14', 1, .7, F), ('bro_2/13', 1, .5, F), ('bro_2/10', 1, .42, W), ('bro_2/0', 2, .85, F)],
    '창고': [('sto_1/0', 1, .85, F), ('sto_1/1', 1, .7, F), ('sto_1/2', 1, .6, F), ('sto_1/5', 1, .75, F), ('sto_1/7', 1, .85, F),
            ('sto_1/11', 1, .8, F), ('sto_3/0', 1, .8, W), ('sto_3/1', 1, .8, W), ('sto_3/2', 1, .75, F), ('sto_1/3', 1, .7, F),
            ('sto_3/7', 1, .85, F), ('sto_3/14', 1, .7, F), ('sto_3/12', 1, .6, F), ('sto_1/13', 1, .6, F), ('sto_3/4', 1, .45, F)],
    '교무실': [('off_1/6', 2, .85, F), ('off_3/1', 2, .7, F), ('off_3/3', 2, .75, F), ('off_3/4', 2, .78, F), ('off_3/5', 2, .72, F),
              ('off_1/3', 1, .85, W), ('off_3/0', 1, .95, W), ('off_1/8', 1, .85, W), ('off_1/7', 1, .85, F), ('off_3/2', 1, .8, F)],
    '급식실': [('caf_1/11', 2, .9, F), ('caf_1/12', 2, .9, F), ('caf_1/13', 2, .9, F), ('caf_3/5', 2, .78, F), ('caf_3/4', 2, .78, F),
              ('caf_3/9', 1, .9, F), ('caf_3/2', 2, .8, W), ('caf_3/8', 1, .85, W), ('caf_1/9', 1, .6, F), ('caf_3/6', 1, .85, W)],
    '보건실': [('nur_2/3', 2, .85, F), ('nur_2/5', 2, .85, F), ('nur_1/11', 2, .85, F), ('nur_2/1', 1, .78, W),
              ('nur_1/0', 1, .8, W), ('nur_2/2', 2, .75, W), ('nur_1/3', 1, .45, F), ('nur_1/7', 1, .32, F), 
              ('nur_1/12', 2, .85, F), ('nur_2/0', 1, .7, F)],
}
PICS = ['pic_1/0', 'pic_1/1', 'pic_1/2', 'pic_1/3', 'pic_1/4', 'pic_1/5', 'pic_1/6', 'pic_1/7', 'pic_3/0', 'pic_3/1', 'pic_3/3', 'pic_3/4', 'pic_3/5', 'pic_3/6']


def peel_shadow(a):
    """가장자리에 남은 옅은 그림자(회색·보랏빛)를 바깥부터 벗겨요. 진한 외곽선이 나오면 멈춰요"""
    rgb = a[..., :3].astype(int); al = a[..., 3] > 0
    lum = rgb @ [0.3, 0.59, 0.11]; mx, mn = rgb.max(2), rgb.min(2); sat = (mx - mn) / np.maximum(mx, 1)
    shadowish = (lum > 105) & ((sat < 0.16) | ((rgb[..., 2] > rgb[..., 0] + 8) & (rgb[..., 2] >= rgb[..., 1]) & (sat < 0.4)))
    for _ in range(40):
        out = ~al
        border = al & (np.roll(out, 1, 0) | np.roll(out, -1, 0) | np.roll(out, 1, 1) | np.roll(out, -1, 1))
        kill = border & shadowish
        if not kill.any(): break
        al &= ~kill
    a = a.copy(); a[..., 3] = al * 255
    return a


def pixel_art(im, width, px=2, colors=48, sat=1.15):
    a = peel_shadow(np.asarray(im.convert('RGBA')))
    ys, xs = np.where(a[..., 3] > 0)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h0, w0 = a.shape[:2]
    sw = max(2, round(width / px)); sh = max(2, round(h0 * sw / w0))
    pm = a.astype(float); pm[..., :3] *= pm[..., 3:4] / 255
    small = np.asarray(Image.fromarray(pm.astype(np.uint8), 'RGBA').resize((sw, sh), Image.BOX)).astype(float)
    al = small[..., 3]; rgb = small[..., :3] / np.maximum(al[..., None] / 255, 1e-3)
    out = np.zeros((sh, sw, 4), np.uint8); out[..., :3] = np.clip(rgb, 0, 255); out[..., 3] = (al > 120) * 255
    from PIL import ImageEnhance
    out[..., :3] = np.asarray(ImageEnhance.Color(Image.fromarray(out[..., :3])).enhance(sat))
    q = Image.fromarray(out[..., :3]).quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGB')
    qa = np.dstack([np.asarray(q), out[..., 3]]).astype(np.uint8)
    m = qa[..., 3] > 0
    edge = m & ~(np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1))
    qa[edge, :3] = (qa[edge, :3] * 0.5).astype(np.uint8)   # 바깥 테두리 진하게
    return Image.fromarray(qa, 'RGBA').resize((sw * px, sh * px), Image.NEAREST)


def main():
    os.makedirs(OUT, exist_ok=True)
    table = {}
    for room, lst in ROOM_PROPS.items():
        table[room] = []
        for src, n, wf, place in lst:
            key = src.replace('/', '_')
            im = pixel_art(Image.open(os.path.join(CUT, src + '.png')), wf * 2 * TS * n)
            im.save(os.path.join(OUT, key + '.png'))
            table[room].append({'k': key, 'n': n, 'wall': place == W})
    pics = []
    for src in PICS:
        key = src.replace('/', '_')
        pixel_art(Image.open(os.path.join(CUT, src + '.png')), 52, px=2, colors=40, sat=1.05).save(os.path.join(OUT, key + '.png'))
        pics.append(key)
    js = 'const ROOM_PROPS = ' + json.dumps(table, ensure_ascii=False) + ';\nconst WALL_PICS = ' + json.dumps(pics) + ';\n'
    open(os.path.join(OUT, 'props.js'), 'w').write(js)
    print(sum(len(v) for v in table.values()), 'props,', len(pics), 'pictures')


if __name__ == '__main__':
    main()
