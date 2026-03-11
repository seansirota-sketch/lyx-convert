<<<<<<< HEAD
# lyx-convert
=======
# 📐 PDF → LaTeX — מבחני מתמטיקה

אפליקציית Streamlit להמרת PDF של מבחני מתמטיקה לפורמט LaTeX / LyX.

---

## ⚡ התקנה מהירה

### דרישות מקדימות
- Python 3.9+
- **poppler** (נדרש עבור `pdf2image`):
  - **macOS:** `brew install poppler`
  - **Ubuntu/Debian:** `sudo apt-get install poppler-utils`
  - **Windows:** הורד מ-https://github.com/oschwartz10612/poppler-windows/releases ← חלץ לתיקייה ‹C:\poppler› ← הוסף `C:\poppler\Library\bin` ל-PATH

### התקנת תלויות Python

```bash
pip install -r requirements.txt
```

### הרצת האפליקציה

```bash
streamlit run app.py
```

הדפדפן ייפתח אוטומטית בכתובת `http://localhost:8501`

---

## 🔑 הגדרת API Key

1. גש ל-[console.anthropic.com](https://console.anthropic.com)
2. צור API Key חדש
3. הדבק אותו בשדה **"Anthropic API Key"** בצד שמאל של האפליקציה

---

## 🚀 שימוש

1. הכנס את ה-API Key בסרגל הצד
2. לחץ **"העלאת קובץ PDF"** ובחר את קובץ המבחן
3. כוון את הגדרות העמודים ו-DPI אם צריך
4. לחץ **"המר ל-LaTeX"**
5. העתק את הטקסט או הורד קובץ `.tex`

---

## 📋 פורמט הפלט

| סוג | פורמט |
|-----|--------|
| נוסחה בשורה | `$E = mc^2$` |
| נוסחה בשורה נפרדת | `$$\int_0^\infty f(x)\,dx$$` |
| שאלה ראשית | `## שאלה 1` |
| תת-שאלה | `### סעיף א'` |

---

## 💡 טיפים לתוצאות מיטביות

- **DPI 200–250** מאוזן בין דיוק למהירות
- PDF ברזולוציה טובה → תוצאות טובות יותר
- לכ-15 עמודים לוקח בממוצע 20–40 שניות

---

## 📁 מבנה קבצים

```
pdf_to_latex_app/
├── app.py            # קוד האפליקציה הראשי
├── requirements.txt  # תלויות Python
└── README.md         # הוראות שימוש
```
>>>>>>> c3ca0b4 (first commit)
