# prodapp.py  (PRODUCT → JSON EXTRACTOR)
from __future__ import annotations
import os, re, json
from typing import Dict, Any
import streamlit as st
from dotenv import load_dotenv

# Import your Groq-backed extractor
# prodbot.py must expose: get_response(user_input: str) -> str
from prodbot import get_response  # uses your SYSTEM_PROMPT for JSON-only output

RAW_JSON_PATTERN = re.compile(r"\{[\s\S]*\}$", re.MULTILINE)  # greedy JSON object at end

def coerce_json(text: str) -> Dict[str, Any]:
    """
    Try strict JSON parse. If vendor added stray text, attempt to extract the last
    JSON object from response. Raises ValueError on failure.
    """
    try:
        return json.loads(text)
    except Exception:
        pass
    m = RAW_JSON_PATTERN.search(text.strip())
    if m:
        return json.loads(m.group(0))
    s = text.strip()
    first = s.find("{"); last = s.rfind("}")
    if first != -1 and last != -1 and last > first:
        return json.loads(s[first:last + 1])
    raise ValueError("Model did not return valid JSON.")

def download_bytes(obj: Dict[str, Any]) -> bytes:
    return json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")

# ======= PUBLIC RENDER FUNCTION =======
def render_extractor():
    # ────────────────────────────────────────────────────────────────────────────
    # ENV & PAGE
    # ────────────────────────────────────────────────────────────────────────────
    load_dotenv()
    # When run standalone, set page config; when imported (hub), ignore duplicate calls.
    try:
        st.set_page_config(
            page_title="Product → JSON Extractor",
            page_icon="🧩",
            layout="centered",
            initial_sidebar_state="collapsed",
        )
    except Exception:
        pass

    # ────────────────────────────────────────────────────────────────────────────
    # SIDEBAR (debug)
    # ────────────────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("⚙️ Debug")
        st.write("Python:", os.sys.executable)
        st.write("CWD:", os.getcwd())
        st.write("GROQ_API_KEY present:", bool(os.getenv("GROQ_API_KEY")))
        st.caption("Ensure prodbot.py defines SYSTEM_PROMPT and get_response().")

    # ────────────────────────────────────────────────────────────────────────────
    # HEADER
    # ────────────────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="text-align:center;margin-top:8px;">
          <div style="font-size:34px;font-weight:700;">Product → JSON Extractor</div>
          <div style="color:#888;margin-top:6px;">
            Paste any product description. Get a consistent JSON back. Download the JSON file.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    # ────────────────────────────────────────────────────────────────────────────
    # INPUT AREA
    # ────────────────────────────────────────────────────────────────────────────
    sample = "Apple iPhone 15 Pro Max – 256GB, Titanium, 48MP camera, A17 Pro chip. Price: $1199."
    desc = st.text_area("Product description", value="", height=180, placeholder=sample)

    col_run, col_clear = st.columns([1, 1])
    run = col_run.button("Extract JSON", type="primary", use_container_width=True)
    if col_clear.button("Clear", use_container_width=True):
        st.session_state.pop("last_json", None)
        st.rerun()

    st.divider()

    # ────────────────────────────────────────────────────────────────────────────
    # PROCESS
    # ────────────────────────────────────────────────────────────────────────────
    if run:
        if not desc.strip():
            st.error("Please paste a product description.")
        else:
            with st.spinner("Extracting…"):
                try:
                    raw = get_response(desc)   # model returns text; expected JSON per SYSTEM_PROMPT
                    data = coerce_json(raw)
                    st.session_state["last_json"] = data
                except Exception as e:
                    st.error(f"Failed to parse JSON: {e}")
                    st.stop()

    # ────────────────────────────────────────────────────────────────────────────
    # OUTPUT
    # ────────────────────────────────────────────────────────────────────────────
    if "last_json" in st.session_state:
        parsed = st.session_state["last_json"]

        st.subheader("Result")
        st.json(parsed, expanded=True)

        st.caption("Raw JSON string")
        st.code(json.dumps(parsed, ensure_ascii=False, indent=2), language="json")

        st.download_button(
            "⬇️ Download JSON",
            data=download_bytes(parsed),
            file_name="product.json",   # file contains ONLY the JSON
            mime="application/json",
            use_container_width=True,
        )

    # ────────────────────────────────────────────────────────────────────────────
    # FOOTER
    # ────────────────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="text-align:center;color:#999;margin-top:24px;">
          Built for consistent, machine-readable outputs.
        </div>
        """,
        unsafe_allow_html=True,
    )

# Allow standalone run
if __name__ == "__main__":
    render_extractor()
