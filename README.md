Headless Email Scraper API

A headless, concurrent email scraper with caching, retries, and API access. Built with FastAPI, Playwright, Redis, and RQ, fully Docker-ready for one-click deployment.

Features

Crawl root page + up to 10 internal pages

Extract emails concurrently (configurable concurrency)

Handles timeouts and automatic retries

Cache results in Redis for 24 hours

Simple API for job submission and results retrieval

Fully containerized with Docker & Docker Compose

Requirements

Ubuntu 20.04+ (or any Linux VPS)

Docker

Docker Compose

Quick Start (One-Click VPS Deployment)
1. Install Docker & Docker Compose
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker

2. Clone the Repository
git clone https://github.com/emailengineer/headless-email-scraper.git
cd headless-email-scraper

3. Start the Services
docker-compose up --build -d


This will start three containers:

scraper_api → FastAPI API server (port 8000)

scraper_worker → Background scraping worker

scraper_redis → Redis for caching and job queue

4. Submit a Crawl Job
curl -X POST "http://<VPS-IP>:8000/crawl" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com"}'


Response:

{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "queued"
}

5. Check Job Result
curl "http://<VPS-IP>:8000/result/<job_id>"


Response (example):

{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "emails": ["contact@example.com", "support@example.com"]
}

Configuration

Max pages per crawl: 10 (set in scraper.py via MAX_PAGES)

Concurrency: 3 pages at a time (CONCURRENCY)

Cache TTL: 24 hours (CACHE_TTL)

Timeout per page: 15 seconds (PAGE_TIMEOUT)

Retries per page: 2 (RETRIES)

All parameters can be adjusted in scraper.py.

Stopping Services
docker-compose down

Notes

Ensure the VPS has enough RAM (~1-2 GB recommended) for Playwright Chromium instances.

Redis caching prevents re-scraping the same URL multiple times within the TTL.

Avoid crawling sites aggressively; respect site policies and robots.txt.

License

MIT License – free to use and modify.