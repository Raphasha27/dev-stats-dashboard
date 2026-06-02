# Dev Stats Dashboard

A web dashboard that visualizes your GitHub contribution stats, repo activity, and coding patterns.

## Features

- Contribution heatmap (like GitHub but self-hosted)
- Language breakdown across all repos
- Commit frequency timeline
- Top repos by activity
- Streak tracking

## Quick Start

```bash
# Python version
pip install -e .
export GITHUB_TOKEN=your_token
dev-stats --username your_username

# Or use the web UI
python -m dev_stats.web
```
