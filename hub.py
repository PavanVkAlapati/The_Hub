# the_hub/hub.py
import os
import importlib
import streamlit as st

# ---------- Page ----------
FAVICON = os.path.join("assets", "favicon.png")
try:
    st.set_page_config(
        page_title="The Hub",
        page_icon=FAVICON if os.path.exists(FAVICON) else "🧭",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
except Exception:
    # Ignore duplicate set_page_config when sub-apps are imported
    pass

# ---------- Simple router ----------
ROUTE = st.session_state.get("route", "hub")
def goto(name: str):
    st.session_state["route"] = name
    st.rerun()

def _import_first(mod_names):
    """Import first module that exists from list of names."""
    for name in mod_names:
        try:
            return importlib.import_module(name)
        except Exception:
            continue
    return None

def _call_render(mod, candidates):
    """Call first render function that exists in module."""
    for fn in candidates:
        if hasattr(mod, fn):
            return getattr(mod, fn)()
    st.error(f"None of the render functions found: {candidates}")

# ---------- Hub tiles ----------
if ROUTE == "hub":
    st.markdown(
        """
        <div style="text-align:center;margin:10px 0 24px;">
          <div style="font-size:36px;font-weight:800;">The Hub</div>
          <div style="color:#888;">Choose a tool to launch</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            """
            <div style="padding:18px;border:1px solid rgba(0,0,0,0.1);
                        border-radius:16px;min-height:180px;">
              <div style="font-size:22px;font-weight:700;">🧠 Chat Therapy</div>
              <div style="color:#666;margin-top:6px;">
                Therapist-style chat with export to PDF/Markdown.
              </div>
              <div style="margin-top:16px;">
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open Therapy", type="primary", use_container_width=True):
            goto("therapy")
        st.markdown("</div></div>", unsafe_allow_html=True)

    with c2:
        st.markdown(
            """
            <div style="padding:18px;border:1px solid rgba(0,0,0,0.1);
                        border-radius:16px;min-height:180px;">
              <div style="font-size:22px;font-weight:700;">🧩 Product → JSON Extractor</div>
              <div style="color:#666;margin-top:6px;">
                Paste a product description, get strict JSON and download it.
              </div>
              <div style="margin-top:16px;">
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open Extractor", type="primary", use_container_width=True):
            goto("extractor")
        st.markdown("</div></div>", unsafe_allow_html=True)

# ---------- Therapy app ----------
elif ROUTE == "therapy":
    st.sidebar.button("⬅️ Back to Hub", use_container_width=True, on_click=lambda: goto("hub"))
    # Prefer app3.py; fall back to app2.py
    mod = _import_first(["app3", "app2"])
    if not mod:
        st.error("Could not import app3.py or app2.py. Ensure one of them is present in the_hub folder.")
    else:
        _call_render(mod, ["render_therapy", "render"])

# ---------- Product extractor ----------
elif ROUTE == "extractor":
    st.sidebar.button("⬅️ Back to Hub", use_container_width=True, on_click=lambda: goto("hub"))
    # Prefer prodapp.py; fall back to prodapp2.py
    mod = _import_first(["prodapp", "prodapp2"])
    if not mod:
        st.error("Could not import prodapp.py or prodapp2.py. Ensure one of them is present in the_hub folder.")
    else:
        _call_render(mod, ["render_extractor", "render"])
