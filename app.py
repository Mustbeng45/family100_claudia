import json
import streamlit as st
import time

st.set_page_config(page_title="Famili 100 – Ulang Tahun Claudia", layout="wide")

# ----------------- STATE -----------------
def init_state():
    defaults = {
        "q_index": 0,
        "revealed": set(),          # indeks jawaban yang sudah terbuka (tetap terbuka)
        "questions": [],
        "trigger": None,            # "wrong" | None
        "last_revealed": None,      # indeks jawaban yang baru benar
        "highlight_start": None,    # timestamp mulai highlight 2 detik
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
        st.session_state["highlight_start"] = None

def prev_question():
    if st.session_state["q_index"] > 0:
        st.session_state["q_index"] -= 1
        st.session_state["revealed"].clear()
        st.session_state["trigger"] = None
        st.session_state["last_revealed"] = None
        st.session_state["highlight_start"] = None

def reveal_answer(idx: int):
    st.session_state["revealed"].add(idx)            # permanen terbuka
    st.session_state["last_revealed"] = idx          # ini yang akan di-highlight 2 detik
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
st.caption("Highlight BENAR hanya 2 detik + popup SALAH auto-hilang")

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
        st.session_state["trigger"] = None
        found = False
        for i, a in enumerate(q["answers"]):
            if guess_norm == a["text"].lower():
                if i not in st.session_state["revealed"]:
                    reveal_answer(i)
                    st.success(f"✅ Benar! {a['text']} ({a['points']} poin)")
                else:
                    # sudah terbuka, tapi tetap kasih sedikit feedback
                    st.info(f"Sudah terbuka: {a['text']}")
                found = True
                break
        if not found:
            st.session_state["trigger"] = "wrong"
            st.warning("❌ Jawaban salah!")

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

    # sisipkan auto-refresh sekali jika highlight masih aktif
    if (
        st.session_state["last_revealed"] is not None
        and st.session_state["highlight_start"] is not None
    ):
        elapsed = now - st.session_state["highlight_start"]
        remaining_ms = int(max(50, (HILIGHT_SEC - elapsed) * 1000))
        if elapsed < HILIGHT_SEC:
            # reload sekali saat highlight selesai, supaya tampilan kembali normal
            st.markdown(
                f"""<script>
                    setTimeout(function() {{
                        if (window?.location) window.location.reload();
                    }}, {remaining_ms});
                </script>""",
                unsafe_allow_html=True,
            )
        else:
            # matikan flag highlight (jawaban tetap terbuka)
            st.session_state["last_revealed"] = None
            st.session_state["highlight_start"] = None

    for r in range(rows):
        cols = st.columns(grid_cols)
        for c_idx, c in enumerate(cols):
            idx = r * grid_cols + c_idx
            if idx >= len(answers):
                continue

            ans = answers[idx]
            is_open = idx in st.session_state["revealed"]
            is_new = (
                is_open
                and st.session_state["last_revealed"] == idx
                and st.session_state["highlight_start"] is not None
                and (now - st.session_state["highlight_start"]) < HILIGHT_SEC
            )

            # style: default abu-abu; saat baru benar -> nyala hijau + glow
            border = "limegreen" if is_new else "#ccc"
            bg = "#b6ffb3" if is_new else "#f9f9f9"
            text_color = "black" if is_new else "#333"
            glow = (
                "box-shadow: 0 0 60px 22px rgba(50,205,50,0.9); animation: pulse 1.2s ease-in-out;"
                if is_new else ""
            )

            with c:
                st.markdown(
                    f"""
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
                    """,
                    unsafe_allow_html=True,
                )

                # tombol untuk host membuka jawaban satu-per-satu kalau belum ketebak
                if not is_open:
                    if st.button(f"👀 Tampilkan #{idx + 1}", key=f"show_{idx}"):
                        reveal_answer(idx)
                        st.rerun()

# ----------------- POPUP SALAH (auto-hilang 2 detik) -----------------
def popup_salah():
    st.markdown(
        """
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
        <script>
          // auto-remove overlay setelah 2 detik + 200ms buffer
          setTimeout(function() {
            const el = document.getElementById('popup-wrong');
            if (el) el.remove();
          }, 2200);
        </script>
        <style>
        @keyframes fadeZoom {
          0%   { opacity:0; transform: scale(0.5); }
          30%  { opacity:1; transform: scale(1.1); }
          80%  { opacity:1; transform: scale(1.0); }
          100% { opacity:0; transform: scale(1.25); }
        }
        @keyframes shake {
          0%,100%{ transform:translate(0,0); }
          20%    { transform:translate(-15px,0); }
          40%    { transform:translate(15px,0); }
          60%    { transform:translate(-15px,0); }
          80%    { transform:translate(15px,0); }
        }
        .shake {
          animation: fadeZoom 2s ease-out forwards, shake 0.5s ease-in-out infinite;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

if st.session_state["trigger"] == "wrong":
    popup_salah()
    # langsung reset trigger agar tidak muncul lagi pada rerun berikutnya
    st.session_state["trigger"] = None

st.caption("Made with ❤️ — highlight BENAR 2 detik & popup SALAH auto-hilang")
