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

# Docker
To setup build
```docker compose build```
To run script
```docker compose run scraper conda run -n mecha_match python run_spiders.py arg1```
To stop
```docker compose down```
Experiment
```docker compose run scraper bash```