# -*- coding: utf-8 -*-
"""由 data.py 產生行程頁的各個片段（地圖 SVG、地鐵圖、每日卡片、圖例、快速尋找）。"""
import math, html, json, urllib.parse
from data import (PLACES, STATION, CAT, MODE, DAYS, REGIONS, ASK,
                  METRO_STATIONS, METRO_LINES)

def esc(s): return html.escape(str(s), quote=True)
def naver(q): return "https://map.naver.com/p/search/" + urllib.parse.quote(q)

def station_of(key):
    zh, line, m = STATION[key]
    return f'{zh}站（{line} 線）· 步行約 {max(1, round(m/75))} 分（{m} m）'

# ---------------- projection（地圖與地鐵圖共用，切換時位置一致） ----------------
lonMin, lonMax = 126.888, 127.072
latMin, latMax = 37.500, 37.590
MW, MH = 830, 452
def project(lon, lat):
    return ((lon-lonMin)/(lonMax-lonMin)*MW, (latMax-lat)/(latMax-latMin)*MH)

# ---------------- 站點編號、同站判斷 ----------------
nodes = {}
for d in sorted(DAYS):
    o = 0; prev = None
    for it in DAYS[d]["items"]:
        if it["k"] != "stop":
            continue
        o += 1; it["ord"] = o
        it["n"] = PLACES[it["key"]][0]
        it["same_station"] = (STATION[it["key"]][0] == prev)
        prev = STATION[it["key"]][0]
        if it.get("offmap"):
            continue
        _, lon, lat, _ = PLACES[it["key"]]
        x, y = project(lon, lat)
        nodes[it["key"]] = {"day": d, "ord": o, "x": x, "y": y, "cat": it["cat"],
                            "key": it["key"], "name": it["n"], "t": it["t"]}

MIN = 23.0
nl = list(nodes.values())
for _ in range(700):
    moved = False
    for i in range(len(nl)):
        for j in range(i+1, len(nl)):
            a, b = nl[i], nl[j]
            dx, dy = b["x"]-a["x"], b["y"]-a["y"]
            dist = math.hypot(dx, dy)
            if dist < MIN:
                moved = True
                if dist < 0.01: dx, dy, dist = 0.6, 0.4, 0.72
                p = (MIN-dist)/2; ux, uy = dx/dist, dy/dist
                a["x"] -= ux*p; a["y"] -= uy*p
                b["x"] += ux*p; b["y"] += uy*p
    if not moved: break
for n in nl:
    n["x"] = round(n["x"], 1); n["y"] = round(n["y"], 1)

# ---------------- 路線圖 SVG ----------------
region_boxes, region_labels = [], []
for label, keys in REGIONS:
    ks = [k for k in keys if k in nodes]
    if not ks: continue
    xs = [nodes[k]["x"] for k in ks]; ys = [nodes[k]["y"] for k in ks]
    pad = 26
    x0, x1 = min(xs)-pad, max(xs)+pad
    y0, y1 = min(ys)-pad, max(ys)+pad
    region_boxes.append(
      f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1-x0:.1f}" height="{y1-y0:.1f}" rx="16" class="regionbox"/>')
    region_labels.append(
      f'<g class="region"><rect x="{x0:.1f}" y="{y0-19:.1f}" width="{len(label)*11.5+14:.0f}" '
      f'height="18" rx="9" class="regionchip"/>'
      f'<text x="{x0+7:.1f}" y="{y0-6:.1f}" class="regiontext">{esc(label)}</text></g>')

def route_pts(d):
    pts = sorted([n for n in nl if n["day"] == d], key=lambda n: n["ord"])
    if d == 5: pts = [nodes["hotel"]] + pts
    return pts

groups = []
for d in sorted(DAYS):
    pts = route_pts(d)
    if not pts: continue
    parts = []
    if len(pts) > 1:
        poly = " ".join(f'{p["x"]},{p["y"]}' for p in pts)
        parts.append(f'<polyline points="{poly}" fill="none" stroke="var(--d{d})" '
                     f'stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>')
    for p in pts:
        if p["cat"] == "stay": continue
        lbl = f'DAY {d} 第 {p["ord"]} 站 · {p["name"]} · {p["t"]}'
        parts.append(
          f'<g class="pin" data-name="{esc(p["name"])}" data-time="{p["t"]}" data-d="{d}" data-ord="{p["ord"]}">'
          f'<title>{esc(lbl)}</title>'
          f'<circle cx="{p["x"]:.1f}" cy="{p["y"]:.1f}" r="11.5" fill="var(--d{d})" '
          f'stroke="var(--mapbg)" stroke-width="2.5"/>'
          f'<circle class="pinhit" cx="{p["x"]:.1f}" cy="{p["y"]:.1f}" r="16" fill="transparent"/>'
          f'<text x="{p["x"]:.1f}" y="{p["y"]+4:.1f}" text-anchor="middle" class="pnum">{p["ord"]}</text></g>')
    groups.append(f'<g class="dayg" data-day="{d}">\n' + "\n".join(parts) + "\n</g>")

h = nodes["hotel"]
anchor = (f'<g class="anchor pin" data-name="서울역 라움169（住宿）" data-time="每日出發點" data-d="0" data-ord="H">'
          f'<title>住宿：서울역 라움169</title>'
          f'<rect x="{h["x"]-10.5:.1f}" y="{h["y"]-10.5:.1f}" width="21" height="21" rx="5" '
          f'transform="rotate(45 {h["x"]} {h["y"]})" fill="var(--ink)" stroke="var(--mapbg)" stroke-width="2.5"/>'
          f'<text x="{h["x"]:.1f}" y="{h["y"]+4:.1f}" text-anchor="middle" class="pnum anchor-t">H</text>'
          f'<text x="{h["x"]:.1f}" y="{h["y"]+27:.1f}" text-anchor="middle" class="anchor-l">首爾站・住宿</text></g>')

open("frag_map.svg.txt", "w", encoding="utf-8").write(
    '<g class="regionboxes">\n' + "\n".join(region_boxes) + '\n</g>\n'
    + "\n".join(groups) + "\n" + anchor + '\n'
    + '<g class="regionlabels">\n' + "\n".join(region_labels) + '\n</g>')

# ---------------- 地鐵圖 SVG ----------------
MS = {ko: (zh, lines, *project(lon, lat), days)
      for ko, zh, lines, lon, lat, days in METRO_STATIONS}

seg = []
for lname, colour, path in METRO_LINES:
    pts = " ".join(f'{MS[s][2]:.1f},{MS[s][3]:.1f}' for s in path if s in MS)
    seg.append(f'<polyline class="mline" data-line="{lname}" points="{pts}" fill="none" '
               f'stroke="{colour}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')

dots = []
for ko, zh, lines, lon, lat, days in METRO_STATIONS:
    x, y = project(lon, lat)
    interchange = "·" in lines
    r = 7.5 if interchange else 5.5
    dots.append(
      f'<g class="mstation" data-days="{" ".join(map(str, days))}" data-zh="{esc(zh)}" data-name="{esc(zh)}站" data-time="{esc(lines)} 線">'
      f'<title>{esc(zh)}站（{esc(lines)}）</title>'
      f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r+4:.1f}" class="mhalo"/>'
      f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" class="mdot{" ix" if interchange else ""}"/>'
      f'<text x="{x:.1f}" y="{y-r-6:.1f}" text-anchor="middle" class="mlabel">{esc(zh)}</text></g>')

legend_lines = "".join(
    f'<span class="mlg"><i style="background:{c}"></i>{("機場快線" if n=="A" else n+" 號線")}</span>'
    for n, c, _ in METRO_LINES)

open("frag_metro.svg.txt", "w", encoding="utf-8").write(
    '<g class="mlines">\n' + "\n".join(seg) + '\n</g>\n'
    + '<g class="mstations">\n' + "\n".join(dots) + '\n</g>')
open("frag_metrolegend.txt", "w", encoding="utf-8").write(legend_lines)

# ---------------- 每日卡片 ----------------
def picks_html(it):
    ps = it.get("picks")
    if not ps: return ""
    rows = "".join(
      f'<li><span class="pkname">{esc(n)}</span><span class="pkdesc">{esc(d)}</span>'
      f'<span class="pkmeta">🕘 {esc(hh)}</span>'
      f'<a class="pkmap" href="{naver(a)}" target="_blank" rel="noopener noreferrer">{esc(a)} ↗</a></li>'
      for n, d, hh, a in ps)
    return f'<div class="picks"><div class="pkhead">巷內必吃推薦</div><ul>{rows}</ul></div>'

def info_block(it):
    key = it["key"]
    addr = PLACES[key][3]
    hours = it.get("hours", ASK)
    rows, labels = [], []
    if it.get("note"):
        rows.append(f'<dt>說明</dt><dd>{esc(it["note"])}</dd>'); labels.append("說明")
    if not it.get("same_station"):
        rows.append(f'<dt>最近地鐵站</dt><dd>{esc(station_of(key))}</dd>'); labels.append("地鐵站")
    unk = ' class="unk"' if hours == ASK else ''
    rows.append(f'<dt>營業時間</dt><dd{unk}>{esc(hours)}</dd>'); labels.append("營業時間")
    rows.append(f'<dt>地址</dt><dd class="addr">{esc(addr)}</dd>'); labels.append("地址")
    return (f'<details class="stopinfo">'
            f'<summary><span class="sumico" aria-hidden="true"></span>{" · ".join(labels)}</summary>'
            f'<dl class="infogrid">{"".join(rows)}</dl>'
            f'<a class="navermap" href="{naver(addr)}" target="_blank" rel="noopener noreferrer">在 Naver 地圖開啟 ↗</a>'
            f'{picks_html(it)}</details>')

cards = []
for d in sorted(DAYS):
    D = DAYS[d]
    chips = '<span class="asep">→</span>'.join(f'<span class="achip">{esc(a)}</span>' for a in D["areas"])
    rows = []
    for it in D["items"]:
        if it["k"] == "move":
            mode = it.get("mode", "walk")
            rows.append(f'<li class="tr move {mode}"><span class="tt">{it["t"]}</span>'
              f'<span class="tbody"><span class="mbadge">{MODE[mode]}</span>'
              f'<span class="tn">{esc(it["n"])}</span>'
              + (f'<span class="tnote">{esc(it["note"])}</span>' if it.get("note") else "") + '</span></li>')
        else:
            num = "H" if it["cat"] == "stay" else str(it["ord"])
            off = ' offmap' if it.get("offmap") else ''
            sub = ""
            if it.get("sub"):
                sub = ('<span class="sublist">'
                       + "".join(f'<span class="subchip">{esc(x)}</span>' for x in it["sub"])
                       + '</span>')
            stn = STATION[it["key"]][0]
            rows.append(
              f'<li class="tr stop{off}" id="stop-{it["key"]}" data-station="{esc(stn)}">'
              f'<span class="tt">{it["t"]}</span>'
              f'<span class="tbody"><span class="tnum">{num}</span>'
              f'<span class="tag {it["cat"]}">{CAT[it["cat"]]}</span>'
              f'<span class="tn">{esc(it["n"])}</span>{sub}{info_block(it)}</span></li>')
    sc = sum(1 for it in D["items"] if it["k"] == "stop")
    cards.append(f'''<section class="daycard" data-day="{d}" style="--c:var(--d{d})">
  <header class="dhead">
    <span class="dnum">{d}</span>
    <span class="dmeta"><span class="ddate">DAY {d} · {D["date"]} {D["dow"]}</span>
    <span class="dtheme">{esc(D["theme"])}</span></span>
    <span class="dcount">{sc} 站</span>
  </header>
  <div class="arearoute">{chips}</div>
  <ol class="tl">
{chr(10).join(rows)}
  </ol>
</section>''')
open("frag_cards.html.txt", "w", encoding="utf-8").write("\n\n".join(cards))

# ---------------- 地圖頁清單 ----------------
leg = []
for d in sorted(DAYS):
    D = DAYS[d]; rows = []
    for it in D["items"]:
        if it["k"] != "stop": continue
        num = "H" if it["cat"] == "stay" else str(it["ord"])
        extra = ' <span class="lo">（地圖外）</span>' if it.get("offmap") else ''
        zh, _, m = STATION[it["key"]]
        rows.append(f'<li><span class="lnum">{num}</span><span class="ltime">{it["t"]}</span>'
                    f'<span class="tag {it["cat"]}">{CAT[it["cat"]]}</span>'
                    f'<span class="lname">{esc(it["n"])}{extra}'
                    f'<span class="lstn">{esc(zh)}站 · {max(1,round(m/75))}分</span></span></li>')
    leg.append(f'<div class="lgroup" style="--c:var(--d{d})">'
               f'<h3><span class="lbar"></span>DAY {d} · {esc(D["theme"])}</h3><ul>{"".join(rows)}</ul></div>')
open("frag_legend.html.txt", "w", encoding="utf-8").write("\n".join(leg))

# ---------------- 快速尋找 ----------------
QF = [("food","美食"), ("shop","購物"), ("sight","景點"), ("dessert","甜點"), ("cafe","咖啡廳")]
qf = []
for cat, label in QF:
    ent = []
    for d in sorted(DAYS):
        for it in DAYS[d]["items"]:
            if it["k"] != "stop" or it["cat"] != cat: continue
            ent.append(f'<li><button type="button" data-target="stop-{it["key"]}" data-day="{d}">'
                       f'<span class="qfday" style="--c:var(--d{d})">D{d}</span>'
                       f'<span class="qfname">{esc(it["n"])}</span>'
                       f'<span class="qftime">{it["t"]}</span></button></li>')
    if ent:
        qf.append(f'<details class="qf" data-cat="{cat}">'
                  f'<summary><span class="qfdot tag {cat}"></span>{label}'
                  f'<span class="qfn">{len(ent)}</span></summary><ul>{"".join(ent)}</ul></details>')
open("frag_quickfind.html.txt", "w", encoding="utf-8").write(
    '<div class="quickfind"><span class="qflabel">快速尋找</span>' + "".join(qf) + '</div>')

print("stops:", len(nl), "| regions:", len(region_boxes), "| metro stations:", len(METRO_STATIONS))
for d in sorted(DAYS):
    print(f"  DAY {d}:", [f'{n["ord"]}:{n["key"]}' for n in route_pts(d)])
