# app2.py  (THERAPY CHAT)
from __future__ import annotations
import os, re, time
from typing import List, Dict
import streamlit as st
from dotenv import load_dotenv
from fpdf import FPDF
from datetime import datetime

# ================== ENV / PAGE ==================
load_dotenv()
# When run standalone, set page config; when imported (hub), ignore duplicate calls.
try:
    st.set_page_config(page_title="Chat Therapy",
                       page_icon="assets/favicon.png",
                       initial_sidebar_state="collapsed")
except Exception:
    pass

from agent import get_response  # uses your existing streaming Groq wrapper

# ================== UI HELPERS ==================
THERAPIST_ICON = "assets/favicon.png"
SOLUTION_ICON  = "assets/green.png"
OOS_ICON       = "assets/red.png"

def show_crisis_banner(text: str):
    t = (text or "").lower()
    if any(k in t for k in ["suicide", "self-harm", "kill myself", "hurt myself"]):
        st.info("If you're in danger or considering self-harm, call 988 (U.S.) or local emergency services.", icon="🆘")

def classify_avatar(text: str) -> str:
    t = (text or "").lower()
    oos = ["outside my scope","out of scope","cannot assist","i can’t assist","i can't assist",
           "i can’t help","i can't help","contact hr","report to hr","authorities",
           "legal advice","lawsuit","file a case","police report","financial advice",
           "tax advice","not able to help"]
    if any(x in t for x in oos):
        return OOS_ICON
    solution = ["steps","plan","solution","checklist","follow these","next actions",
                "here’s how","here is how","actionable","tl;dr","tldr"]
    if any(x in t for x in solution):
        return SOLUTION_ICON
    return THERAPIST_ICON

def stream_text(s: str, delay: float = 0.02):
    for part in re.split(r'(\n\n+|\n)', s):
        if part:
            yield part
            time.sleep(delay)

def build_full_prompt(history: List[Dict[str, str]], latest: str, mode: str, max_turns: int = 24) -> str:
    pruned = [m for m in history if m["role"] in ("user","assistant")]
    if len(pruned) > max_turns:
        pruned = pruned[-max_turns:]
    history_lines = [("User" if m["role"]=="user" else "Assistant") + f": {m['content']}" for m in pruned]
    history_text = "\n".join(history_lines) if history_lines else "(none)"

    if mode == "Segmented explainer":
        style_rule = ("When explaining, use up to 4 sections: TL;DR, Key Points, Steps, Next Actions. "
                      "Keep ≤180 words total. Each bullet ≤14 words. End with: 'Want me to expand any section?'.")
    else:
        style_rule = ("Empathetic, precise, non-clinical. No medications. Stay in mental-wellbeing scope. "
                      "Keep answers ≤80 words; 2–5 short bullets when useful; ≤2 clarifying questions.")

    return ( "System: You are Mr.TomBot, a supportive therapist-style AI.\n"
             f"Style rules: {style_rule}\n\n"
             f"Previous conversation:\n{history_text}\n\n"
             f"Latest query:\n{latest}" )

# ----------- Export helpers (ALWAYS return bytes) -----------
def _export_pdf_bytes(messages: List[Dict[str, str]], title="Chat Therapy") -> bytes:
    pdf = FPDF()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    font_path = "assets/DejaVuSans.ttf"
    if os.path.exists(font_path):
        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.add_font("DejaVu", "B", font_path, uni=True)
        body_font = ("DejaVu", "", 10); head_font = ("DejaVu", "B", 16); role_font = ("DejaVu", "B", 11)
        use_latin1 = False
    else:
        body_font = ("Arial", "", 10); head_font = ("Arial", "B", 16); role_font = ("Arial", "B", 11)
        use_latin1 = True

    pdf.set_title(title); pdf.set_author("Chat Therapy")
    pdf.set_font(*head_font); pdf.cell(w=0, h=10, txt=title)
    pdf.set_xy(x=pdf.l_margin, y=pdf.get_y() + 6)

    usable_w = pdf.w - pdf.l_margin - pdf.r_margin
    for m in messages:
        role = "You" if m["role"]=="user" else "Assistant"
        pdf.set_font(*role_font); pdf.multi_cell(usable_w, 6, f"{role}:", align="L")
        pdf.set_font(*body_font)
        raw = m.get("content") or ""
        safe = raw.replace("\t"," ").replace("\r","")
        if use_latin1:
            safe = safe.encode("latin-1","replace").decode("latin-1")
        pdf.multi_cell(usable_w, 6, safe, align="L")
        pdf.set_xy(x=pdf.l_margin, y=pdf.get_y()+2)

    out = pdf.output(dest='S')
    if isinstance(out, (bytes, bytearray)):
        return bytes(out)
    if isinstance(out, str):
        return out.encode('latin-1', 'replace')
    return bytes(out)

def _export_md_bytes(messages: List[Dict[str, str]]) -> bytes:
    lines = []
    for m in messages:
        role = "You" if m["role"]=="user" else "Assistant"
        lines.append(f"**{role}:**\n\n{m['content']}\n")
    return ("\n---\n".join(lines)).encode("utf-8")

# ======= PUBLIC RENDER FUNCTION =======
def render_therapy():
    # ================== SIDEBAR ==================
    with st.sidebar:
        st.header("⚙️ Debug")
        st.write("Python:", os.sys.executable)
        st.write("CWD:", os.getcwd())
        st.write("GROQ_API_KEY present:", bool(os.getenv("GROQ_API_KEY")))
        mode = st.radio("Reply style", ["Therapist (concise)", "Segmented explainer"], index=0)
        if st.button("🆕 New chat", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # ================== SESSION ==================
    if "messages" not in st.session_state:
        st.session_state.messages: List[Dict[str, str]] = []

    # ================== HEADER ==================
    st.markdown("""
    <div style='text-align:center;'>
      <img src='assets/favicon.png' width='70' style='border-radius:50%; margin-bottom:8px;'>
      <h1>Chat Therapy</h1>
      <p style='color:gray;'>Your calm space to talk things through 🌿</p>
    </div>
    """, unsafe_allow_html=True)

    # Welcome card
    if not st.session_state.messages:
        st.markdown("""
        <div style="display:flex;justify-content:center;margin-top:24px;">
          <div style="max-width:720px;padding:16px;border-radius:16px;
                      background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);">
            <div style="font-weight:700;font-size:18px;margin-bottom:4px;">Welcome 👋</div>
            <div>What’s on your mind today? Try: “I’m feeling overwhelmed about work.”</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # History
    for m in st.session_state.messages:
        avatar = m.get("avatar") if m["role"] == "assistant" else None
        with st.chat_message(m["role"], avatar=avatar):
            st.markdown(m["content"])

    # Input / Response
    if prompt := st.chat_input("What’s on your mind?"):
        show_crisis_banner(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        full_prompt = build_full_prompt(st.session_state.messages, prompt, mode, max_turns=24)
        try:
            reply_text = get_response(full_prompt) or "[No response]"
        except Exception as e:
            reply_text = f"[Error contacting model] {e}"

        avatar_path = classify_avatar(reply_text)
        with st.chat_message("assistant", avatar=avatar_path):
            if len(reply_text) > 500:
                st.write_stream(stream_text(reply_text))
            else:
                st.markdown(reply_text)

        st.session_state.messages.append({"role": "assistant", "content": reply_text, "avatar": avatar_path})

    # ================== FOOTER: EXPORT ==================
    # (Keeping your layout; these helpers output bytes)
    if st.session_state.get("messages"):
        col1, col2 = st.columns(2)
        with col1:
            if st.download_button("⬇️ Download PDF", data=_export_pdf_bytes(st.session_state["messages"]),
                                  file_name=f"chat_therapy_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                  mime="application/pdf", use_container_width=True):
                pass
        with col2:
            if st.download_button("⬇️ Download Markdown", data=_export_md_bytes(st.session_state["messages"]),
                                  file_name=f"chat_therapy_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                                  mime="text/markdown", use_container_width=True):
                pass

# Allow standalone run
if __name__ == "__main__":
    render_therapy()
