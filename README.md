# ✉️ AI Email Assistant

A simple web app that drafts professional emails for you. Give it the
recipient's name, an email subject, and a short description of what the
email is about — the app uses **Google Gemini** to write a complete,
ready-to-send draft, which you can edit, copy, or download.

Built with **Python**, **Streamlit**, and the **Gemini API**.

---

## Features

- Takes recipient name, subject, and topic as input (plus optional recipient
  role, sender name, and key points to include)
- Choice of tone (Formal, Professional, Friendly, Casual, Persuasive,
  Apologetic), email type (follow-up, meeting request, thank-you, etc.), and
  length
- Input validation (required fields, basic email format check)
- Retry logic for transient Gemini API errors, with clear error messages
- Edit the generated draft in place before using it
- Download the draft as a `.txt` file
- Regenerate a new version with one click
- Session history of everything you've generated so far

---

## Project structure

```
.
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .gitignore
└── README.md
```

---

## 1. Prerequisites

- Python 3.9 or later
- A free Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

---

## 2. Local setup

```bash
# Clone your repo
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

# (Recommended) create a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Provide your API key

You have three options — use whichever is most convenient:

**Option A — paste it into the app's sidebar** (simplest, no setup needed;
the key is kept only in that browser session and never saved to disk).

**Option B — Streamlit secrets file** (recommended for local dev):

Create `.streamlit/secrets.toml` in the project root:

```toml
GEMINI_API_KEY = "your-api-key-here"
```

This file is already excluded via `.gitignore`, so it won't be committed.

**Option C — environment variable:**

```bash
export GEMINI_API_KEY="your-api-key-here"   # Windows: set GEMINI_API_KEY=your-api-key-here
```

### Run the app

```bash
streamlit run app.py
```

Streamlit will open the app in your browser at `http://localhost:8501`.

---

## 3. Usage

1. Fill in the recipient's name, your name, the email subject, and a short
   description of what the email should say.
2. (Optional) Add the recipient's role, any key points to include, and pick
   a tone/type/length in the sidebar.
3. Click **Generate Email**.
4. Edit the draft if needed, then **download it** or copy it directly from
   the text box.

---

## 4. Deploying to Streamlit Community Cloud

1. Push this project to a public (or private) GitHub repository:

   ```bash
   git init
   git add .
   git commit -m "Initial commit: AI Email Assistant"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git push -u origin main
   ```

2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with
   GitHub.
3. Click **New app**, select your repository/branch, and set the main file
   path to `app.py`.
4. Under **Advanced settings → Secrets**, add:

   ```toml
   GEMINI_API_KEY = "your-api-key-here"
   ```

5. Click **Deploy**. Streamlit Cloud will install `requirements.txt`
   automatically and give you a public URL.

> Users can also paste their own key into the sidebar at runtime, so the
> app works even if you don't set a default key in secrets.

---

## 5. Testing notes

The app's core logic (input sanitization, email-format validation, and
prompt construction) is written as pure functions in `app.py` so it can be
tested independently of the Streamlit UI. During development this project
was verified by:

- Compiling `app.py` to catch syntax errors
- Running `streamlit run app.py` headlessly and confirming it serves
  successfully
- Unit-testing `sanitize()`, `is_valid_email()`, and `build_prompt()` with
  a range of normal, empty, and edge-case inputs

If you add new logic, prefer keeping it in small, pure functions near the
top of `app.py` so it stays easy to test the same way.

---

## 6. Troubleshooting

| Problem | Likely cause / fix |
|---|---|
| "No Gemini API key found" | Add a key in the sidebar, `secrets.toml`, or the `GEMINI_API_KEY` env var |
| "The API key was rejected" | Double-check you copied the full key from AI Studio with no extra spaces |
| "Rate limit reached" | You're on the free tier and sent too many requests too quickly — wait a bit and retry |
| App won't start | Confirm you're using Python 3.9+ and ran `pip install -r requirements.txt` |

---

## License

Free to use and modify for personal or portfolio projects.

---

## Deployment

Link: https://ai-email-assistant-03.streamlit.app/

---
