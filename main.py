from apps.scraper_coolingpost import get_cooling_post_news
from apps.scraper_refindustry import get_refindustry_news
from apps.scraper_natural_refrigerants import get_natural_refrigerants_news
from apps.scraper_trane_technologies import get_trane_news
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import flet as ft
import time
import pandas as pd

def main(page:ft.Page):
    page.window.width = 1800
    page.window.height = 950
    page.window.resizable = False,
    page.horizontal_alignment = 'center'
    page.vertical_alignment = 'center'
    page.title = 'News Scraper Dashboard'
    page.theme = ft.Theme('Dark')
    page.update()

    def scrape_all(e):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920x1080')
        options.add_argument('--log-level=3')
        driver = webdriver.Chrome(options=options)
        scrapers = [
            get_cooling_post_news,
            get_refindustry_news,
            get_natural_refrigerants_news,
            get_trane_news
        ]
        try:
            for scraper in scrapers:
                start = time.time()
                print(f"Running {scraper.__name__}...")
                scraper(driver)
                duration = time.time() - start
                print(f"{scraper.__name__} completed in {duration:.2f} seconds\n")
                time.sleep(2)
        finally:
            driver.quit()

        df1 = pd.read_csv('csv/ref_industry_news.csv')
        df2 = pd.read_csv('csv/cooling_post_news.csv')
        df3 = pd.read_csv('csv/natural_refrigerants_news.csv')
        df4 = pd.read_csv('csv/trane_technologies_news.csv')
        combined_df = pd.concat([df1, df2, df3, df4], ignore_index=True)
        combined_df.to_csv('csv/combined_news.csv', index=False)
        
        combined_csv = pd.read_csv('csv/combined_news.csv')
        combined_csv_df = pd.DataFrame(combined_csv)
        
        def headers(df:pd.DataFrame):
            return [ft.DataColumn(ft.Text(col)) for col in combined_csv_df.columns]
        
        def rows(df: pd.DataFrame):
            def open_link(e):
                page.launch_url(e.control.data)

            rows = []
            for index, row in df.iterrows():
                row_cells = []
                for header in df.columns:
                    cell_value = str(row[header])

                    if cell_value.startswith("http://") or cell_value.startswith("https://"):
                        cell_content = ft.TextButton(
                            text="Visit",
                            data=cell_value,
                            on_click=open_link,
                            style=ft.ButtonStyle(color=ft.Colors.BLUE)
                        )
                    else:
                        cell_content = ft.Text(cell_value, color='#1F2134')

                    if header == "Title":
                        cell_widget = ft.Container(
                            content=cell_content,
                            width=600
                        )
                    else:
                        cell_widget = cell_content

                    row_cells.append(ft.DataCell(cell_widget))
                rows.append(ft.DataRow(cells=row_cells))
            return rows

                
        scrape_result = ft.DataTable(
                        columns=headers(combined_csv_df),
                        bgcolor='#DCDCDC',
                        rows=rows(combined_csv_df),
                        column_spacing=20,
                        heading_row_color='#1F2134',
                        data_row_color={ft.ControlState.HOVERED: "0x30CCCCCC"},
                        show_checkbox_column=True,
                        border=ft.border.all(1, ft.Colors.GREY),
                        width=1800
                        )
        
        output_section.controls.append(scrape_result)
        page.update()
        
    output_section = ft.Column(
        width=1800,
        height=750,
        scroll="auto",
        controls=[]
    )

    container = ft.Container(
        width = 1800,
        height = 900,
        content=ft.Column(
            controls=[
                ft.Container(
                    height=150,
                    content=ft.Row(
                        controls=[
                        ft.Container(
                            height=100,
                            content=ft.ElevatedButton(
                                text='SCRAPE!',
                                width=300,
                                height=20,
                                on_click=scrape_all
                            )
                        )
                        ]
                    )
                    ),
                ft.Container(
                    height=750,
                    content=output_section
                )
            ]
        )
    )

    page.add(container)
    
ft.app(target=main)