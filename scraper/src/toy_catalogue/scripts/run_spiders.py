from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import typer
from pathlib import Path
from toy_catalogue.config.config_manager import ConfigManager
from toy_catalogue.config.schema.external.config import (
    FileConfig,
    PackageConfig,
    UrlConfig,
)
from toy_catalogue.utils.session_manager import SessionManager
from toy_catalogue.spiders.generic_spider import GenericSpider

app = typer.Typer()


@app.command()
def main(
    site: str,
    config_file: Path = typer.Option(None, "--file", help="Path to local JSON config"),
    config_url: str = typer.Option(None, "--url", help="URL to load config from"),
):
    if config_file:
        spec = FileConfig(type="file", path=str(config_file))
    elif config_url:
        spec = UrlConfig(type="url", url=config_url)
    else:
        spec = PackageConfig(type="package", resource=f"sites/{site}.json")

    config = ConfigManager.load_config(spec)
    print("config created", config)
    session = SessionManager.create_session(config, mode="fresh")
    print("Session created", session)

    # process = CrawlerProcess(settings)  # Load settings.py
    process = CrawlerProcess(get_project_settings())
    process.crawl(GenericSpider, context=session)

    process.start()
    print("Crawler finished")  # Blocks until all spiders finish
