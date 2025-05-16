# Setup
## For Conda
```conda activate mecha_match```

# Scraping
1. Setup Write config file in ```/scraper/config/scrapy_rules``` based on example_rule
2. Run Scraper
```python scraper/run_spiders.py```

# Testing
```python -m pytest```

# Linting
```pre-commit run --all-files```