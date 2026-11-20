# 유담 앞·뒤 걷기, 하람 동작 시트를 잘라 게임 장면(220x190, 발 110,178)으로 만들어요
# 실행: /opt/homebrew/bin/python3.10 tools/cut_extra_frames.py  (그 뒤 tools/clean_edges.py)
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cut_sprites as cs

ROOT = cs.ROOT
OUT = os.path.join(ROOT, 'img')
JOBS = {
    'frontback': ({'rows': [4, 4]}, 'yd', {'walkf': [0, 1, 2, 1], 'walkb': [4, 5, 6, 7]}),
    'haram_act': ({'rows': [4, 4], 'ref': [4, 5]}, 'hr', {'run': [0, 1, 2, 3], 'idle': [4, 5], 'punch': [6, 7]}),
}


def main():
    for sheet, (spec, folder, anims) in JOBS.items():
        frames = cs.cut_sheet(sheet, spec)
        os.makedirs(os.path.join(OUT, folder), exist_ok=True)
        for an, idx in anims.items():
            for k, i in enumerate(idx):
                frames[i].save(os.path.join(OUT, folder, f'{an}_{k}.png'))
        print(sheet, len(frames))


if __name__ == '__main__':
    main()
