from .scraper_coolingpost import get_cooling_post
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
from .scraper_ecobee import get_ecobee
from .scraper_johnson_controls import get_johnsonControls_news
from .scraper_embraco import get_embraco

def get_exceptions():
    exceptions = [
        get_HPA,
        get_jarn,
        get_embraco,
        get_mitsubishi_electric_hvac,
        get_sanhua,
        get_sanhua_group,
        get_acr_journal,
        get_copeland_news,
        get_natural_refrigerants_news,
        get_EHPA,
        get_contracting_business,
        get_contractor_mag,
        get_fleet_owner,
        get_PHCP_pros,
        get_HPA,
        get_climate_control_news,
        get_DOE,
        get_IEA,
        get_rac_plus,
        get_viessmann_news,
        get_LGHVAC_NA,
        get_thermoking_europe,
        get_contractor_mag,
        get_contracting_business,
        get_tecumseh,
        get_carrier_news,
        get_carrier_group_news,
        get_beijer_ref,
        get_bitzer_news,
        get_cooling_post,
        get_ecobee,
        get_johnsonControls_news,
        get_lennox_news,
        get_BDRthermea_news,
        get_trane_news
    ]
    return exceptions