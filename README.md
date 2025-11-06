# 🧭 The Hub

**The Hub** is a unified Streamlit workspace that hosts multiple intelligent agents under one interface.  
Currently, it includes:

- 🧠 **Chat Therapy App** — A conversational AI designed for reflective, therapeutic-style dialogue, with export to PDF/Markdown.
- 🧩 **Product → JSON Extractor** — An intelligent parser that converts free-form product descriptions into structured JSON for analytics and automation.

---

## 🚀 Features

| Feature | Description |
|----------|-------------|
| **Central Hub (hub.py)** | Provides an interactive landing page with tiles to access each sub-app. |
| **Therapy Agent** | Offers contextual, safe, patient-style conversation flow powered by LLM. |
| **Product Extractor Agent** | Converts natural language product data into machine-readable JSON. |
| **Local Sessions** | Each sub-app saves chats/sessions to JSON for continuity. |
| **Groq + LangChain Support** | Uses `groq:llama-3.3-70b-versatile` for fast, factual responses. |
| **Simple Deployment** | Runs fully in Streamlit, ready to push to GitHub and Streamlit Cloud. |

---

## 🗂️ Folder Structure

```
the_hub/
├── hub.py                # Main launcher (Hub UI)
├── app3.py               # Chat Therapy app (alias: app2.py)
├── prodapp2.py           # Product → JSON Extractor (alias: prodapp.py)
├── prodbot.py            # Backend logic for product agent
├── agent.py              # Backend logic for therapy agent
├── assets/
│   ├── favicon.png
│   ├── green.png         # Used by therapy app
│   ├── red.png           # Used by therapy app
│   └── DejaVuSans.ttf    # Font for PDF export
├── sessions/             # Auto-created user session files (ignored in .gitignore)
├── .env                  # Contains GROQ_API_KEY and configs (ignored in Git)
├── requirements.txt      # Python dependencies
├── .gitignore
└── README.md
```

---

## 🧰 Installation

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/the_hub.git
cd the_hub
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate    # (Linux/macOS)
venv\Scripts\activate       # (Windows)
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the root directory:
```
GROQ_API_KEY=your_groq_api_key_here
```

---

## ▶️ Running the App

```bash
streamlit run hub.py
```

This launches **The Hub** in your browser (usually `http://localhost:8501`).

From the home screen:
- Click **🧠 Chat Therapy** to open the reflective conversation app.  
- Click **🧩 Product Extractor** to use the structured JSON conversion tool.

---

## 🧩 Requirements

Minimum dependencies (included in `requirements.txt`):

```
streamlit
python-dotenv
langchain
groq
fpdf
pandas
```

> Optional: `openpyxl` and `matplotlib` if you plan to visualize or export additional data later.

---

## 🛡️ Notes & Best Practices

- Never commit `.env` or any file containing API keys or secrets.  
- Session data (`/sessions/`) and temporary logs are already excluded via `.gitignore`.  
- Use separate Groq API keys for development and production environments.  
- You can add new agent tiles by extending the tile block inside `hub.py`.

---

## 💡 Future Expansion

- [ ] Add AI-driven sales assistant (plug-and-play module)  
- [ ] Include analytics visualization for extracted JSON data  
- [ ] Deploy to Streamlit Cloud or HuggingFace Spaces  
- [ ] Integrate Supabase for persistent chat storage  

---

## 👨‍💻 Author

**Venkata Pavan Kumar Alapati**  
🎓 M.S. Data Analytics | Clark University  
💼 AI & Data Engineer • Creator of *AIIDA* and *Stomes* projects  

---

## 📜 License

This project is released under the **MIT License** — you’re free to modify and distribute it with attribution.
