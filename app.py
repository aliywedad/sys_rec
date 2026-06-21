import base64

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components
from audio_recorder_streamlit import audio_recorder

from src.data_cleaning import load_and_clean
from src.mistral_client import chat_turn, format_results
from src.recommender import Recommender, engineer_features
from src.voice import audio_hash, text_to_speech_bytes, transcribe_audio_bytes

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Immo.AI — Mauritania Property Finder",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
/* ── Global ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer { visibility: hidden; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0c29 0%, #302b63 60%, #24243e 100%);
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stNumberInput label { color: #a0aec0 !important; font-size: 0.82em; }

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 14px;
}

/* ── Property card ── */
.prop-card {
    background: linear-gradient(135deg, #1a1f36 0%, #1e2a45 100%);
    border: 1px solid #2d4a8a;
    border-radius: 14px;
    padding: 18px;
    margin: 10px 0;
    transition: border-color 0.2s, transform 0.2s;
}
.prop-card:hover { border-color: #4f8bf9; transform: translateY(-2px); }
.prop-title { font-size: 1.05em; font-weight: 600; color: #90cdf4; margin-bottom: 6px; }
.prop-price { font-size: 1.4em; font-weight: 700; color: #68d391; }
.prop-meta  { font-size: 0.82em; color: #a0aec0; margin-top: 4px; }
.prop-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72em;
    font-weight: 600;
    margin: 2px 2px 0 0;
}
.badge-available { background: #1c4532; color: #68d391; }
.badge-sold      { background: #4a1942; color: #fc8181; }
.badge-score     { background: #1a365d; color: #90cdf4; }

/* ── Tab active ── */
[data-baseweb="tab-list"] { border-bottom: 2px solid #2d4a8a; }
button[data-baseweb="tab"][aria-selected="true"] { border-bottom: 2px solid #4f8bf9 !important; color: #4f8bf9 !important; }

/* ── Chat container ── */
.chat-wrap { max-height: 62vh; overflow-y: auto; padding: 8px 0; }

/* ── Welcome banner ── */
.welcome-banner {
    background: linear-gradient(135deg, #0f0c29, #302b63);
    border: 1px solid #4f8bf9;
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 24px;
    text-align: center;
}
.welcome-banner h1 { font-size: 2em; color: #90cdf4; margin: 0 0 8px; }
.welcome-banner p  { color: #a0aec0; margin: 0; font-size: 1.05em; }

/* ── Divider ── */
hr { border-color: #2d4a8a; }

/* ── Jarvis waveform ── */
.jarvis-wave {
    display: inline-flex;
    align-items: center;
    gap: 3px;
    vertical-align: middle;
    margin-left: 8px;
}
.jarvis-wave span {
    display: block;
    width: 3px;
    background: #4f8bf9;
    border-radius: 2px;
    animation: jwave 1.3s infinite ease-in-out;
}
.jarvis-wave span:nth-child(1){height:6px;animation-delay:0.0s;}
.jarvis-wave span:nth-child(2){height:14px;animation-delay:0.1s;}
.jarvis-wave span:nth-child(3){height:20px;animation-delay:0.2s;}
.jarvis-wave span:nth-child(4){height:14px;animation-delay:0.1s;}
.jarvis-wave span:nth-child(5){height:6px;animation-delay:0.0s;}
@keyframes jwave {
    0%,100%{transform:scaleY(0.4);opacity:0.4;}
    50%{transform:scaleY(1);opacity:1;}
}
</style>
""",
    unsafe_allow_html=True,
)

# ── Constants ─────────────────────────────────────────────────────────────────
GREETING = "Good day, sir. **What are you looking for?**"

WAKE_RESPONSE = "At your service, sir."

# Words that trigger the wake response (without routing to Mistral)
_WAKE_ONLY = {"hey jarvis", "hi jarvis", "hello jarvis", "okay jarvis", "jarvis"}

# Prefixes to strip before passing the remainder to Mistral
_WAKE_PREFIXES = [
    "hey jarvis", "hi jarvis", "hello jarvis",
    "okay jarvis", "ok jarvis", "jarvis",
]

TEST_QUERIES = [
    "villa Tevragh Zeina luxury",
    "cheap house Arafat",
    "apartment Ksar affordable",
    "land terrain constructible",
    "commercial space office",
    "maison dar vendre Sebkha",
    "duplex Dar Naim",
    "studio apartment Teyarett",
]

# ═══════════════════════════════════════════════════════════════════════════════
# DATA & MODEL
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="Loading property data…")
def get_data() -> pd.DataFrame:
    return load_and_clean("e-commerce-mr.csv")


@st.cache_resource(show_spinner="Training recommendation model…")
def get_recommender(_df: pd.DataFrame) -> Recommender:
    r = Recommender(category="real_estate")
    r.fit(_df)
    return r


df = get_data()
re_df = engineer_features(df[df["Category"] == "real_estate"].copy())
rec = get_recommender(df)

# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
def autoplay_audio(audio_bytes: bytes) -> None:
    """Inject a JS Audio object that plays immediately — no visible widget."""
    b64 = base64.b64encode(audio_bytes).decode("utf-8")
    components.html(
        f"""
        <script>
        (function(){{
            var a = new Audio("data:audio/mp3;base64,{b64}");
            a.play().catch(function(e){{ console.warn("Autoplay blocked:", e); }});
        }})();
        </script>
        """,
        height=0,
        scrolling=False,
    )


def _init_state():
    if "conv" not in st.session_state:
        st.session_state.conv = []
    if "display" not in st.session_state:
        greeting_audio = text_to_speech_bytes(
            "Good day, sir. What are you looking for?"
        )
        st.session_state.display = [
            {"role": "assistant", "content": GREETING, "audio": greeting_audio}
        ]
    if "last_audio" not in st.session_state:
        st.session_state.last_audio = None
    if "played" not in st.session_state:
        st.session_state.played = set()
    if "searching" not in st.session_state:
        st.session_state.searching = False

_init_state()

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🏠 Immo.AI")
    st.caption("Mauritania Real Estate · voursa.com")
    st.markdown("---")

    c1, c2 = st.columns(2)
    c1.metric("Total Listings", f"{len(df):,}")
    c2.metric("Real Estate", f"{len(re_df):,}")
    c1.metric("Available", f"{re_df['Is_Available'].sum():,}")
    c2.metric("Sold", f"{(~re_df['Is_Available']).sum():,}")

    st.markdown("---")
    st.markdown("### 🔍 Search Filters")
    st.caption("Applied automatically during chat.")

    price_min = st.number_input("Min Price (MRU)", value=0, step=50_000)
    price_max = st.number_input(
        "Max Price (MRU)",
        value=int(re_df["Price_MRU"].quantile(0.95)),
        step=100_000,
    )
    locations = ["Any"] + sorted(re_df["Main_Location"].unique().tolist())
    loc_filter = st.selectbox("Neighborhood", options=locations)
    n_results = st.slider("Results to show", 3, 10, 5)
    avail_only = st.checkbox("Available only", value=True)

    st.markdown("---")
    if st.button("🗑️ Reset Conversation", use_container_width=True):
        for key in ("conv", "display", "last_audio", "played", "searching"):
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.markdown("---")
    st.caption("**Algorithm:** TF-IDF + Hybrid Scoring  \n**AI:** Mistral Large  \n**STT/TTS:** Google")

# ═══════════════════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════════════════
tab_chat, tab_eda, tab_eval = st.tabs(["🤖 AI Assistant", "📊 Data Explorer", "📈 Evaluation"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — AI CHATBOT
# ═══════════════════════════════════════════════════════════════════════════════
with tab_chat:
    st.markdown(
        """<div class='welcome-banner'>
        <h1>🏠 Immo<span style='color:#4f8bf9'>.</span>AI</h1>
        <p>Your intelligent real estate assistant for Mauritania — speak or type to find your perfect property</p>
        </div>""",
        unsafe_allow_html=True,
    )

    # ── Property card renderer ────────────────────────────────────────────────
    def render_property_card(r: dict, idx: int):
        badge_status = (
            "<span class='prop-badge badge-available'>✓ Available</span>"
            if r["Status"] == "Available"
            else "<span class='prop-badge badge-sold'>Sold</span>"
        )
        badge_score = f"<span class='prop-badge badge-score'>Score {r['score_pct']}%</span>"
        badge_bucket = f"<span class='prop-badge badge-score'>{r['price_bucket'].capitalize()}</span>"

        title_safe = str(r["Title"])[:70]
        loc_safe = str(r["Location"])[:50]

        col_img, col_info = st.columns([1, 2], gap="medium")
        with col_img:
            if r.get("Image"):
                st.image(r["Image"], use_container_width=True)
            else:
                st.markdown(
                    "<div style='background:#1e2a45;border-radius:8px;height:120px;"
                    "display:flex;align-items:center;justify-content:center;"
                    "color:#4a5568;font-size:2em;'>🏠</div>",
                    unsafe_allow_html=True,
                )
        with col_info:
            st.markdown(
                f"""<div>
                <div class='prop-title'>{title_safe}</div>
                <div class='prop-price'>{r['Price_MRU']:,.0f} <span style='font-size:0.6em;color:#a0aec0'>MRU</span></div>
                <div class='prop-meta'>📍 {loc_safe}</div>
                <div class='prop-meta'>👁️ {int(r['Views'])} views</div>
                <div style='margin-top:8px'>{badge_status} {badge_score} {badge_bucket}</div>
                </div>""",
                unsafe_allow_html=True,
            )
            if r.get("Link"):
                st.link_button("View Listing →", r["Link"], use_container_width=False)

    # ── Render chat history ───────────────────────────────────────────────────
    last_idx = len(st.session_state.display) - 1
    for i, msg in enumerate(st.session_state.display):
        is_latest = i == last_idx
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
            if msg["role"] == "assistant" and msg.get("audio") and is_latest:
                st.markdown(
                    msg["content"]
                    + "<div class='jarvis-wave'>"
                    + "<span></span>" * 5
                    + "</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(msg["content"])
            # Auto-play only once per message
            if msg.get("audio") and i not in st.session_state.played:
                autoplay_audio(msg["audio"])
                st.session_state.played.add(i)
            if msg.get("recs"):
                st.markdown(f"---\n**Found {len(msg['recs'])} matching properties:**")
                for i, r in enumerate(msg["recs"], 1):
                    with st.expander(
                        f"🏠 #{i} — {str(r['Title'])[:55]} · {r['Price_MRU']:,.0f} MRU · {r['Main_Location']}",
                        expanded=(i == 1),
                    ):
                        render_property_card(r, i)

    # ── Input row ─────────────────────────────────────────────────────────────
    st.markdown("---")
    col_input, col_mic = st.columns([5, 1])

    with col_input:
        user_text = st.chat_input("Type your message…")

    with col_mic:
        st.markdown("<div style='padding-top:6px'>", unsafe_allow_html=True)
        audio_bytes = audio_recorder(
            pause_threshold=3.0,
            sample_rate=16_000,
            text="",
            icon_size="2x",
            key="mic",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Determine query from text or voice ────────────────────────────────────
    query = None

    if user_text:
        query = user_text

    elif audio_bytes:
        h = audio_hash(audio_bytes)
        if h != st.session_state.last_audio:
            st.session_state.last_audio = h
            with st.spinner("🎙️ Transcribing…"):
                query = transcribe_audio_bytes(audio_bytes)
            if query:
                st.info(f"🎙️ You said: *{query}*")
            else:
                st.warning("Couldn't understand the audio. Please try again or type your message.")

    # ── Process query ─────────────────────────────────────────────────────────
    if query:
        q_lower = query.lower().strip(" .,!")

        # ── Wake word handling ──
        if q_lower in _WAKE_ONLY:
            wake_audio = text_to_speech_bytes(WAKE_RESPONSE)
            st.session_state.display.append({"role": "user", "content": query})
            st.session_state.display.append(
                {"role": "assistant", "content": WAKE_RESPONSE, "audio": wake_audio}
            )
            st.rerun()

        # Strip wake prefix so only the real request goes to Mistral
        for prefix in _WAKE_PREFIXES:
            if q_lower.startswith(prefix):
                query = query[len(prefix):].strip(" .,!")
                break

        if not query:
            st.rerun()

        # Add to display + Mistral history
        st.session_state.display.append({"role": "user", "content": query})
        st.session_state.conv.append({"role": "user", "content": query})

        # Call Mistral
        with st.spinner("Alex is thinking…"):
            reply_text, search_params = chat_turn(st.session_state.conv)

        # Add assistant reply to history
        st.session_state.conv.append({"role": "assistant", "content": reply_text})

        recs = []
        final_text = reply_text

        # ── Run recommender if search triggered ──
        if search_params:
            loc = search_params.get("location") or (loc_filter if loc_filter != "Any" else None)
            p_min = search_params.get("price_min") or (price_min if price_min > 0 else None)
            p_max = search_params.get("price_max") or (price_max if price_max > 0 else None)
            keywords = search_params.get("keywords") or query

            with st.spinner("🔍 Searching listings…"):
                results = rec.recommend(
                    query=keywords,
                    min_price=p_min,
                    max_price=p_max,
                    location=loc,
                    top_n=n_results,
                    available_only=avail_only,
                )
            recs = results.to_dict("records") if not results.empty else []

            with st.spinner("✍️ Formatting results…"):
                final_text = format_results(query, recs)

            # Let Mistral know about the results so follow-up questions work
            st.session_state.conv.append(
                {"role": "assistant", "content": final_text}
            )

        # ── TTS ──
        with st.spinner("🔊 Generating voice response…"):
            audio_resp = text_to_speech_bytes(final_text)

        st.session_state.display.append(
            {
                "role": "assistant",
                "content": final_text,
                "audio": audio_resp,
                "recs": recs,
            }
        )
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DATA EXPLORER
# ═══════════════════════════════════════════════════════════════════════════════
with tab_eda:
    st.header("📊 Data Explorer")
    st.caption(f"Dataset: **{len(df):,}** clean listings · {df['Category'].nunique()} categories · {df['Main_Location'].nunique()} locations")

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Listings", f"{len(df):,}")
    k2.metric("Real Estate", f"{len(re_df):,}")
    k3.metric("Median Price (MRU)", f"{re_df['Price_MRU'].median():,.0f}")
    k4.metric("Total Views", f"{int(df['Views'].sum()):,}")

    st.markdown("---")

    # Row 1
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Listings by Category")
        cat = df["Category"].value_counts()
        fig = px.pie(
            values=cat.values, names=cat.index,
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(showlegend=False, margin=dict(t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Availability — Real Estate")
        status = re_df["Status"].value_counts()
        fig = px.bar(
            x=status.index, y=status.values,
            color=status.index,
            color_discrete_map={"Available": "#68d391", "Sold Out": "#fc8181"},
            labels={"x": "", "y": "Count"},
            text_auto=True,
        )
        fig.update_layout(showlegend=False, margin=dict(t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

    # Price distribution
    st.subheader("Price Distribution — Real Estate")
    p95 = re_df["Price_MRU"].quantile(0.95)
    fig = px.histogram(
        re_df[re_df["Price_MRU"] <= p95], x="Price_MRU", nbins=60,
        color_discrete_sequence=["#4f8bf9"],
        labels={"Price_MRU": "Price (MRU)"},
    )
    fig.add_vline(
        x=re_df["Price_MRU"].median(),
        line_dash="dash", line_color="#fc8181",
        annotation_text=f"Median: {re_df['Price_MRU'].median():,.0f} MRU",
        annotation_font_color="#fc8181",
    )
    fig.update_layout(margin=dict(t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

    # Row 3
    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Top 10 Neighborhoods")
        top_loc = re_df["Main_Location"].value_counts().head(10)
        fig = px.bar(
            x=top_loc.values, y=top_loc.index, orientation="h",
            color=top_loc.values, color_continuous_scale="Blues",
            labels={"x": "Listings", "y": ""},
        )
        fig.update_layout(
            yaxis={"categoryorder": "total ascending"},
            coloraxis_showscale=False, margin=dict(t=0)
        )
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.subheader("Median Price by Neighborhood")
        med = (
            re_df.groupby("Main_Location")["Price_MRU"]
            .median().sort_values(ascending=False).head(10)
        )
        fig = px.bar(
            x=med.index, y=med.values,
            color=med.values, color_continuous_scale="Oranges",
            labels={"x": "", "y": "Median Price (MRU)"},
            text_auto=".3s",
        )
        fig.update_layout(coloraxis_showscale=False, margin=dict(t=0))
        st.plotly_chart(fig, use_container_width=True)

    # Scatter
    st.subheader("Views vs. Price by Neighborhood")
    scatter = re_df[re_df["Price_MRU"] <= p95]
    fig = px.scatter(
        scatter, x="Price_MRU", y="Views",
        color="Main_Location", hover_data=["Title"],
        opacity=0.6,
        labels={"Price_MRU": "Price (MRU)", "Views": "Views"},
    )
    fig.update_layout(showlegend=False, margin=dict(t=0))
    st.plotly_chart(fig, use_container_width=True)

    # Box plot
    st.subheader("Price Spread by Top Neighborhoods")
    top8 = re_df["Main_Location"].value_counts().head(8).index
    box_df = re_df[re_df["Main_Location"].isin(top8) & (re_df["Price_MRU"] <= p95)]
    fig = px.box(
        box_df, x="Main_Location", y="Price_MRU",
        color="Main_Location",
        labels={"Main_Location": "Neighborhood", "Price_MRU": "Price (MRU)"},
        notched=True,
    )
    fig.update_layout(showlegend=False, margin=dict(t=0))
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("🗂️ Raw Data (first 50 rows — Real Estate)"):
        st.dataframe(
            re_df[["Title", "Price_MRU", "Main_Location", "Views", "Status", "Date_Posted", "price_bucket"]]
            .head(50),
            use_container_width=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — EVALUATION
# ═══════════════════════════════════════════════════════════════════════════════
with tab_eval:
    st.header("📈 Model Evaluation")

    st.markdown("""
**Evaluation method:** Precision@K proxy — fraction of top-K results with hybrid score > 0.1.

**Hybrid score** = 0.65 × text_similarity + 0.15 × price_compat + 0.12 × popularity + 0.08 × recency
    """)

    col_run, col_k = st.columns([2, 1])
    with col_k:
        eval_k = st.slider("K (top results)", 3, 10, 5)

    with col_run:
        run_eval = st.button("▶ Run Evaluation", type="primary", use_container_width=True)

    if run_eval:
        with st.spinner("Running evaluation…"):
            metrics = rec.evaluate(TEST_QUERIES, k=eval_k)
            rows = []
            for q in TEST_QUERIES:
                r = rec.recommend(q, top_n=eval_k)
                rows.append({
                    "Query": q,
                    "Results": len(r),
                    "Max Score (%)": float(r["score_pct"].max()) if not r.empty else 0,
                    "Avg Score (%)": float(r["score_pct"].mean().round(1)) if not r.empty else 0,
                    "Median Price (MRU)": f"{r['Price_MRU'].median():,.0f}" if not r.empty else "—",
                })

        m1, m2, m3 = st.columns(3)
        m1.metric("Queries Tested", metrics["queries_tested"])
        m2.metric(f"Precision@{eval_k}", f"{metrics['precision_at_k']:.1%}")
        m3.metric("Avg Hybrid Score", f"{metrics['avg_hybrid_score']:.3f}")

        st.markdown("---")
        st.subheader("Per-query breakdown")
        eval_df = pd.DataFrame(rows)
        st.dataframe(eval_df, use_container_width=True)

        fig = px.bar(
            eval_df, x="Query", y="Max Score (%)",
            color="Max Score (%)", color_continuous_scale="Greens",
            text="Max Score (%)",
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(
            coloraxis_showscale=False,
            xaxis_tickangle=-30,
            yaxis_range=[0, 100],
            margin=dict(t=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("System Architecture")
    st.markdown("""
| Component | Detail |
|---|---|
| **Algorithm** | Content-Based Filtering + Hybrid Scoring |
| **Text Vectorization** | TF-IDF, char n-grams (2–4), 8,000 features |
| **Similarity** | Cosine Similarity |
| **Hybrid Weights** | Text 65% · Price 15% · Popularity 12% · Recency 8% |
| **Feature Engineering** | Price bucket · Log-popularity · Exponential recency decay |
| **Conversational AI** | Mistral Large (multi-turn, structured info extraction) |
| **Speech-to-Text** | Google Speech Recognition (AR / FR / EN) |
| **Text-to-Speech** | Google TTS (gTTS) |
| **Dataset** | 1,852 real estate listings — voursa.com Mauritania |

> 📄 See **[ALGORITHM.md](ALGORITHM.md)** for the full technical explanation of algorithm choice and feature engineering.
    """)
