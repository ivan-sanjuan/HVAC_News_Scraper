from .scraper_coolingpost import get_cooling_post_news
from .scraper_refindustry import get_refindustry_news
from .scraper_natural_refrigerants import get_natural_refrigerants_news
from .scraper_trane_technologies import get_trane_news
from .scraper_danfoss import get_danfoss_news
from .scraper_LG_B2B import get_LG_news
from .scraper_copeland import get_copeland_news
from .scraper_carrier import get_carrier_news
from .scraper_viessmann import get_viessmann_news
from .scraper_lennox import get_lennox_news
from .scraper_BDR_thermea import get_BDRthermea_news
from .scraper_honeywell import get_honeywell_news

def get_scrapers():
    scrapers = [
            # get_cooling_post_news,
            # get_refindustry_news,
            # get_natural_refrigerants_news,
            # get_trane_news,
            # get_danfoss_news,
            # get_LG_news,
            # get_copeland_news,
            # get_carrier_news,
            # get_viessmann_news,
            # get_lennox_news,
            # get_BDRthermea_news,
            get_honeywell_news
        ]
    return scrapers