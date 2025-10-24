import json
import streamlit as st
import time

st.set_page_config(page_title="Famili 100 – Ulang Tahun Claudia", layout="wide")

# ----------------- STATE -----------------
def init_state():
    defaults = {
        "q_index": 0,
        "revealed": set(),
        "questions": [],
        "last_revealed": None,
        "highlight_start": None
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
        st.session_state["last_revealed"] = None
        st.session_state["highlight_start"] = None

def prev_question():
    if st.session_state["q_index"] > 0:
        st.session_state["q_index"] -= 1
        st.session_state["revealed"].clear()
        st.session_state["last_revealed"] = None
        st.session_state["highlight_start"] = None

def reveal_answer(idx: int):
    st.session_state["revealed"].add(idx)
    st.session_state["last_revealed"] = idx
    st.session_state["highlight_start"] = time.time()

# ----------------- INIT & LOAD -----------------
init_state()

try:
    with open("questions_claudia.json", "r", encoding="utf-8") as f:
        qs = json.load(f)
except FileNotFoundError:
    qs = []
if not st.session_state["questions"]:
    st.session_state["questions"] = qs

# ----------------- UI -----------------
st.title("🎉 Famili 100: Ulang Tahun Claudia")
st.caption("Versi tanpa popup, highlight BENAR 2 detik 💚")

q = current_question()
if not q:
    st.info("Belum ada pertanyaan.")
    st.stop()

left, right = st.columns([1, 2])

# ----------------- KIRI: FORM -----------------
with left:
    st.header("🧠 Tebak Jawaban")
    st.markdown(f"**Pertanyaan {st.session_state['q_index']+1}/{len(st.session_state['questions'])}:**")
    st.markdown(f"### {q['question']}")

    with st.form("guess_form", clear_on_submit=True):
        guess = st.text_input("Ketik jawabanmu di sini:")
        submit = st.form_submit_button("💬 Kirim Jawaban")

    if submit and guess:
        guess_norm = guess.strip().lower()
        found = False
        for i, a in enumerate(q["answers"]):
            if guess_norm == a["text"].lower():
                reveal_answer(i)
                st.success(f"✅ Benar! {a['text']} ({a['points']} poin)")
                found = True
                break
        if not found:
            st.info("❌ Belum tepat, coba lagi!")

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ Sebelumnya"):
            prev_question()
            st.rerun()
    with c2:
        if st.button("Berikutnya ➡️"):
            next_question()
            st.rerun()

# ----------------- KANAN: GRID JAWABAN -----------------
with right:
    st.markdown("### 🔍 Jawaban:")
    answers = q.get("answers", [])
    grid_cols = 2
    rows = (len(answers) + grid_cols - 1) // grid_cols

    now = time.time()
    HILIGHT_SEC = 2.0

    if st.session_state["highlight_start"] is not None:
        elapsed = now - st.session_state["highlight_start"]
        remaining_ms = int(max(50, (HILIGHT_SEC - elapsed) * 1000))
        if elapsed < HILIGHT_SEC:
            st.markdown(
                f"""<script>
                    setTimeout(function() {{
                        if (window?.location) window.location.reload();
                    }}, {remaining_ms});
                </script>""",
                unsafe_allow_html=True,
            )
        else:
            st.session_state["last_revealed"] = None
            st.session_state["highlight_start"] = None

    for r in range(rows):
        cols = st.columns(grid_cols)
        for c_idx, c in enumerate(cols):
            idx = r * grid_cols + c_idx
            if idx >= len(answers): continue

            ans = answers[idx]
            is_open = idx in st.session_state["revealed"]
            is_highlight = (
                st.session_state["last_revealed"] == idx and
                st.session_state["highlight_start"] and
                now - st.session_state["highlight_start"] < HILIGHT_SEC
            )

            border = "limegreen" if is_highlight else "#ccc"
            bg = "#b6ffb3" if is_highlight else "#f9f9f9"
            text_color = "black" if is_highlight else "#333"
            glow = (
                "box-shadow: 0 0 60px 22px rgba(50,205,50,0.9); animation: pulse 1.2s ease-in-out;"
                if is_highlight else ""
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
                    {glow}
                ">
                    <h3>#{idx + 1}</h3>
                    {"<h2>" + ans['text'] + " — <b>" + str(ans['points']) + " poin</b></h2>" if is_open else "<h2 style='color:#888;'>❌ Belum Terbuka</h2>"}
                </div>
                <style>
                @keyframes pulse {{
                    0%   {{ transform: scale(1);   box-shadow: 0 0 0 0 rgba(50,205,50,0.0); }}
                    50%  {{ transform: scale(1.05); box-shadow: 0 0 70px 25px rgba(50,205,50,0.9); }}
                    100% {{ transform: scale(1);   box-shadow: 0 0 0 0 rgba(50,205,50,0.0); }}
                }}
                </style>
                """, unsafe_allow_html=True)

                if not is_open:
                    if st.button(f"👀 Tampilkan #{idx + 1}", key=f"show_{idx}"):
                        reveal_answer(idx)
                        st.rerun()

st.caption("Made with ❤️ untuk ulang tahun Claudia — tanpa popup, highlight 2 detik 💚")
