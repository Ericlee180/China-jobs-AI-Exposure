# China Job Market Visualizer

A benchmark / port of Andrej Karpathy's [jobs](https://github.com/karpathy/jobs) project, adapted for China's job market. Uses data from China's official 职业数字展馆 (Digital Career Museum) covering **111 occupations**, with LLM-powered AI exposure scoring.

**Live demo: [Ericlee180.github.io/china-jobs](https://Ericlee180.github.io/china-jobs)**

## What's here

This project follows the same pipeline as Karpathy's original:
- Scrape occupation data from official Chinese sources
- Convert to clean Markdown format
- Score each occupation for "AI Exposure" (0-10) using LLM
- Visualize as an interactive treemap

Each rectangle's **area** represents estimated employment scale; **color** shows AI exposure score.

## Data pipeline

1. **Get occupation list** (`get_occupations.py`) — Fetch all 111 occupations from API → `occupations-cn-full.json`
2. **Scrape details** (`scrape.py`) — Download career detail JSONs → `html/`
3. **Convert to Markdown** (`process.py`) — JSON → readable Markdown → `pages/`
4. **Tabulate** (`make_csv.py`) — Extract structured fields → `occupations.csv`
5. **Score** (`score.py`) — LLM scores each occupation (0-10 + rationale) → `scores.json`
6. **Build site data** (`build_site_data.py`) — Merge data → `site/data.json`
7. **Website** (`site/index.html`) — Interactive treemap visualization

## Key files

| File | Description |
|------|-------------|
| `occupations-cn-full.json` | Master list of 111 occupations |
| `occupations.csv` | Structured summary (education, grades, etc.) |
| `scores.json` | AI exposure scores (0-10) with rationales |
| `pages/` | Markdown files for each occupation |
| `site/` | Static website with treemap |

## Scoring rubric (AI Exposure 0-10)

| Score | Category | Description |
|-------|----------|-------------|
| 0-2 | Minimal | Physical/hands-on work, real-time human interaction |
| 3-4 | Low | Mostly physical; AI assists with peripheral tasks |
| 5-6 | Moderate | Mix of physical and knowledge work |
| 7-8 | High | Predominantly computer-based knowledge work |
| 9-10 | Very high | Fully digital, routine information processing |

## Setup

```bash
# Clone
git clone https://github.com/your-username/china-jobs.git
cd china-jobs

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Step by step
```bash
python get_occupations.py      # Fetch occupation list (optional — file already included)
python scrape.py               # Download career details
python process.py              # Convert JSON → Markdown
python make_csv.py             # Extract CSV summary
python score.py                # Run LLM scoring (requires API key)
python build_site_data.py      # Build frontend data
```

### Serve locally
```bash
cd site && python -m http.server 8000
```

## Scoring with LLM
Requires an API key. Supported options:

DeepSeek (recommended for China): DEEPSEEK_API_KEY=your_key in .env

## Data source
职业数字展馆 — China's official Digital Career Museum, maintained by the Ministry of Human Resources and Social Security.

## Acknowledgments
Andrej Karpathy / jobs — Original inspiration and architecture

China's Ministry of Human Resources and Social Security — Open career data

## Disclaimer
This is a personal research tool. AI exposure scores are rough LLM estimates, not rigorous predictions.
