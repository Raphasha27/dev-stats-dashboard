"""dev-stats-dashboard - GitHub contribution statistics dashboard."""

import http.server
import json
import os
import urllib.request

PORT = int(os.environ.get("PORT", 8000))
USERNAME = os.environ.get("GITHUB_USER", "Raphasha27")
TOKEN = os.environ.get("GITHUB_TOKEN", "")


def fetch_repos():
    """Fetch public repos for the given user."""
    url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=updated"
    req = urllib.request.Request(url)
    if TOKEN:
        req.add_header("Authorization", f"token {TOKEN}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def fetch_languages(repo_name):
    """Fetch language breakdown for a repo."""
    url = f"https://api.github.com/repos/{USERNAME}/{repo_name}/languages"
    req = urllib.request.Request(url)
    if TOKEN:
        req.add_header("Authorization", f"token {TOKEN}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def build_page():
    repos = fetch_repos()
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    total_forks = sum(r.get("forks_count", 0) for r in repos)
    total_issues = sum(r.get("open_issues_count", 0) for r in repos)
    lang_data = {}
    for r in repos[:10]:
        langs = fetch_languages(r["name"])
        for lang, bytes_ in langs.items():
            lang_data[lang] = lang_data.get(lang, 0) + bytes_

    lang_pct = {}
    total_bytes = sum(lang_data.values())
    if total_bytes:
        for lang, b in sorted(lang_data.items(), key=lambda x: -x[1])[:8]:
            lang_pct[lang] = round(b / total_bytes * 100, 1)

    repos_html = "".join(
        f"""<tr>
          <td><a href="{r['html_url']}">{r['name']}</a></td>
          <td>{r.get('language', '-')}</td>
          <td>{r.get('stargazers_count', 0)}</td>
          <td>{r.get('forks_count', 0)}</td>
          <td>{r.get('open_issues_count', 0)}</td>
        </tr>"""
        for r in sorted(repos, key=lambda x: -x.get("stargazers_count", 0))
    )

    lang_bars = "".join(
        f"""<div class="lang-bar">
          <span class="lang-name">{lang}</span>
          <div class="bar-track">
            <div class="bar-fill" style="width:{pct}%"></div>
          </div>
          <span class="lang-pct">{pct}%</span>
        </div>"""
        for lang, pct in lang_pct.items()
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dev Stats Dashboard - {USERNAME}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1117; color: #c9d1d9; padding: 2rem; }}
  h1 {{ color: #58a6ff; margin-bottom: 0.5rem; }}
  .subtitle {{ color: #8b949e; margin-bottom: 2rem; }}
  .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .stat-card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1.5rem; text-align: center; }}
  .stat-card .number {{ font-size: 2rem; font-weight: 700; color: #58a6ff; }}
  .stat-card .label {{ color: #8b949e; font-size: 0.9rem; }}
  table {{ width: 100%; border-collapse: collapse; background: #161b22; border-radius: 8px; overflow: hidden; }}
  th, td {{ padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid #30363d; }}
  th {{ background: #21262d; color: #8b949e; font-weight: 600; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 0.05em; }}
  td a {{ color: #58a6ff; text-decoration: none; }}
  td a:hover {{ text-decoration: underline; }}
  .lang-section {{ margin-top: 2rem; }}
  .lang-section h2 {{ color: #c9d1d9; margin-bottom: 1rem; }}
  .lang-bar {{ display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem; }}
  .lang-name {{ width: 120px; color: #c9d1d9; font-size: 0.9rem; }}
  .bar-track {{ flex: 1; height: 12px; background: #21262d; border-radius: 6px; overflow: hidden; }}
  .bar-fill {{ height: 100%; background: linear-gradient(90deg, #58a6ff, #1f6feb); border-radius: 6px; }}
  .lang-pct {{ width: 50px; text-align: right; color: #8b949e; font-size: 0.9rem; }}
  .footer {{ margin-top: 2rem; text-align: center; color: #484f58; font-size: 0.8rem; }}
</style>
</head>
<body>
<h1>📊 Dev Stats Dashboard</h1>
<p class="subtitle">GitHub statistics for <strong>{USERNAME}</strong></p>
<div class="stats">
  <div class="stat-card"><div class="number">{len(repos)}</div><div class="label">Repositories</div></div>
  <div class="stat-card"><div class="number">{total_stars}</div><div class="label">Stars</div></div>
  <div class="stat-card"><div class="number">{total_forks}</div><div class="label">Forks</div></div>
  <div class="stat-card"><div class="number">{total_issues}</div><div class="label">Open Issues</div></div>
</div>
<h2>Repositories</h2>
<table>
  <thead><tr><th>Name</th><th>Language</th><th>Stars</th><th>Forks</th><th>Issues</th></tr></thead>
  <tbody>{repos_html}</tbody>
</table>
<div class="lang-section">
  <h2>Language Breakdown</h2>
  {lang_bars if lang_bars else '<p style="color:#8b949e;">No language data available.</p>'}
</div>
<div class="footer">Auto-generated by dev-stats-dashboard</div>
</body>
</html>"""


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(build_page().encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    server = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Serving at http://localhost:{PORT}")
    server.serve_forever()
