import os
import sys
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

PIXELA_USERNAME = os.getenv("PIXELA_USERNAME")
PIXELA_TOKEN    = os.getenv("PIXELA_TOKEN")
BREVO_API_KEY   = os.getenv("BREVO_API_KEY")
REPORT_FROM     = os.getenv("REPORT_FROM_EMAIL")
REPORT_TO       = os.getenv("REPORT_TO_EMAIL")

BASE_URL = f"https://pixe.la/v1/users/{PIXELA_USERNAME}"
HEADERS  = {"X-USER-TOKEN": PIXELA_TOKEN}

COLOR_HEX = {
    "shibafu": "#7bc96f",
    "momiji":  "#e05d44",
    "sora":    "#4a90d9",
    "ichou":   "#f0c419",
    "ajisai":  "#9b59b6",
    "kuro":    "#555",
}


def get_graphs():
    r = requests.get(f"{BASE_URL}/graphs", headers=HEADERS)
    r.raise_for_status()
    return r.json().get("graphs", [])


def get_pixels_last_week(graph_id):
    today    = datetime.today()
    week_ago = today - timedelta(days=6)
    url = (
        f"{BASE_URL}/graphs/{graph_id}/pixels"
        f"?from={week_ago.strftime('%Y%m%d')}"
        f"&to={today.strftime('%Y%m%d')}"
        f"&withBody=true"
    )
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json().get("pixels", [])


def day_cells(pixels, week_ago):
    dates_qty = {p["date"]: p["quantity"] for p in pixels}
    cells = ""
    for i in range(7):
        day   = (week_ago + timedelta(days=i)).strftime("%Y%m%d")
        label = (week_ago + timedelta(days=i)).strftime("%a")
        qty   = dates_qty.get(day)
        if qty:
            cells += (
                f'<td style="padding:5px 7px;text-align:center;background:#7bc96f;'
                f'color:white;border-radius:4px;font-size:12px;">'
                f'{qty}<br><span style="font-size:10px;opacity:0.85">{label}</span></td>'
                f'<td style="width:4px"></td>'
            )
        else:
            cells += (
                f'<td style="padding:5px 7px;text-align:center;background:#efefef;'
                f'color:#bbb;border-radius:4px;font-size:12px;">'
                f'—<br><span style="font-size:10px">{label}</span></td>'
                f'<td style="width:4px"></td>'
            )
    return cells


def build_html(graphs_data):
    today    = datetime.today()
    week_ago = today - timedelta(days=6)
    date_range = f"{week_ago.strftime('%b %d')} – {today.strftime('%b %d, %Y')}"

    rows = ""
    for graph, pixels in graphs_data:
        color   = COLOR_HEX.get(graph.get("color", ""), "#7bc96f")
        total   = sum(float(p["quantity"]) for p in pixels) if pixels else 0
        active  = len(pixels)
        summary = (
            f"{total:.0f} {graph['unit']} across {active} day{'s' if active != 1 else ''}"
            if pixels else "No activity"
        )
        cells = day_cells(pixels, week_ago)
        rows += f"""
        <tr>
          <td style="padding:12px 16px;border-bottom:1px solid #f0f0f0;vertical-align:top;">
            <div style="display:flex;align-items:center;gap:7px;">
              <span style="width:9px;height:9px;border-radius:50%;background:{color};display:inline-block;flex-shrink:0;"></span>
              <span style="font-weight:600;font-size:14px;">{graph['name']}</span>
            </div>
            <div style="font-size:12px;color:#999;margin-top:3px;padding-left:16px;">{summary}</div>
          </td>
          <td style="padding:12px 16px;border-bottom:1px solid #f0f0f0;vertical-align:middle;">
            <table style="border-collapse:separate;border-spacing:0;"><tr>{cells}</tr></table>
          </td>
        </tr>
        """

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:24px;background:#f4f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <div style="max-width:680px;margin:0 auto;background:white;border-radius:8px;overflow:hidden;border:1px solid #e0e0e0;">

    <div style="background:#1a1a2e;color:white;padding:20px 24px;">
      <div style="font-size:18px;font-weight:600;">Weekly Habit Report</div>
      <div style="font-size:13px;opacity:0.6;margin-top:4px;">{date_range}</div>
    </div>

    <table style="width:100%;border-collapse:collapse;">
      <thead>
        <tr style="background:#fafafa;">
          <th style="padding:9px 16px;text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:0.5px;color:#aaa;font-weight:600;border-bottom:1px solid #eee;">Habit</th>
          <th style="padding:9px 16px;text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:0.5px;color:#aaa;font-weight:600;border-bottom:1px solid #eee;">Last 7 Days</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>

    <div style="padding:14px 24px;background:#fafafa;font-size:11px;color:#ccc;text-align:center;border-top:1px solid #eee;">
      Generated {today.strftime('%Y-%m-%d %H:%M')} · Pixela
    </div>
  </div>
</body>
</html>"""


def send_email(html, subject):
    r = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={
            "api-key":      BREVO_API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "sender":      {"email": REPORT_FROM},
            "to":          [{"email": REPORT_TO}],
            "subject":     subject,
            "htmlContent": html,
        },
    )
    r.raise_for_status()
    return r.json()


def main():
    missing = [v for v in ["PIXELA_USERNAME", "PIXELA_TOKEN", "BREVO_API_KEY", "REPORT_FROM_EMAIL", "REPORT_TO_EMAIL"] if not os.getenv(v)]
    if missing:
        print(f"Missing env vars: {', '.join(missing)}")
        sys.exit(1)

    print("Fetching graphs...")
    graphs = get_graphs()
    print(f"Found {len(graphs)} graph(s)")

    graphs_data = []
    for graph in graphs:
        print(f"  {graph['id']}: fetching last 7 days...")
        pixels = get_pixels_last_week(graph["id"])
        graphs_data.append((graph, pixels))

    html = build_html(graphs_data)

    today    = datetime.today()
    week_ago = today - timedelta(days=6)
    subject  = f"Habit Report — {week_ago.strftime('%b %d')} to {today.strftime('%b %d')}"

    print(f"Sending to {REPORT_TO}...")
    result = send_email(html, subject)
    print(f"Sent! id={result.get('id')}")


if __name__ == "__main__":
    main()
