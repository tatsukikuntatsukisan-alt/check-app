import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="中間チェックシート作成アプリ", layout="wide")
st.title("📋 中間チェックシート自動生成アプリ")

# サイドバー設定
st.sidebar.header("⚙️ シート設定")
grade_text = st.sidebar.text_input("学年表記", "小学校3年生")
title_time = st.sidebar.text_input("時間設定（分）", "15")
main_question = st.sidebar.text_input("中央の問い", "いまの自分は どんな感じ？")

columns_data = []
default_states = [
    {"label": "【ノリノリ！】", "sub": "(スイスイ描ける)", "color": "#4A90E2", "bg": "#EBF3FA"},
    {"label": "【ちょっとストップ】", "sub": "(ちょっと迷っている)", "color": "#E67E22", "bg": "#FDF2E9"},
    {"label": "【かなりピンチ！】", "sub": "(全然進まない…)", "color": "#E74C3C", "bg": "#FDEDEC"}
]

for i in range(3):
    st.sidebar.markdown("---")
    st.sidebar.subheader(f"柱 {i+1}")
    label = st.sidebar.text_input(f"状態見出し {i+1}", default_states[i]["label"], key=f"label_{i}")
    sub = st.sidebar.text_input(f"状態の補足 {i+1}", default_states[i]["sub"], key=f"sub_{i}")
    action1 = st.sidebar.text_input(f"行動案 1 (柱 {i+1})", "行動パターン 1", key=f"a1_{i}")
    action2 = st.sidebar.text_input(f"行動案 2 (柱 {i+1})", "行動パターン 2", key=f"a2_{i}")
    columns_data.append({"label": label, "sub": sub, "action1": action1, "action2": action2, "color": default_states[i]["color"], "bg": default_states[i]["bg"]})

# 画像生成処理
img = Image.new("RGB", (1920, 1080), "#FFFFFF")
draw = ImageDraw.Draw(img)
font_large = font_mid = font_small = ImageFont.load_default()

draw.rectangle([20, 20, 1900, 1060], outline="#4A5568", width=12)
draw.text((60, 50), grade_text, fill="#333333", font=font_mid)
draw.rectangle([400, 40, 1520, 120], fill="#FEF9E7", outline="#F1C40F", width=6)
draw.text((450, 50), f"{title_time}分ちゅうかんチェック！", fill="#D35400", font=font_large)
draw.rectangle([550, 140, 1370, 200], fill="#FFFFFF", outline="#333333", width=4)
draw.text((580, 148), main_question, fill="#2C3E50", font=font_mid)

col_width = 560
start_x = 80
gap = 40
for i, col in enumerate(columns_data):
    x = start_x + i * (col_width + gap)
    draw.rectangle([x, 240, x + col_width, 360], fill=col["bg"], outline=col["color"], width=5)
    draw.text((x + 20, 255), col["label"], fill=col["color"], font=font_mid)
    draw.text((x + 20, 310), col["sub"], fill="#555555", font=font_small)
    arrow_x = x + col_width // 2
    draw.line([(arrow_x, 370), (arrow_x, 410)], fill="#7F8C8D", width=6)
    draw.rectangle([x, 420, x + col_width, 480], fill="#FFFFFF", outline=col["color"], width=4)
    draw.text((x + 100, 430), "【こうやって変えよう】", fill=col["color"], font=font_small)
    draw.rectangle([x, 500, x + col_width, 740], fill="#FAFAFA", outline="#BDC3C7", width=3)
    draw.text((x + 20, 520), f"• {col['action1']}", fill="#2C3E50", font=font_mid)
    draw.rectangle([x, 760, x + col_width, 1000], fill="#FAFAFA", outline="#BDC3C7", width=3)
    draw.text((x + 20, 780), f"• {col['action2']}", fill="#2C3E50", font=font_mid)

# エラー箇所を修正した表示
st.image(img, use_container_width=True)
buf = io.BytesIO()
img.save(buf, format="PNG")
st.download_button(label="📥 画像をダウンロード", data=buf.getvalue(), file_name="checklist.png", mime="image/png")
