# Draw Things(:7860)로 새 괴물 그림을 만들어요 → art/drawthings/mon/<key>.png (있으면 건너뜀)
import os, json, base64, time, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'art/drawthings/mon')
STYLE = ('16-bit pixel art game monster sprite, a living angry {x} with a funny cartoon face, small arms with white gloves and little legs, '
         'mischievous and cute, three-quarter view, single character, full body, crisp large pixels, clean dark outline, bright colors, '
         'centered, plain flat white background, no shadow, no text')
BOSS = ('16-bit pixel art game boss sprite, {x}, menacing but funny, single character, full body, crisp large pixels, clean dark outline, '
        'bright colors, centered, plain flat white background, no shadow, no text')
MON = {
    'pencil':  STYLE.format(x='yellow pencil with a sharp tip pointing forward, ready to charge'),
    'globe':   STYLE.format(x='spinning school globe on a stand'),
    'textbook': STYLE.format(x='open red hardcover school textbook whose two covers flap like wings, the book itself has the angry face on its pages, no animal, no bird'),
    'tray':    STYLE.format(x='silver school lunch tray holding a frisbee pose'),
    'bell':    STYLE.format(x='golden school bell ringing loudly'),
    'mop':     STYLE.format(x='wet mop with a dripping gray mop head as hair'),
    'locker':  BOSS.format(x='a giant teal school locker monster with its door open like a mouth full of teeth and big angry eyes, small legs'),
    'piano':   BOSS.format(x='a grand piano monster with keys as teeth and an angry face, music notes floating around'),
    'vending': BOSS.format(x='a red school vending machine monster with an angry screen face and soda cans, small legs'),
    'mother':  BOSS.format(x='a giant floating purple alien cube mothership with one huge glowing eye, rubik cube pattern, little alien pilots, tentacle cables'),
}
def gen(k, prompt):
    path = os.path.join(OUT, k + '.png')
    if os.path.exists(path): return
    body = {'prompt': prompt, 'width': 768, 'height': 768, 'steps': 8, 'seed': -1, 'guidance_scale': 1}
    t = time.time()
    r = json.load(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:7860/sdapi/v1/txt2img', data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'}), timeout=900))
    open(path, 'wb').write(base64.b64decode(r['images'][0])); print(k, round(time.time() - t), 's', flush=True)
if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for k, p in MON.items():
        for a in range(3):
            try: gen(k, p); break
            except Exception as e: print(k, 'error', e, flush=True); time.sleep(10)
    print('done', flush=True)
