from .scraper_coolingpost import get_cooling_post_news
from .scraper_refindustry import get_refindustry_news
from .scraper_natural_refrigerants import get_natural_refrigerants_news
from .scraper_trane_technologies import get_trane_news
from .scraper_danfoss import get_danfoss_news
from .scraper_LG_Global import get_LG_news
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
from .scraper_jarn import get_jarn
from .scraper_EHPA import get_EHPA
from .scraper_contracting_business import get_contracting_business
from .scraper_contractor_mag import get_contractor_mag
from .scraper_ACHR import get_ACHR
from .scraper_acr_journal import get_acr_journal
from .scraper_fleet_owner import get_fleet_owner
from .scraper_rac_plus import get_rac_plus
from .scraper_PHCP_pros import get_PHCP_pros
from .scraper_HV_UK import get_HV_UK
from .scraper_climate_control import get_climate_control_news
from .scraper_DOE import get_DOE
from .scraper_iea import get_IEA
from .scraper_HPA import get_HPA
from .scraper_LG_HVAC import get_LGHVAC_NA

def get_scrapers():
    scrapers = [
            get_cooling_post_news,
            get_refindustry_news,
            get_natural_refrigerants_news,
            get_jarn,
            get_ACHR,
            get_EHPA,
            get_contracting_business,
            get_contractor_mag,
            get_acr_journal,
            get_fleet_owner,
            get_rac_plus,
            get_PHCP_pros,
            get_HV_UK,
            get_climate_control_news,
            get_DOE,
            get_IEA,
            get_HPA,
            get_trane_news,
            # get_trane_commercial,
            get_danfoss_news,
            get_LG_news,
            get_LGHVAC_NA,
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