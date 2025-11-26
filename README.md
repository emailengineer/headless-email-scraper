# Headless Email Scraper API

This is a headless, concurrent email scraper with caching, retries, and API access. Built with **FastAPI**, **Playwright**, **Redis**, and **RQ**.

## Features
- Crawl root page + top 10 internal pages
- Extract emails concurrently
- Handle timeouts & retries
- Cache results for 24 hours
- Docker-ready for one-click deployment

## Requirements
- Docker
- Docker Compose

## Quick Start (One-Click)
Clone repo:

```bash
git clone https://github.com/yourusername/headless-email-scraper.git
cd headless-email-scraper


Run everything:

docker-compose up --build -d


curl -X POST "http://<VPS-IP>:8000/crawl" -H "Content-Type: application/json" -d '{"url": "https://example.com"}'



---

# ** One-Click Deployment on Any VPS**

1. Install **Docker** and **Docker Compose**:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker
git clone https://github.com/emailengineer/headless-email-scraper.git
cd headless-email-scraper
docker-compose up --build -d


