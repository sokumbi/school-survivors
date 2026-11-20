# Draw Things(맥 앱, HTTP API :7860)로 교실 소품을 하나씩 만들어요 (흰 바탕에 물건 하나)
# 이미 있는 파일은 건너뛰어요. 결과: art/drawthings/props/<key>.png
# 실행: /opt/homebrew/bin/python3.10 tools/dt_room_props.py
import os, json, base64, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'art/drawthings/props')
STYLE = ('isometric 16-bit pixel art game asset, single {x}, 2:1 isometric angle facing down-left, crisp large pixels, '
         'limited color palette, clean dark outline, SNES style, cheerful colors, centered, plain flat white background, no shadow, no text')
# key: (설명, 칸 n, 폭 비율, 'floor'/'wall', 방)
ITEMS = {
    'sci_bench': ('black science lab bench with glass beakers and flasks', 2, .85, 'floor', '과학실'),
    'sci_micro': ('microscope on a small wooden lab table', 1, .75, 'floor', '과학실'),
    'sci_skel': ('human skeleton model on a stand', 1, .5, 'floor', '과학실'),
    'sci_globe': ('globe on a wooden stand', 1, .55, 'floor', '과학실'),
    'sci_cab': ('tall glass chemical cabinet with colorful bottles', 1, .8, 'wall', '과학실'),
    'mus_drum': ('drum kit with cymbals', 2, .8, 'floor', '음악실'),
    'mus_xylo': ('wooden xylophone on legs', 1, .8, 'floor', '음악실'),
    'mus_cello': ('cello leaning on a stand', 1, .45, 'wall', '음악실'),
    'mus_stand': ('music stand with sheet music', 1, .45, 'floor', '음악실'),
    'art_easel': ('wooden easel with a colorful landscape painting canvas', 1, .7, 'floor', '미술실'),
    'art_bust': ('white plaster bust sculpture on a pedestal', 1, .55, 'floor', '미술실'),
    'art_table': ('art class table with paint palettes, brushes and paint jars', 2, .8, 'floor', '미술실'),
    'art_shelf': ('wooden shelf with clay pots and vases', 1, .85, 'wall', '미술실'),
    'lib_shelf': ('tall wooden bookshelf full of colorful books', 1, .95, 'wall', '도서실'),
    'lib_table': ('wooden reading table with open books and two chairs', 2, .85, 'floor', '도서실'),
    'lib_cart': ('library book cart with books', 1, .7, 'floor', '도서실'),
    'lib_bean': ('round beanbag chair', 1, .65, 'floor', '도서실'),
    'com_desk': ('computer desk with monitor, keyboard and office chair', 2, .85, 'floor', '컴퓨터실'),
    'com_rack': ('server rack cabinet with blinking lights', 1, .75, 'wall', '컴퓨터실'),
    'com_print': ('office printer on a small stand', 1, .7, 'floor', '컴퓨터실'),
    'bro_cam': ('professional tv camera on a tripod', 1, .6, 'floor', '방송실'),
    'bro_desk': ('broadcast desk with monitors and audio mixer', 2, .85, 'floor', '방송실'),
    'bro_light': ('black studio spotlight lamp on a tall black tripod stand, round lamp head', 1, .5, 'floor', '방송실'),
    'bro_mic': ('microphone on a stand', 1, .4, 'floor', '방송실'),
    'sto_boxes': ('stack of cardboard boxes', 1, .8, 'floor', '창고'),
    'sto_mop': ('mop in a yellow bucket', 1, .55, 'floor', '창고'),
    'sto_balls': ('metal cart full of sports balls', 1, .75, 'floor', '창고'),
    'sto_rack': ('metal storage shelf with boxes', 1, .85, 'wall', '창고'),
    'off_desk': ('empty wooden office desk with laptop, stacks of papers and a coffee mug, empty office chair, no people, nobody', 2, .85, 'floor', '교무실'),
    'off_copy': ('big office photocopier machine', 1, .8, 'wall', '교무실'),
    'off_file': ('gray metal filing cabinet', 1, .7, 'wall', '교무실'),
    'off_sofa': ('small sofa with a coffee table', 2, .8, 'floor', '교무실'),
    'caf_counter': ('school cafeteria serving counter with food trays', 2, .9, 'wall', '급식실'),
    'caf_table': ('long cafeteria table with lunch trays and stools', 2, .9, 'floor', '급식실'),
    'caf_rice': ('big rice cooker on a cart', 1, .6, 'floor', '급식실'),
    'caf_milk': ('blue crate of milk cartons', 1, .55, 'floor', '급식실'),
    'nur_bed': ('hospital bed with white sheets and a pillow', 2, .85, 'floor', '보건실'),
    'nur_med': ('white medicine cabinet with a red cross', 1, .75, 'wall', '보건실'),
    'nur_scale': ('doctor office weighing scale with a tall height measuring rod, white and gray, no people', 1, .45, 'floor', '보건실'),
    'nur_iv': ('hospital IV pole, a tall thin metal stand on wheels with a clear saline bag hanging at the top, no people', 1, .35, 'floor', '보건실'),
    'nur_screen': ('folding hospital privacy screen', 1, .7, 'floor', '보건실'),
}


def gen(key, desc):
    path = os.path.join(OUT, key + '.png')
    if os.path.exists(path): return
    body = {'prompt': STYLE.format(x=desc), 'width': 768, 'height': 768, 'steps': 8, 'seed': -1, 'guidance_scale': 1}
    t = time.time()
    req = urllib.request.Request('http://127.0.0.1:7860/sdapi/v1/txt2img', data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
    r = json.load(urllib.request.urlopen(req, timeout=900))
    open(path, 'wb').write(base64.b64decode(r['images'][0]))
    print(key, round(time.time() - t), 's', flush=True)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for k, v in ITEMS.items():
        for attempt in range(3):
            try: gen(k, v[0]); break
            except Exception as e: print(k, 'error', e, flush=True); time.sleep(10)
    print('done', flush=True)
