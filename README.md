# INVESTMATCH – Forensic Tool Recommender (Streamlit Edition)

A **rule‑based, AI‑free** recommendation engine that helps investigators find the most suitable digital forensics and OSINT tools based on their case requirements.  
The system uses weighted scoring to rank tools – fast, transparent, and fully deterministic.

## ✨ Features

- **Soft matching** – no hard exclusions; all tools are scored, mismatches are penalised.
- **Weighted scoring** – priorities: capabilities (35%), budget (20%), skill level (15%), platform (10%), access restrictions (10%), region (5%), quality (5%).
- **Two‑page interface** – main page for input + results, detail page for full tool information.
- **Streamlit powered** – pure Python, no HTML/JS, easy to deploy.
- **No API costs** – everything runs locally with your database(SQLite for testing).

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Elthiero/investmatch-hackathon.git
cd investmatch-hackathon
```

### 2. Set up a virtual environment

```bash
python -m venv venv             #create virtual environment
source venv/bin/activate        # Linux/macOS
or .\venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If you don’t have a `requirements.txt`, install manually:

```bash
pip install streamlit sqlalchemy pydantic
```

### 4. Prepare the database

First, initialise the database and import the tool data:

```bash
python admin.py --init
python admin.py --load list_of_tools.json
```

Verify the import:

```bash
python admin.py --list
```

### 5. Run the Streamlit app

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

## 📁 Project Structure

```
.
├── app.py                      # Main Streamlit page (input + results)
├── pages/
│   └── detail.py               # Tool detail page (accessed via query params)
├── database.py                 # SQLAlchemy engine & session
├── models.py                   # ForensicTool ORM model
├── schemas.py                  # Pydantic scenario input model
├── recommendation/
│   └── rule_based.py           # Hard filters + weighted scoring logic
├── admin.py                    # CLI for DB init, load, list, clear
├── list_of_tools_data.json     # Tool dataset (provided)
└── requirements.txt            # Dependencies
```

## ⚙️ How the Recommendation Works

1. **User submits a scenario** (investigation type, region, capabilities, budget, skill, platform, access level).
2. **All tools information are retrieved** from the database.
3. **Weighted scoring** calculates a 0‑100 score for each tool based on:
   - Capability match (ratio of required capabilities present)
   - Budget compatibility (free/paid/both)
   - Skill level (tool must not exceed user skill)
   - Platform support
   - Access restrictions (public/corporate/law enforcement)
   - Region match
   - Evidentiary admissibility quality
   - added some logic when filtering and checking match.
4. **Top 5 tools** are displayed with a short explanation.
5. Click **“View Details”** to see all stored fields for a tool.

## 🛠️ Admin Commands

| Command | Description |
|---------|-------------|
| `python admin.py --init` | Create database tables |
| `python admin.py --load list_of_tools.json` | Import tools from JSON |
| `python admin.py --list` | List all tool names |
| `python admin.py --clear` | Delete all tools (prompts confirmation) |

## 📦 Dependencies

- Python 3.9+
- Streamlit ≥ 1.33.0
- SQLAlchemy
- python-dotenv (optional)

Install all with:

```bash
pip install streamlit sqlalchemy pydantic
```

## 🧪 Testing

There are no automated tests yet, but you can manually verify:

- Run `python admin.py --list` after loading data.
- Launch Streamlit, try different scenarios, and check that scores are consistent.

## 🤝 Contributing

Contributions are welcome! Please open an issue or pull request for any improvements, bug fixes, or new features.

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- Tool data compiled from public sources.
- Built with [Streamlit](https://streamlit.io/) and [SQLAlchemy](https://www.sqlalchemy.org/)