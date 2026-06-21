"""Generate a comprehensive beginner-friendly PDF for the Immo.AI project."""

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ── Palette ───────────────────────────────────────────────────────────────────
DARK_BG   = colors.HexColor("#0f0c29")
BLUE      = colors.HexColor("#4f8bf9")
LIGHT_BLUE= colors.HexColor("#90cdf4")
GREEN     = colors.HexColor("#68d391")
GRAY      = colors.HexColor("#a0aec0")
WHITE     = colors.white
BLACK     = colors.HexColor("#1a202c")
CARD_BG   = colors.HexColor("#1e2a45")
ORANGE    = colors.HexColor("#ed8936")
RED       = colors.HexColor("#fc8181")

PAGE_W, PAGE_H = A4
W = PAGE_W

# ── Styles ────────────────────────────────────────────────────────────────────
base = getSampleStyleSheet()

def S(name, **kw):
    return ParagraphStyle(name, **kw)

styles = {
    "cover_title": S("cover_title", fontSize=34, textColor=LIGHT_BLUE,
                     alignment=TA_CENTER, fontName="Helvetica-Bold",
                     spaceAfter=10, leading=42),
    "cover_sub":   S("cover_sub",   fontSize=16, textColor=GRAY,
                     alignment=TA_CENTER, spaceAfter=6),
    "cover_tag":   S("cover_tag",   fontSize=11, textColor=GREEN,
                     alignment=TA_CENTER, spaceAfter=4),

    "h1": S("h1", fontSize=22, textColor=LIGHT_BLUE, fontName="Helvetica-Bold",
            spaceBefore=18, spaceAfter=8, leading=28),
    "h2": S("h2", fontSize=16, textColor=BLUE, fontName="Helvetica-Bold",
            spaceBefore=14, spaceAfter=6, leading=22),
    "h3": S("h3", fontSize=13, textColor=GREEN, fontName="Helvetica-Bold",
            spaceBefore=10, spaceAfter=4, leading=18),

    "body": S("body", fontSize=11, textColor=BLACK, leading=17,
              alignment=TA_JUSTIFY, spaceAfter=6),
    "body_c": S("body_c", fontSize=11, textColor=BLACK, leading=17,
                alignment=TA_LEFT, spaceAfter=4),

    "code": S("code", fontSize=9.5, fontName="Courier", textColor=colors.HexColor("#2d3748"),
              backColor=colors.HexColor("#edf2f7"), leading=14,
              leftIndent=12, rightIndent=12, spaceBefore=4, spaceAfter=8,
              borderPad=6),

    "bullet": S("bullet", fontSize=11, textColor=BLACK, leading=16,
                leftIndent=18, spaceAfter=3, bulletIndent=6),

    "caption": S("caption", fontSize=9, textColor=GRAY, alignment=TA_CENTER, spaceAfter=6),
    "note":    S("note",    fontSize=10, textColor=ORANGE, leading=15, spaceAfter=6,
                 leftIndent=10),
    "toc":     S("toc",    fontSize=11, textColor=BLACK, leading=16,
                 leftIndent=6, spaceAfter=2),
}

def HR():
    return HRFlowable(width="100%", thickness=1, color=colors.HexColor("#bee3f8"),
                      spaceAfter=8, spaceBefore=4)

def SP(h=0.3):
    return Spacer(1, h * cm)

def H(text, level=1):
    return Paragraph(text, styles[f"h{level}"])

def P(text):
    return Paragraph(text, styles["body"])

def Code(text):
    return Paragraph(text.replace("\n", "<br/>").replace(" ", "&nbsp;"),
                     styles["code"])

def Bullet(items, prefix="•"):
    return [Paragraph(f"{prefix}&nbsp;&nbsp;{t}", styles["bullet"]) for t in items]

def Note(text):
    return Paragraph(f"⚡ <i>{text}</i>", styles["note"])


# ── Table helpers ─────────────────────────────────────────────────────────────
HDR_STYLE = TableStyle([
    ("BACKGROUND",  (0, 0), (-1, 0), BLUE),
    ("TEXTCOLOR",   (0, 0), (-1, 0), WHITE),
    ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE",    (0, 0), (-1, -1), 9.5),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f0f4ff"), WHITE]),
    ("GRID",        (0, 0), (-1, -1), 0.4, colors.HexColor("#bee3f8")),
    ("VALIGN",      (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 7),
    ("RIGHTPADDING",(0, 0), (-1, -1), 7),
    ("TOPPADDING",  (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
])


def make_table(data, col_widths):
    rows = []
    for ri, row in enumerate(data):
        rows.append([Paragraph(str(cell), ParagraphStyle(
            "tc", fontSize=9.5, leading=13,
            textColor=WHITE if ri == 0 else BLACK,
            fontName="Helvetica-Bold" if ri == 0 else "Helvetica",
        )) for cell in row])
    t = Table(rows, colWidths=col_widths)
    t.setStyle(HDR_STYLE)
    return t


# ── Content builder ───────────────────────────────────────────────────────────

def build_content():
    story = []

    # ─────────────────────────────────────────────────────────────────────────
    # COVER PAGE
    # ─────────────────────────────────────────────────────────────────────────
    story += [
        SP(5),
        Paragraph("🏠 Immo.AI", styles["cover_title"]),
        Paragraph("Mauritania Real Estate Recommendation System", styles["cover_sub"]),
        SP(0.3),
        HR(),
        SP(0.2),
        Paragraph("Complete Technical Documentation", styles["cover_tag"]),
        Paragraph("For Beginners — From Zero to Full Understanding", styles["cover_tag"]),
        SP(1.5),
        Paragraph("Built with: Python · Streamlit · TF-IDF · Mistral AI · Google STT · edge-tts",
                  styles["caption"]),
        SP(0.5),
        Paragraph("Dataset: voursa.com — Mauritania's Largest Property Marketplace",
                  styles["caption"]),
        SP(0.5),
        Paragraph("Author: aliywedad  ·  Date: June 2026", styles["caption"]),
        PageBreak(),
    ]

    # ─────────────────────────────────────────────────────────────────────────
    # TABLE OF CONTENTS
    # ─────────────────────────────────────────────────────────────────────────
    story += [
        H("Table of Contents"),
        HR(),
    ]
    toc_items = [
        ("1.", "Project Overview — What Is Immo.AI?"),
        ("2.", "Project Architecture — How All Pieces Connect"),
        ("3.", "The Dataset — Where The Data Comes From"),
        ("4.", "Data Preprocessing — Cleaning Raw Data"),
        ("5.", "Feature Engineering — Making Data Smarter"),
        ("6.", "The Recommender System Algorithm"),
        ("   6a.", "Why Content-Based Filtering?"),
        ("   6b.", "Algorithms We DID NOT Use & Why"),
        ("   6c.", "TF-IDF: The Text Similarity Engine"),
        ("   6d.", "Hybrid Scoring Formula"),
        ("7.", "Voice to Text — How The Microphone Works"),
        ("8.", "Text to Speech — How The AI Speaks Back"),
        ("9.", "The AI Brain — Mistral Large & JARVIS"),
        ("10.", "The Web App — Streamlit UI"),
        ("11.", "Evaluation — How We Measure Quality"),
        ("12.", "Future Improvements"),
        ("13.", "Glossary — Key Terms Explained"),
    ]
    for num, title in toc_items:
        story.append(Paragraph(f"<b>{num}</b>&nbsp;&nbsp;{title}", styles["toc"]))
    story.append(PageBreak())

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 1 — PROJECT OVERVIEW
    # ─────────────────────────────────────────────────────────────────────────
    story += [
        H("1. Project Overview — What Is Immo.AI?"),
        HR(),
        P("Immo.AI is an intelligent real estate assistant for <b>Mauritania</b>. "
          "Think of it as a smart helper that you can <b>talk to</b> — using your "
          "voice or keyboard — and it will find property listings that match what you "
          "are looking for, from a database of over 1,852 real properties scraped from "
          "<b>voursa.com</b>, Mauritania's largest online marketplace."),
        SP(),
        P("Imagine you say: <i>\"Hey Jarvis, find me a villa in Tevragh Zeina under "
          "2 million MRU\"</i> — the system will:"),
    ]
    story += Bullet([
        "Convert your voice to text using Google's Speech Recognition",
        "Send that text to Mistral AI (like ChatGPT but by a French company)",
        "Mistral extracts: type=villa, location=Tevragh Zeina, max_price=2,000,000",
        "The recommender searches the database using TF-IDF + Hybrid Scoring",
        "Top results are formatted by Mistral and spoken back to you using neural TTS",
    ])
    story += [
        SP(),
        Note("This is a FULL AI pipeline: Voice → Text → NLP Understanding → "
             "Smart Search → Results → Voice response. All in real-time."),
        SP(0.5),
    ]

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 2 — ARCHITECTURE
    # ─────────────────────────────────────────────────────────────────────────
    story += [
        PageBreak(),
        H("2. Project Architecture — How All Pieces Connect"),
        HR(),
        P("Below is the complete data flow. Think of it like an assembly line where "
          "each step transforms the user's request into a useful answer."),
        SP(0.4),
        Code(
            "USER (voice or text)\n"
            "        |\n"
            "        v\n"
            "[src/voice.py]  transcribe_audio_bytes()\n"
            "  Google Speech Recognition (AR / FR / EN)\n"
            "        |\n"
            "        v\n"
            "[src/mistral_client.py]  chat_turn()\n"
            "  Mistral Large: understands request, asks follow-up questions\n"
            "  Emits <SEARCH>{keywords, location, price_min, price_max}</SEARCH>\n"
            "        |\n"
            "        v\n"
            "[src/recommender.py]  Recommender.recommend()\n"
            "  TF-IDF vectorisation + Cosine Similarity\n"
            "  + Price / Popularity / Recency hybrid scores\n"
            "        |\n"
            "        v\n"
            "[src/mistral_client.py]  format_results()\n"
            "  Mistral formats top listings as JARVIS briefing\n"
            "        |\n"
            "        v\n"
            "[src/voice.py]  text_to_speech_bytes()\n"
            "  edge-tts: British Neural TTS (JARVIS voice)\n"
            "        |\n"
            "        v\n"
            "USER hears the response + sees property cards in app"
        ),
        SP(0.5),
        H("File Structure", level=2),
    ]

    fs_data = [
        ["File / Folder", "Role", "Key Functions"],
        ["app.py", "Main Streamlit web application — UI, tabs, layout", "get_data(), get_recommender(), render_property_card()"],
        ["chatbot.py", "Original CLI prototype (voice chatbot without recommender)", "speak(), listen(), chat()"],
        ["e-commerce-mr.csv", "Raw dataset — 1,852+ property listings from voursa.com", "Input data"],
        ["src/data_cleaning.py", "Cleans and normalises the raw CSV", "_parse_price(), _parse_days_ago(), _main_location(), load_and_clean()"],
        ["src/recommender.py", "Core ML engine — TF-IDF + Hybrid Scoring", "engineer_features(), Recommender.fit(), recommend(), evaluate()"],
        ["src/mistral_client.py", "Mistral AI integration — JARVIS personality, search trigger, result formatting", "chat_turn(), format_results()"],
        ["src/voice.py", "Speech-to-Text + Text-to-Speech", "transcribe_audio_bytes(), text_to_speech_bytes(), audio_hash()"],
        ["requirements.txt", "Python package dependencies list", "—"],
        [".env", "Secret API keys (never commit to git)", "MISTRAL_API_KEY"],
    ]
    story.append(make_table(fs_data, [3*cm, 4.5*cm, 8.5*cm]))
    story.append(SP())

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 3 — DATASET
    # ─────────────────────────────────────────────────────────────────────────
    story += [
        PageBreak(),
        H("3. The Dataset — Where The Data Comes From"),
        HR(),
        P("The dataset is stored in <b>e-commerce-mr.csv</b> — a ~1.7 MB CSV file "
          "containing property listings scraped from <b>voursa.com</b>, Mauritania's "
          "main classifieds website."),
        SP(0.3),
        H("Dataset Statistics", level=2),
    ]
    ds_data = [
        ["Metric", "Value"],
        ["Total raw rows (approx)", "~2,000+"],
        ["After cleaning (real estate)", "1,852 listings"],
        ["Categories", "real_estate, vehicles, electronics, etc."],
        ["Locations covered", "Nouakchott districts + other Mauritanian cities"],
        ["Price range (after cleaning)", "~50,000 — 50,000,000 MRU"],
        ["Time period", "Listings from past days to years ago"],
    ]
    story.append(make_table(ds_data, [7*cm, 9*cm]))
    story += [
        SP(0.4),
        H("Raw CSV Columns", level=2),
    ]
    col_data = [
        ["Column Name", "What It Contains", "Example Value"],
        ["Title", "Property listing headline", "\"Villa F5 Tevragh Zeina avec jardin\""],
        ["Price", "Raw price string with currency", "\"1,500,000 MRU\""],
        ["Location+Name", "Full location text (renamed to Location)", "\"Tevragh Zeina, Nouakchott\""],
        ["Date_Posted", "Relative date string", "\"3 days ago\" / \"2 months ago\""],
        ["Views", "Number of times the listing was viewed", "\"842\""],
        ["Status", "Listing availability", "\"Available\" / \"Sold Out\""],
        ["Category", "Type of listing", "\"real_estate\""],
        ["Link", "URL to the listing on voursa.com", "https://voursa.com/..."],
        ["Image", "URL of the listing photo", "https://...jpg"],
    ]
    story.append(make_table(col_data, [3.5*cm, 5*cm, 7.5*cm]))

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 4 — DATA PREPROCESSING
    # ─────────────────────────────────────────────────────────────────────────
    story += [
        PageBreak(),
        H("4. Data Preprocessing — Cleaning Raw Data"),
        HR(),
        P("Raw data from real websites is <b>messy</b>. Prices have commas and "
          "currency symbols. Locations are inconsistently formatted. Some entries are "
          "duplicates or have nonsensical values. Before we can use any algorithm, we "
          "must clean the data. This is done in <b>src/data_cleaning.py</b>."),
        SP(0.3),
        H("Step 1: Price Parsing — _parse_price()", level=2),
        P("The Price column contains strings like <i>\"1,500,000 MRU\"</i>. We need a "
          "pure number. The function uses <b>regex</b> to strip every character that "
          "is NOT a digit, converting <i>\"1,500,000 MRU\"</i> → <b>1500000.0</b>. "
          "If the resulting number is ≤ 1, we treat it as invalid (placeholder entry) "
          "and discard it."),
        Code(
            "def _parse_price(raw):\n"
            "    digits = re.sub(r'[^\\d]', '', str(raw))  # Remove non-digits\n"
            "    val = float(digits)\n"
            "    return None if val <= 1 else val  # Discard junk values"
        ),
        H("Step 2: Date Parsing — _parse_days_ago()", level=2),
        P("Dates come as human-readable strings: <i>\"3 days ago\"</i>, "
          "<i>\"2 months ago\"</i>, <i>\"1 year ago\"</i>. We convert these to an "
          "integer number of days so we can compute freshness mathematically."),
        Code(
            "# '3 days ago'   → 3\n"
            "# '2 months ago' → 60  (2 × 30)\n"
            "# '1 year ago'   → 365\n"
            "# '5 hours ago'  → 0   (same day)"
        ),
        H("Step 3: Location Normalisation — _main_location()", level=2),
        P("Location strings vary wildly: <i>\"Tevragh Zeina, Nouakchott, Mauritania\"</i>, "
          "<i>\"Tev. Zeina\"</i>, etc. We match against a hard-coded list of known "
          "Mauritanian neighborhoods (Tevragh Zeina, Ksar, Arafat, Teyarett, Dar Naim, "
          "Toujounine, Sebkha, El Mina, Riyad, Nouadhibou, etc.) and return the "
          "canonical name. If no match, we take the first word."),
        H("Step 4: Removing Invalid Rows", level=2),
    ]
    story += Bullet([
        "Drop rows with no price (Price_MRU is NaN) or empty Title",
        "Strip whitespace from Title and remove empty-string titles",
    ])
    story += [
        H("Step 5: Outlier Removal (Per-Category Percentile Clipping)", level=2),
        P("Some listings have absurd prices — a typo turning 1,500,000 into "
          "1,500,000,000. These outliers would break our scoring. We compute the "
          "<b>1st and 99th percentile</b> of prices <b>per category</b> and discard "
          "everything outside that range."),
        Code(
            "for cat, group in df.groupby('Category'):\n"
            "    lo = group['Price_MRU'].quantile(0.01)\n"
            "    hi = group['Price_MRU'].quantile(0.99)\n"
            "    # Keep only rows within [lo, hi]"
        ),
        H("Step 6: Deduplication", level=2),
        P("If two rows have the same Title + Price + Main_Location, they are the same "
          "listing posted twice. We keep only one copy using pandas <b>drop_duplicates</b>."),
        H("Step 7: Views Normalisation", level=2),
        P("The Views column sometimes contains text or missing values. We convert it "
          "to a number, replacing errors with 0: "
          "<code>pd.to_numeric(df['Views'], errors='coerce').fillna(0)</code>"),
        SP(0.3),
        Note("After all cleaning steps, we have a clean, reliable dataset ready "
             "for feature engineering and recommendation."),
    ]

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 5 — FEATURE ENGINEERING
    # ─────────────────────────────────────────────────────────────────────────
    story += [
        PageBreak(),
        H("5. Feature Engineering — Making Data Smarter"),
        HR(),
        P("Raw data has Title and Price. But our algorithm needs <b>numerical vectors</b> "
          "(lists of numbers) to compute similarity. Feature engineering transforms "
          "raw columns into meaningful numbers. This is done in "
          "<b>src/recommender.py → engineer_features()</b>."),
        SP(0.3),
        H("Feature 1: Price Bucket (Categorical Label)", level=2),
        P("We divide all prices into 5 equal-sized groups using <b>quantile cuts</b> "
          "(pd.qcut). Each group gets a label:"),
    ]
    story.append(make_table([
        ["Bucket", "Meaning", "Price Range (approx)"],
        ["budget",     "Cheapest 20% of listings", "< 200,000 MRU"],
        ["affordable", "Next 20%",                  "200K – 500K MRU"],
        ["mid-range",  "Middle 20%",                "500K – 1.5M MRU"],
        ["premium",    "Upper 20%",                 "1.5M – 5M MRU"],
        ["luxury",     "Most expensive 20%",        "> 5M MRU"],
    ], [3*cm, 4*cm, 5*cm]))
    story += [
        SP(0.3),
        P("This label is then <b>appended to the text</b> that gets vectorised, so a "
          "query for \"cheap apartment\" will match budget/affordable listings better."),
        H("Feature 2: The Combined Text Field (_text)", level=2),
        P("We concatenate multiple columns into a single text field:"),
        Code(
            "df['_text'] = (Title + ' ' + Location + ' '\n"
            "               + Main_Location + ' ' + price_bucket)"
        ),
        P("This single text field is what the TF-IDF vectoriser reads. It combines "
          "the property name, location details, and price category into one rich "
          "description."),
        H("Feature 3: Popularity Score (Log-Normalised Views)", level=2),
        P("The number of views ranges from 0 to 50,000+. Such a huge range causes "
          "problems — a 50,000-view listing would completely dominate a 2,000-view one. "
          "We apply a <b>logarithm</b> to compress the scale:"),
        Code(
            "log_views = log(1 + views)  # log1p handles 0 views safely\n"
            "popularity = (log_views - min) / (max - min)  # Normalise to [0,1]"
        ),
        P("Result: a listing with 50,000 views scores ~1.0, one with 1,000 views "
          "scores ~0.6, and one with 10 views scores ~0.2. The differences are "
          "meaningful but not extreme."),
        H("Feature 4: Recency Score (Exponential Decay)", level=2),
        P("A listing posted today is more likely to still be available than one posted "
          "2 years ago. We model this with an <b>exponential decay</b> function:"),
        Code(
            "recency_score = exp(−days_ago / 30)\n\n"
            "# Examples:\n"
            "# Posted today (0 days):   exp(0)    = 1.00\n"
            "# Posted 1 month ago:       exp(-1)   = 0.37\n"
            "# Posted 3 months ago:      exp(-3)   = 0.05\n"
            "# Posted 1 year ago:        exp(-12)  ≈ 0.00"
        ),
        SP(0.3),
        H("Feature Summary Table", level=2),
    ]
    story.append(make_table([
        ["Feature", "Type", "Formula", "Purpose"],
        ["_text",           "Text",    "Title + Location + price_bucket",    "Input to TF-IDF"],
        ["price_bucket",    "String",  "pd.qcut(Price_MRU, q=5)",            "Semantic price label"],
        ["popularity_score","Float 0-1","normalize(log1p(Views))",           "Proxy quality signal"],
        ["recency_score",   "Float 0-1","exp(−days_ago / 30)",               "Freshness signal"],
        ["price_normalized","Float 0-1","MinMaxScaler on Price_MRU",         "Numeric price comparison"],
    ], [3*cm, 2.5*cm, 5.5*cm, 5*cm]))

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 6 — RECOMMENDER ALGORITHM
    # ─────────────────────────────────────────────────────────────────────────
    story += [
        PageBreak(),
        H("6. The Recommender System Algorithm"),
        HR(),
        P("A <b>recommender system</b> is an algorithm that, given a user's request, "
          "selects and ranks items from a database by how well they match. Think of "
          "Netflix recommending movies, or Amazon recommending products — same idea, "
          "applied to Mauritanian real estate."),
        SP(0.3),
        H("6a. Why Content-Based Filtering?", level=2),
        P("There are three main families of recommendation algorithms. The choice "
          "depends entirely on <b>what data is available</b>:"),
    ]
    story.append(make_table([
        ["Algorithm Family", "What It Needs", "Available?", "Our Decision"],
        ["Collaborative Filtering\n(User-User)",
         "Many users + their ratings/purchases\nto find 'users like you'",
         "NO — no user accounts", "Cannot use"],
        ["Collaborative Filtering\n(Item-Item)",
         "Which items users viewed/bought together\n(co-occurrence patterns)",
         "NO — no purchase/click log", "Cannot use"],
        ["Matrix Factorisation\n(SVD, ALS, NMF)",
         "User × Item interaction matrix\n(ratings or implicit feedback)",
         "NO — no interaction data", "Cannot use"],
        ["Neural CF / BERT4Rec",
         "Large labelled interaction dataset\n+ GPU compute",
         "NO — no labels, overkill", "Cannot use"],
        ["Knowledge Graph",
         "Ontology of property attributes\n(bedrooms, m², proximity to services)",
         "PARTIAL — only views", "Future work"],
        ["Content-Based Filtering ✓",
         "Item descriptions: title, price,\nlocation, views, date",
         "YES — all available", "USED HERE"],
    ], [3.5*cm, 5*cm, 3*cm, 3*cm]))
    story += [
        SP(0.3),
        P("<b>Content-Based Filtering</b> describes what the user wants "
          "(through conversation) and finds the most similar items based on "
          "their descriptions. No historical user data needed — perfect for a "
          "new platform."),

        H("6b. Algorithms We Did NOT Use — And Why", level=2),
        H("Collaborative Filtering (User-User / Item-Item)", level=3),
        P("These are the most popular recommendation algorithms used by Netflix and "
          "Amazon. They find patterns across many users: if Ali and Fatima both liked "
          "listings A, B, C, and Fatima also liked D, then Ali might like D too. "
          "<b>Problem:</b> This requires a database of users and their interaction "
          "history. Our system has no registered users, no ratings, and no purchase "
          "history. We only have listing metadata."),

        H("Matrix Factorisation (SVD, ALS, NMF)", level=3),
        P("These algorithms decompose a large User × Item matrix into smaller "
          "hidden factors (latent features). Spotify uses a variant of this. "
          "<b>Problem:</b> Without the User × Item matrix, these algorithms "
          "literally cannot be computed. They need user-item interactions as input."),

        H("Neural Networks / Deep Learning (BERT4Rec, NeuMF)", level=3),
        P("Modern deep learning models can learn complex patterns from interaction "
          "sequences. <b>Problems:</b> (1) Require tens of thousands of user "
          "interaction examples to train meaningfully; (2) Require GPU infrastructure; "
          "(3) Our dataset has 1,852 items — far too small to benefit from deep "
          "learning. A simple TF-IDF outperforms a neural network on small datasets."),

        H("Sentence Transformers / Semantic Search", level=3),
        P("Models like paraphrase-multilingual-MiniLM could understand that "
          "<i>\"maison\"</i> and <i>\"villa\"</i> are semantically related. "
          "<b>Problem:</b> These models have sizes of 100MB–400MB, require more "
          "compute, and need GPU for real-time inference. For this project's scale, "
          "TF-IDF with character n-grams achieves comparable results. This is marked "
          "as a future improvement."),

        H("6c. TF-IDF — The Text Similarity Engine", level=2),
        P("<b>TF-IDF</b> stands for Term Frequency – Inverse Document Frequency. "
          "It is a classical NLP technique that turns text into a numerical vector, "
          "where important and rare words get higher weights."),
        SP(0.2),
        H("What is TF-IDF? (For Beginners)", level=3),
        P("Imagine you have 1,000 property listings. The word 'the' appears in every "
          "single one — it carries zero information. But 'Tevragh Zeina' appears in "
          "only 150 listings — it is specific and informative. TF-IDF automatically "
          "assigns higher weight to rare, specific words:"),
        Code(
            "TF  (Term Frequency)     = How often does the word appear\n"
            "                           in THIS document?\n\n"
            "IDF (Inverse Doc Freq)   = How RARE is the word across\n"
            "                           ALL documents? (log(N/df))\n\n"
            "TF-IDF = TF × IDF\n\n"
            "  'the' in property text → TF high, IDF low → score ≈ 0\n"
            "  'Tevragh Zeina'        → TF varies, IDF high → score high\n"
            "  'villa'                → TF varies, IDF medium → medium score"
        ),
        H("Why Character N-grams? (Not Words)", level=3),
        P("Standard TF-IDF splits text into words. But our data contains "
          "<b>Arabic and French</b> mixed together. Arabic has complex morphology — "
          "the word for 'house' has 12+ forms depending on grammar. Instead of words, "
          "we use <b>character n-grams</b>: sequences of 2–4 characters."),
        Code(
            "# Word-level: 'villa' = 1 token\n"
            "# Char 2-gram: 'villa' = ['vi', 'il', 'll', 'la']\n"
            "# Char 3-gram: 'villa' = ['vil', 'ill', 'lla']\n"
            "# Char 4-gram: 'villa' = ['vill', 'illa']\n\n"
            "# This means 'villa', 'Villla' (typo), 'villaa' all\n"
            "# share many n-grams → fuzzy matching for free!"
        ),
        P("Benefits: handles Arabic without a tokenizer, handles spelling variants, "
          "handles French words embedded in Arabic text. Setting: <b>ngram_range=(2,4), "
          "max_features=8000, sublinear_tf=True, analyzer='char_wb'</b>."),

        H("Cosine Similarity — How We Compare Vectors", level=3),
        P("After TF-IDF converts texts to vectors (lists of 8,000 numbers), we need "
          "to measure how similar a query vector is to each listing's vector. We use "
          "<b>cosine similarity</b>: the cosine of the angle between two vectors."),
        Code(
            "cosine_similarity = (A · B) / (|A| × |B|)\n\n"
            "# Result: 0.0 = completely different\n"
            "#         1.0 = identical\n"
            "#         0.7 = very similar\n"
            "#         0.3 = somewhat related\n\n"
            "# Example: query='villa Tevragh Zeina'\n"
            "#   Listing A (villa, Tevragh Zeina) → similarity = 0.82\n"
            "#   Listing B (apartment, Arafat)    → similarity = 0.11"
        ),

        H("6d. Hybrid Scoring Formula", level=2),
        P("Text similarity alone is not enough. A listing perfectly matching the "
          "keywords but priced at 10× the budget, or listed 3 years ago, is not a "
          "good recommendation. We combine four signals into a <b>weighted hybrid score</b>:"),
        Code(
            "final_score = (0.65 × text_similarity)\n"
            "            + (0.15 × price_compatibility)\n"
            "            + (0.12 × popularity_score)\n"
            "            + (0.08 × recency_score)"
        ),
        SP(0.3),
    ]
    story.append(make_table([
        ["Component", "Weight", "What It Measures", "Why This Weight?"],
        ["Text Similarity",    "65%", "How well the title/location/type matches the user's query",
         "Query keywords are the PRIMARY signal — what the user asked for"],
        ["Price Compatibility","15%", "How well the price fits the user's budget (1 = perfect, 0 = over budget)",
         "Budget is a HARD constraint in real estate — 2nd most important"],
        ["Popularity Score",   "12%", "How many views the listing has (log-normalised)",
         "Proxy signal: popular listings are often better quality or priced"],
        ["Recency Score",      "8%",  "How recently the listing was posted (exponential decay)",
         "Fresh listings more likely still available — tie-breaker"],
    ], [3.5*cm, 1.5*cm, 5*cm, 5*cm]))
    story += [
        SP(0.3),
        Note("The weights were chosen based on domain knowledge: in real estate, "
             "WHAT you want and HOW MUCH you can pay dominate everything else. "
             "These weights can be tuned with user feedback data in the future."),
    ]

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 7 — VOICE TO TEXT
    # ─────────────────────────────────────────────────────────────────────────
    story += [
        PageBreak(),
        H("7. Voice to Text — How The Microphone Works"),
        HR(),
        P("When the user clicks the microphone button in the app, their voice is "
          "recorded as a <b>WAV audio file</b> (raw audio bytes). These bytes are "
          "then sent to Google's Speech Recognition service via the "
          "<b>SpeechRecognition</b> Python library. This is handled in "
          "<b>src/voice.py → transcribe_audio_bytes()</b>."),
        SP(0.3),
        H("Step-by-Step Process", level=2),
    ]
    story += Bullet([
        "User presses mic button → audio_recorder_streamlit captures audio at 16,000 Hz sample rate",
        "Audio bytes are written to a temporary WAV file on disk",
        "The SpeechRecognition library loads the WAV file as an AudioFile",
        "We try 3 languages in order: English (en-US) → Moroccan Arabic (ar-MA) → French (fr-FR)",
        "The first language that returns a non-empty result is used",
        "The temporary file is deleted and the transcribed text string is returned",
        "If all 3 languages fail, we return None and show a warning to the user",
    ])
    story += [
        SP(0.3),
        Code(
            "def transcribe_audio_bytes(audio_bytes: bytes) -> str | None:\n"
            "    # Save audio bytes to temp WAV file\n"
            "    with tempfile.NamedTemporaryFile(suffix='.wav') as f:\n"
            "        f.write(audio_bytes)\n"
            "    # Load and try multiple languages\n"
            "    with sr.AudioFile(tmp) as source:\n"
            "        audio = recognizer.record(source)\n"
            "    for lang in ('en-US', 'ar-MA', 'fr-FR'):\n"
            "        text = recognizer.recognize_google(audio, language=lang)\n"
            "        if text: return text  # Return first successful result"
        ),
        H("Audio Deduplication — audio_hash()", level=2),
        P("Streamlit re-runs the entire Python script on every user interaction. "
          "Without a deduplication check, the same audio clip would be re-transcribed "
          "on every rerun. We solve this with an <b>MD5 hash</b>: we compute a "
          "fingerprint of the audio bytes and only process it if the hash is different "
          "from the last processed audio."),
        H("Wake Word Detection", level=2),
        P("The app recognises wake words like <i>\"Hey Jarvis\"</i>, <i>\"Hi Jarvis\"</i>. "
          "If the transcribed text matches exactly, the AI replies with "
          "<i>\"At your service, sir\"</i> without calling the full recommender pipeline. "
          "If the text starts with a wake prefix, the prefix is stripped and only "
          "the actual query is sent to Mistral."),
        H("Older Voice Chatbot Prototype — chatbot.py", level=2),
        P("The file <b>chatbot.py</b> is the original command-line prototype built "
          "before the Streamlit app. It uses:"),
    ]
    story += Bullet([
        "speech_recognition for microphone input (real-time stream, not file upload)",
        "gTTS (Google Text-to-Speech) for audio output",
        "pygame to play the generated MP3 audio",
        "Mistral API for the chat conversation (no recommender, no property search)",
    ])
    story += [
        P("This prototype proved the voice + LLM pipeline worked before integrating "
          "the recommender system and building the Streamlit UI."),
    ]

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 8 — TEXT TO SPEECH
    # ─────────────────────────────────────────────────────────────────────────
    story += [
        PageBreak(),
        H("8. Text to Speech — How The AI Speaks Back"),
        HR(),
        P("After the AI generates a response text, we convert it back to audio so "
          "the user can hear it. This is handled in "
          "<b>src/voice.py → text_to_speech_bytes()</b>."),
        SP(0.3),
        H("Two TTS Engines Used in This Project", level=2),
    ]
    story.append(make_table([
        ["Engine", "Library", "Where Used", "Voice Quality", "Language"],
        ["Google TTS", "gTTS", "chatbot.py (prototype)", "Standard, robotic", "English"],
        ["Microsoft Neural TTS", "edge-tts", "src/voice.py (production)", "Neural, JARVIS-like", "EN + AR"],
    ], [3.5*cm, 2.5*cm, 3.5*cm, 3*cm, 3*cm]))
    story += [
        SP(0.3),
        H("The Production TTS: Microsoft edge-tts", level=2),
        P("The production app uses <b>edge-tts</b>, which connects to Microsoft Azure's "
          "Neural TTS service for free via the Edge browser API. It produces "
          "high-quality, natural-sounding speech — specifically the voice "
          "<b>en-GB-RyanNeural</b> (British male), chosen to sound like JARVIS from "
          "Iron Man."),
        Code(
            "JARVIS_VOICE = 'en-GB-RyanNeural'  # British male neural voice\n"
            "ARABIC_VOICE = 'ar-EG-ShakirNeural' # Egyptian Arabic male\n"
            "JARVIS_RATE  = '-5%'  # Slightly slower, more authoritative\n\n"
            "# Language detection: if >25% of characters are Arabic,\n"
            "# switch to the Arabic voice automatically\n"
            "def _is_arabic(text):\n"
            "    arabic_chars = sum(1 for c in text if '\\u0600' <= c <= '\\u06ff')\n"
            "    return arabic_chars > len(text) * 0.25"
        ),
        H("Why Async? — asyncio", level=2),
        P("The edge-tts library is <b>asynchronous</b> — it uses Python's async/await "
          "syntax to fetch audio without blocking. Since Streamlit runs synchronously, "
          "we create a new event loop, run the async function to completion, then "
          "close the loop. The result is raw MP3 bytes that we encode as base64 "
          "and inject into JavaScript for autoplay."),
        H("Autoplay in the Browser", level=2),
        P("Web browsers block audio autoplay by default for security. We work around "
          "this by injecting a hidden JavaScript snippet that creates an <code>Audio</code> "
          "object with a base64-encoded MP3 data URI and plays it immediately. The "
          "<code>played</code> set in session state ensures each message plays only once."),
    ]

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 9 — MISTRAL / JARVIS
    # ─────────────────────────────────────────────────────────────────────────
    story += [
        PageBreak(),
        H("9. The AI Brain — Mistral Large & JARVIS"),
        HR(),
        P("<b>Mistral Large</b> is a large language model (LLM) made by the French "
          "AI company Mistral AI. It is comparable to GPT-4 in capability. We use it "
          "for two distinct purposes in this project."),
        SP(0.3),
        H("Purpose 1: Conversational Understanding (chat_turn)", level=2),
        P("Mistral acts as a conversational agent with a very specific "
          "<b>system prompt</b> that gives it the JARVIS personality. The conversation "
          "follows a structured flow: gather property type → budget → neighborhood "
          "→ special requirements → confirm → trigger search."),
        P("The key innovation is the <b>&lt;SEARCH&gt; tag</b>: when Mistral has "
          "collected enough information, it appends a JSON block at the end of its "
          "response:"),
        Code(
            "<SEARCH>{\"keywords\": \"villa garden\",\n"
            "         \"location\": \"Tevragh Zeina\",\n"
            "         \"price_min\": null,\n"
            "         \"price_max\": 2000000}</SEARCH>"
        ),
        P("Python then extracts this JSON using regex, parses it, and passes the "
          "parameters to the recommender. The &lt;SEARCH&gt; tag is stripped from "
          "the displayed text — the user only sees the JARVIS dialogue."),
        H("Purpose 2: Result Formatting (format_results)", level=2),
        P("After the recommender returns matching listings, we pass them back to "
          "Mistral with a prompt asking it to write a professional JARVIS-style "
          "briefing. This transforms raw data into a polished response like: "
          "<i>\"I've located three properties matching your criteria, sir. "
          "The most promising is a 5-room villa in Tevragh Zeina at 1,800,000 MRU — "
          "well within your budget and with 842 views, indicating strong market "
          "interest, sir.\"</i>"),
        H("JARVIS Personality Rules", level=2),
    ]
    story += Bullet([
        "Always addresses user as 'sir' — at least once per message",
        "Opens with: 'Yes, sir', 'Of course, sir', 'Right away, sir', etc.",
        "Formal British English — never casual ('Hey!', 'Sure!', 'Awesome!')",
        "Maximum 3 sentences per reply — concise and precise",
        "References data like an AI: 'I've cross-referenced the database', 'The analysis indicates'",
        "One question per message — structured conversation flow",
    ])
    story += [
        H("Multi-Turn Conversation Memory", level=2),
        P("The full conversation history is stored in "
          "<b>st.session_state.conv</b> as a list of messages: "
          "<code>[{'role': 'user', 'content': '...'}, {'role': 'assistant', 'content': '...'}]</code>. "
          "This entire history is sent with every API call, so Mistral always has "
          "context. The display history (<b>st.session_state.display</b>) is separate "
          "— it also stores audio bytes and property card data for rendering."),
    ]

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 10 — STREAMLIT UI
    # ─────────────────────────────────────────────────────────────────────────
    story += [
        PageBreak(),
        H("10. The Web App — Streamlit UI"),
        HR(),
        P("<b>Streamlit</b> is a Python library that turns Python scripts into "
          "interactive web apps with no JavaScript or HTML needed. The main app "
          "is <b>app.py</b>."),
        SP(0.3),
        H("Three Tabs", level=2),
    ]
    story.append(make_table([
        ["Tab", "What It Shows"],
        ["🤖 AI Assistant", "The main chatbot: mic button, chat history, property cards with images/links/scores"],
        ["📊 Data Explorer", "Interactive charts: price distribution, top neighborhoods, views vs. price scatter, raw data table"],
        ["📈 Evaluation", "Run Precision@K evaluation on 8 test queries, see per-query scores, system architecture summary"],
    ], [4*cm, 12*cm]))
    story += [
        SP(0.3),
        H("Sidebar Filters", level=2),
        P("The sidebar shows live dataset statistics and allows the user to set:"),
    ]
    story += Bullet([
        "Min / Max Price (MRU) — applied to recommender queries",
        "Neighborhood filter — dropdown of all available locations",
        "Results to show — slider from 3 to 10",
        "Available only checkbox — filter out sold listings",
        "Reset Conversation button — clears all session state",
    ])
    story += [
        H("Property Cards", level=2),
        P("Each recommended property is rendered as a rich card inside an expander. "
          "The card shows: listing image (or placeholder), title, price in MRU, "
          "location, view count, availability badge, hybrid score percentage, "
          "price bucket badge, and a link button to the original voursa.com listing."),
        H("Caching Strategy", level=2),
        P("Two Streamlit cache decorators prevent re-loading data on every interaction:"),
    ]
    story += Bullet([
        "@st.cache_data — caches the cleaned DataFrame (load_and_clean) across sessions",
        "@st.cache_resource — caches the fitted Recommender object (expensive: builds TF-IDF matrix)",
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 11 — EVALUATION
    # ─────────────────────────────────────────────────────────────────────────
    story += [
        PageBreak(),
        H("11. Evaluation — How We Measure Quality"),
        HR(),
        P("Without user feedback (ratings, clicks), formal evaluation is challenging. "
          "We use a <b>Precision@K proxy metric</b>."),
        SP(0.3),
        H("What is Precision@K?", level=2),
        P("For a given query, we retrieve the top K results. Precision@K is the "
          "fraction of those K results that are considered 'relevant'. In our case, "
          "we define a result as relevant if its <b>hybrid score > 0.1</b> "
          "(meaning the text similarity is non-zero — at least some keyword matched)."),
        Code(
            "Precision@K = (number of relevant results in top K) / K\n\n"
            "Example: query='villa Tevragh Zeina', K=5\n"
            "  → 4 out of 5 results have score > 0.1\n"
            "  → Precision@5 = 4/5 = 0.80 (80%)"
        ),
        H("Test Query Set", level=2),
    ]
    story.append(make_table([
        ["Query", "What It Tests"],
        ["villa Tevragh Zeina luxury",    "High-end specific search"],
        ["cheap house Arafat",            "Budget + location"],
        ["apartment Ksar affordable",     "Type + location + price tier"],
        ["land terrain constructible",    "Mixed language (FR/EN)"],
        ["commercial space office",       "Non-residential property type"],
        ["maison dar vendre Sebkha",      "French/Arabic mix"],
        ["duplex Dar Naim",               "Specific property type + location"],
        ["studio apartment Teyarett",     "Small apartment search"],
    ], [7*cm, 9*cm]))
    story += [
        SP(0.3),
        H("Limitations of Current Evaluation", level=2),
        P("This proxy metric is better than nothing, but it has limitations:"),
    ]
    story += Bullet([
        "A result with score > 0.1 might still be irrelevant to a human evaluator",
        "We cannot compute NDCG or MAP without human-labelled relevance judgements",
        "The test set is small (8 queries) — may not represent all real user needs",
        "Evaluation is not cross-validated — no train/test split on the dataset",
    ])
    story += [
        SP(0.3),
        P("Better evaluation would require: collecting real user click data, "
          "asking domain experts to rate results, or running A/B tests comparing "
          "different algorithm configurations."),
    ]

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 12 — FUTURE IMPROVEMENTS
    # ─────────────────────────────────────────────────────────────────────────
    story += [
        PageBreak(),
        H("12. Future Improvements"),
        HR(),
    ]
    story.append(make_table([
        ["Improvement", "Impact", "Difficulty"],
        ["Multilingual sentence-transformers\n(paraphrase-multilingual-MiniLM)",
         "Better Arabic semantic matching — understands that 'villa' ≈ 'dar' ≈ 'منزل'",
         "Medium — needs GPU or API"],
        ["User session logging → implicit CF",
         "Unlock collaborative filtering signals from click/view patterns",
         "High — needs auth + DB"],
        ["Price-per-m² feature",
         "Fairer comparison across property sizes if area data added",
         "Low — data collection needed"],
        ["Re-ranking with LLM based on full conversation",
         "Higher precision for complex requirements",
         "Medium — more API calls"],
        ["Map visualisation (folium / pydeck)",
         "Show properties on an interactive map of Nouakchott",
         "Low — library integration"],
        ["Saved searches and alerts",
         "Notify users when new matching listings appear",
         "High — needs backend"],
        ["Rigorous evaluation (NDCG, MAP)",
         "Real accuracy measurement for algorithm comparison",
         "Medium — needs human labels"],
        ["FAISS vector index for speed",
         "Sub-millisecond search on 100K+ listings",
         "Low — library swap"],
    ], [5*cm, 7.5*cm, 3.5*cm]))

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 13 — GLOSSARY
    # ─────────────────────────────────────────────────────────────────────────
    story += [
        PageBreak(),
        H("13. Glossary — Key Terms Explained"),
        HR(),
    ]
    glossary = [
        ("Algorithm", "A set of rules or instructions that a computer follows to solve a problem."),
        ("API", "Application Programming Interface — a way for two programs to communicate. We call Mistral's API to get AI responses."),
        ("Async / asyncio", "A Python programming style where tasks can run concurrently without blocking each other, like downloading a file while doing something else."),
        ("Chatbot", "A program that has a text or voice conversation with a human, mimicking human dialogue."),
        ("Collaborative Filtering", "A recommendation method that uses patterns from many users ('people like you also liked...')."),
        ("Content-Based Filtering", "A recommendation method that compares the content/description of items to find similar ones."),
        ("Cosine Similarity", "A way to measure how similar two vectors are, based on the angle between them. 1.0 = identical, 0.0 = completely different."),
        ("CSV", "Comma-Separated Values — a simple spreadsheet format where each row is a line and columns are separated by commas."),
        ("Exponential Decay", "A mathematical curve where a value decreases rapidly at first then more slowly. Used for recency scoring."),
        ("Feature Engineering", "The process of creating new useful columns (features) from raw data to improve algorithm performance."),
        ("Hybrid Score", "A combined score that blends multiple signals (text, price, popularity, recency) with different weights."),
        ("LLM", "Large Language Model — an AI trained on billions of text examples, capable of understanding and generating natural language (e.g., Mistral, GPT-4)."),
        ("Log / log1p", "Logarithm — a mathematical operation that compresses large ranges. log(10)=1, log(1000)=3, log(1,000,000)=6."),
        ("MD5 Hash", "A fingerprint of data — the same input always gives the same hash, different inputs give different hashes. Used to detect duplicate audio."),
        ("Min-Max Scaling", "Normalising values to the range [0, 1] by: (value - min) / (max - min)."),
        ("N-gram", "A sequence of N consecutive characters or words. Char 3-gram of 'villa' = ['vil', 'ill', 'lla']."),
        ("NLP", "Natural Language Processing — the field of AI dealing with human language (reading, writing, speaking, understanding)."),
        ("Outlier", "A data point that is far from the typical range (e.g., a house listed at 1 billion MRU — likely a typo)."),
        ("Percentile", "A value below which a certain percentage of observations fall. 99th percentile = value that 99% of data is below."),
        ("Precision@K", "The fraction of the top K retrieved results that are actually relevant."),
        ("Quantile", "Dividing data into equal-sized groups. Quintiles (q=5) divide into 5 groups of 20% each."),
        ("Regex", "Regular Expression — a pattern for matching text. r'[^\\d]' matches any non-digit character."),
        ("Recommender System", "An algorithm that suggests relevant items to users based on their preferences or item features."),
        ("Session State", "In Streamlit, a dictionary that persists data across reruns of the app for a single user session."),
        ("Speech Recognition", "The technology that converts spoken audio into text. We use Google's service."),
        ("STT", "Speech-to-Text — converting audio/voice into written text."),
        ("Streamlit", "A Python library for building interactive web apps without needing JavaScript or HTML."),
        ("TF-IDF", "Term Frequency–Inverse Document Frequency — a way to convert text to numbers, giving higher weight to rare, specific words."),
        ("TTS", "Text-to-Speech — converting written text into spoken audio."),
        ("Vector", "A list of numbers. TF-IDF turns text into a vector of 8,000 numbers representing word importances."),
        ("WAV", "A raw audio file format. Uncompressed — large but high quality. Used internally before sending to Speech Recognition."),
    ]
    story.append(make_table(
        [["Term", "Definition"]] + [[t, d] for t, d in glossary],
        [3.5*cm, 12.5*cm]
    ))

    # ─────────────────────────────────────────────────────────────────────────
    # FINAL PAGE
    # ─────────────────────────────────────────────────────────────────────────
    story += [
        PageBreak(),
        SP(3),
        HR(),
        Paragraph("End of Documentation", ParagraphStyle(
            "end", fontSize=18, textColor=LIGHT_BLUE,
            alignment=TA_CENTER, fontName="Helvetica-Bold", spaceAfter=10)),
        Paragraph(
            "Immo.AI — Mauritania Real Estate Recommendation System<br/>"
            "Built with Content-Based Filtering · TF-IDF · Mistral AI · Google STT · Microsoft TTS",
            ParagraphStyle("endsub", fontSize=11, textColor=GRAY,
                           alignment=TA_CENTER, spaceAfter=6, leading=16)),
        SP(0.5),
        Paragraph("June 2026 · aliywedad · 22086@supnum.mr",
                  ParagraphStyle("endfoot", fontSize=9, textColor=GRAY,
                                 alignment=TA_CENTER)),
        HR(),
    ]

    return story


# ── Page decoration ───────────────────────────────────────────────────────────

def on_first_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#f7faff"))
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.restoreState()


def on_later_pages(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#f7faff"))
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    # Footer
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRAY)
    canvas.drawString(2*cm, 1.2*cm, "Immo.AI — Mauritania Real Estate Recommendation System")
    canvas.drawRightString(PAGE_W - 2*cm, 1.2*cm, f"Page {doc.page}")
    canvas.restoreState()


# ── Main ──────────────────────────────────────────────────────────────────────

OUTPUT = "/home/aliy/Projects/system_recomendation-old/system_recomendation/Immo_AI_Documentation.pdf"

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    leftMargin=2.2*cm,
    rightMargin=2.2*cm,
    topMargin=2.2*cm,
    bottomMargin=2.5*cm,
    title="Immo.AI — Mauritania Real Estate Recommendation System",
    author="aliywedad",
    subject="Complete Technical Documentation for Beginners",
)

doc.build(
    build_content(),
    onFirstPage=on_first_page,
    onLaterPages=on_later_pages,
)

print(f"PDF generated: {OUTPUT}")
