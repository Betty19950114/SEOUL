# -*- coding: utf-8 -*-
"""依行程整理的韓文常用句，供現場出示給店員看。"""
import html
def esc(s): return html.escape(str(s), quote=True)

# (中文, 韓文, 羅馬拼音, 備註)
SECTIONS = [
 ("點餐・用餐", "food", [
   ("兩位", "두 명이요", "du myeong-i-yo", "進店時先講這句"),
   ("請給我這個（指菜單）", "이거 주세요", "i-geo ju-se-yo", "配合手指最好用"),
   ("兩人份", "2인분 주세요", "i-in-bun ju-se-yo", ""),
   ("要等多久？", "얼마나 기다려야 돼요?", "eol-ma-na gi-da-ryeo-ya dwae-yo?", "熱門店先問再決定排不排"),
   ("可以先候位嗎？", "웨이팅 걸어도 돼요?", "we-i-ting geo-reo-do dwae-yo?", "웨이팅＝候位，韓國店家常用"),
   ("可以坐這裡嗎？", "여기 앉아도 돼요?", "yeo-gi an-ja-do dwae-yo?", ""),
   ("請不要太辣", "덜 맵게 해주세요", "deol maep-ge hae-ju-se-yo", "獵奇辣炒年糕必備"),
   ("完全不要辣", "안 맵게 해주세요", "an maep-ge hae-ju-se-yo", ""),
   ("哪一個最好吃？", "뭐가 제일 맛있어요?", "mwo-ga je-il ma-si-sseo-yo?", ""),
   ("請幫我打包", "포장해 주세요", "po-jang-hae ju-se-yo", ""),
   ("請結帳", "계산해 주세요", "gye-san-hae ju-se-yo", ""),
   ("可以刷卡嗎？", "카드 되나요?", "ka-deu doe-na-yo?", ""),
   ("可以分開結帳嗎？", "따로 계산해 주세요", "tta-ro gye-san-hae ju-se-yo", "兩人各付各的"),
   ("這裡只收現金嗎？", "현금만 받아요?", "hyeon-geum-man ba-da-yo?", "市場攤販常見"),
   ("請再給我一份小菜", "반찬 좀 더 주세요", "ban-chan jom deo ju-se-yo", "小菜通常可免費續"),
   ("請給我水", "물 좀 주세요", "mul jom ju-se-yo", ""),
   ("我對○○過敏", "저는 ○○ 알레르기가 있어요", "jeo-neun ○○ al-le-reu-gi-ga i-sseo-yo", "海鮮 해산물／花生 땅콩／蛋 계란"),
   # ── 點咖啡 ──
   ("冰美式兩杯", "아이스 아메리카노 두 잔이요", "a-i-seu a-me-ri-ka-no du jan-i-yo", "「아아」是韓國人的簡稱，直接講也通"),
   ("熱拿鐵一杯", "따뜻한 라떼 한 잔이요", "tta-tteu-tan la-tte han jan-i-yo", "熱 따뜻한／冰 아이스"),
   ("大杯的", "큰 사이즈로 주세요", "keun sa-i-jeu-ro ju-se-yo", "韓國多用 톨／그란데，講 큰 거 也通"),
   ("內用", "먹고 갈게요", "meok-go gal-ge-yo", "點餐時店員第一句多半問這個"),
   ("外帶", "테이크아웃이요", "te-i-keu-a-u-si-yo", "或講 가지고 갈게요"),
   ("請少冰", "얼음 조금만 넣어주세요", "eo-reum jo-geum-man neo-eo-ju-se-yo", ""),
   ("請去冰", "얼음 빼주세요", "eo-reum ppae-ju-se-yo", ""),
   ("請少糖", "덜 달게 해주세요", "deol dal-ge hae-ju-se-yo", "糖漿 시럽 也可單獨說 시럽 빼주세요"),
   ("換成燕麥奶", "오트밀크로 바꿔주세요", "o-teu-mil-keu-ro ba-kkwo-ju-se-yo", "豆奶 두유"),
   ("有推薦的嗎？", "추천 메뉴 있어요?", "chu-cheon me-nyu i-sseo-yo?", ""),
   ("有內用座位嗎？", "매장에 자리 있어요?", "mae-jang-e ja-ri i-sseo-yo?", "弘大、聖水的咖啡廳常客滿"),
   ("可以幫我裝紙袋嗎？", "종이봉투에 담아주세요", "jong-i-bong-tu-e da-ma-ju-se-yo", ""),
 ]),
 ("購物", "shop", [
   ("多少錢？", "얼마예요?", "eol-ma-ye-yo?", ""),
   ("可以試穿嗎？", "입어봐도 돼요?", "i-beo-bwa-do dwae-yo?", ""),
   ("有大一號的嗎？", "한 사이즈 큰 거 있어요?", "han sa-i-jeu keun geo i-sseo-yo?", "小一號是 작은 거"),
   ("有其他顏色嗎？", "다른 색 있어요?", "da-reun saek i-sseo-yo?", ""),
   ("可以退稅嗎？", "택스 리펀 되나요?", "taek-seu ri-peon doe-na-yo?", "單店滿 ₩15,000 多可辦"),
   ("請分開包裝", "따로 포장해 주세요", "tta-ro po-jang-hae ju-se-yo", "買伴手禮很好用"),
   ("我再看看", "좀 더 볼게요", "jom deo bol-ge-yo", "婉拒推銷"),
   ("這個有貨嗎？", "이거 재고 있어요?", "i-geo jae-go i-sseo-yo?", ""),
 ]),
 ("交通", "transit", [
   ("請問這裡怎麼去？", "여기 어떻게 가요?", "yeo-gi eo-tteo-ke ga-yo?", "拿手機地圖指給對方看"),
   ("請載我到這個地址", "이 주소로 가주세요", "i ju-so-ro ga-ju-se-yo", "計程車出示地址畫面"),
   ("請在這裡停", "여기서 세워 주세요", "yeo-gi-seo se-wo ju-se-yo", ""),
   ("這班車有到○○嗎？", "이거 ○○ 가나요?", "i-geo ○○ ga-na-yo?", ""),
   ("幾號出口？", "몇 번 출구예요?", "myeot beon chul-gu-ye-yo?", ""),
   ("要坐幾站？", "몇 정거장 가야 돼요?", "myeot jeong-geo-jang ga-ya dwae-yo?", ""),
   ("這張卡可以加值嗎？", "이 카드 충전 돼요?", "i ka-deu chung-jeon dwae-yo?", "T-money 加值"),
 ]),
 ("住宿", "stay", [
   ("我要辦入住", "체크인 할게요", "che-keu-in hal-ge-yo", ""),
   ("我要退房", "체크아웃 할게요", "che-keu-a-ut hal-ge-yo", ""),
   ("可以寄放行李嗎？", "짐 좀 맡길 수 있을까요?", "jim jom mat-gil su i-sseul-kka-yo?", "第五天早上必用"),
   ("我來拿行李", "짐 찾으러 왔어요", "jim cha-jeu-reo wa-sseo-yo", ""),
 ]),
 ("這趟行程專用", "trip", [
   ("請給我兩張自由券", "자유이용권 두 장 주세요", "ja-yu-i-yong-gwon du jang ju-se-yo", "愛寶樂園售票口"),
   ("接駁巴士在哪裡搭？", "셔틀버스 어디서 타요?", "syeo-teul-beo-seu eo-di-seo ta-yo?", "愛寶樂園往返必問"),
   ("請給我兩人份的辣燉白帶魚", "갈치조림 2인분 주세요", "gal-chi-jo-rim i-in-bun ju-se-yo", "南大門갈치조림골목"),
   ("一隻雞一份，加刀削麵", "닭한마리 하나랑 칼국수 사리 주세요", "dak-han-ma-ri ha-na-rang kal-guk-su sa-ri ju-se-yo", "陳玉華必點吃法"),
   ("最後請幫我炒飯", "마지막에 볶음밥 해주세요", "ma-ji-ma-ge bo-kkeum-bap hae-ju-se-yo", "一隻雞收尾"),
   ("今天噴泉幾點？", "오늘 분수 몇 시예요?", "o-neul bun-su myeot si-ye-yo?", "盤浦大橋"),
   ("今天有營業嗎？", "오늘 영업해요?", "o-neul yeong-eop-hae-yo?", "週日或公休日先問"),
 ]),
 ("狀況題", "help", [
   ("我迷路了", "길을 잃었어요", "gi-reul i-reo-sseo-yo", ""),
   ("我的東西掉了", "물건을 잃어버렸어요", "mul-geo-neul i-reo-beo-ryeo-sseo-yo", ""),
   ("我不太舒服", "몸이 좀 안 좋아요", "mo-mi jom an jo-a-yo", ""),
   ("附近有藥局嗎？", "근처에 약국 있어요?", "geun-cheo-e yak-guk i-sseo-yo?", ""),
   ("請幫我叫救護車", "구급차 좀 불러 주세요", "gu-geup-cha jom bul-leo ju-se-yo", "緊急電話 119"),
   ("可以借充電嗎？", "충전 좀 해도 될까요?", "chung-jeon jom hae-do doel-kka-yo?", ""),
 ]),
]

blocks = []
for title, sid, rows in SECTIONS:
    items = "".join(
      f'<li class="ph" tabindex="0" role="button" data-ko="{esc(ko)}" data-zh="{esc(zh)}">'
      f'<span class="ph-zh">{esc(zh)}</span>'
      f'<span class="ph-ko">{esc(ko)}</span>'
      f'<span class="ph-ro">{esc(ro)}</span>'
      + (f'<span class="ph-note">{esc(note)}</span>' if note else "")
      + '</li>'
      for zh, ko, ro, note in rows)
    blocks.append(f'<section class="phsec" id="ph-{sid}">'
                  f'<h2>{esc(title)}<span class="phn">{len(rows)}</span></h2>'
                  f'<ul class="phlist">{items}</ul></section>')

nav = "".join(f'<a class="phnav" href="#ph-{sid}">{esc(t)}</a>' for t, sid, _ in SECTIONS)
open("frag_phrases.html.txt", "w", encoding="utf-8").write(
    f'<div class="phnavbar">{nav}</div>' + "".join(blocks))
print("phrases:", sum(len(r) for _, _, r in SECTIONS), "句 /", len(SECTIONS), "類")
