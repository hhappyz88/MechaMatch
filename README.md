# Setup
## Frontend
```cd frontend```
```npm run dev -- --open```
## Backend
### For Conda
```conda env create -f environment.yml```
```conda activate mecha_match```
### Scraping
1. Setup Write config file in ```/scraper/src/toy_catalogue/config/rules/sites```
2. Run Scraper
```run-spiders {filename}```
## Docker Pulls
```docker pull jhao104/proxy_pool```

## Docker
To create docker containers
```docker run -d --name redis -p 6379:6379 -v "$Env:USERPROFILE/redis_data"```
```docker run -d --name proxy_pool -p 5010:5010   --env DB_CONN=redis://host.docker.internal:6379/0   jhao104/proxy_pool:latest```

To pause docker containers
```docker stop proxy_pool```
```docker stop redis```

To start docker containers
```docker start proxy_pool```
```docker start redis```

List docker containers
```docker ps```
```docker ps -a```

Rmove stopped containers
```docker container prune```

Check logs 
```docker logs -f <container_name>```

# Testing
```python -m pytest```

# Linting
```pre-commit run --all-files```

# Docker
## Setup single engine
To setup build
```docker build -t name .```

## Setup Stack
To setup build
```docker compose build```
To run script
```docker compose run scraper conda run -n mecha_match python run_spiders.py arg1```
To stop
```docker compose down```
Experiment
```docker compose run scraper bash```