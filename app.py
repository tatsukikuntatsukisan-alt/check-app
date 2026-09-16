import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import urllib.request
import os

st.set_page_config(page_title="中間チェックシート作成アプリ", layout="wide")
st.title("📋 中間チェックシート自動生成アプリ")

# 手書き風・丸ゴシック（Rounded Mplus）の自動ダウンロード
FONT_PATH = "rounded-mplus.ttf"
if not os.path.exists(FONT_PATH) or os.path.getsize(FONT_PATH) < 1000:
    font_url = "https://github.com/google/fonts/raw/main/ofl/mplusrounded1c/MPLUSRounded1c-Bold.ttf"
    try:
        urllib.request.urlretrieve(font_url, FONT_PATH)
    except Exception as e:
        st.warning(f"フォント読み込み失敗: {e}")

# サイドバー設定
st.sidebar.header("⚙️ シート設定")
grade_text = st.sidebar.text_input("学年表記", "小学校3年生")
title_time = st.sidebar.text_input("時間設定（分）", "15")
main_question = st.sidebar.text_input("中央の問い", "いまの自分は どんな感じ？")

columns_data = []
default_states = [
    {"label": "【ノリノリ！】", "sub": "(スイスイ描ける)", "color": "#2980B9", "bg": "#EBF5FB", "header_bg": "#AED6F1"},
    {"label": "【ちょっとストップ】", "sub": "(ちょっと迷っている)", "color": "#D35400", "bg": "#FEF5E7", "header_bg": "#FAD7A0"},
    {"label": "【かなりピンチ！】", "sub": "(全然進まない…)", "color": "#C0392B", "bg": "#FDEDEC", "header_bg": "#F9EBEA"}
]

for i in range(3):
    st.sidebar.markdown("---")
    st.sidebar.subheader(f"柱 {i+1}")
    label = st.sidebar.text_input(f"状態見出し {i+1}", default_states[i]["label"], key=f"label_{i}")
    sub = st.sidebar.text_input(f"状態の補足 {i+1}", default_states[i]["sub"], key=f"sub_{i}")
    action1 = st.sidebar.text_input(f"行動案 1 (柱 {i+1})", "「やり方」を変える", key=f"a1_{i}")
    action2 = st.sidebar.text_input(f"行動案 2 (柱 {i+1})", "「ばしょ」を変える", key=f"a2_{i}")
    columns_data.append({
        "label": label, "sub": sub, "action1": action1, "action2": action2,
        "color": default_states[i]["color"], "bg": default_states[i]["bg"], "header_bg": default_states[i]["header_bg"]
    })

# キャンバス準備
img = Image.new("RGB", (1920, 1080), "#FAFAFA")
draw = ImageDraw.Draw(img)

# フォントサイズ設定
try:
    font_title = ImageFont.truetype(FONT_PATH, 55)
    font_large = ImageFont.truetype(FONT_PATH, 42)
    font_mid = ImageFont.truetype(FONT_PATH, 32)
    font_small = ImageFont.truetype(FONT_PATH, 24)
except:
    font_title = font_large = font_mid = font_small = ImageFont.load_default()

# 外枠フレーム（二重枠風）
draw.rounded_rectangle([15, 15, 1905, 1065], radius=20, outline="#34495E", width=8)

# 学年タグ
draw.rounded_rectangle([40, 35, 300, 95], radius=30, fill="#27AE60")
draw.text((65, 45), grade_text, fill="#FFFFFF", font=font_mid)

# タイトルリボン
draw.rounded_rectangle([380, 35, 1540, 125], radius=25, fill="#F1C40F", outline="#D4AC0D", width=6)
draw.text((430, 48), f"⏰ {title_time}分ちゅうかんチェック！", fill="#7D6608", font=font_title)

# 中央の問いかけ吹き出し
draw.rounded_rectangle([520, 145, 1400, 215], radius=20, fill="#FFFFFF", outline="#34495E", width=5)
draw.text((560, 155), main_question, fill="#2C3E50", font=font_large)

# 3列分岐レイアウト
col_width = 560
start_x = 80
gap = 40

for i, col in enumerate(columns_data):
    x = start_x + i * (col_width + gap)

    # 1. 状態カード
    draw.rounded_rectangle([x, 245, x + col_width, 365], radius=25, fill=col["header_bg"], outline=col["color"], width=6)
    draw.text((x + 25, 260), col["label"], fill=col["color"], font=font_large)
    draw.text((x + 30, 318), col["sub"], fill="#5D6D7E", font=font_small)

    # 矢印描画 (↓)
    arrow_x = x + col_width // 2
    draw.polygon([(arrow_x - 18, 375), (arrow_x + 18, 375), (arrow_x, 405)], fill=col["color"])

    # 2. 変えよう見出し
    draw.rounded_rectangle([x, 415, x + col_width, 475], radius=20, fill="#FFFFFF", outline=col["color"], width=5)
    draw.text((x + 120, 425), "【こうやって変えよう】", fill=col["color"], font=font_mid)

    # 矢印描画 (↓)
    draw.polygon([(arrow_x - 18, 485), (arrow_x + 18, 485), (arrow_x, 510)], fill=col["color"])

    # 3. 行動選択肢 1
    draw.rounded_rectangle([x, 525, x + col_width, 765], radius=20, fill=col["bg"], outline="#BDC3C7", width=4)
    draw.text((x + 25, 545), f"• {col['action1']}", fill="#2C3E50", font=font_mid)

    # 4. 行動選択肢 2
    draw.rounded_rectangle([x, 785, x + col_width, 1025], radius=20, fill=col["bg"], outline="#BDC3C7", width=4)
    draw.text((x + 25, 805), f"• {col['action2']}", fill="#2C3E50", font=font_mid)

# アプリ画面への表示と保存
st.image(img, use_container_width=True)
buf = io.BytesIO()
img.save(buf, format="PNG")
st.download_button(label="📥 チェックシート画像(PNG)を保存", data=buf.getvalue(), file_name="cute_checklist.png", mime="image/png")
