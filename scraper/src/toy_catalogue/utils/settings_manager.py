from scrapy.utils.project import get_project_settings
from datetime import datetime, timezone
import os
import json
from toy_catalogue.config.parameters import JOB_ROOT


def update_job_list(spider, metadata):
    path = os.path.join(JOB_ROOT, spider.name, f"{spider.name}.json")
    if os.path.isfile(path):
        with open(path, "r") as f:
            data = json.load(f)
    else:
        data = {}
    with open(path, "w") as f:
        run = spider.settings.get("JOBDIR")
        data[run] = metadata
        json.dump(data, f, indent=2)


def list_jobs(site=None):
    try:
        if site:
            base = os.path.join(JOB_ROOT, f"{site}", f"{site}.json")
            print(base)
        with open(base, "r") as f:
            meta = json.load(f)
            return [(item["name"], item["start_time"]) for item in meta.values()]
    except Exception:
        return []


def create_settings(site_name: str):
    jobs = list_jobs(site_name)
    for i, (name, timestamp) in enumerate(jobs):
        print(f"[{i}] {name} (started {timestamp})")
    choice = input("Select a job to resume (Enter for fresh crawl): ")
    settings = get_project_settings()
    if not choice:
        settings.set(
            "JOBDIR",
            os.path.join(
                JOB_ROOT,
                f"{site_name}",
                f"{datetime.now(timezone.utc).date()}-run{len(list_jobs(site_name))+1}",
            ),
        )
        print("a")
    else:
        settings.set(
            "JOBDIR",
            os.path.join(
                JOB_ROOT,
                f"{site_name}",
                f"{datetime.now(timezone.utc).date()}-run{int(choice)}",
            ),
        )
    return settings
    # if "proxy" in sys.argv:
    #     mw = settings.get("DOWNLOADER_MIDDLEWARES", {})
    #     mw.update({
    #         "toy_catalogue.middlewares.JhaoProxyMiddleware": 500,
    #     })
    #     settings.set('DOWNLOADER_MIDDLEWARES', mw)
