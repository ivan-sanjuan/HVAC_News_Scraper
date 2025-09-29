from .scraper_coolingpost import get_cooling_post, CoolingPostNews
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
# from .scraper_trane_commercial import get_trane_commercial
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
from .scraper_LG_Electronics_NA import get_LG_Electronics_NA
from .scraper_generac import get_generac
from .scraper_nidec import get_nidec
from .scraper_beijer_ref import get_beijer_ref
from .scraper_daikin_corporate import get_daikin_corporate
from .scraper_daikin_europe import get_daikin_EU
from .scraper_daikin_applied import get_daikin_applied
from .scraper_GEA import get_GEA
from .scraper_stiebel_eltron import get_stiebel_eltron
from .scraper_resideo import get_resideo
from .scraper_residio_investor import get_resideo_investor
from .scraper_spx import get_SPX
from .scraper_rheem import get_rheem
from .scraper_hussman import get_hussmann
from .scraper_panasonic_hvac import get_panasonic_hvac
from .scraper_panasonic_global import get_panasonic_global
from .scraper_panasonic_uk import get_panasonic_uk
from .scraper_atmoszero import get_atmoszero
from .scraper_mesa_labs import get_mesa_labs
from .scraper_mitsubishi_electric_hvac import get_mitsubishi_electric_hvac
from .scraper_mitsubishi_electric_global import get_mitsubishi_electric_global
from .scraper_mitsubishi_electric_sci import get_mitsubishi_electric_sci
from .scraper_parker_sporlan import get_parker_sporlan
from .scraper_rechi import get_rechi
from .scraper_schott import get_schott
from .scraper_secop import get_secop
from .scraper_sensata import get_sensata
from .scraper_tive import get_tive
from .scraper_nibe import get_nibe
from .scraper_tecumseh import get_tecumseh
from .scraper_watsco import get_watsco
from .scraper_sanhua import get_sanhua
from .scraper_sanhua_group import get_sanhua_group
from .scraper_icm_controls import get_icm_controls
from .scraper_midea import get_midea
from .scraper_rees_scientific import get_rees_scientific
from .scraper_carrier_groups import get_carrier_group_news
# get_ACHR,
def get_scrapers():
    scrapers = [
            {'func':get_trane_news,'root':'https://www.tranetechnologies.com/en/index/news/news-archive.html'},
            {'func':get_danfoss_news,'root':'https://www.danfoss.com/en/about-danfoss/news/?pageSize=15&sort=startDate_desc'},
            {'func':get_LG_news,'root':'https://www.lgnewsroom.com/'},
            {'func':get_LG_Electronics_NA,'root':'https://www.lg.com/us/press-release'},
            {'func':get_copeland_news,'root':'https://www.copeland.com/'},
            {'func':get_carrier_news,'root':'https://www.corporate.carrier.com/news/?typefilter=Press%20Releases'},
            {'func':get_carrier_group_news,'root':'https://www.carrier.com/residential/en/us/news/'},
            {'func':get_viessmann_news,'root':'https://www.viessmann-climatesolutions.com/en/newsroom.html'},
            {'func':get_lennox_news,'root':'https://investor.lennox.com/news-events/news-releases'},
            # get_BDRthermea_news,
            # get_honeywell_news,
            # get_thermoking,
            # get_delta_trak_news,
            # get_generac,
            # get_nidec,
            # get_beijer_ref,
            # get_daikin_corporate,
            # get_daikin_EU,
            # get_daikin_applied,
            # get_GEA,
            # get_stiebel_eltron,
            # get_resideo,
            # get_resideo_investor,
            # get_SPX,
            # get_rheem,
            # get_hussmann,
            # get_panasonic_global,
            # get_panasonic_hvac,
            # get_panasonic_uk,
            # get_atmoszero,
            # get_mesa_labs,
            # get_mitsubishi_electric_global,
            # get_mitsubishi_electric_hvac,
            # get_mitsubishi_electric_sci,
            # get_parker_sporlan,
            # get_rechi,
            # get_schott,
            # get_secop,
            # get_sensata,
            # get_tive,
            # get_nibe,
            # get_tecumseh,
            # get_watsco,
            # get_sanhua,
            # get_sanhua_group,
            # get_icm_controls,
            # get_midea,
            # get_rees_scientific,
            # get_refindustry_news,
            {'func':get_cooling_post,'root':'https://www.coolingpost.com/'},
            # get_natural_refrigerants_news,
            # get_EHPA,
            # get_contracting_business,
            # get_contractor_mag,
            # get_acr_journal,
            # get_fleet_owner,
            # get_rac_plus,
            # get_PHCP_pros,
            # get_climate_control_news,
            {'func':get_DOE,'root':'https://www.energy.gov/'},
            {'func':get_IEA,'root':'https://www.iea.org/news'},
            {'func':get_HPA,'root':'https://www.heatpumps.org.uk/news-events/'},
            {'func':get_jarn,'root':'https://www.ejarn.com/'},
            {'func':get_carel,'root':'https://www.carel.com/news'},
            {'func':get_bitzer_news,'root':'https://www.bitzer.de/gb/en/press/'},
            {'func':get_LGHVAC_NA,'root':'https://lghvac.com/about-lg/'},
            {'func':get_thermoking_europe,'root':'https://europe.thermoking.com/media-room'},
            {'func':get_HV_UK,'root':'https://www.hvnplus.co.uk/news/'},
        ]
    return scrapers