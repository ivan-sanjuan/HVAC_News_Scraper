from apps.scraper_coolingpost import get_cooling_post_news
from apps.scraper_refindustry import get_refindustry_news
from apps.scraper_natural_refrigerants import get_natural_refrigerants_news
from apps.scraper_trane_technologies import get_trane_news
from apps.scraper_danfoss import get_danfoss_news
from apps.scraper_LG_B2B import get_LG_news
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
import flet as ft
import time
import pandas as pd
import sys


class UILogStream:
        def __init__(self, log_func):
            self.log_func = log_func

        def write(self, message):
            if message.strip(): 
                self.log_func(message)

        def flush(self):
            pass
  
def main(page:ft.Page):
    page.window.width = 1800
    page.window.height = 950
    page.window.resizable = False,
    page.horizontal_alignment = 'center'
    page.vertical_alignment = 'center'
    page.title = 'News Scraper Dashboard'

    page.update()

    def scrape_all(e):
        output_section.controls.clear()
        
        try:
            coverage_days = int(coverage_input.value)
        except ValueError:
            search_status.value = 'Invalid coverage days. Please enter a number.'
            search_status.update()
            return
        
        def append_log(message):
            log_list.controls.append(ft.Text(message,color='#354850'))
            sys.stdout = UILogStream(append_log)
            sys.stderr = UILogStream(append_log)
            log_list.update()
        
        def runtime():
            total_seconds = sum(total_duration)
            return timedelta(seconds=total_seconds)
        
        def format_runtime(td):
            total_seconds = int(td.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        
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
            get_LG_news
        ]
        
        try:
            total_duration = []
            total_tasks = len(scrapers)
            for i, scraper in enumerate(scrapers):
                search_status.value = 'Starting to scrape..'
                start = time.time()
                if i == 0:
                    append_log(search_status.value)
                else:
                    pass
                progress_bar.visible = True
                status_1 = f"Running {scraper.__name__}... ({i+1} of {total_tasks})"
                search_status.value = f'Running {scraper.__name__}... ({i+1} of {total_tasks})'
                search_status.update()
                append_log(status_1)
                progress_bar.value = (i+1)/total_tasks
                progress_bar.update()
                scraper(driver,coverage_days=coverage_days)
                duration = time.time() - start
                status_2 = f"{scraper.__name__} completed in {duration:.2f} seconds"
                append_log(status_2)
                progress_bar.value = (i+1)/total_tasks
                progress_bar.update()
                total_duration.append(duration)
                time.sleep(2)
        finally:
            status_report_generation = 'SCRAPING COMPLETE, GENERATING REPORT...'
            total_time = runtime()
            report = f'TOTAL Runtime: {format_runtime(total_time)}'
            append_log(status_report_generation)
            append_log(report)
            time.sleep(1)
            driver.quit()
            
        df1 = pd.read_csv('csv/ref_industry_news.csv')
        df2 = pd.read_csv('csv/cooling_post_news.csv')
        df3 = pd.read_csv('csv/natural_refrigerants_news.csv')
        df4 = pd.read_csv('csv/trane_technologies_news.csv')
        df5 = pd.read_csv('csv/danfoss_news.csv')
        df6 = pd.read_csv('csv/LG_News.csv')
        combined_df = pd.concat([df1, df2, df3, df4, df5, df6], ignore_index=True)
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
            
        output_section.controls.append(scrape_result)
        page.update()
    
    output_section = ft.Column(
        width=1800,
        height=715,
        scroll="auto",
        controls=[]
    )
    
    search_field = ft.TextField(
        border_radius=10,
        height=50,
        label='Search Keywords',
        bgcolor='#ffffff',
        color='#354850',
        width=400,
        border_width=2,
        border_color='#BAA186',
        focused_border_color='#354850',
        on_change=lambda e: filter_items(e.control.value),
        label_style=ft.TextStyle(
            color='#354850',
            size=12,
        )
    )

    search_status = ft.Text(
        value='ON STAND-BY...',
        size=15,
        color='#354850',
        width=400,
    )
    
    progress_bar = ft.ProgressBar(
        width=1735,
        visible=False,
        color = "#52CBFB",
        bar_height=20,
        border_radius=ft.border_radius.all(10)
    )
    
    scrape_button = ft.Container( 
        width=300,
        height=50,
        content=ft.ElevatedButton(
            text='START SCRAPING...',
            icon=ft.Icons.MANAGE_SEARCH_OUTLINED,
            icon_color='#52CBFB',
            elevation=5,
            width=200,
            height=20,
            on_click=scrape_all,
            bgcolor='#354850',
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=30),
                text_style=ft.TextStyle(size=20, weight=ft.FontWeight.NORMAL),
                color="#FFFFFF"
            ),
        )
    )
    
    coverage_input = ft.TextField(
        width=73,
        height=50,
        label='DURATION',
        max_length=2,
        value=3,
        multiline=False,
        fill_color='#ffffff',
        color='#354850',
        border_width=2,
        border_radius=10,
        border_color='#BAA186',
        focused_border_color='#354850',
        text_align=ft.TextAlign.CENTER,
        label_style=ft.TextStyle(
            color='#354850',
            size=12,
        )
    )
    
    log_list = ft.ListView(
        expand=False,
        spacing=3,
        auto_scroll=True,
        padding=ft.padding.only(top=15,bottom=15,right=0,left=0)
    )

    container = ft.Container(
        width = 1800,
        height = 900,
        border_radius=15,
        content=ft.Column(
            controls=[
                ft.Container(  ####-----CONTROLS SECTION-----####
                    padding = ft.padding.all(15),
                    bgcolor="#FABB75",
                    height=135,
                    width=1800,
                        content=ft.Row(
                            controls=[
                                ft.Container( 
                                    width=1800,
                                    height=150,
                                    content=ft.Row(
                                        controls=[
                                            ft.Container(   #---- 1ST COLUMN OF CONTROLS
                                                width=1200,
                                                content=ft.Column(
                                                    controls=[  #---- 1st Row of Controls
                                                        ft.Row( 
                                                            controls=[
                                                                scrape_button,
                                                                coverage_input,
                                                                search_field
                                                            ]
                                                        ),
                                                        ft.Column(
                                                            controls=[
                                                                search_status,
                                                                progress_bar
                                                            ]
                                                        )
                                                    ]
                                                )
                                            ),
                                            ft.Container(
                                                content=log_list
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
                    bgcolor='#354850',
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
