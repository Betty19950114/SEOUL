# -*- coding: utf-8 -*-
"""把 build.py 產生的片段與素材組進最終 HTML。"""
import re, pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent   # 專案根目錄
def read(p): return pathlib.Path(p).read_text(encoding='utf-8')

css       = read('base.css')
mapextra  = read('map_extra.css')
f600      = read('bsd600.b64').strip()
f800      = read('bsd800.b64').strip()
hero      = read('hero_b64.txt').strip()
mapsvg    = read('frag_map.svg.txt')
metrosvg  = read('frag_metro.svg.txt')
metroleg  = read('frag_metrolegend.txt')
cards     = read('frag_cards.html.txt')
legend    = read('frag_legend.html.txt')
quickfind = read('frag_quickfind.html.txt')

css = css.replace('__FONT600__', f600).replace('__FONT800__', f800)

def fill(tpl, extra_css='', **kw):
    s = read(tpl).replace('__CSS__', css + extra_css)
    s = (s.replace('__MAPSVG__', mapsvg)
          .replace('__METROSVG__', metrosvg)
          .replace('__METROLEGEND__', metroleg))
    for k, v in kw.items():
        s = s.replace(f'__{k}__', v)
    return s

idx = fill('tpl_index.html', HERO=hero, CARDS=cards, QUICKFIND=quickfind)
mp  = fill('tpl_map.html', extra_css='\n' + mapextra, LEGEND=legend)

for name, body in [('index.html', idx), ('map.html', mp)]:
    left = sorted(set(re.findall(r'__[A-Z0-9]+__', body)))
    (OUT / name).write_text(body, encoding='utf-8')
    print(f'{name:12s} {len(body)//1024:4d} KB   unreplaced: {left}')
