from apps.scraper_coolingpost import get_cooling_post_news
from apps.scraper_refindustry import get_refindustry_news
from apps.scraper_natural_refrigerants import get_natural_refrigerants_news
from apps.scraper_trane_technologies import get_trane_news
from apps.scraper_danfoss import get_danfoss_news
from apps.scraper_LG_B2B import get_LG_B2B_news
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
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.YELLOW,
    )
    page.update()

    def scrape_all(e):
        output_section.controls.clear()
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920x1080')
        options.add_argument('--log-level=3')
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36")
        driver = webdriver.Chrome(options=options)
        search_status.update()
        scrapers = [
            get_cooling_post_news,
            get_refindustry_news,
            get_natural_refrigerants_news,
            get_trane_news,
            get_danfoss_news,
            get_LG_B2B_news
        ]
        try:
            total_tasks = len(scrapers)
            for i, scraper in enumerate(scrapers):
                search_status.value = 'Starting to scrape..'
                progress_bar.visible = True
                start = time.time()
                print(f"Running {scraper.__name__}... ({i+1} of {total_tasks})")
                progress_bar.value = (i+1)/total_tasks
                progress_bar.update()
                search_status.value = f'Running {scraper.__name__}... ({i+1} of {total_tasks})'
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
        df6 = pd.read_csv('csv/LG_B2B_news.csv')
        combined_df = pd.concat([df1, df2, df3, df4, df5, df6], ignore_index=True)
        combined_df.to_csv('csv/combined_news.csv', index=False)
        
        combined_csv = pd.read_csv('csv/combined_news.csv', parse_dates=['PublishDate'])
        combined_csv_df = pd.DataFrame(combined_csv)
        
        def headers(df: pd.DataFrame):
            def sort_handler(index):
                return lambda e: sort_table(index, e.ascending)
            return [
                ft.DataColumn(
                    label=ft.Text(col),
                    on_sort=sort_handler(i)
                )
                for i, col in enumerate(df.columns)
            ]
        
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
        
        def sort_table(index, ascending):
            if index == 0:
                combined_csv_df.sort(
                    key=lambda x: x[0], reverse=False
                )
            else:
                combined_csv_df.sort(key=lambda x: x[0], reverse=not ascending)
            scrape_result.rows = rows(combined_csv_df)
            scrape_result.sort_column_index = index
            scrape_result.sort_column_index = ascending
            scrape_result.update()
        
        scrape_result = ft.DataTable(
                        columns=headers(combined_csv_df),
                        sort_column_index=0,
                        sort_ascending=True,
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
    
    def filter_items(e):
        output_section.controls.clear()
        query = e.strip().lower()
        df = pd.read_csv('csv/combined_news.csv')
        filtered_df = df[
            df.apply(
            lambda row: 
            query in str(row['Title']).lower() 
            or query in str(row['Summary']).lower()
            or query in str(row['Source']).lower(), 
            axis=1
            )
        ]

        def headers(df: pd.DataFrame):
            return [ft.DataColumn(ft.Text(col)) for col in df.columns]

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
            columns=headers(filtered_df),
            sort_column_index=0,
            sort_ascending=True,
            bgcolor='#DCDCDC',
            rows=rows(filtered_df),
            column_spacing=20,
            heading_row_color='#1F2134',
            data_row_color={ft.ControlState.HOVERED: "0x30CCCCCC"},
            show_checkbox_column=True,
            border=ft.border.all(1, ft.Colors.GREY),
            width=1800
        )
        
        def sort_table(index, ascending):
            filtered_df.sort(key=lambda x: x[index], reverse=not ascending)
            scrape_result.rows = rows(filtered_df)
            scrape_result.sort_column_index = index
            scrape_result.sort_ascending = ascending
            scrape_result.update()
            
        output_section.controls.append(scrape_result)
        page.update()
    
    output_section = ft.Column(
        width=1800,
        height=715,
        scroll="auto",
        controls=[]
    )
    
    search_field = ft.TextField(
        border_radius=3,
        label='Search Keywords',
        bgcolor='#ffffff',
        width=400,
        on_change=lambda e: filter_items(e.control.value)
    )

    search_status = ft.Text(
        value='ON STAND-BY...',
        size=15,
        color="#B3B3B3",
        width=400,
    )
    
    progress_bar = ft.ProgressBar(
        width=1735,
        visible=False,
        color = "#18B100"
    )
    
    scrape_button = ft.Container( 
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

    container = ft.Container(
        width = 1800,
        height = 900,
        border_radius=15,
        content=ft.Column(
            controls=[
                ft.Container(  ####-----CONTROLS SECTION-----####
                    padding = ft.padding.all(15),
                    bgcolor="#555555",
                    height=135,
                    width=1800,
                        content=ft.Row(
                            controls=[
                                ft.Container( 
                                    width=1800,
                                    height=150,
                                    content=ft.Column(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    scrape_button,
                                                    search_field
                                                ]
                                            ),
                                            ft.Container(),
                                            search_status,
                                            progress_bar                                               
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
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        
                                    ]
                                )
                            )
                            ,
                            output_section
                        ]
                    )
                )
            ]
        )
    )

    page.add(container)
    
ft.app(target=main)
