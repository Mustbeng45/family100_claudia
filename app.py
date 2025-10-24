import json
import streamlit as st
from typing import List, Dict, Any
import time

st.set_page_config(page_title="Famili 100 – Ulang Tahun Claudia", layout="wide")

# ----------------- STATE -----------------
def init_state():
    defaults = {
        "q_index": 0,
        "revealed": set(),
        "questions": [],
        "trigger": None,
        "last_revealed": None,
        "popup_time": 0
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def current_question():
    if not st.session_state["questions"]:
        return {}
    return st.session_state["questions"][st.session_state["q_index"]]


def next_question():
    if st.session_state["q_index"] < len(st.session_state["questions"]) - 1:
        st.session_state["q_index"] += 1
        st.session_state["revealed"].clear()
        st.session_state["trigger"] = None
        st.session_state["last_revealed"] = None


def prev_question():
    if st.session_state["q_index"] > 0:
        st.session_state["q_index"] -= 1
        st.session_state["revealed"].clear()
        st.session_state["trigger"] = None
        st.session_state["last_revealed"] = None


def reveal_answer(index: int):
    st.session_state["revealed"].add(index)


# ----------------- INIT -----------------
init_state()

# ----------------- LOAD QUESTIONS -----------------
try:
    with open("questions_claudia.json", "r", encoding="utf-8") as f:
        qs = json.load(f)
except FileNotFoundError:
    qs = []
if not st.session_state["questions"]:
    st.session_state["questions"] = qs


# ----------------- UI -----------------
st.title("🎉 Famili 100: Ulang Tahun Claudia")
st.caption("Versi lengkap: highlight, popup, dan tombol tampilkan jawaban 💚💥")

q = current_question()
if not q:
    st.info("Belum ada pertanyaan.")
    st.stop()

col_left, col_right = st.columns([1, 2])

# ----------------- KIRI: FORM -----------------
with col_left:
    st.header("🧠 Tebak Jawaban")
    st.markdown(f"**Pertanyaan {st.session_state['q_index']+1}/{len(st.session_state['questions'])}:**")
    st.markdown(f"### {q['question']}")

    with st.form("guess_form", clear_on_submit=True):
        g = st.text_input("Ketik jawabanmu di sini:")
        s = st.form_submit_button("💬 Kirim Jawaban")

    if s and g:
        st.session_state["trigger"] = None
        found = False
        for i, a in enumerate(q["answers"]):
            if g.strip().lower() == a["text"].lower():
                if i not in st.session_state["revealed"]:
                    st.session_state["revealed"].add(i)
                    st.session_state["last_revealed"] = i
                    st.session_state["trigger"] = "correct"
                    st.success(f"✅ Benar! {a['text']} ({a['points']} poin)")
                found = True
                break
        if not found:
            st.session_state["trigger"] = "wrong"
            st.session_state["popup_time"] = time.time()
            st.warning("❌ Jawaban salah!")

    st.divider()
    left, right = st.columns(2)
    with left:
        if st.button("⬅️ Sebelumnya"):
            prev_question()
            st.rerun()
    with right:
        if st.button("Berikutnya ➡️"):
            next_question()
            st.rerun()

# ----------------- KANAN: GRID JAWABAN -----------------
with col_right:
    st.markdown("### 🔍 Jawaban:")
    answers = q.get("answers", [])
    grid_cols = 2
    rows = (len(answers) + grid_cols - 1) // grid_cols

    for r in range(rows):
        cols = st.columns(grid_cols)
        for c_idx, c in enumerate(cols):
            idx = r * grid_cols + c_idx
            if idx < len(answers):
                ans = answers[idx]
                is_revealed = idx in st.session_state["revealed"]
                is_new = idx == st.session_state["last_revealed"]

                border = "limegreen" if is_revealed else "#ccc"
                bg = "#b6ffb3" if is_revealed else "#f9f9f9"
                text_color = "black" if is_revealed else "#333"
                extra_effect = (
                    "box-shadow: 0 0 60px 20px limegreen; animation: pulse 1.2s ease-in-out;"
                    if is_new else ""
                )

                with c:
                    st.markdown(f"""
                    <div style="
                        border: 3px solid {border};
                        border-radius: 14px;
                        padding: 14px;
                        text-align: center;
                        background-color: {bg};
                        color: {text_color};
                        font-weight: bold;
                        transition: all 0.3s ease;
                        {extra_effect}
                    ">
                        <h3>#{idx + 1}</h3>
                        {"<h2>" + ans['text'] + " — <b>" + str(ans['points']) + " poin</b></h2>" if is_revealed else "<h2 style='color:#888;'>❌ Belum Terbuka</h2>"}
                    </div>
                    <style>
                    @keyframes pulse {{
                        0% {{transform: scale(1); box-shadow: 0 0 0 0 limegreen;}}
                        50% {{transform: scale(1.08); box-shadow: 0 0 70px 25px limegreen;}}
                        100% {{transform: scale(1); box-shadow: 0 0 0 0 limegreen;}}
                    }}
                    </style>
                    """, unsafe_allow_html=True)

                    # Tombol tampilkan satu per satu
                    if not is_revealed:
                        if st.button(f"👀 Tampilkan #{idx + 1}", key=f"show_{idx}"):
                            reveal_answer(idx)
                            st.rerun()

# ----------------- POPUP SALAH -----------------
def popup_salah():
    st.markdown("""
    <div id="popup-wrong" class="shake" style="
        position: fixed;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        background: rgba(255,0,0,0.35);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        animation: fadeZoom 2s ease-out forwards;">
        <h1 style="
            font-size: 180px;
            color: #ff0000;
            text-shadow: 0 0 40px white, 0 0 80px red;
            font-weight: 900;
            font-family: 'Arial Black', sans-serif;
        ">SALAH!!! 💥</h1>
    </div>
    <style>
    @keyframes fadeZoom {{
      0% {{opacity:0; transform: scale(0.5);}}
      30% {{opacity:1; transform: scale(1.1);}}
      80% {{opacity:1; transform: scale(1);}}
      100% {{opacity:0; transform: scale(1.3);}}
    }}
    @keyframes shake {{
      0%,100%{{transform:translate(0,0);}}
      20%{{transform:translate(-15px,0);}}
      40%{{transform:translate(15px,0);}}
      60%{{transform:translate(-15px,0);}}
      80%{{transform:translate(15px,0);}}
    }}
    .shake {{
      animation: fadeZoom 2s ease-out forwards, shake 0.6s ease-in-out infinite;
    }}
    </style>
    """, unsafe_allow_html=True)


if st.session_state["trigger"] == "wrong":
    popup_salah()
    st.session_state["trigger"] = None

st.caption("Made with ❤️ untuk ulang tahun Claudia — versi lengkap dengan tombol tampilkan jawaban 💚💥")
