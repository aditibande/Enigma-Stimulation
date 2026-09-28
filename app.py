import streamlit as st
from enigma import Enigma, ROTORS, REFLECTORS, A

ROWS = ["QWERTZUIO", "ASDFGHJK", "PYXCVBNML"]
SLOTS = ("Left", "Middle", "Right")

st.set_page_config(page_title="Enigma Machine", page_icon="🔐", layout="centered")

st.markdown(
    """
<style>
.title {text-align:center; color:#b5924a; letter-spacing:.5em; font-size:1.8rem;
        font-weight:700; margin-bottom:.5rem;}
.rotors {display:flex; justify-content:center; gap:18px; margin:.5rem 0 1rem;}
.win {width:68px; height:80px; line-height:80px; text-align:center; background:#080808;
      border:3px solid #b5924a; border-radius:6px; color:#f2e9d0;
      font:700 42px 'Courier New', monospace;}
.rname {text-align:center; color:#b5924a; font-size:.75rem; margin-top:4px;}
.panel {background:#0c0c0c; border:2px solid #4a4a4a; border-radius:12px;
        padding:18px 6px 10px; margin-bottom:1rem;}
.row {display:flex; justify-content:center; gap:clamp(4px, 1.6vw, 14px); margin-bottom:12px;}
.lamp {width:clamp(26px, 8vw, 48px); aspect-ratio:1; border-radius:50%; background:#262626;
       border:2px solid #5a5a5a; color:#6a6a6a; display:flex; align-items:center;
       justify-content:center; font-weight:700; font-size:clamp(.7rem, 2.6vw, 1.1rem);
       transition:all .15s;}
.lamp.on {background:#fff2a8; border-color:#ffd75e; color:#2a2100;
          box-shadow:0 0 10px 4px rgba(255,215,94,.85), 0 0 28px 10px rgba(255,215,94,.4);}
[data-testid="stHorizontalBlock"] {flex-wrap:nowrap !important; gap:.35rem !important;}
[data-testid="stColumn"] {min-width:0 !important;}
[class*="st-key-k_"] {width:100%;}
[class*="st-key-k_"] button {width:100%; aspect-ratio:1; min-height:0; padding:0;
        border-radius:50%; background:#2a2a2a; border:3px solid #8c8c8c; color:#e8e8e8;
        font-weight:700;}
[class*="st-key-k_"] button:hover {border-color:#b5924a; color:#ffd75e;}
[class*="st-key-k_"] button:active {background:#6b6b6b;}
</style>
""",
    unsafe_allow_html=True,
)


def group(s):
    return " ".join(s[i:i + 5] for i in range(0, len(s), 5)) or " "


def make(config):
    names, refl, rings, positions, plug = config
    return Enigma(rotors=names, reflector=refl, rings=rings, positions=positions, plugboard=plug)


def reset():
    s = st.session_state
    s.machine = make(s.config)
    s.inp = ""
    s.out = ""
    s.lit = None


def press(ch):
    s = st.session_state
    out = s.machine.encrypt_char(ch)
    s.inp += ch
    s.out += out
    s.lit = out


def lamp_html(ch, lit):
    cls = "lamp on" if ch == lit else "lamp"
    return f'<div class="{cls}">{ch}</div>'


with st.sidebar:
    st.header("Settings")
    names = [
        st.selectbox(f"{slot} rotor", list(ROTORS), index=i, key=f"rotor{i}")
        for i, slot in enumerate(SLOTS)
    ]
    refl = st.selectbox("Reflector", list(REFLECTORS), key="refl")
    rings = [
        int(st.number_input(f"{slot} ring", 1, 26, 1, key=f"ring{i}"))
        for i, slot in enumerate(SLOTS)
    ]
    positions = "".join(
        st.selectbox(f"{slot} start", list(A), key=f"pos{i}") for i, slot in enumerate(SLOTS)
    )
    plug = st.text_input("Plugboard pairs", placeholder="AB CD EF", key="plug")

pairs = plug.upper().split()
used = "".join(pairs)
if len(set(names)) < 3:
    st.error("Each rotor must be different.")
    st.stop()
if (len(pairs) > 10 or any(len(p) != 2 for p in pairs)
        or not all(ch in A for ch in used) or len(set(used)) != len(used)):
    st.error("Plugboard: up to 10 pairs of distinct letters, e.g. AB CD EF.")
    st.stop()

config = (tuple(names), refl, tuple(rings), positions, " ".join(pairs))
if st.session_state.get("config") != config:
    st.session_state.config = config
    reset()

s = st.session_state
rotors = (s.machine.left, s.machine.mid, s.machine.right)

st.markdown('<div class="title">ENIGMA</div>', unsafe_allow_html=True)

windows = "".join(
    f'<div><div class="win">{A[r.pos]}</div><div class="rname">{n}</div></div>'
    for r, n in zip(rotors, names)
)
st.markdown(f'<div class="rotors">{windows}</div>', unsafe_allow_html=True)

lamp_rows = "".join(
    '<div class="row">' + "".join(lamp_html(ch, s.lit) for ch in row) + "</div>" for row in ROWS
)
st.markdown(f'<div class="panel">{lamp_rows}</div>', unsafe_allow_html=True)

for row in ROWS:
    n = len(row)
    cols = st.columns([10 - n] + [2] * n + [10 - n])
    for i, ch in enumerate(row):
        cols[i + 1].button(ch, key=f"k_{ch}", on_click=press, args=(ch,))

st.button("Reset rotors & clear", on_click=reset)

st.caption("Input")
st.code(group(s.inp), language=None)
st.caption("Output")
st.code(group(s.out), language=None)

with st.expander("Encrypt or decrypt a whole message"):
    text = st.text_area("Message", placeholder="Type or paste text here")
    if st.button("Run through machine", key="run_all"):
        st.code(make(config).encrypt(text), language=None)
