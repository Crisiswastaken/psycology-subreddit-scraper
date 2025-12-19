# PsycoScraper

PsycoScraper is a small set of Python utilities to scrape, clean, and export Reddit posts focused on psychology and mental-health-related subreddits. It includes a scraping script that collects post titles and bodies, a cleaning/compilation pipeline that deduplicates and prepares a JSONL dataset, and a converter to render posts to PDF.

**Key features:**
- Scrape top posts from multiple psychology / mental health subreddits using PRAW (Reddit API wrapper).
- Clean and deduplicate collected posts into a single `compiled_clean.jsonl` dataset.
- Export cleaned posts to PDF using ReportLab.

**Quick links:**
- Scripts: [scripts](scripts)
- Docs: [docs](docs/venv-setup.md)
- Outputs: [output](output)

**Requirements**
- Python 3.8+
- See `requirements.txt` for primary packages; install with:

```bash
pip install -r requirements.txt
```

Note: `json` and `time` are part of the Python standard library. For `.env` support, the scraper optionally uses `python-dotenv` (install with `pip install python-dotenv`).

**Setup**
1. Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
pip install python-dotenv
```

3. Create a Reddit app to get API credentials:

- Visit https://www.reddit.com/prefs/apps and create a script app. Save `client_id`, `client_secret`, and set a `user_agent`.

4. Add credentials to a `.env` file in the project root (or set environment variables):

```
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
USER_AGENT=your_user_agent_here
OUTPUT_DIRECTORY=output
OUTPUT_FILENAME=reddit_psych_posts.json
```

**Usage**

- Run the scraper (collect posts):

```bash
python scripts/scraper.py
```

This will connect to Reddit in read-only mode, iterate through the configured `SUBREDDITS` (see `scripts/scraper.py`), and save results to the `output/` directory.

- Clean and compile scraped JSON files into JSONL (one post per line):

```bash
python scripts/clean_compile.py
```

The default output filename is `compiled_clean.jsonl`.

- Convert a JSON/JSONL dataset to PDF:

```bash
python scripts/convert_pdf.py
# or import json_to_pdf from scripts/convert_pdf and call in Python
```

**Outputs**
- Raw per-run JSON files are written to `output/`.
- Cleaned dataset: `compiled_clean.jsonl` (one JSON post per line) — suitable for analysis or model training.
- Example PDF export: `compiled_posts.pdf` (when running the converter).

**Configuration & customization**
- Edit `scripts/scraper.py` to change `SUBREDDITS`, `POST_LIMIT`, `REQUEST_DELAY`, or output filename/location.
- `scripts/clean_compile.py` contains options for minimum body length, duplicate removal, and input/output paths.

**Testing**
- A small check script exists at `tests/reddit-api-check.py` that demonstrates a minimal PRAW connection.

**Contributing**
- Contributions are welcome. Open an issue or a pull request with a clear description and tests/examples when appropriate.

**License**
- See the `LICENSE` file in this repository for license details.

**Contact**
- If you want help or have questions, open an issue or reach out via the contact information in the repository.




