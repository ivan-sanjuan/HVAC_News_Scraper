from apps.scraper_coolingpost import get_coolingpost
from apps.scraper_refindustry import get_ref_industry
import pandas as pd


get_coolingpost()
get_ref_industry()

df1 = pd.read_csv('ref_industry_news.csv')
df2 = pd.read_csv('cooling_post_news.csv')

combined_df = pd.concat([df1, df2], ignore_index=True)

combined_df.to_csv('combined_news.csv', index=False)