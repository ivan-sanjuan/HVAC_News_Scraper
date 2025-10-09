from apps._scrapers import get_scrapers
from apps._paths import get_paths
from apps._exceptions import get_exceptions
from apps._useragents import user_agents
from apps._response import get_scraper_classes
from apps._save_dialog import launch_dialog
import certifi
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
import win32com.client as outlook
from pandas.errors import EmptyDataError
from selenium.common.exceptions import TimeoutException, WebDriverException
from functools import partial
from requests.exceptions import ReadTimeout, ConnectTimeout, RequestException, SSLError
from tkinter import Tk, filedialog
import socket
import requests
import pyautogui
import random
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
                        style=ft.ButtonStyle(color=ft.Colors.BLUE),
                    )
                else:
                    cell_content = ft.Text(cell_value, color='#1F2134')

                if header == "Title":
                    cell_widget = ft.Container(
                        content=cell_content,
                        width=450
                    )
                else:
                    cell_widget = cell_content

                row_cells.append(ft.DataCell(cell_widget))
            rows.append(ft.DataRow(cells=row_cells,
                                   color={
                                    ft.ControlState.HOVERED: '#AAA089',
                                    ft.ControlState.SELECTED: '#93C7A1',
                                    ft.ControlState.DEFAULT: '#DEDAC6',
                                    }
                                    )
                        )
        return rows
    
    def output(self):        
        self.scrape_result = ft.DataTable(
                        columns=self.headers(),
                        heading_text_style=ft.TextStyle(color="#ffffff",weight=ft.FontWeight.BOLD),
                        sort_column_index=0,
                        sort_ascending=True,
                        bgcolor='#DEDAC6',
                        rows=self.rows(),
                        column_spacing=15,
                        heading_row_color='#2B2B2B',
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
        print('Polling started')
        buffer = io.StringIO()
        while True:
            msg_type, payload = await ui_queue.get()
            
            if msg_type == "log":
                log_list.controls.append(ft.Text(payload, color='#DEDAC6'))

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
                
            elif msg_type == "start_log":
                task = asyncio.create_task(append_log(buffer))
                
            elif msg_type == "end_log":
                print("Logging ended..")
                task.cancel()
                with open("scrape_log.txt", "w", encoding="utf-8") as f:
                    f.write(buffer.getvalue())
            
            elif msg_type == "nudge_on":
                sleep = asyncio.create_task(prevent_sleep(payload))
                
            
            elif msg_type == "nudge_off":
                sleep.cancel()
                print('Nudges is now DISABLED.')
                
            page.update()
            await asyncio.sleep(0.1)
    
            
    async def append_log(buffer):
        sys.stdout = buffer
        print("Logging started..")
        original_stdout = sys.stdout
        output_section_log.controls.append(output_section_log_text)
        while True:
            output_section_log_text.value = buffer.getvalue()
            page.update()
            await asyncio.sleep(0.2)
    
    async def prevent_sleep(condition):
        print('Nudges: ACTIVE; Preventing desktop to sleep while scrape is ongoing.')
        while True:
            if condition == True:
                pyautogui.moveRel(1, 1, duration=0.1)
                pyautogui.moveRel(-1, 1, duration=0.1)
                await asyncio.sleep(30)
        
    def start_scraping(e):
        scrape_button_disabled()
        page.run_task(poll_ui)
        page.run_task(scrape_all)
        
    def check_head(url):
        response = None
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/117 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.google.com/",
            }
            response = requests.get(url,headers=headers,timeout=(15,15),stream=True)
            response.close()
            if response.status_code == 403:
                print('Status code returns 403, retrying...')
                response = requests.head(url,headers=headers, timeout=(20,20), verify=False)
            else:
                print(f'Site returned status code: {response.status_code}')
        except requests.exceptions.SSLError:
            print('SSL Certificate is being bypassed for this site.')
            response = requests.get(url,headers=headers,timeout=(20,20),stream=True,verify=False)
            response.close()
        except requests.RequestException as e:
            print(f"Request failed: {e}")
        if response:
            return response.status_code
        if not response:
            print(f'Site failed to respond, please visit the site instead.')
            pass
            
    async def call_scrape_function(scraper,driver,coverage_days):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None,scraper,driver,coverage_days)
    
    async def scrape_all():
        await ui_queue.put(('clear_output','clear'))
        await ui_queue.put(('show_progress',True))
        await ui_queue.put(('start_log','start'))
        await ui_queue.put(('nudge_on',True))
        await asyncio.sleep(1)
        def runtime():
            total_seconds = sum(total_duration)
            return timedelta(seconds=total_seconds)
        
        def format_runtime(td):
            total_seconds = int(td.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        
        failed_scrapers = []
        def failed_scrapers_func(source,link,scraper_type):
            failed_scrapers.append(
                {
                    'PublishDate':'-----',
                    'Source':source,
                    'Type':scraper_type,
                    'Title':'Failed scrape',
                    'Summary':'Please visit the site instead.',
                    'Link':link
                }
            )
        
        options = Options()
        scrapers = get_scrapers()
        exceptions = get_exceptions()
        useragents = user_agents()
        csv_paths = get_paths()
        user_agent = random.choice(useragents)
        print(f'User Agent: {user_agent}')
        if any(exception in scrapers for exception in exceptions):
            options.page_load_strategy = 'eager'
        options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920x1080')
        options.add_argument('--log-level=3')
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(f'user-agent={user_agent}')
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(1920, 1080)
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
            failed_list = []
            total_tasks = len(scrapers)
            for i, scrape in enumerate(scrapers):
                scraper = scrape.get('func')
                url = scrape.get('url')
                scraper_name = scrape.get('name')
                scraper_type = scrape.get('type')
                print(f'\nTrying to access: {scraper_name}')
                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(None,check_head,url)
                if not response:
                    pass
                if scraping_active == True:
                    await ui_queue.put(('status', 'Starting to scrape..'))
                    start = time.time()
                    if i == 0:
                        await ui_queue.put(('log', 'Starting to scrape.'))
                    else:
                        pass
                    await ui_queue.put(('status',f'Running {scraper_name} scraper... ({i+1} of {total_tasks})'))
                    await ui_queue.put(('log',f'Running {scraper_name} scraper... ({i+1} of {total_tasks})'))
                    await ui_queue.put(('progress',(i+1)/total_tasks))
                    if coverage_input.value == '' or coverage_input.value == '0':
                        coverage_days = 1
                    else:
                        coverage_days = int(coverage_input.value)
                    try:
                        if response == 200:
                            try:
                                print(f'✅{scraper_name} returned [200]"OK" RESPONSE.')
                                await asyncio.sleep(1)
                                await loop.run_in_executor(None,scraper,driver,coverage_days)
                            except (ReadTimeout, ConnectTimeout) as e:
                                if len(failed_list) == 0:
                                    failed_scraper_log.controls.append(failed_scraper_title)
                                print(f'⛔{scraper_name} Error: {e}')
                                failed_scrapers_func(scraper_name,url,scraper_type)
                                failed_list.append(f'⚠️{scraper_name}')
                                failed_scraper_log.controls.append(failed_scraper_log_text)
                                failed_scraper_log_text.value = ('\n'.join(failed_list))
                                page.update()
                                pass
                            except (RequestException,socket.timeout) as e:
                                if len(failed_list) == 0:
                                    failed_scraper_log.controls.append(failed_scraper_title)
                                print(f'⛔{scraper_name} Error: {e}')
                                failed_scrapers_func(scraper_name,url,scraper_type)
                                failed_list.append(f'⚠️{scraper_name}')
                                failed_scraper_log.controls.append(failed_scraper_log_text)
                                failed_scraper_log_text.value = ('\n'.join(failed_list))
                                page.update()
                                pass
                            except Exception as e:
                                if 'localhost' in str(e) or '127.0.0.1' in str(e):
                                    print(f'⚠️ Proxy or middleware timeout for {scraper_name} scraper.')
                                    if len(failed_list) == 0:
                                        failed_scraper_log.controls.append(failed_scraper_title)
                                    print(f'⛔{scraper_name} Error: {e}')
                                    failed_scrapers_func(scraper_name,url,scraper_type)
                                    failed_list.append(f'⚠️{scraper_name}')
                                    failed_scraper_log.controls.append(failed_scraper_log_text)
                                    failed_scraper_log_text.value = ('\n'.join(failed_list))
                                    page.update()
                                    pass
                                elif 'port=443' in str(e):
                                    print(f'⚠️ Proxy or middleware timeout for {scraper_name} scraper.')
                                    if len(failed_list) == 0:
                                        failed_scraper_log.controls.append(failed_scraper_title)
                                    print(f'⛔{scraper_name} Error: {e}')
                                    failed_scrapers_func(scraper_name,url,scraper_type)
                                    failed_list.append(f'⚠️{scraper_name}')
                                    failed_scraper_log.controls.append(failed_scraper_log_text)
                                    failed_scraper_log_text.value = ('\n'.join(failed_list))
                                    page.update()
                                    pass
                        else:
                            if len(failed_list) == 0:
                                failed_scraper_log.controls.append(failed_scraper_title)
                            print(f'⛔Site is not responding properly.')
                            failed_scrapers_func(scraper_name,url,scraper_type)
                            failed_list.append(f'⚠️{scraper_name}')
                            failed_scraper_log.controls.append(failed_scraper_log_text)
                            failed_scraper_log_text.value = ('\n'.join(failed_list))
                            page.update()
                            pass
                    except Exception as f:
                        print(f'An error has occured: {f}')
                    except WebDriverException as f:
                        print(f'A general WebDriver error occured: {f}')
                    duration = time.time() - start
                    await ui_queue.put(('log',f"{scraper_name} completed in {duration:.2f} seconds"))
                    await ui_queue.put(('progress',(i+1)/total_tasks))
                    total_duration.append(duration)
                    await asyncio.sleep(0.1)
                else:
                    # await ui_queue.put(('end_log','end'))
                    break
        finally:
            failed_df = pd.DataFrame(failed_scrapers)
            await save_csv_async(failed_df,'csv/failed_scrapers.csv')
            status_report_generation = 'SCRAPING COMPLETE, GENERATING REPORT...'
            total_time = runtime()
            await ui_queue.put(('nudge_off',False))
            await asyncio.sleep(0.2)
            report = f'TOTAL Runtime: {format_runtime(total_time)}'
            driver.quit()
            await asyncio.sleep(0.2)
            await ui_queue.put(('log',status_report_generation))
            await ui_queue.put(('log',report))
            await asyncio.sleep(0.2)
            await ui_queue.put(('status',report))
            await asyncio.sleep(0.1)
        
        valid_dfs = []
        for path in csv_paths:
            if os.path.getsize(path) == 0:
                print(f'Skipping empty file: {path}')
                continue
            try:
                today=datetime.today()
                df = await read_csv_async(path)
                if not df.empty:
                    valid_dfs.append(df)
                else:
                    print(f'Skipping empty DataFrame: {path}')
            except pd.errors.EmptyDataError:
                pass
            except Exception as g:
                print(f'Error reading {path}: {g}')
            except UnboundLocalError:
                print(f'NO NEW News at the moment: {today}')
            await asyncio.sleep(0.1)
            
        if len(valid_dfs) > 0:
            combined_df = pd.concat(valid_dfs, ignore_index=True)
            sorted_df = combined_df.sort_values(by='PublishDate',ascending=False)
            await save_csv_async(sorted_df,'csv/combined_news.csv')
            combined_csv = await read_csv_async('csv/combined_news.csv')
            combined_csv_df = pd.DataFrame(combined_csv)
            scraped_data = ScrapedData(None,combined_csv_df,page)
            await ui_queue.put(("display_output", scraped_data.run()))
            scrape_button_enabled()
            await asyncio.sleep(0.1)
            await ui_queue.put(('end_log','end'))
        else:
            today=datetime.today()
            today_formatted=today.strftime('%B %d, %Y | %X')
            print(f'NO NEW News at the moment: {today_formatted}')
            await asyncio.sleep(0.1)
            await ui_queue.put({'status',f'No NEW News at the moment: {today_formatted}'})
            await asyncio.sleep(0.1)
            scrape_button_enabled()
            await asyncio.sleep(0.1)
            await ui_queue.put(('end_log','end'))
    
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
        if not search_field.value == '':
            dropdown.visible = False
            dropdown.visible = True
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
    
    async def send_to_outlook(e):
        try:
            pythoncom.CoInitialize()
            today=datetime.today()
            today_formatted=today.strftime('%B %d, %Y')
            olApp = outlook.Dispatch(f'Outlook.Application')
            mail_item = olApp.CreateItem(0)
            mail_item.Subject = f'Scraped News for {today_formatted}'
            await create_report()
            today_csv=datetime.today()
            today_csv_formatted=today_csv.strftime('%Y-%m-%d')
            base_dir = os.path.dirname(os.path.abspath(__file__))
            filename_scraped_news = os.path.join(base_dir, 'csv\\Reports', f'scraped_news_{today_csv_formatted}.csv')
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
        output_section_log.visible = True
        output_section_log_container.visible = True
        toggle_switch.disabled = True
        toggle_switch.visible = False
        progress_bar.visible = True
        dropdown.disabled = True
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
        output_section_log.visible = False
        output_section_log_container.visible = False
        toggle_switch.disabled = False
        toggle_switch.label = ' VIEWING: RESULTS'
        toggle_switch.value = True
        toggle_switch.visible = True
        progress_bar.visible = False
        dropdown.disabled = False
        dropdown.fill_color = '#ffffff'
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
        
    def toggle_output_section(e):
        if toggle_switch.value == True:
            output_section.visible = True
            output_section_log_container.visible = False
        else:
            output_section.visible = False
            output_section_log_container.visible = True
            output_section_log.visible = True
            failed_scraper_log.visible = True
        toggle_switch.label = (' VIEWING: RESULTS' if toggle_switch.value == True else ' VIEWING: SCRAPING REPORT')
        page.update()
    
    async def handle_search_change(e):
        await filter_items(e.control.value)
        
    def stopping_scrape(e):
        threading.Thread(
            target=stop_scraping,
            args=(e,),
            daemon=True
        ).start()
    
    def run_save_dialog(e):
        file_path = launch_dialog()
        store_filepath(file_path)
    
    def store_filepath(file_path):
        search_status.value = f'Saved to:\n{file_path}'
        search_status.update()
    
    output_section_log_text = ft.Text(
        size=16,
        value='', 
        color="#474747",
        weight=ft.FontWeight.W_400
        )
    
    failed_scraper_log_text = ft.Text(
        size=18,
        value='', 
        color="#474747",
        weight=ft.FontWeight.W_400
        )
    
    failed_scraper_title = ft.Text(
        value='Failed Scraper List:',
        size=20,
        color=color_primary_dark
        )
    
    output_section = ft.Column(
        scroll="auto",
        controls=[]
    )
    
    failed_scraper_log = ft.ListView(
        height=570,
        width=400,
        expand=False,
        spacing=3,
        auto_scroll=True,
        padding=ft.padding.only(top=15,bottom=15,right=15,left=15),
        controls=[]
    )
    
    output_section_log = ft.ListView(
        height=570,
        width=1100,
        expand=False,
        spacing=3,
        auto_scroll=True,
        visible=False,
        padding=ft.padding.only(top=15,bottom=15,right=15,left=15)
    )
    
    output_section_log_container = ft.Container(
        height = 570,
        expand = True,
        content=ft.Row(
            height=570,
            controls=[
                output_section_log,
                failed_scraper_log
            ]
        )
    )
    
    output_section_stack = ft.Stack(
        height=570,
        width=1500,
        controls=[
            output_section,
            output_section_log_container
        ]
    )
    
    search_field = ft.TextField(
        border_radius=10,
        height=50,
        label='SEARCH KEYWORDS',
        hint_text='''ex. acquisitions, farm to fork''',
        bgcolor=color_neutral_light,
        color='#354850',
        disabled=True,
        width=368,
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
        size=13,
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
        width=383,
        height=50,
        content=ft.ElevatedButton(
            text='START SCRAPING...',
            icon=ft.Icons.MANAGE_SEARCH_OUTLINED,
            icon_color='#2B2B2B',
            elevation=5,
            width=383,
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
        width=383,
        height=50,
        content=ft.ElevatedButton(
            text='STOP SCRAPING',
            icon=ft.Icons.CANCEL_OUTLINED,
            icon_color="#DEDAC6",
            width=383,
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
        width=222,
        height=30,
        content=ft.ElevatedButton(
            text='SEND TO OUTLOOK',
            icon=ft.Icons.ATTACH_EMAIL_ROUNDED,
            elevation=5,
            width=220,
            height=20,
            on_click=send_to_outlook,
            bgcolor=color_tint_lilac,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                text_style=ft.TextStyle(size=14, weight=ft.FontWeight.NORMAL),
                color="#2B2B2B"
            ),
        )
    )
    
    reload_last_result = ft.Container( 
        width=222,
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
        width=220,
        height=30,
        content=ft.ElevatedButton(
            text='SAVE CSV',
            icon=ft.Icons.SAVE_ALT_ROUNDED,
            elevation=5,
            width=200,
            height=20,
            on_click=run_save_dialog,
            bgcolor=color_tint_lilac,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                text_style=ft.TextStyle(size=14, weight=ft.FontWeight.NORMAL),
                color="#2B2B2B"
            ),
        )
    )
    
    scrape_buttons_stack = ft.Stack(
        width=383,
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
    
    toggle_switch = ft.Switch(
        on_change = toggle_output_section,
        disabled = True,
        value = True,
        label = ' RESULTS AND REPORTS TOGGLE',
        active_color=color_tint_mint,
        inactive_track_color=color_primary_dark,
        # visible = False
    )
    
    footer_stack = ft.Stack(
        controls=[
            progress_bar,
            toggle_switch
        ]
    )
    
    dropdown = ft.Dropdown(
        width=222,
        filled=True,
        fill_color="#AAA089",
        color='#354850',
        hint_text='News Type',
        hint_style=ft.TextStyle(
            color='#2B2B2B',
            size=14
        ),
        disabled=True,
        border_width=2,
        border_radius=10,
        on_change=handle_search_change,
        focused_border_color=color_tint_mint,
        # value='ALL Type',
        options=[
            # ft.dropdown.Option('ALL Type'),
            ft.dropdown.Option('Company News'),
            ft.dropdown.Option('Industry News')
        ],
        # content_padding=ft.Padding(top=0,bottom=0,left=10,right=10)
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
                                            date_time_field,
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
                                                                dropdown,
                                                                
                                                            ]
                                                        ),
                                                        ft.Row(
                                                            controls=[
                                                                search_status,
                                                                reload_last_result,
                                                                save_result,
                                                                send_report
                                                                
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
                    content=output_section_stack
                    
                ),
                ft.Container(
                    padding=ft.padding.only(left=15,right=15,top=0,bottom=0),
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                width=1300,
                                content=footer_stack
                                # ft.Row(
                                #     controls = [
                                #         toggle_switch,
                                #         progress_bar
                                #         ]
                                #     )
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
