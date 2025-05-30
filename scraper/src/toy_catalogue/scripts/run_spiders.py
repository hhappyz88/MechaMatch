from scrapy.crawler import CrawlerProcess
from toy_catalogue.spiders.spider_factory import (
    create_spider,
)  # Import your spider
from scrapy.utils.project import get_project_settings
import typer
from pathlib import Path
from toy_catalogue.config_manager import ConfigManager
from toy_catalogue.config_spec import FileConfig, PackageConfig, UrlConfig

app = typer.Typer()


@app.command()
def main(
    site: str,
    config_file: Path = typer.Option(None, "--file", help="Path to local JSON config"),
    config_url: str = typer.Option(None, "--url", help="URL to load config from"),
):
    # rule_config = create_rules(sys.argv[1])
    # settings = create_settings(sys.argv[1])
    # rule_path = os.path.join(
    #     "toy_catalogue", "config", "scrapy_rules", f"{sys.argv[1]}.json"
    # )
    # with open(rule_path, "r") as f:
    #     config = json.load(f)
    if config_file:
        spec = FileConfig(type="file", path=str(config_file))
    elif config_url:
        spec = UrlConfig(type="url", url=config_url)
    else:
        # default to bundled config
        spec = PackageConfig(type="package", resource=f"sites/{site}.json")
    config = ConfigManager.load_config(spec)
    Spider = create_spider(config)  # Create the spider dynamically
    print("Spider created")
    # process = CrawlerProcess(settings)  # Load settings.py
    process = CrawlerProcess(get_project_settings())
    process.crawl(Spider)
    print("Crawler was added")  # Should print

    process.start()
    print("Crawler finished")  # Blocks until all spiders finish
