# 產生器

行程頁由這裡的腳本產生，**請勿直接編輯根目錄的 index.html / map.html**。

```bash
cd build && python3 build.py && python3 assemble.py
```

- `data.py`　行程內容、地點座標、地鐵站資料、地鐵圖線路
- `build.py`　產生地圖 SVG、地鐵圖、每日卡片、圖例、快速尋找片段
- `assemble.py`　把片段與字型／圖片素材組進 `../index.html`、`../map.html`
- `tpl_*.html` `base.css` `map_extra.css`　版型與樣式
- `*.b64` `img_b64.json`　內嵌字型與圖片（勿刪）

`shopping.html` 目前為獨立靜態檔，未納入此流程。
