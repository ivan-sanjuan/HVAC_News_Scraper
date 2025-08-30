from apps._scrapers import get_scrapers
from apps._paths import get_paths
from apps import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
import win32com.client as outlook
import pythoncom
import flet as ft
import asyncio
import time
import pandas as pd
import sys
import os


class UILogStream:
        def __init__(self, log_func):
            self.log_func = log_func

        def write(self, message):
            if message.strip(): 
                self.log_func(message)

        def flush(self):
            pass
        
class ScrapedData:
    def __init__(self,e,dataframe,output_section,page):
        self.df = dataframe
        self.output_section = output_section
        self.page = page
        self.e = e
        
    def headers(self):
            return [ft.DataColumn(ft.Text(col)) for col in self.df.columns]
        
    def rows(self):
        def open_link():
            self.page.launch_url(self.e.control.data)

        rows = []
        for index, row in self.df.iterrows():
            row_cells = []
            for header in self.df.columns:
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
    
    def output(self):        
        scrape_result = ft.DataTable(
                        columns=self.headers(),
                        sort_column_index=0,
                        sort_ascending=True,
                        bgcolor='#DEDAC6',
                        rows=self.rows(),
                        column_spacing=15,
                        heading_row_color='#2B2B2B',
                        data_row_color={ft.ControlState.HOVERED: "0x30CCCCCC"},
                        show_checkbox_column=True,
                        border=ft.border.all(1, '#78655E'),
                        width=1500
                        )
        self.output_section.controls.append(scrape_result)
        self.page.update()
        
    def run(self):
        self.headers()
        self.rows()
        self.output()
  
def main(page:ft.Page):
    page.window.width = 1500
    page.window.height = 820
    page.window.resizable = True,
    page.horizontal_alignment = 'center'
    page.vertical_alignment = 'center'
    page.title = 'News Scraper Dashboard'
    page.window.frameless = True
    page.window.bgcolor = ft.Colors.TRANSPARENT
    page.bgcolor = ft.Colors.TRANSPARENT
    page.update()
        
    def stop_scraping(e):
        global scraping_active
        scraping_active = False
        print('Stopping scrape... Please wait.')
    
    def scrape_all(e):
        output_section.controls.clear()
        scrape_button_disabled()
        page.update()
        
        def append_log(message):
            log_list.controls.append(ft.Text(message,color='#DEDAC6'))
            sys.stdout = UILogStream(append_log)
            # sys.stderr = UILogStream(append_log)
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
        scrapers = get_scrapers()
        csv_paths = get_paths()
        for csv in csv_paths:
            if os.path.isfile(csv):
                empty = []
                empty_df = pd.DataFrame(empty)
                empty_df.to_csv(csv, index=False)
            else:
                continue
        try:
            global scraping_active
            scraping_active = True
            total_duration = []
            total_tasks = len(scrapers)
            for i, scraper in enumerate(scrapers):
                if scraping_active == True:
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
                    if coverage_input.value == '' or coverage_input.value == '0':
                        coverage_days = 1
                    else:
                        coverage_days = int(coverage_input.value)
                    scraper(driver,coverage_days=coverage_days)
                    duration = time.time() - start
                    status_2 = f"{scraper.__name__} completed in {duration:.2f} seconds"
                    append_log(status_2)
                    progress_bar.value = (i+1)/total_tasks
                    progress_bar.update()
                    total_duration.append(duration)
                    time.sleep(2)
                else:
                    break
        finally:
            status_report_generation = 'SCRAPING COMPLETE, GENERATING REPORT...'
            total_time = runtime()
            report = f'TOTAL Runtime: {format_runtime(total_time)}'
            append_log(status_report_generation)
            append_log(report)
            time.sleep(1)
            driver.quit()
            search_status.value = report
            scrape_button_enabled()
            page.update()
        
        valid_dfs = []
        for path in csv_paths:
            if os.path.getsize(path) == 0:
                print(f'Skipping empty file: {path}')
                continue
            try:
                df = pd.read_csv(path)
                if not df.empty:
                    valid_dfs.append(df)
                else:
                    print(f'Skipping empty DataFrame: {path}')
            except pd.errors.EmptyDataError:
                print(f'{path} has no content')
            except Exception as e:
                print(f'Error reading {path}: {e}')
            except UnboundLocalError:
                today=datetime.today()
                print(f'NO NEW News at the moment: {today}')
        if len(valid_dfs) > 0:
            combined_df = pd.concat(valid_dfs, ignore_index=True)
            filename_scraped_news = f'csv/combined_news.csv'
            combined_df.to_csv(filename_scraped_news, index=False)
            combined_csv = pd.read_csv(filename_scraped_news)
            combined_csv_df = pd.DataFrame(combined_csv)
            initial_scrape = ScrapedData(e,combined_csv_df,output_section,page)
            initial_scrape.run()
        else:
            today=datetime.today()
            today_formatted=today.strftime('%B %d, %Y | %X')
            print(f'NO NEW News at the moment: {today_formatted}')
            search_status.value = f'No NEW News at the moment: {today_formatted}'
            search_status.update()
    
    def filter_items(e):
        output_section.controls.clear()
        query = e.strip().lower()
        filename_scraped_news = f'csv/combined_news.csv'
        df = pd.read_csv(filename_scraped_news)
        filtered_df = df[
            df.apply(
            lambda row: 
            query in str(row['Title']).lower() 
            or query in str(row['Summary']).lower()
            or query in str(row['Source']).lower()
            or query in str(row['Type']).lower(), 
            axis=1
            )
        ]
        filtered_result = ScrapedData(e,filtered_df,output_section,page)
        filtered_result.run()
        
    def minimize_window(e):
        page.window.minimized = True
        page.update()
        
    def destroy_window(e):
        page.window.destroy()
        page.update()
        
    def refresh_time(e):
        while True:
            current_time = datetime.now().strftime('%c')
            date_time_field.value = f"|  {current_time}"
            time.sleep(1)
            page.update()

    def create_report():
        today_csv=datetime.today()
        today_csv_formatted=today_csv.strftime('%Y-%m-%d')
        combined_news = pd.read_csv('csv/combined_news.csv')
        df = pd.DataFrame(combined_news)
        report = df.to_csv(f'csv/scraped_news_{today_csv_formatted}.csv', index=False)
        return report
    
    def send_to_outlook(e):
        pythoncom.CoInitialize()
        today=datetime.today()
        today_formatted=today.strftime('%B %d, %Y')
        olApp = outlook.Dispatch(f'Outlook.Application')
        mail_item = olApp.CreateItem(0)
        mail_item.Subject = f'Scraped News for {today_formatted}'
        create_report()
        today_csv=datetime.today()
        today_csv_formatted=today_csv.strftime('%Y-%m-%d')
        base_dir = os.path.dirname(os.path.abspath(__file__))
        filename_scraped_news = os.path.join(base_dir, 'csv', f'scraped_news_{today_csv_formatted}.csv')
        mail_item.Attachments.Add(filename_scraped_news)
        mail_item.Display()
        pythoncom.CoUninitialize()

    def report_issue(e):
        pythoncom.CoInitialize()
        olApp = outlook.Dispatch(f'Outlook.Application')
        mail_item = olApp.CreateItem(0)
        mail_item.Subject = 'Issue on HVACR NEWS Scraper Tool'
        mail_item.Display()
        pythoncom.CoUninitialize()
    
    def scrape_button_disabled():
        scrape_running_button.visible = True
        scrape_button.visible = False
        scrape_button.disabled = True
        scrape_running_button.disabled = False
        search_field.disabled = True
        coverage_input.disabled = True
        search_field.bgcolor = "#888888"
        coverage_input.bgcolor = "#888888"
        send_report.disabled = True
        send_report.visible = False
        page.update()
    
    def scrape_button_enabled():
        scrape_button.visible = True
        scrape_button.disabled = False
        scrape_running_button.visible = False
        scrape_running_button.disabled = True
        search_field.disabled = False
        coverage_input.disabled = False
        search_field.bgcolor = "#ffffff"
        search_field.disabled = False
        coverage_input.bgcolor = "#ffffff"
        send_report.disabled = False
        send_report.visible = True
        page.update()
        
    max_value = 30
    def validate_number(e):
        try:
            value=int(e.control.value)
            if value>max_value:
                e.control.value = str(max_value)
                search_status.value = f'I can only scrape {max_value} days worth of news.. (reliably, atleast.)'
            else:
                search_status.value = 'ON STAND-BY...'
        except ValueError:
            search_status.value = "you can leave it blank (i'll still change it to 1 :D)"
        search_status.update()
    
    output_section = ft.Column(
        scroll="auto",
        controls=[]
    )
    
    search_field = ft.TextField(
        border_radius=10,
        height=50,
        label='Search Keywords',
        hint_text="ex. acquisitions",
        bgcolor='#888888',
        color='#354850',
        disabled=True,
        width=400,
        border_width=2,
        focused_border_color="#AB5637",
        on_change=lambda e: filter_items(e.control.value),
        label_style=ft.TextStyle(
            color='#354850',
            size=12,
        )
    )
    
    coverage_input = ft.TextField(
        width=73,
        height=50,
        hint_text='Days',
        label='RANGE',
        max_length=2,
        input_filter=ft.NumbersOnlyInputFilter(),
        value='',
        multiline=False,
        bgcolor='#ffffff',
        color='#354850',
        border_width=2,
        border_radius=10,
        focused_border_color='#AB5637',
        text_align=ft.TextAlign.CENTER,
        keyboard_type=ft.KeyboardType.NUMBER,
        on_change=validate_number,
        label_style=ft.TextStyle(
            color='#354850',
            size=12,
        )
    )

    search_status = ft.Text(
        value='ON STAND-BY...',
        size=15,
        color='#DEDAC6',
        width=400,
    )
    
    progress_bar = ft.ProgressBar(
        visible=False,
        color = "#6AADCD",
        bar_height=20,
        border_radius=ft.border_radius.all(10)
    )
    
    scrape_button = ft.Container( 
        width=300,
        height=50,
        content=ft.ElevatedButton(
            text='START SCRAPING...',
            icon=ft.Icons.MANAGE_SEARCH_OUTLINED,
            icon_color='#2B2B2B',
            elevation=5,
            width=200,
            height=20,
            on_click=scrape_all,
            bgcolor='#6AADCD',
            visible=True,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=30),
                text_style=ft.TextStyle(size=18, weight=ft.FontWeight.W_500),
                color="#2B2B2B"
            ),
        )
    )
    
    scrape_running_button = ft.Container( 
        width=300,
        height=50,
        content=ft.ElevatedButton(
            text='STOP SCRAPING',
            icon=ft.Icons.CANCEL_OUTLINED,
            icon_color="#DEDAC6",
            width=200,
            height=20,
            on_click=stop_scraping,
            bgcolor='#AB5637',
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=30),
                text_style=ft.TextStyle(size=18, weight=ft.FontWeight.NORMAL),
                color='#DEDAC6'
            ),
        )
    )
    
    send_report = ft.Container( 
        width=250,
        height=50,
        visible=False,
        content=ft.ElevatedButton(
            text='SEND TO OUTLOOK',
            icon=ft.Icons.ATTACH_EMAIL_ROUNDED,
            icon_color='#78655E',
            elevation=5,
            width=200,
            height=20,
            on_click=send_to_outlook,
            bgcolor='#DEDAC6',
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=30),
                text_style=ft.TextStyle(size=18, weight=ft.FontWeight.NORMAL),
                color="#2B2B2B"
            ),
        )
    )
    
    scrape_buttons_stack = ft.Stack(
        width=300,
        height=50,
        controls=[
            scrape_running_button,
            scrape_button
        ]
    )
    
    log_list = ft.ListView(
        height=100,
        expand=False,
        spacing=3,
        auto_scroll=True,
        padding=ft.padding.only(top=15,bottom=15,right=0,left=0)
    )
    
    close_button = ft.IconButton(
        icon=ft.Icons.CLOSE_OUTLINED,
        icon_color='#DEDAC6',
        on_click=destroy_window,
        hover_color="#AB5637"
    )
    
    minimize_button = ft.IconButton(
        icon=ft.Icons.MINIMIZE_OUTLINED,
        icon_color='#DEDAC6',
        on_click=minimize_window,
        hover_color="#AB5637"
    )
    
    window_controls = ft.Row(
        controls=[
            minimize_button,
            close_button
        ]
    )
    
    date_time_field = ft.Text(
        value='',
        color='#DEDAC6'
    )
    
    tool_name = ft.Text(
        value='HVACR News - Scraper Tool',
        color='#DEDAC6',
        weight=ft.FontWeight.W_500
    )

    container = ft.Container(
        width = 1500,
        height = 800,
        bgcolor="#2B2B2B",
        border_radius=15,
        content=ft.Column(
            controls=[
                ft.WindowDragArea(
                    ft.Container(
                        bgcolor="#78655E",
                        width=1500,
                        height=35,                                      
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Container(
                                    padding=ft.padding.only(left=15,right=0,top=0,bottom=0),
                                    content=ft.Row(
                                        controls=[
                                            tool_name,
                                            date_time_field
                                        ]
                                    )
                                ),
                                window_controls,
                            ]
                        )
                    )
                ),
                ft.Container(  ####-----CONTROLS SECTION-----####
                    bgcolor="#2B2B2B",
                    width=1500,
                        content=ft.Row(
                            controls=[
                                ft.Container(
                                    width=1500,
                                    content=ft.Row(
                                        controls=[
                                            ft.Container(   #---- 1st COLUMN OF CONTROLS
                                                padding = ft.padding.all(15),
                                                width=1100,
                                                content=ft.Column(
                                                    controls=[  
                                                        ft.Row( 
                                                            controls=[
                                                                scrape_buttons_stack,
                                                                coverage_input,
                                                                search_field,
                                                                send_report
                                                            ]
                                                        ),
                                                        ft.Column(
                                                            controls=[
                                                                search_status,
                                                                
                                                            ]
                                                        )
                                                    ]
                                                )
                                            ),
                                            ft.Container(   #---- 2nd COLUMN OF CONTROLS
                                                content=log_list
                                            ),
                                            
                                        ]
                                    )
                                )
                            ]
                        )
                    ),
                ft.Container( ####-----OUTPUT_SECTION-----####
                    padding = ft.padding.all(15),
                    height=585,
                    width=1500,
                    bgcolor='#DEDAC6',
                    on_hover=refresh_time,
                    content=output_section
                    
                ),
                ft.Container(
                    padding=ft.padding.only(left=15,right=15,top=0,bottom=0),
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                width=1300,
                                content=progress_bar
                            ),
                            ft.TextButton(
                                'Report an Issue',
                                on_click=report_issue,
                                icon=ft.Icons.REPORT_PROBLEM_OUTLINED,
                                style=ft.ButtonStyle(
                                    color='#ffffff'
                                )
                            ),
                        ]
                    )
                )
            ]
        )
    )
    
    page.add(container)
    
    
ft.app(target=main)
