import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import urllib.request
import os

st.set_page_config(page_title="中間チェックシート作成アプリ", layout="wide")
st.title("📋 中間チェックシート自動生成アプリ（カスタム版）")

# 丸ゴシックフォントの取得
FONT_PATH = "rounded-mplus.ttf"
if not os.path.exists(FONT_PATH) or os.path.getsize(FONT_PATH) < 1000:
    font_url = "https://github.com/google/fonts/raw/main/ofl/mplusrounded1c/MPLUSRounded1c-Bold.ttf"
    try:
        urllib.request.urlretrieve(font_url, FONT_PATH)
    except Exception as e:
        st.warning(f"フォント読み込み失敗: {e}")

# --- サイドバー設定 ---
st.sidebar.header("⚙️ 1. 基本テキスト設定")
grade_text = st.sidebar.text_input("学年表記", "小学校3年生")
title_text = st.sidebar.text_input("メインタイトル", "15分ちゅうかんチェック！")
main_question = st.sidebar.text_input("中央の問い", "いまの自分は どんな感じ？")

st.sidebar.markdown("---")
st.sidebar.header("🎨 2. テーマ・パーツ色設定")
show_clock = st.sidebar.checkbox("タイトル時計アイコンを表示", value=True)
clock_size = st.sidebar.slider("時計アイコンサイズ", 15, 50, 25)

default_states = [
    {"label": "【ノリノリ！】", "sub": "(スイスイ描ける)", "color": "#2980B9", "bg": "#EBF5FB", "header_bg": "#AED6F1", "icon": "smile"},
    {"label": "【ちょっとストップ】", "sub": "(ちょっと迷っている)", "color": "#D35400", "bg": "#FEF5E7", "header_bg": "#FAD7A0", "icon": "star"},
    {"label": "【かなりピンチ！】", "sub": "(全然進まない…)", "color": "#C0392B", "bg": "#FDEDEC", "header_bg": "#F9EBEA", "icon": "sad"}
]

columns_data = []
for i in range(3):
    st.sidebar.markdown("---")
    st.sidebar.subheader(f"📌 柱 {i+1} の設定")
    label = st.sidebar.text_input(f"状態見出し {i+1}", default_states[i]["label"], key=f"label_{i}")
    sub = st.sidebar.text_input(f"状態の補足 {i+1}", default_states[i]["sub"], key=f"sub_{i}")
    action1 = st.sidebar.text_input(f"行動案 1 (柱 {i+1})", "「やり方」を変える", key=f"a1_{i}")
    action2 = st.sidebar.text_input(f"行動案 2 (柱 {i+1})", "「ばしょ」を変える", key=f"a2_{i}")
    
    col1, col2, col3 = st.sidebar.columns(3)
    with col1:
        color = st.color_picker(f"メイン色 {i+1}", default_states[i]["color"], key=f"c_{i}")
    with col2:
        header_bg = st.color_picker(f"見出し背景 {i+1}", default_states[i]["header_bg"], key=f"hbg_{i}")
    with col3:
        bg = st.color_picker(f"カード背景 {i+1}", default_states[i]["bg"], key=f"bg_{i}")
        
    show_icon = st.sidebar.checkbox(f"アイコン表示 (柱 {i+1})", value=True, key=f"s_ic_{i}")
    icon_size = st.sidebar.slider(f"アイコンサイズ (柱 {i+1})", 15, 50, 30, key=f"ic_sz_{i}")

    columns_data.append({
        "label": label, "sub": sub, "action1": action1, "action2": action2,
        "color": color, "bg": bg, "header_bg": header_bg, 
        "icon": default_states[i]["icon"], "show_icon": show_icon, "icon_size": icon_size
    })

st.sidebar.markdown("---")
st.sidebar.header("🖼️ 3. 自由イラスト挿入（最大3つ）")

extra_images = []
for idx in range(1, 4):
    up_file = st.sidebar.file_uploader(f"イラスト {idx} (PNG/JPG)", type=["png", "jpg", "jpeg"], key=f"img_{idx}")
    if up_file is not None:
        c1, c2, c3 = st.sidebar.columns(3)
        with c1:
            pos_x = st.slider(f"位置 X #{idx}", 0, 1920, 1600 if idx==1 else 100, key=f"px_{idx}")
        with c2:
            pos_y = st.slider(f"位置 Y #{idx}", 0, 1080, 30 if idx==1 else 800, key=f"py_{idx}")
        with c3:
            img_size = st.slider(f"サイズ #{idx}", 50, 500, 200, key=f"sz_{idx}")
        extra_images.append({"file": up_file, "x": pos_x, "y": pos_y, "size": img_size})

# --- キャンバス描画処理 ---
img = Image.new("RGB", (1920, 1080), "#FAFAFA")
draw = ImageDraw.Draw(img)

try:
    font_title = ImageFont.truetype(FONT_PATH, 52)
    font_large = ImageFont.truetype(FONT_PATH, 38)
    font_mid = ImageFont.truetype(FONT_PATH, 30)
    font_small = ImageFont.truetype(FONT_PATH, 22)
except:
    font_title = font_large = font_mid = font_small = ImageFont.load_default()

def draw_centered_text(draw, bbox, text, font, fill):
    x1, y1, x2, y2 = bbox
    tb = draw.textbbox((0, 0), text, font=font)
    w = tb[2] - tb[0]
    h = tb[3] - tb[1]
    x = x1 + (x2 - x1 - w) / 2
    y = y1 + (y2 - y1 - h) / 2 - tb[1]
    draw.text((x, y), text, font=font, fill=fill)

# 外枠
draw.rounded_rectangle([15, 15, 1905, 1065], radius=20, outline="#34495E", width=8)

# 学年タグ
draw.rounded_rectangle([40, 35, 260, 95], radius=30, fill="#27AE60")
draw_centered_text(draw, [40, 35, 260, 95], grade_text, font_mid, "#FFFFFF")

# タイトルリボン
r_box = [340, 35, 1420, 125]
draw.polygon([(320, 80), (340, 35), (340, 125)], fill="#D4AC0D")
draw.polygon([(1440, 80), (1420, 35), (1420, 125)], fill="#D4AC0D")
draw.rounded_rectangle(r_box, radius=20, fill="#F1C40F", outline="#D4AC0D", width=6)
draw_centered_text(draw, r_box, title_text, font_title, "#7D6608")

# 時計描画
if show_clock:
    cx, cy, r = 1370, 50, clock_size
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill="#FFFFFF", outline="#34495E", width=4)
    draw.line([(cx, cy), (cx, cy-int(r*0.6))], fill="#34495E", width=4)
    draw.line([(cx, cy), (cx+int(r*0.4), cy)], fill="#34495E", width=4)
    draw.line([(cx-int(r*0.7), cy-int(r*0.7)), (cx-int(r*1.1), cy-int(r*1.1))], fill="#34495E", width=3)
    draw.line([(cx+int(r*0.7), cy-int(r*0.7)), (cx+int(r*1.1), cy-int(r*1.1))], fill="#34495E", width=3)

# 中央の問いかけ
q_box = [450, 145, 1470, 215]
draw.rounded_rectangle(q_box, radius=20, fill="#FFFFFF", outline="#34495E", width=5)
draw_centered_text(draw, q_box, main_question, font_large, "#2C3E50")

# 3列レイアウト描画
col_width = 560
start_x = 80
gap = 40

for i, col in enumerate(columns_data):
    x = start_x + i * (col_width + gap)

    # 1. 状態ヘッダー
    h_box = [x, 245, x + col_width, 365]
    draw.rounded_rectangle(h_box, radius=25, fill=col["header_bg"], outline=col["color"], width=6)
    
    # アイコン描画
    if col["show_icon"]:
        ic_x, ic_y = x + 50, 305
        cr = col["icon_size"]
        if col["icon"] == "smile":
            draw.ellipse([ic_x-cr, ic_y-cr, ic_x+cr, ic_y+cr], fill="#F9E79F", outline=col["color"], width=3)
            draw.arc([ic_x-int(cr*0.6), ic_y-int(cr*0.3), ic_x+int(cr*0.6), ic_y+int(cr*0.5)], start=0, end=180, fill=col["color"], width=3)
        elif col["icon"] == "star":
            draw.polygon([(ic_x, ic_y-cr), (ic_x+int(cr*0.3), ic_y-int(cr*0.3)), (ic_x+cr, ic_y-int(cr*0.3)), (ic_x+int(cr*0.4), ic_y+int(cr*0.2)), (ic_x+int(cr*0.6), ic_y+cr), (ic_x, ic_y+int(cr*0.5)), (ic_x-int(cr*0.6), ic_y+cr), (ic_x-int(cr*0.4), ic_y+int(cr*0.2)), (ic_x-cr, ic_y-int(cr*0.3)), (ic_x-int(cr*0.3), ic_y-int(cr*0.3))], fill="#F9E79F", outline=col["color"])
        elif col["icon"] == "sad":
            draw.ellipse([ic_x-cr, ic_y-cr, ic_x+cr, ic_y+cr], fill="#F9E79F", outline=col["color"], width=3)
            draw.arc([ic_x-int(cr*0.6), ic_y+int(cr*0.1), ic_x+int(cr*0.6), ic_y+int(cr*0.8)], start=180, end=360, fill=col["color"], width=3)

    offset_l = 80 if col["show_icon"] else 20
    draw_centered_text(draw, [x + offset_l, 250, x + col_width, 310], col["label"], font_large, col["color"])
    draw_centered_text(draw, [x + offset_l, 310, x + col_width, 355], col["sub"], font_small, "#5D6D7E")

    # 矢印 (↓)
    arrow_x = x + col_width // 2
    draw.polygon([(arrow_x - 20, 375), (arrow_x + 20, 375), (arrow_x, 405)], fill=col["color"])

    # 2. 変えよう見出し
    c_box = [x, 415, x + col_width, 475]
    draw.rounded_rectangle(c_box, radius=20, fill="#FFFFFF", outline=col["color"], width=5)
    draw_centered_text(draw, c_box, "【こうやって変えよう】", font_mid, col["color"])

    # 矢印 (↓)
    draw.polygon([(arrow_x - 20, 485), (arrow_x + 20, 485), (arrow_x, 510)], fill=col["color"])

    # 3. 行動選択肢 1
    a1_box = [x, 525, x + col_width, 765]
    draw.rounded_rectangle(a1_box, radius=20, fill=col["bg"], outline="#BDC3C7", width=4)
    draw_centered_text(draw, a1_box, f"• {col['action1']}", font_mid, "#2C3E50")

    # 4. 行動選択肢 2
    a2_box = [x, 785, x + col_width, 1025]
    draw.rounded_rectangle(a2_box, radius=20, fill=col["bg"], outline="#BDC3C7", width=4)
    draw_centered_text(draw, a2_box, f"• {col['action2']}", font_mid, "#2C3E50")

# アップロード画像の合成（自由位置・自由サイズ）
for item in extra_images:
    try:
        user_img = Image.open(item["file"]).convert("RGBA")
        # アスペクト比を維持してリサイズ
        user_img.thumbnail((item["size"], item["size"]))
        img.paste(user_img, (item["x"], item["y"]), user_img)
    except Exception as e:
        st.warning(f"画像合成エラー: {e}")

# アプリ画面に描画
st.image(img, use_container_width=True)

buf = io.BytesIO()
img.save(buf, format="PNG")
st.download_button(label="📥 チェックシート画像(PNG)をダウンロード", data=buf.getvalue(), file_name="custom_checklist.png", mime="image/png")
