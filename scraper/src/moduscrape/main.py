from scrapy.crawler import CrawlerProcess
import typer
from moduscrape.config.config_manager import load_config
from moduscrape.config.schema.external.config import PackageConfig
from moduscrape.spiders.core_spider import CoreSpider
from moduscrape.config.settings import build_settings, load_config_from_package

app = typer.Typer()


@app.command()
def main(site: str):
    # Scrapy settings
    core = load_config_from_package("core_settings.toml")
    custom = load_config_from_package("custom_settings.toml")
    settings = build_settings(core, custom)

    # Traversal settings
    config = load_config(PackageConfig(type="package", resource=f"sites/{site}.json"))

    # SessionContext
    # session_ctx = create_session(config=config, mode="fresh")

    process = CrawlerProcess(settings)
    process.crawl(CoreSpider, config)
    process.start()
