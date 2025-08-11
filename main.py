from apps.scraper_coolingpost import get_cooling_post_news
from apps.scraper_refindustry import get_refindustry_news
from apps.scraper_natural_refrigerants import get_natural_refrigerants_news
from apps.scraper_trane_technologies import get_trane_news
from apps.scraper_danfoss import get_danfoss_news
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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
    page.theme = ft.Theme('Light')
    page.update()

    def scrape_all(e):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920x1080')
        options.add_argument('--log-level=3')
        driver = webdriver.Chrome(options=options)
        search_status.update()
        scrapers = [
            get_cooling_post_news,
            get_refindustry_news,
            get_natural_refrigerants_news,
            get_trane_news,
            get_danfoss_news
        ]
        try:
            for scraper in scrapers:
                search_status.value = 'Starting to scrape..'
                start = time.time()
                print(f"Running {scraper.__name__}...")
                search_status.value = f'Running {scraper.__name__}...'
                search_status.update()
                scraper(driver)
                duration = time.time() - start
                print(f"{scraper.__name__} completed in {duration:.2f} seconds")
                search_status.value = f'{scraper.__name__} completed in {duration:.2f} seconds'
                search_status.update()
                time.sleep(2)
        finally:
            search_status.value = 'SCRAPING COMPLETE...'
            driver.quit()

        df1 = pd.read_csv('csv/ref_industry_news.csv')
        df2 = pd.read_csv('csv/cooling_post_news.csv')
        df3 = pd.read_csv('csv/natural_refrigerants_news.csv')
        df4 = pd.read_csv('csv/trane_technologies_news.csv')
        df5 = pd.read_csv('csv/danfoss_news.csv')
        combined_df = pd.concat([df1, df2, df3, df4, df5], ignore_index=True)
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
    search_field = ft.TextField(
        border_radius=3,
        label='Search Keywords',
        bgcolor='#ffffff',
    )
    
    search_status = ft.Text(
        value='ON STAND-BY...',
        size=15,
        color="#B3B3B3"
    )

    container = ft.Container(
        width = 1800,
        height = 900,
        border_radius=15,
        content=ft.Column(
            controls=[
                ft.Container(  ####-----CONTROLS SECTION-----####
                    padding = ft.padding.all(15),
                    bgcolor="#555555",
                    height=150,
                    width=1800,
                        content=ft.Row(
                            controls=[
                                ft.Container( 
                                    width=700,
                                    height=150,
                                    content=ft.Column(
                                        controls=[
                                            ft.Container(
                                                width=300,
                                                height=50,
                                                content=ft.Row(
                                                    controls=[
                                                        search_field,
                                                        search_status
                                                    ]
                                                )
                                            )
                                            ,
                                            ft.Container( 
                                                width=300,
                                                height=50,
                                                content=ft.ElevatedButton(
                                                    text='START SCRAPING...',
                                                    width=200,
                                                    height=20,
                                                    on_click=scrape_all,
                                                    style=ft.ButtonStyle(
                                                        shape=ft.RoundedRectangleBorder(radius=10),
                                                        text_style=ft.TextStyle(size=20, weight=ft.FontWeight.NORMAL)
                                                    ),
                                                )
                                            )   
                                        ]
                                    )
                                )
                            ]
                        )
                    ),
                ft.Container( ####-----OUTPUT_SECTION-----####
                    padding = ft.padding.all(15),
                    height=750,
                    width=1800,
                    content=output_section
                )
            ]
        )
    )

    page.add(container)
    
ft.app(target=main)