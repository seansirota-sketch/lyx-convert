import streamlit as st
import anthropic
import base64
import io
import os
from pdf2image import convert_from_bytes
from PIL import Image

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PDF → LaTeX | מבחני מתמטיקה",
    page_icon="📐",
    layout="wide",
)

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Heebo', sans-serif;
        direction: rtl;
    }

    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2.5rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
        color: white;
    }
    .main-header h1 { font-size: 2.4rem; font-weight: 700; margin-bottom: 0.5rem; }
    .main-header p  { font-size: 1.1rem; opacity: 0.8; margin: 0; }

    .upload-zone {
        border: 2.5px dashed #0f3460;
        border-radius: 14px;
        padding: 2.5rem;
        text-align: center;
        background: #f8f9ff;
        transition: all 0.3s ease;
    }

    .result-box {
        background: #1e1e2e;
        border-radius: 14px;
        padding: 1.5rem;
        font-family: 'Courier New', monospace;
        font-size: 0.88rem;
        color: #cdd6f4;
        line-height: 1.7;
        max-height: 600px;
        overflow-y: auto;
        white-space: pre-wrap;
        word-break: break-word;
        direction: ltr;
        text-align: left;
    }

    .status-processing {
        background: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        text-align: center;
        font-weight: 600;
        color: #664d03;
    }
    .status-success {
        background: #d1fae5;
        border: 1px solid #10b981;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        text-align: center;
        font-weight: 600;
        color: #065f46;
    }
    .info-card {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
    }
    .stTextArea textarea {
        font-family: 'Courier New', monospace !important;
        font-size: 0.85rem !important;
        direction: ltr !important;
        text-align: left !important;
    }
</style>
""", unsafe_allow_html=True)

# ─── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>📐 PDF → LaTeX</h1>
    <p>המרת מבחני מתמטיקה אוטומטית לפורמט LaTeX / LyX</p>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar – Settings ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ הגדרות")

    # ═══════════════════════════════════════════════════════════════
    # 🔑 כאן מזינים את ה-API KEY של Anthropic!
    #
    # איך מקבלים מפתח?
    #   1. היכנס ל: https://console.anthropic.com
    #   2. לחץ "API Keys" בתפריט הצד
    #   3. לחץ "Create Key" ותן לו שם
    #   4. העתק את המפתח (מתחיל ב- sk-ant-...)
    #   5. הדבק אותו בשדה הטקסט למטה
    #
    # ⚠️ אל תשתף את המפתח עם אף אחד!
    # ═══════════════════════════════════════════════════════════════
    api_key = st.text_input(
        "🔑 Anthropic API Key",
        type="password",          # ← מוצג כ-*** לאבטחה
        placeholder="sk-ant-...",
        help="ניתן לקבל מ-console.anthropic.com",
    )

    st.markdown("---")
    st.markdown("### 📋 על האפליקציה")
    st.markdown("""
    <div class="info-card">
    <b>מה האפליקציה עושה?</b><br>
    מעלה PDF של מבחן מתמטיקה, ממיר כל עמוד לתמונה, ומשתמש ב-Claude Vision כדי לחלץ
    את הנוסחאות בפורמט LaTeX מדויק.
    <br><br>
    <b>פורמט הפלט:</b><br>
    • <code>$...$</code> — נוסחה בשורה<br>
    • <code>$$...$$</code> — נוסחה בשורה נפרדת<br>
    • <code>## / ###</code> — כותרות<br>
    • מבנה שאלות / סעיפים
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    max_pages = st.slider("מקסימום עמודים לעיבוד", 1, 20, 15)
    dpi = st.select_slider("רזולוציה (DPI)", options=[150, 200, 250, 300], value=200)


# ─── Helpers ───────────────────────────────────────────────────────────────────

def pdf_to_images(pdf_bytes: bytes, max_pages: int, dpi: int) -> list[Image.Image]:
    """המרת PDF (bytes) לרשימת תמונות PIL — עמוד אחד = תמונה אחת."""
    images = convert_from_bytes(pdf_bytes, dpi=dpi, first_page=1, last_page=max_pages)
    return images


def image_to_base64(img: Image.Image) -> str:
    """
    המרת תמונת PIL ל-Base64 כדי לשלוח ל-API של Anthropic.
    Base64 הוא פורמט טקסטואלי שמאפשר להכניס קבצים בינאריים בתוך JSON.
    """
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=90)
    return base64.standard_b64encode(buf.getvalue()).decode("utf-8")


# ─── System Prompt (הנחיות לקלוד) ─────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert LaTeX transcription assistant specializing in university-level mathematics exams.
Your task is to convert exam pages to clean LaTeX/LyX-compatible text.

CRITICAL RULES:
1. ALL math must be wrapped in LaTeX delimiters:
   - Inline math:  $formula$
   - Display math: $$formula$$
2. Preserve the structure: question numbers (שאלה 1, שאלה 2...) and sub-questions (א', ב', ג').
3. Use Markdown headings: ## for questions, ### for sub-questions.
4. Do NOT add any prose, comments, or explanations of your own.
5. Do NOT output triple-backtick code fences — just raw LaTeX text.
6. Preserve Hebrew text exactly as written.
7. For matrices, use the LaTeX matrix environment: \\begin{pmatrix}...\\end{pmatrix}
8. For systems of equations, use the cases environment.
9. For fractions use \\frac{}{}, for roots \\sqrt{}, for subscripts/superscripts use _ and ^.
10. IGNORE and DO NOT transcribe: page numbers, university logos, repeated headers/footers.
11. Output ONLY the transcribed content — nothing else.
"""

def extract_latex_from_images(images: list[Image.Image], api_key: str) -> str:
    """
    שולח את תמונות הדפים ל-Claude Vision ומקבל בחזרה טקסט LaTeX.

    תהליך:
      1. יוצר client של Anthropic עם ה-API Key שהוכנס
      2. בונה רשימת content blocks: טקסט + תמונות בBase64
      3. שולח ל-Claude ומחזיר את תשובתו
    """
    # ─── יצירת הלקוח עם ה-API KEY ─────────────────────────────────────────────
    # ⬇️ api_key מגיע מהשדה שמילאת בסרגל הצד
    client = anthropic.Anthropic(api_key=api_key)

    # בניית רשימת ה-blocks: הוראות + תמונה לכל עמוד
    content = [
        {
            "type": "text",
            "text": (
                "Please transcribe ALL pages below into clean LaTeX text.\n"
                "Follow the system instructions exactly.\n"
                f"Total pages: {len(images)}\n\n"
                "--- BEGIN TRANSCRIPTION ---"
            ),
        }
    ]

    for i, img in enumerate(images):
        content.append({
            "type": "text",
            "text": f"\n\n=== Page {i + 1} ===\n",
        })
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": image_to_base64(img),   # ← Base64 encoding של התמונה
            },
        })

    # ═══════════════════════════════════════════════════════════════
    # 🤖 שליחה ל-API של Claude
    #
    # model: claude-sonnet-4-6 = Claude 3.5 Sonnet
    #        זהו המודל הכי מדויק לזיהוי נוסחאות מתמטיות מתמונות.
    #        אפשר להחליף ב-"claude-haiku-4-5-20251001" לתגובה מהירה יותר
    #        (אך פחות מדויקת בנוסחאות מורכבות).
    #
    # max_tokens: מספר הטוקנים המקסימלי בתשובה.
    #             8192 מספיק לכ-15 עמודים של מבחן.
    # ═══════════════════════════════════════════════════════════════
    response = client.messages.create(
        model="claude-sonnet-4-6",   # ← Claude 3.5 Sonnet — הכי מדויק לנוסחאות מתמטיות
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}],
    )

    return response.content[0].text


# ─── Main UI ───────────────────────────────────────────────────────────────────

col_upload, col_result = st.columns([1, 1], gap="large")

with col_upload:
    st.markdown("### 📂 העלאת קובץ PDF")
    uploaded = st.file_uploader(
        "גרור קובץ PDF לכאן או לחץ לבחירה",
        type=["pdf"],
        label_visibility="collapsed",
    )

    if uploaded:
        st.success(f"✅ הועלה: **{uploaded.name}** ({uploaded.size / 1024:.1f} KB)")

        # תצוגה מקדימה של עד 3 עמודים ראשונים
        with st.spinner("טוען תצוגה מקדימה..."):
            try:
                preview_imgs = convert_from_bytes(uploaded.read(), dpi=80, first_page=1, last_page=3)
                uploaded.seek(0)   # ← חובה לאפס את הסמן אחרי קריאה ראשונה!
                cols = st.columns(min(len(preview_imgs), 3))
                for i, (c, img) in enumerate(zip(cols, preview_imgs)):
                    with c:
                        st.image(img, caption=f"עמוד {i+1}", use_container_width=True)
            except Exception as e:
                st.warning(f"לא ניתן להציג תצוגה מקדימה: {e}")
                uploaded.seek(0)

        st.markdown("---")

        if not api_key:
            st.warning("⚠️ הכנס Anthropic API Key בסרגל הצד השמאלי כדי להמשיך.")
        else:
            if st.button("🚀 המר ל-LaTeX", type="primary", use_container_width=True):
                with col_result:
                    status_placeholder = st.empty()

                    try:
                        # שלב 1: המרת PDF לתמונות
                        status_placeholder.markdown(
                            '<div class="status-processing">⏳ שלב 1/2 — ממיר PDF לתמונות...</div>',
                            unsafe_allow_html=True,
                        )
                        pdf_bytes = uploaded.read()
                        images = pdf_to_images(pdf_bytes, max_pages=max_pages, dpi=dpi)
                        n = len(images)

                        # שלב 2: שליחה ל-Claude Vision
                        status_placeholder.markdown(
                            f'<div class="status-processing">🤖 שלב 2/2 — שולח {n} עמוד(ים) ל-Claude Vision...</div>',
                            unsafe_allow_html=True,
                        )
                        latex_text = extract_latex_from_images(images, api_key)

                        status_placeholder.markdown(
                            f'<div class="status-success">✅ הומרו {n} עמודים בהצלחה!</div>',
                            unsafe_allow_html=True,
                        )

                        # שמירה ב-session state כדי שהתוצאה תישמר גם אחרי לחיצות נוספות
                        st.session_state["latex_result"] = latex_text
                        st.session_state["filename"]     = uploaded.name

                    except anthropic.AuthenticationError:
                        status_placeholder.error("❌ API Key שגוי — בדוק שהמפתח שהכנסת נכון.")
                    except Exception as e:
                        status_placeholder.error(f"❌ שגיאה: {e}")


with col_result:
    st.markdown("### 📄 תוצאה — LaTeX")

    if "latex_result" in st.session_state:
        latex = st.session_state["latex_result"]

        # תיבת טקסט גדולה להעתקה — Ctrl+A → Ctrl+C
        st.text_area(
            "LaTeX Output  (סמן הכל עם Ctrl+A ואז Ctrl+C להעתקה)",
            value=latex,
            height=500,
            key="latex_ta",
            help="הטקסט מוכן לייבוא ל-LyX דרך: File > Import > LaTeX (plain)",
        )

        # כפתור הורדה כ-.tex
        fname = st.session_state.get("filename", "exam").replace(".pdf", "")
        st.download_button(
            label="⬇️ הורד כקובץ .tex",
            data=latex.encode("utf-8"),
            file_name=f"{fname}.tex",
            mime="text/plain",
            use_container_width=True,
        )

        # סטטיסטיקות
        lines   = latex.count("\n")
        dollars = latex.count("$")
        st.caption(f"📊 {len(latex):,} תווים | {lines:,} שורות | ~{dollars // 2} נוסחאות")

    else:
        st.markdown("""
        <div style="border:2px dashed #cbd5e1;border-radius:12px;padding:3rem;text-align:center;color:#94a3b8;">
            <div style="font-size:3rem;">📋</div>
            <div style="font-size:1.1rem;margin-top:1rem;">התוצאה תופיע כאן לאחר ההמרה</div>
        </div>
        """, unsafe_allow_html=True)


# ─── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#94a3b8;font-size:0.85rem;'>"
    "מופעל על-ידי Claude Sonnet 3.5 Vision · pdf2image · Streamlit"
    "</div>",
    unsafe_allow_html=True,
)
