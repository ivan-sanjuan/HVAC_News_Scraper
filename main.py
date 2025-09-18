from apps._scrapers import get_scrapers
from apps._paths import get_paths
from apps import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
import win32com.client as outlook
from pandas.errors import EmptyDataError
from functools import partial
import threading
import pythoncom
import flet as ft
import asyncio
import time
import pandas as pd
import sys
import os
import queue
import io
import sys

class UILogStream:
        def __init__(self, log_func):
            self.log_func = log_func

        def write(self, message):
            if message.strip(): 
                self.log_func(message)

        def flush(self):
            pass
        
class ScrapedData:
    def __init__(self,e,dataframe,page):
        self.df = dataframe
        self.scrape_result = None
        self.page = page
    
    def open_link(self, e):
            self.page.launch_url(e.control.data)
     
    def headers(self):
            return [ft.DataColumn(ft.Text(col)) for col in self.df.columns]
        
    def rows(self):
        rows = []
        for index, row in self.df.iterrows():
            row_cells = []
            for header in self.df.columns:
                cell_value = str(row[header])

                if cell_value.startswith("http://") or cell_value.startswith("https://"):
                    cell_content = ft.TextButton(
                        text="Visit",
                        data=cell_value,
                        on_click=self.open_link,
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
        self.scrape_result = ft.DataTable(
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
        return self.scrape_result
        
    def run(self):
        return self.output()
  
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
    color_primary_dark = '#1C1C52'
    color_primary = '#0F3CFF'
    color_neutral = '#3D3D34'
    color_neutral_light = '#AAA089'
    color_neutral_lighter = '#D5D0C5'
    color_tint_mint = '#93C7A1'
    color_tint_lilac = '#CECFE9'
    color_tint_orange = '#DF8369'
    ui_queue = asyncio.Queue()
    
    
    def stop_scraping(e):
        global scraping_active
        scraping_active = False
        search_status.value = 'Run will be stopped after this function.. Please wait.'

    async def poll_ui():
        while True:
            msg_type, payload = await ui_queue.get()
            # print(f"Received UI message: {msg_type} → {payload}")
            if msg_type == "log":
                log_list.controls.append(ft.Text(payload, color='#DEDAC6'))
                sys.stdout = UILogStream(append_log)

            elif msg_type == "status":
                search_status.value = payload

            elif msg_type == "progress":
                progress_bar.value = payload

            elif msg_type == "show_progress":
                progress_bar.visible = payload

            elif msg_type == "display_output":
                output_section.controls.clear()
                output_section.controls.append(payload)

            elif msg_type == "clear_output":
                output_section.controls.clear()

            elif msg_type == "done":
                send_report.disabled = False

            page.update()
            await asyncio.sleep(0.1)
            
        
    def append_log(message):
            log_list.controls.append(ft.Text(message,color='#DEDAC6'))
            sys.stdout = UILogStream(append_log)
            # sys.stderr = UILogStream(append_log)
            log_list.update()
        
    def start_scraping(e):
        page.run_task(poll_ui)
        page.run_task(scrape_all)
        
    async def call_scrape_function(scraper,driver,coverage_days):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None,scraper,driver,coverage_days)
    
    async def scrape_all():
        await ui_queue.put(('clear_output','clear'))
        scrape_button_disabled()
        
        def runtime():
            total_seconds = sum(total_duration)
            return timedelta(seconds=total_seconds)
        
        def format_runtime(td):
            total_seconds = int(td.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        
        options = Options()
        scrapers = get_scrapers()
        exceptions = ['get_HPA','get_embraco']
        if any(exception in scrapers for exception in exceptions):
            options.page_load_strategy = 'eager'
        options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920x1080')
        options.add_argument('--log-level=3')
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115 Safari/537.36")
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(1920, 1080)
        csv_paths = get_paths()
        for csv in csv_paths:
            if os.path.isfile(csv):
                empty = []
                empty_df = pd.DataFrame(empty)
                await save_csv_async(empty_df,csv)
                
            else:
                continue
            await asyncio.sleep(0.1)
        try:
            global scraping_active
            scraping_active = True
            total_duration = []
            total_tasks = len(scrapers)
            for i, scraper in enumerate(scrapers):
                if scraping_active == True:
                    await ui_queue.put(('status', 'Starting to scrape..'))
                    start = time.time()
                    if i == 0:
                        await ui_queue.put(('log', 'Starting to scrape.'))
                    else:
                        pass
                    await ui_queue.put(('show_progress',True))
                    await ui_queue.put(('status',f'Running {scraper.__name__}... ({i+1} of {total_tasks})'))
                    await ui_queue.put(('log',f'Running {scraper.__name__}... ({i+1} of {total_tasks})'))
                    await ui_queue.put(('progress',(i+1)/total_tasks))
                    if coverage_input.value == '' or coverage_input.value == '0':
                        coverage_days = 1
                    else:
                        coverage_days = int(coverage_input.value)
                    try:
                        loop = asyncio.get_running_loop()
                        await loop.run_in_executor(None,scraper,driver,coverage_days)
                        await asyncio.sleep(0.1)
                    except Exception as f:
                        print(f'An error has occured: {f}')
                    duration = time.time() - start
                    await ui_queue.put(('log',f"{scraper.__name__} completed in {duration:.2f} seconds"))
                    await ui_queue.put(('progress',(i+1)/total_tasks))
                    total_duration.append(duration)
                    await asyncio.sleep(0.1)
                else:
                    break
        finally:
            status_report_generation = 'SCRAPING COMPLETE, GENERATING REPORT...'
            total_time = runtime()
            report = f'TOTAL Runtime: {format_runtime(total_time)}'
            driver.quit()
            await ui_queue.put(('log',status_report_generation))
            await ui_queue.put(('log',report))
            await ui_queue.put(('status',report))
            scrape_button_enabled()
            await asyncio.sleep(0.1)
        
        valid_dfs = []
        for path in csv_paths:
            if os.path.getsize(path) == 0:
                print(f'Skipping empty file: {path}')
                continue
            try:
                df = await read_csv_async(path)
                if not df.empty:
                    valid_dfs.append(df)
                else:
                    print(f'Skipping empty DataFrame: {path}')
            except pd.errors.EmptyDataError:
                print(f'{path} has no content')
            except Exception as g:
                print(f'Error reading {path}: {g}')
            except UnboundLocalError:
                today=datetime.today()
                print(f'NO NEW News at the moment: {today}')
            await asyncio.sleep(0.1)
        if len(valid_dfs) > 0:
            combined_df = pd.concat(valid_dfs, ignore_index=True)
            await save_csv_async(combined_df,'csv/combined_news.csv')
            combined_csv = await read_csv_async('csv/combined_news.csv')
            combined_csv_df = pd.DataFrame(combined_csv)
            scraped_data = ScrapedData(None,combined_csv_df,page)
            await ui_queue.put(("display_output", scraped_data.run()))
            await asyncio.sleep(0.1)
        else:
            today=datetime.today()
            today_formatted=today.strftime('%B %d, %Y | %X')
            print(f'NO NEW News at the moment: {today_formatted}')
            await ui_queue.put('status',f'No NEW News at the moment: {today_formatted}')
            await asyncio.sleep(0.1)
    
    async def reload_results(e):
        try:
            df = await read_csv_async('csv/combined_news.csv')
            if df.empty:
                raise EmptyDataError
            results = ScrapedData(None,df,page)
            result = results.run()
            output_section.controls = [result,]
            page.update()
            scrape_button_enabled()
        except EmptyDataError:
            search_status.value = 'No results to display.'
            search_status.update()
    
    async def filter_items(e):
        await ui_queue.put(('clear_output','clear'))
        query = e.strip().lower()
        filename_scraped_news = f'csv/combined_news.csv'
        df = await read_csv_async(filename_scraped_news)
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
        filtered_result = ScrapedData(None,filtered_df,page)
        output_section.controls = [filtered_result.run()]
        page.update()
        await ui_queue.put(("display_output",filtered_result.run()))
        
    async def save_csv_async(data,file_path):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None,partial(data.to_csv,file_path,index=False))
    
    async def read_csv_async(file_path):
        loop = asyncio.get_running_loop()
        df = await loop.run_in_executor(None,pd.read_csv,file_path)
        return df
        
    def minimize_window(e):
        page.window.minimized = True
        page.update()
    
    def closing_window(e):
        threading.Thread(
            target=destroy_window,
            daemon=True
        ).start()
    
    def destroy_window():
        page.window.visible = False
        page.window.destroy()
        page.update()
        
    def refresh_time(e):
        while True:
            current_time = datetime.now().strftime('%c')
            date_time_field.value = f"|  {current_time}"
            time.sleep(1)
            page.update()

    async def create_report():
        today_csv=datetime.today()
        today_csv_formatted=today_csv.strftime('%Y-%m-%d')
        combined_news = await read_csv_async('csv/combined_news.csv')
        df = pd.DataFrame(combined_news)
        await save_csv_async(df,f'csv/Reports/scraped_news_{today_csv_formatted}.csv')
    
    def send_to_outlook(e):
        try:
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
            filename_scraped_news = os.path.join(base_dir, 'csv/Reports', f'scraped_news_{today_csv_formatted}.csv')
            mail_item.Attachments.Add(filename_scraped_news)
            mail_item.Display()
            pythoncom.CoUninitialize()
        except EmptyDataError:
            search_status.value = 'No currently saved data to send.'

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
        search_field.bgcolor = color_neutral_light
        coverage_input.bgcolor = color_neutral_light
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
    
    async def handle_search_change(e):
        await filter_items(e.control.value)
          
    def save_csv(e):
        df = pd.read_csv('csv/combined_news.csv')
        df.to_csv(os.path.expanduser("~"))
        
    def stopping_scrape(e):
        threading.Thread(
            target=stop_scraping,
            args=(e,),
            daemon=True
        ).start()
        
        
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    async def save_and_export(path):
        df = await read_csv_async('csv/combined_news.csv')
        await save_csv_async(df, path)

    def handle_save_click(e):
        file_picker.save_file(
            dialog_title="Save scraped results",
            file_name="scraped_results.csv",
            allowed_extensions=["csv"]
        )

    def on_save_result(e: ft.FilePickerResultEvent):
        print('saving')
        if e.path:
            page.run_task(lambda: save_and_export(e.path))

    file_picker.on_result = on_save_result


    
    output_section = ft.Column(
        scroll="auto",
        controls=[]
    )
    
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    
    search_field = ft.TextField(
        border_radius=10,
        height=50,
        label='SEARCH KEYWORDS',
        hint_text="ex. acquisitions",
        bgcolor=color_neutral_light,
        color='#354850',
        disabled=True,
        width=400,
        border_width=2,
        focused_border_color=color_tint_mint,
        on_change=handle_search_change,
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
        focused_border_color=color_tint_mint,
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
        width=383,
    )
    
    progress_bar = ft.ProgressBar(
        visible=False,
        color = color_tint_lilac,
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
            on_click=start_scraping,
            bgcolor=color_tint_mint,
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
            on_click=stopping_scrape,
            bgcolor=color_tint_orange,
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
            bgcolor=color_tint_lilac,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=30),
                text_style=ft.TextStyle(size=18, weight=ft.FontWeight.NORMAL),
                color="#2B2B2B"
            ),
        )
    )
    
    reload_last_result = ft.Container( 
        width=200,
        height=30,
        content=ft.ElevatedButton(
            text='RELOAD RESULT',
            icon=ft.Icons.FOLDER_OPEN_ROUNDED,
            elevation=5,
            width=190,
            height=20,
            on_click=reload_results,
            bgcolor=color_tint_lilac,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                text_style=ft.TextStyle(size=14, weight=ft.FontWeight.NORMAL),
                color="#2B2B2B"
            ),
        )
    )
    
    save_result = ft.Container( 
        width=190,
        height=30,
        content=ft.ElevatedButton(
            text='SAVE',
            icon=ft.Icons.SAVE_ALT_ROUNDED,
            elevation=5,
            width=200,
            height=20,
            on_click=handle_save_click,
            bgcolor=color_tint_lilac,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                text_style=ft.TextStyle(size=14, weight=ft.FontWeight.NORMAL),
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
        on_click=closing_window,
        hover_color=color_tint_orange
    )
    
    minimize_button = ft.IconButton(
        icon=ft.Icons.MINIMIZE_OUTLINED,
        icon_color='#DEDAC6',
        on_click=minimize_window,
        hover_color=color_tint_orange
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
    )

    container = ft.Container(
        width = 1500,
        height = 800,
        bgcolor=color_primary_dark,
        border_radius=15,
        content=ft.Column(
            controls=[
                ft.WindowDragArea(
                    ft.Container(
                        bgcolor=color_primary,
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
                    bgcolor=color_primary_dark,
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
                                                        ft.Row(
                                                            controls=[
                                                                search_status,
                                                                reload_last_result,
                                                                save_result
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
                    height=570,
                    width=1500,
                    bgcolor=color_neutral_lighter,
                    # on_hover=refresh_time,
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
                                    color=color_tint_orange
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
