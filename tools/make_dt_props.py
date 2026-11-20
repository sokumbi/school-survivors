# Draw Things로 만든 교실 소품(art/drawthings/props)을 오려 게임 크기 픽셀 그림(img/rprops/dt_*.png)으로 바꾸고,
# index.html 의 ROOM_PROPS 표를 새로 써요. 벽 그림 액자(WALL_PICS)는 미드저니 것을 그대로 둬요.
# 실행: /opt/homebrew/bin/python3.10 tools/make_dt_props.py
import os, re, sys, json, shutil
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cut_room_props import cut
from make_room_props import pixel_art, TS
from dt_room_props import ITEMS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'art/drawthings/props')
TMP = os.path.join(ROOT, 'art/drawthings/props_cut')
OUT = os.path.join(ROOT, 'img/rprops')
EXTRA = {'mus_piano': ('grand piano', 2, .95, 'floor', '음악실')}


def main():
    items = {**ITEMS, **EXTRA}
    table = {}
    for key, (desc, n, wf, place, room) in items.items():
        src = os.path.join(SRC, key + '.png')
        if not os.path.exists(src): print('없음', key); continue
        d = os.path.join(TMP, key); shutil.rmtree(d, ignore_errors=True)
        k = cut(src, d, min_area=800, gap=4)
        if not k: print('못 오림', key); continue
        big = max((Image.open(os.path.join(d, f'{i}.png')) for i in range(k)), key=lambda im: im.width * im.height)
        pixel_art(big, wf * 2 * TS * n, px=1, sat=1.05).save(os.path.join(OUT, f'dt_{key}.png'))
        table.setdefault(room, []).append({'k': 'dt_' + key, 'n': n, 'wall': place == 'wall'})
    # 이제 안 쓰는 미드저니 소품 그림은 지워요 (원본은 art/roomprops 에 남아 있어요)
    for f in os.listdir(OUT):
        if f.endswith('.png') and not f.startswith('dt_') and not f.startswith('pic_'): os.remove(os.path.join(OUT, f))
    p = os.path.join(ROOT, 'index.html'); s = open(p).read()
    s2 = re.sub(r'const ROOM_PROPS = \{.*?\};', lambda m: 'const ROOM_PROPS = ' + json.dumps(table, ensure_ascii=False) + ';', s, count=1, flags=re.S)
    assert s2 != s or 'dt_' in s
    open(p, 'w').write(s2)
    print(sum(len(v) for v in table.values()), 'props in', len(table), 'rooms')


if __name__ == '__main__':
    main()
