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
from .scraper_ecobee import get_ecobee
# get_ACHR,
def get_scrapers():
    scrapers = [
            {'name':'Trane','type':'Company News','func':get_trane_news,'url':'https://www.tranetechnologies.com/en/index/news/news-archive.html'},
            {'name':'Danfoss','type':'Company News','func':get_danfoss_news,'url':'https://www.danfoss.com/en/about-danfoss/news/?pageSize=15&sort=startDate_desc'},
            {'name':'LG Global','type':'Company News','func':get_LG_news,'url':'https://www.lgnewsroom.com/'},
            {'name':'LG Electronics NA','type':'Company News','func':get_LG_Electronics_NA,'url':'https://www.lg.com/us/press-release'},
            {'name':'Copeland','type':'Company News','func':get_copeland_news,'url':'https://www.copeland.com/'},
            {'name':'Carrier News','type':'Company News','func':get_carrier_news,'url':'https://www.corporate.carrier.com/news/?typefilter=Press%20Releases'},
            {'name':'Carrier Group','type':'Company News','func':get_carrier_group_news,'url':'https://www.carrier.com/residential/en/us/news/'},
            {'name':'Viessmann','type':'Company News','func':get_viessmann_news,'url':'https://www.viessmann-climatesolutions.com/en/newsroom.html'},
            {'name':'Lennox','type':'Company News','func':get_lennox_news,'url':'https://investor.lennox.com/news-events/news-releases'},
            {'name':'BDR Thermea','type':'Company News','func':get_BDRthermea_news,'url':'https://www.bdrthermeagroup.com/stories'},
            {'name':'Honeywell','type':'Company News','func':get_honeywell_news,'url':'https://www.honeywell.com/us/en/press?tab=View+All'},
            {'name':'ThermoKing','type':'Company News','func':get_thermoking,'url':'https://www.thermoking.com/na/en/newsroom.html'},
            {'name':'DeltaTrak','type':'Company News','func':get_delta_trak_news,'url':'https://deltatrak.com/about-us/news-and-insights/'},
            {'name':'Generac','type':'Company News','func':get_generac,'url':'https://www.generac.com/about/news/'},
            {'name':'Nidec','type':'Company News','func':get_nidec,'url':'https://www.nidec.com/en/corporate/news/'},
            {'name':'Beijer Ref','type':'Company News','func':get_beijer_ref,'url':'https://www.beijerref.com/news'},
            {'name':'Daikin Corporate','type':'Company News','func':get_daikin_corporate,'url':'https://www.daikin.com/news'},
            {'name':'Daikin EU','type':'Company News','func':get_daikin_EU,'url':'https://www.daikin.eu/en_us/press-releases.html'},
            {'name':'Daikin Applied','type':'Company News','func':get_daikin_applied,'url':'https://blog.daikinapplied.eu/news-center'},
            {'name':'GEA','type':'Company News','func':get_GEA,'url':'https://www.gea.com/en/company/media/press-releases/'},
            {'name':'Stiebel Eltron','type':'Company News','func':get_stiebel_eltron,'url':'https://www.stiebel-eltron.com/en/home/company/press/press-releases.html'},
            {'name':'Resideo','type':'Company News','func':get_resideo,'url':'https://www.resideo.com/us/en/corporate/newsroom/all-articles/'},
            {'name':'Resideo - Investor','type':'Company News','func':get_resideo_investor,'url':'https://investor.resideo.com/news/default.aspx'},
            {'name':'SPX','type':'Company News','func':get_SPX,'url':'https://spxcooling.com/news/'},
            {'name':'Rheem','type':'Company News','func':get_rheem,'url':'https://www.rheem.com/about/news-releases/'},
            {'name':'Hussmann','type':'Company News','func':get_hussmann,'url':'https://www.hussmann.com/news'},
            {'name':'Panasonic Global','type':'Company News','func':get_panasonic_global,'url':'https://news.panasonic.com/global/'},
            {'name':'Panasonic HVAC','type':'Company News','func':get_panasonic_hvac,'url':'https://www.panasonic.com/global/hvac/news.html'},
            {'name':'Panasonic UK','type':'Company News','func':get_panasonic_uk,'url':'https://www.aircon.panasonic.eu/GB_en/news/more/'},
            {'name':'AtmosZero','type':'Company News','func':get_atmoszero,'url':'https://atmoszero.energy/newsroom/'},
            {'name':'Mesa Labs','type':'Company News','func':get_mesa_labs,'url':'https://investors.mesalabs.com/news/default.aspx'},
            {'name':'Mitsubishi Electric - Global','type':'Company News','func':get_mitsubishi_electric_global,'url':'https://www.mitsubishielectric.com/en/pr/'},
            {'name':'Mitsubishi Electric - HVAC','type':'Company News','func':get_mitsubishi_electric_hvac,'url':'https://www.mitsubishicomfort.com/press-releases'},
            {'name':'Mitsubishi Electric - SCI','type':'Company News','func':get_mitsubishi_electric_sci,'url':'https://www.siamcompressor.com/siamcompressor/en/news-events'},
            {'name':'Parker Sporlan','type':'Company News','func':get_parker_sporlan,'url':'https://www.parker.com/us/en/about-parker/newsroom/news-release-details.html'},
            {'name':'Rechi','type':'Company News','func':get_rechi,'url':'https://www.rechi.com/posts_en/create'},
            {'name':'Schott','type':'Company News','func':get_schott,'url':'https://www.schott.com/en-us/news-and-media/media-releases'},
            {'name':'Secop','type':'Company News','func':get_secop,'url':'https://www.secop.com/updates/news'},
            {'name':'Sensata','type':'Company News','func':get_sensata,'url':'https://www.sensata.com/newsroom'},
            {'name':'Tive','type':'Company News','func':get_tive,'url':'https://www.tive.com/newsroom'},
            {'name':'Nibe','type':'Company News','func':get_nibe,'url':'https://www.nibe.eu/en-gb/about-nibe/nibe-news'},
            {'name':'Tecumseh','type':'Company News','func':get_tecumseh,'url':'https://www.tecumseh.com/NewsAndEvents/News'},
            {'name':'Watsco','type':'Company News','func':get_watsco,'url':'https://investors.watsco.com/news'},
            {'name':'Sanhua','type':'Company News','func':get_sanhua,'url':'https://www.sanhuausa.com/'},
            {'name':'Sanhua Group','type':'Company News','func':get_sanhua_group,'url':'https://www.sanhuagroup.com/en/news.html'},
            {'name':'ICM Controls','type':'Company News','func':get_icm_controls,'url':'https://www.icmcontrols.com/blog/'},
            {'name':'Midea','type':'Company News','func':get_midea,'url':'https://mbt.midea.com/global/news'},
            {'name':'Rees Scientific','type':'Company News','func':get_rees_scientific,'url':'https://reesscientific.com/blog'},
            {'name':'RefIndustry','type':'Industry News','func':get_refindustry_news,'url':'https://refindustry.com/news/'},
            {'name':'CoolingPost','type':'Industry News','func':get_cooling_post,'url':'https://www.coolingpost.com/'},
            {'name':'JARN','type':'Industry News','func':get_jarn,'url':'https://www.ejarn.com/category/eJarn_news_index'},
            {'name':'Natural Refrigerants','type':'Industry News','func':get_natural_refrigerants_news,'url':'https://naturalrefrigerants.com/news/'},
            {'name':'EHPA','type':'Industry News','func':get_EHPA,'url':'https://www.ehpa.org/news-and-resources/'},
            {'name':'Contracting Business','type':'Industry News','func':get_contracting_business,'url':'https://www.contractingbusiness.com/'},
            {'name':'Contractor Mag','type':'Industry News','func':get_contractor_mag,'url':'https://www.contractormag.com/'},
            {'name':'ACR Journal','type':'Industry News','func':get_acr_journal,'url':'https://www.acrjournal.uk/news'},
            {'name':'Fleet Owner','type':'Industry News','func':get_fleet_owner,'url':'https://www.fleetowner.com/refrigerated-transporter/cold-storage-logistics'},
            {'name':'RAC Plus','type':'Industry News','func':get_rac_plus,'url':'https://www.racplus.com/news/'},
            {'name':'PHCP Pros','type':'Industry News','func':get_PHCP_pros,'url':'https://www.phcppros.com/articles/topic/249-hvac'},
            {'name':'Climate Control News','type':'Industry News','func':get_climate_control_news,'url':'https://www.climatecontrolnews.com.au/news/latest'},
            {'name':'DOE','type':'Industry News','func':get_DOE,'url':'https://www.energy.gov/'},
            {'name':'IEA','type':'Industry News','func':get_IEA,'url':'https://www.iea.org/news'},
            {'name':'HPA','type':'Industry News','func':get_HPA,'url':'https://www.heatpumps.org.uk/news-events/'},
            {'name':'Carel','type':'Company News','func':get_carel,'url':'https://www.carel.com/news'},
            {'name':'Bitzer','type':'Company News','func':get_bitzer_news,'url':'https://www.bitzer.de/gb/en/press/'},
            {'name':'LG HVAC - NA','type':'Company News','func':get_LGHVAC_NA,'url':'https://lghvac.com/about-lg/'},
            {'name':'ThermoKing - Europe','type':'Company News','func':get_thermoking_europe,'url':'https://europe.thermoking.com/media-room'},
            {'name':'HV UK','type':'Industry News','func':get_HV_UK,'url':'https://www.hvnplus.co.uk/news/'},
            {'name':'Ecobee','type':'Company News','func':get_ecobee,'url':'https://www.ecobee.com/en-ca/newsroom/'},
        ]
    return scrapers