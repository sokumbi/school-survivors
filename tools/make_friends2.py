# 친구 6명 새 그림: 미드저니 포즈(art/friends2/fp_<who>_<pose>_<i>.png)를 게임 픽셀 그림으로
# → img/h2/<who>_{idle,punch,hurt,joy}.png, <who>_r<n>.png(달리기), ui_<who>_{ready,joy,tired}.png
# 실행: /opt/homebrew/bin/python3.10 tools/make_friends2.py [who ...]
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
from scipy import ndimage
from cut_mj_poses import cutout
from make_room_props import pixel_art
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = f'{R}/art/friends2'
# 포즈: 'pose_i' 또는 'pose_iF'(좌우 뒤집기). 모두 오른쪽을 보게
PICKS = {
    'minjun': {'idle': 'idle_2', 'punch': 'punch_2', 'hurt': 'hurt_2', 'joy': 'joy_1',
               'run': ['con_0', 'air_2', 'con_1', 'air_1', 'con_3', 'air_3']},
    'seoyeon': {'idle': 'idle_3', 'punch': 'punch_3', 'hurt': 'hurt_0', 'joy': 'joy_3',
                'run': ['con_1', 'air_1', 'pass_1', 'con_2', 'air_2', 'pass_3']},
    'jiho': {'idle': 'idle_2', 'punch': 'punch_1', 'hurt': 'hurt_2', 'joy': 'joy_2',
             'run': ['con_3', 'air_1', 'pass_1', 'air_3', 'con_1', 'con_0']},
    'haeun': {'idle': 'idle_3', 'punch': 'punch_3', 'hurt': 'hurt_2', 'joy': 'joy_2',
              'run': ['con_2', 'air_3', 'con_3', 'con_1F', 'air_1F', 'pass_1']},
    'doyun': {'idle': 'idle_0', 'punch': 'punch_1', 'hurt': 'hurt_1', 'joy': 'joy_1',
              'run': ['con_0', 'air_3', 'pass_1', 'air_2', 'con_3', 'pass_0']},
    'sua': {'idle': 'idle_0', 'punch': 'punch_3', 'hurt': 'hurt_2', 'joy': 'joy_1',
            'run': ['con_2F', 'air_1', 'con_1', 'air_0', 'pass_1', 'pass_3']},
}
HT = {'idle': 132, 'punch': 132, 'hurt': 128, 'joy': 136, 'run': 128}


def clean(pa):
    a = np.asarray(pa).copy(); h = a.shape[0]
    rgb = a[..., :3].astype(int); lum = rgb @ [.3, .59, .11]; sat = (rgb.max(2) - rgb.min(2)) / np.maximum(rgb.max(2), 1)
    zone = np.zeros(a.shape[:2], bool); zone[h - 8:] = True
    a[zone & (lum > 95) & (sat < .3), 3] = 0          # 바닥 그림자 줄
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    tint = ((b > r + 25) & (lum > 90)) | ((r > 170) & (g > 150) & (b < r - 35))   # 파랑·노랑 바닥 그림자
    z2 = np.zeros(a.shape[:2], bool); z2[h - 14:] = True; a[z2 & tint & (sat > .2), 3] = 0
    olive = (b < r * 0.6) & (g > r * 0.75) & (lum > 60); a[z2 & olive, 3] = 0   # 노란 그림자 테두리
    lab, k = ndimage.label(a[..., 3] > 0, structure=np.ones((3, 3)))
    if k > 1:                                           # 가장 큰 덩어리만 (옆에 붙은 얼굴 그림·반짝이 지우기)
        sz = ndimage.sum(np.ones_like(lab), lab, range(1, k + 1)); a[lab != 1 + int(np.argmax(sz)), 3] = 0
    return Image.fromarray(a, 'RGBA')


def frame(who, spec, H):
    flip = spec.endswith('F'); spec = spec.rstrip('F'); pose, i = spec.rsplit('_', 1)
    a, al = cutout(Image.open(f'{SRC}/fp_{who}_{pose}_{i}.png'))
    lab, k = ndimage.label(al, structure=np.ones((3, 3)))   # 원본에서도 가장 큰 사람만
    if k > 1:
        sz = ndimage.sum(np.ones_like(lab), lab, range(1, k + 1)); al = al & (lab == 1 + int(np.argmax(sz)))
    al = ndimage.binary_fill_holes(al)   # 이·눈 흰자처럼 안쪽 구멍 메우기
    ys, xs = np.where(al); c = Image.fromarray(np.dstack([a, al * 255]).astype(np.uint8)[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 'RGBA')
    if flip: c = c.transpose(Image.FLIP_LEFT_RIGHT)
    w0 = min(200, round(c.width * H / c.height))
    pa = clean(pixel_art(c, w0, px=1, colors=48, sat=1.08)); pa = pa.crop(pa.getbbox())
    if abs(pa.height - H) > 3:   # 지운 뒤 키가 달라졌으면 한 번 더 맞춰요
        pa = clean(pixel_art(c, min(200, round(w0 * H / pa.height)), px=1, colors=48, sat=1.08)); pa = pa.crop(pa.getbbox())
    fr = Image.new('RGBA', (220, 190)); fr.paste(pa, (110 - pa.width // 2, 178 - pa.height), pa); return fr


def build(who):
    p = PICKS[who]
    for pose in ('idle', 'punch', 'hurt', 'joy'): frame(who, p[pose], HT[pose]).save(f'{R}/img/h2/{who}_{pose}.png')
    for n, sp in enumerate(p['run']): frame(who, sp, HT['run']).save(f'{R}/img/h2/{who}_r{n}.png')
    for f, src in (('ready', 'idle'), ('joy', 'joy'), ('tired', 'hurt')):
        im = Image.open(f'{R}/img/h2/{who}_{src}.png'); im.crop(im.getbbox()).save(f'{R}/img/h2/ui_{who}_{f}.png')
    print(who, len(p['run']), 'run frames')


if __name__ == '__main__':
    for w in (sys.argv[1:] or PICKS): build(w)
