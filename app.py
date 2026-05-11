"""
SHL Assessment Advisor — Streamlit Chat Frontend
Schema: RecommendationResponse { reply, recommendations: [{name, url, test_type, duration}], end_of_conversation }
Run: streamlit run app.py
"""

import streamlit as st
import requests

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SHL Assessment Advisor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background: #f5f6fa; color: #1a1d27; }

[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e2e5ef;
}
[data-testid="stSidebar"] * { color: #1a1d27 !important; }

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 900px;
}

/* Header */
.shl-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem; letter-spacing: 0.2em;
    color: #9ca3af; text-transform: uppercase; margin-bottom: 4px;
}
.shl-title { font-size: 1.7rem; font-weight: 700; color: #111827; margin-bottom: 4px; }
.shl-sub   { font-size: 0.875rem; color: #6b7280; margin-bottom: 1.4rem; }

/* Chat bubbles */
.msg-wrap { display: flex; margin-bottom: 0.9rem; align-items: flex-start; gap: 10px; }
.msg-wrap.user { flex-direction: row-reverse; }

.avatar {
    width: 30px; height: 30px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.7rem; font-weight: 700; flex-shrink: 0;
}
.avatar.bot  { background: #0f4c81; color: #fff; }
.avatar.user { background: #e5e7eb; color: #374151; }

.bubble {
    max-width: 76%; padding: 0.7rem 1rem;
    border-radius: 14px; font-size: 0.875rem; line-height: 1.65;
    white-space: pre-wrap; word-break: break-word;
}
.bubble.bot {
    background: #ffffff; border: 1px solid #e2e5ef;
    color: #1a1d27; border-top-left-radius: 4px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.bubble.user {
    background: #0f4c81; color: #ffffff;
    border-top-right-radius: 4px;
}

/* Divider */
.divider { border: none; border-top: 1px solid #e2e5ef; margin: 1rem 0; }

/* Intent badge */
.intent-badge {
    display: inline-block;
    background: #eff6ff; color: #1d4ed8;
    border: 1px solid #bfdbfe; border-radius: 20px;
    font-size: 0.72rem; font-weight: 600;
    letter-spacing: 0.06em; text-transform: uppercase;
    padding: 2px 10px; margin-bottom: 0.75rem;
}

/* Section label */
.rec-section-label {
    font-size: 0.72rem; font-weight: 600;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: #6b7280; margin: 0 0 0.6rem 0;
}

/* Recommendation table (custom HTML) */
.rec-table {
    width: 100%; border-collapse: collapse;
    font-size: 0.85rem; background: #fff;
    border: 1px solid #e2e5ef; border-radius: 10px;
    overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.rec-table th {
    background: #f9fafb; color: #6b7280;
    font-size: 0.72rem; font-weight: 600;
    letter-spacing: 0.08em; text-transform: uppercase;
    padding: 0.6rem 1rem; text-align: left;
    border-bottom: 1px solid #e2e5ef;
}
.rec-table td {
    padding: 0.65rem 1rem; color: #1a1d27;
    border-bottom: 1px solid #f3f4f6; vertical-align: middle;
}
.rec-table tr:last-child td { border-bottom: none; }
.rec-table tr:hover td { background: #f9fafb; }
.rec-name-cell { font-weight: 600; color: #111827; }
.rec-link {
    font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;
    color: #0f4c81; text-decoration: none;
}
.rec-link:hover { text-decoration: underline; }
.type-tag {
    display: inline-block;
    background: #f0f9ff; color: #0369a1;
    border: 1px solid #bae6fd; border-radius: 4px;
    font-size: 0.7rem; font-weight: 500; padding: 1px 7px;
}
.duration-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem; color: #6b7280;
}

/* Comparison table — styled via Streamlit markdown container */
[data-testid="stMarkdownContainer"] table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
    background: #fff;
    border: 1px solid #e2e5ef;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    margin-top: 0.5rem;
}
[data-testid="stMarkdownContainer"] th {
    background: #f9fafb;
    color: #6b7280;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.6rem 1rem;
    text-align: left;
    border-bottom: 1px solid #e2e5ef;
}
[data-testid="stMarkdownContainer"] td {
    padding: 0.65rem 1rem;
    color: #1a1d27;
    border-bottom: 1px solid #f3f4f6;
    vertical-align: top;
}
[data-testid="stMarkdownContainer"] tr:last-child td { border-bottom: none; }
[data-testid="stMarkdownContainer"] tr:hover td { background: #f9fafb; }

/* Input */
[data-testid="stTextInput"] input {
    background: #fff; border: 1.5px solid #d1d5db;
    border-radius: 8px; color: #111827; font-size: 0.9rem;
    padding: 0.55rem 0.85rem;
}
[data-testid="stTextInput"] input:focus {
    border-color: #0f4c81;
    box-shadow: 0 0 0 3px rgba(15,76,129,0.12);
    outline: none;
}

/* Buttons */
.stButton > button {
    background: #0f4c81 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px;
    font-weight: 500; font-size: 0.875rem;
    padding: 0.5rem 1.1rem;
    transition: background 0.15s;
}
.stButton > button:hover { background: #0d3f6e !important; }
.stButton > button p,
.stButton > button span,
.stButton > button div {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "recommendations" not in st.session_state:
    st.session_state.recommendations = []
if "intent" not in st.session_state:
    st.session_state.intent = ""
if "compare_reply" not in st.session_state:
    st.session_state.compare_reply = ""
if "input_key" not in st.session_state:
    st.session_state.input_key = 0

# ── Sidebar ───────────────────────────────────────────────────────────────────
API_URL = "https://conversational-shl-assessment-recommender.onrender.com"

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown("---")
    if st.button("🗑 Clear conversation", use_container_width=True):
        st.session_state.messages        = []
        st.session_state.recommendations = []
        st.session_state.intent          = ""
        st.session_state.compare_reply   = ""
        st.session_state.input_key      += 1
        st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.78rem; color:#6b7280; line-height:1.75;'>
    <b style='color:#374151;'>How to use</b><br>
    Describe the role you're hiring for. The agent will ask clarifying questions, then recommend SHL assessments.<br><br>
    <b style='color:#374151;'>Try saying:</b><br>
    • "I'm hiring a Java developer"<br>
    • "Add a personality test"<br>
    • "Only tests under 20 minutes"<br>
    • "Compare OPQ32 and MQ"
    </div>
    """, unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<p class="shl-eyebrow">SHL · Assessment Intelligence</p>
<h1 class="shl-title">Assessment Advisor</h1>
<p class="shl-sub">Describe a role or hiring need — the agent finds the right SHL Individual Test Solutions through conversation.</p>
""", unsafe_allow_html=True)

# ── Example starters ──────────────────────────────────────────────────────────
if not st.session_state.messages:
    examples = [
        "I'm hiring a mid-level Java developer",
        "Graduate intake — cognitive + personality",
        "Sales manager, remote testing required",
        "Compare OPQ32 and MQ assessments",
    ]
    cols = st.columns(2)
    for i, ex in enumerate(examples):
        with cols[i % 2]:
            if st.button(ex, key=f"ex_{i}"):
                st.session_state["_pending"] = ex
                st.rerun()
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ── Chat history ──────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    role    = msg["role"]
    content = msg["content"]
    if role == "user":
        st.markdown(f"""
        <div class="msg-wrap user">
            <div class="avatar user">You</div>
            <div class="bubble user">{content}</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="msg-wrap">
            <div class="avatar bot">SHL</div>
            <div class="bubble bot">{content}</div>
        </div>""", unsafe_allow_html=True)

# ── Comparison table (shown when intent == compare) ───────────────────────────
if st.session_state.intent == "compare" and st.session_state.compare_reply:
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("<span class='intent-badge'>Intent: compare</span>", unsafe_allow_html=True)
    st.markdown("<p class='rec-section-label'>🔍 Assessment Comparison</p>", unsafe_allow_html=True)
    # LLM returns a markdown table; st.markdown renders it natively,
    # styled by the [data-testid="stMarkdownContainer"] rules in the CSS above.
    st.markdown(st.session_state.compare_reply)

# ── Recommendations table (shown for recommend / refine) ──────────────────────
if st.session_state.recommendations:
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    if st.session_state.intent and st.session_state.intent != "compare":
        st.markdown(
            f"<span class='intent-badge'>Intent: {st.session_state.intent}</span>",
            unsafe_allow_html=True,
        )
    st.markdown("<p class='rec-section-label'>📋 Recommended Assessments</p>", unsafe_allow_html=True)

    rows = ""
    for rec in st.session_state.recommendations:
        name      = rec.get("name", "")
        url       = rec.get("url", "#")
        test_type = rec.get("test_type", "—")
        duration  = rec.get("duration", "—")
        dur_str   = f"{duration} min" if isinstance(duration, int) else (str(duration) if duration else "—")

        rows += f"""
        <tr>
            <td class="rec-name-cell">{name}</td>
            <td><span class="type-tag">{test_type}</span></td>
            <td><span class="duration-tag">{dur_str}</span></td>
            <td><a class="rec-link" href="{url}" target="_blank">View →</a></td>
        </tr>"""

    st.markdown(f"""
    <table class="rec-table">
        <thead>
            <tr>
                <th>Assessment</th>
                <th>Type</th>
                <th>Duration</th>
                <th>Catalog</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    """, unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
pending = st.session_state.pop("_pending", None)

col1, col2 = st.columns([6, 1])
with col1:
    user_input = st.text_input(
        "Message",
        value=pending or "",
        placeholder="Describe the role or ask about assessments…",
        label_visibility="collapsed",
        key=f"chat_input_{st.session_state.input_key}",
    )
with col2:
    send = st.button("Send →", use_container_width=True)

# ── Send logic ────────────────────────────────────────────────────────────────
def send_message(text: str):
    text = text.strip()
    if not text:
        return

    st.session_state.messages.append({"role": "user", "content": text})
    compare_table = ""
    try:
        resp = requests.post(
            f"{API_URL}/chat",
            json={
                "messages": [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
            },
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()

        # Schema: reply, recommendations, end_of_conversation
        reply = data.get("reply", "Sorry, I couldn't process that.")

        compare_table = data.get("compare_table", "")

        recs = data.get("recommendations", [])

        # Derive intent locally — API no longer sends it
        intent = ""
        if "compare" in text.lower():
            intent = "compare"
        elif recs:
            intent = "recommend"

    except requests.exceptions.ConnectionError:
        reply  = "⚠️ Cannot reach the API.\nRun: uvicorn api.main:app --reload --port 8000"
        intent = "error"
        recs   = []
    except Exception as e:
        reply  = f"⚠️ Error: {e}"
        intent = "error"
        recs   = []

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.intent = intent

    if intent == "compare":
        st.session_state.compare_reply = compare_table
        st.session_state.recommendations = []
    elif recs:
        st.session_state.recommendations = recs
        st.session_state.compare_reply   = ""   # clear compare on new recs

    # Increment key → forces text_input to re-render empty next run
    st.session_state.input_key += 1
    st.rerun()

if send and user_input:
    with st.spinner("Finding SHL assessments..."):
        send_message(user_input)

elif pending:
    with st.spinner("Finding SHL assessments..."):
        send_message(pending)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; margin-top:2rem; font-size:0.73rem; color:#9ca3af;'>
    Individual Test Solutions only · Source:
    <a href='https://www.shl.com/solutions/products/productcatalog/' target='_blank'
       style='color:#0f4c81; text-decoration:none;'>SHL Product Catalog</a>
</div>
""", unsafe_allow_html=True)