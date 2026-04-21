# simple

A minimal interface for managing [Pixela](https://pixe.la) habit graphs, plus a weekly email report.

## Files

| File | Purpose |
|------|---------|
| `index.html` | Web UI to manage graphs and pixels |
| `serve.py` | Local server that injects `.env` credentials into the UI |
| `report.py` | Pulls last 7 days of data and emails a summary |
| `run_report.sh` | Pulls latest code from git and runs `report.py` |
| `requirements.txt` | Python dependencies |
| `.env` | Secrets (do not commit) |

## Setup

```bash
pip install -r requirements.txt
```

Fill in `.env`:

```
PIXELA_USERNAME=your-username
PIXELA_TOKEN=your-token

BREVO_API_KEY=your-brevo-api-key
REPORT_FROM_EMAIL=reports@yourdomain.com
REPORT_TO_EMAILS=you@example.com,other@gmail.com
```

## Web UI

```bash
python serve.py
```

Opens `http://localhost:8765` with your username and token pre-loaded. From there you can:

- Load, create, update, and delete graphs
- Add, get, update, and delete individual pixels
- Fetch a date range of pixels
- View graph stats

## Weekly Report

```bash
python report.py
```

Fetches the last 7 days across all your graphs and sends an HTML email via [Brevo](https://brevo.com).

### Running on a remote server

```bash
# Clone and add your .env (once)
git clone https://github.com/hrmainland/Habits.git
cd Habits
nano simple/.env

# Run manually
bash simple/run_report.sh

# Or schedule weekly via cron (Mondays 8am)
crontab -e
# 0 8 * * 1 /bin/bash /home/youruser/Habits/simple/run_report.sh >> /home/youruser/habits.log 2>&1
```

`run_report.sh` does a `git pull` before each run so it stays up to date automatically.

## Domain setup (Brevo)

1. Brevo dashboard → **Senders & IPs → Domains → Add domain**
2. Add the SPF and DKIM DNS records to your domain provider
3. Click verify, then set `REPORT_FROM_EMAIL` to any address on that domain
