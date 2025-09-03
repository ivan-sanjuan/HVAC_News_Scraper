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
from .scraper_trane_commercial import get_trane_commercial
from .scraper_thermoking import get_thermoking
from .scraper_thermoking_europe import get_thermoking_europe
from .scraper_carel import get_carel
from .scraper_deltatrak import get_delta_trak_news
from .scraper_bitzer import get_bitzer_news

def get_scrapers():
    scrapers = [
            get_cooling_post_news,
            get_refindustry_news,
            get_natural_refrigerants_news,
            get_trane_news,
            get_trane_commercial,
            get_danfoss_news,
            get_LG_news,
            get_copeland_news,
            get_carrier_news,
            get_viessmann_news,
            get_lennox_news,
            get_BDRthermea_news,
            get_honeywell_news,
            get_thermoking,
            get_thermoking_europe,
            get_carel,
            get_delta_trak_news,
            get_bitzer_news
        ]
    return scrapers