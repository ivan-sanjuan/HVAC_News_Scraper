from tkinter import Tk, filedialog
import pandas as pd
from datetime import datetime

def launch_dialog():
    today = datetime.today().strftime("%Y-%m-%d_%H-%M")
    default_name = f"Scraped_data_{today}.csv"

    root = Tk()
    root.withdraw()

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        initialfile=default_name,
        filetypes=[("CSV files", "*.csv")],
        title="Save scraped results"
    )
    # file_save = FileResponse(file_path)
    # file_save.run()
    if file_path:
        df = pd.read_csv("csv/combined_news.csv")
        df.to_csv(file_path, index=False)
        print(f"✅ Saved to {file_path}")

if __name__ == "__main__":
    launch_dialog()