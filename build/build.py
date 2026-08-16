# -*- coding: utf-8 -*-
"""由 data.py 產生行程頁的各個片段（地圖 SVG、地鐵圖、每日卡片、圖例、快速尋找）。"""
import math, html, json, urllib.parse
from data import (PLACES, STATION, CAT, MODE, DAYS, REGIONS, ASK, EXIT,
                  METRO_STATIONS, METRO_LINES, LINE_COLOUR)

def esc(s): return html.escape(str(s), quote=True)
def naver(q): return "https://map.naver.com/p/search/" + urllib.parse.quote(q)
def nmap(q):
    """Naver 地圖 App 深層連結；未安裝時由前端退回網頁版"""
    return ("nmap://search?query=" + urllib.parse.quote(q)
            + "&appname=betty19950114.github.io")

METRO_ZH = {z for _, z, *_ in METRO_STATIONS}

def ordlabel(n):
    """1→A 2→B … 27→AA"""
    out = ""
    while n > 0:
        n, r = divmod(n-1, 26)
        out = chr(65+r) + out
    return out

def linelabel(line):
    """純線號補「號線」；混合線別（如 2·機場快線·京義中央）維持原樣"""
    return f'{line} 號線' if all(c.isdigit() or c == '·' for c in line) else line

def station_of(key):
    zh, line, m = STATION[key]
    head = f'{zh}站（{linelabel(line)}）'
    if m < 0:                       # 非步行可達（愛寶樂園需轉接駁巴士）
        return head + '需轉免費接駁巴士，非步行可達'
    ex = EXIT.get(key)
    if ex:
        head += f'{ex} 號出口'
    return f'{head}・步行 {max(1, round(m/75))} 分（{m} m）'      # 間隔號，不留多餘空白

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
        if it["cat"] == "stay":
            it["ord"] = None          # 住宿不佔字母序
        else:
            o += 1; it["ord"] = ordlabel(o)
        it["n"] = PLACES[it["key"]][0]
        it["same_station"] = (STATION[it["key"]][0] == prev)
        prev = STATION[it["key"]][0]
        if it.get("offmap"):
            continue
        _, lon, lat, _ = PLACES[it["key"]]
        x, y = project(lon, lat)
        nodes[it["key"]] = {"day": d, "ord": it["ord"], "x": x, "y": y, "cat": it["cat"],
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

ORDER = {}
for d in sorted(DAYS):
    seq = [i["key"] for i in DAYS[d]["items"] if i["k"] == "stop"]
    for i, k in enumerate(seq):
        ORDER[k] = i

def route_pts(d):
    pts = sorted([n for n in nl if n["day"] == d], key=lambda n: ORDER[n["key"]])
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
        lbl = f'DAY {d} · {p["ord"]} · {p["name"]} · {p["t"]}'
        parts.append(
          f'<g class="pin" data-name="{esc(p["name"])}" data-time="{p["t"]}" data-d="{d}" '
          f'data-ord="{p["ord"]}" data-stop="stop-{p["key"]}">'
          f'<title>{esc(lbl)}</title>'
          f'<circle cx="{p["x"]:.1f}" cy="{p["y"]:.1f}" r="11.5" fill="var(--d{d})" '
          f'stroke="var(--mapbg)" stroke-width="2.5"/>'
          f'<circle class="pinhit" cx="{p["x"]:.1f}" cy="{p["y"]:.1f}" r="16" fill="transparent"/>'
          f'<text x="{p["x"]:.1f}" y="{p["y"]+4:.1f}" text-anchor="middle" class="pnum">{p["ord"]}</text></g>')
    groups.append(f'<g class="dayg" data-day="{d}">\n' + "\n".join(parts) + "\n</g>")

h = nodes["hotel"]
anchor = (f'<g class="anchor pin" data-name="서울역 라움169（住宿）" data-time="每日出發點" data-d="0" data-ord="住" data-stop="stop-hotel">'
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
mpos = {}
for ko, zh, lines, lon, lat, days, nums in METRO_STATIONS:
    x, y = project(lon, lat)
    mpos[ko] = {"ko": ko, "zh": zh, "lines": lines, "x": x, "y": y, "days": days, "nums": nums}

# 圓點放大到能容納站號，故需拉開間距
ml = list(mpos.values())
MMIN = 34.0
for _ in range(600):
    moved = False
    for i in range(len(ml)):
        for j in range(i+1, len(ml)):
            a, b = ml[i], ml[j]
            dx, dy = b["x"]-a["x"], b["y"]-a["y"]
            dist = math.hypot(dx, dy)
            if dist < MMIN:
                moved = True
                if dist < 0.01: dx, dy, dist = 0.6, 0.4, 0.72
                pu = (MMIN-dist)/2; ux, uy = dx/dist, dy/dist
                a["x"] -= ux*pu; a["y"] -= uy*pu
                b["x"] += ux*pu; b["y"] += uy*pu
    if not moved: break

seg = []
for lname, colour, path in METRO_LINES:
    pts = " ".join(f'{mpos[st]["x"]:.1f},{mpos[st]["y"]:.1f}' for st in path if st in mpos)
    seg.append(f'<polyline class="mline" data-line="{lname}" points="{pts}" fill="none" '
               f'stroke="{colour}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')

SHORT = {"東大門歷史文化公園": "東大門歷史文化", "高速巴士客運站": "高速巴士"}

# 標籤預設放上方；若與已放置的標籤重疊就改放下方
placed = []
def label_y(st, txt):
    w = len(txt) * 11.5 + 6
    for dy, anchor in ((-18, "above"), (24, "below")):
        box = (st["x"] - w/2, st["y"] + dy - 11, st["x"] + w/2, st["y"] + dy + 3)
        if not any(box[0] < q[2] and q[0] < box[2] and box[1] < q[3] and q[1] < box[3] for q in placed):
            placed.append(box)
            return dy
    placed.append((st["x"] - w/2, st["y"] + 24 - 11, st["x"] + w/2, st["y"] + 24 + 3))
    return 24

dots = []
for st in sorted(ml, key=lambda a: (a["y"], a["x"])):
    x, y = st["x"], st["y"]
    pline, pnum = st["nums"][0]
    colour = LINE_COLOUR.get(pline, "#888")
    allnums = "　".join(f'{l} 號線 {n}' if l != "A" else f'機場快線 {n}' for l, n in st["nums"])
    txt = SHORT.get(st["zh"], st["zh"])
    dy = label_y(st, txt)
    dots.append(
      f'<g class="mstation" data-days="{" ".join(map(str, st["days"]))}" data-zh="{esc(st["zh"])}" '
      f'data-name="{esc(st["zh"])}站 {esc(pnum)}" data-time="{esc(allnums)}">'
      f'<title>{esc(st["zh"])}站（{esc(allnums)}）</title>'
      f'<circle cx="{x:.1f}" cy="{y:.1f}" r="17" class="mhalo"/>'
      f'<circle cx="{x:.1f}" cy="{y:.1f}" r="13" class="mdot" fill="{colour}"/>'
      f'<text x="{x:.1f}" y="{y+3.6:.1f}" text-anchor="middle" class="mnum">{esc(pnum)}</text>'
      f'<text x="{x:.1f}" y="{y+dy:.1f}" text-anchor="middle" class="mlabel">{esc(txt)}</text></g>')

legend_lines = "".join(
    f'<span class="mlg"><i style="background:{c}"></i>{("機場快線" if n=="A" else n+" 號線")}</span>'
    for n, c, _ in METRO_LINES)

open("frag_metro.svg.txt", "w", encoding="utf-8").write(
    '<g class="mlines">\n' + "\n".join(seg) + '\n</g>\n'
    + '<g class="mstations">\n' + "\n".join(dots) + '\n</g>')
open("frag_metrolegend.txt", "w", encoding="utf-8").write(legend_lines)

# ---------------- 每日卡片 ----------------
def subs_html(it):
    ss = it.get("sub")
    if not ss: return ""
    rows = ""
    for name, q, note, hrs, addr in ss:
        known = not addr.startswith("確切門牌") and not addr.startswith("地址依")
        rows += (f'<li><span class="pkname">{esc(name)}</span>'
                 f'<span class="pkdesc">{esc(note)}</span>'
                 f'<span class="pkmeta">🕘 {esc(hrs)}</span>'
                 f'<span class="pkmeta{"" if known else " unk"}">📍 {esc(addr)}</span>'
                 f'<a class="actbtn pkmap" href="{naver(addr if known else q)}" '
                 f'data-nmap="{esc(nmap(addr if known else q))}" '
                 f'target="_blank" rel="noopener noreferrer">'
                 f'<span class="aico" aria-hidden="true">🗺</span>Naver開啟</a></li>')
    return f'<div class="picks"><div class="pkhead">此站包含 {len(ss)} 家</div><ul>{rows}</ul></div>'

def picks_html(it):
    ps = it.get("picks")
    if not ps: return ""
    rows = "".join(
      f'<li><span class="pkname">{esc(n)}</span><span class="pkdesc">{esc(d)}</span>'
      f'<span class="pkmeta">🕘 {esc(hh)}</span>'
      f'<span class="pkmeta">📍 {esc(a)}</span>'
      f'<a class="actbtn pkmap" href="{naver(a)}" data-nmap="{esc(nmap(a))}" '
      f'target="_blank" rel="noopener noreferrer">'
      f'<span class="aico" aria-hidden="true">🗺</span>Naver開啟</a></li>'
      for n, d, hh, a in ps)
    return f'<div class="picks"><div class="pkhead">巷內必吃推薦</div><ul>{rows}</ul></div>'

def metro_btn(it):
    zh = STATION[it["key"]][0]
    if zh not in METRO_ZH:
        return ""
    return (f'<button type="button" class="actbtn tometro" data-station="{esc(zh)}" '
            f'data-stop="stop-{it["key"]}" data-label="{esc(it["n"])}">'
            f'<span class="aico" aria-hidden="true">🚇</span>在地鐵圖查看</button>')

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
            f'<summary><span class="sumico" aria-hidden="true"></span>詳細說明</summary>'
            f'<dl class="infogrid">{"".join(rows)}</dl>'
            f'<div class="stopacts">'
            f'<a class="actbtn navermap" href="{naver(addr)}" data-nmap="{esc(nmap(addr))}" '
            f'target="_blank" rel="noopener noreferrer">'
            f'<span class="aico" aria-hidden="true">🗺</span>Naver開啟</a>'
            f'{metro_btn(it)}</div>'
            f'{subs_html(it)}{picks_html(it)}</details>')

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
            num = it["ord"]
            off = ' offmap' if it.get("offmap") else ''
            sub = ""
            if it.get("sub"):
                sub = ('<span class="sublist">'
                       + "".join(f'<span class="subchip">{esc(x[0])}</span>' for x in it["sub"])
                       + '</span>')
            stn = STATION[it["key"]][0]
            rows.append(
              f'<li class="tr stop{off}" id="stop-{it["key"]}" data-station="{esc(stn)}">'
              f'<span class="tt">{it["t"]}</span>'
              f'<span class="tbody">' + (f'<span class="tnum">{num}</span>' if num else '') +
              f'<span class="tag {it["cat"]}">{CAT[it["cat"]]}</span>'
              f'<span class="tn">{esc(it["n"])}</span>{sub}{info_block(it)}</span></li>')
    sc = sum(1 for it in D["items"] if it["k"] == "stop")
    cards.append(f'''<section class="daycard" id="day{d}" data-day="{d}" style="--c:var(--d{d})">
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
        num = it["ord"] or ""
        extra = ' <span class="lo">（地圖外）</span>' if it.get("offmap") else ''
        zh, _, m = STATION[it["key"]]
        rows.append(f'<li><span class="lnum">{num}</span><span class="ltime">{it["t"]}</span>'
                    f'<span class="tag {it["cat"]}">{CAT[it["cat"]]}</span>'
                    f'<span class="lname">{esc(it["n"])}{extra}'
                    f'<span class="lstn">{esc(zh)}站 · {max(1,round(m/75))}分</span></span></li>')
    leg.append(f'<div class="lgroup" style="--c:var(--d{d})">'
               f'<h3><span class="lbar"></span><span class="lgtitle">DAY {d} · {esc(D["theme"])}</span>'
               f'<a class="daylink" href="index.html#day{d}">看行程 →</a></h3>'
               f'<ul>{"".join(rows)}</ul></div>')
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
