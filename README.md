# Setup
## For Conda
conda activate mecha_match

# Proxies
python toy_catalogue/proxy_manager

# Scraping
scrapy crawl site_spider -a start_url=https://example.com

# Testing
python -m pytest

# Linting
pre-commit run --all-files