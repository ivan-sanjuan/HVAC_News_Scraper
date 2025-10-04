from tkinter import Tk, filedialog
import pandas as pd
from datetime import datetime

def launch_dialog():
    today = datetime.today().strftime("%Y-%m-%d")
    default_name = f"Scraped_data_{today}.csv"
    
    root = Tk()
    root.withdraw()
    root.lift()
    root.attributes("-topmost", True)
    root.focus_force()
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        initialfile=default_name,
        filetypes=[("CSV files", "*.csv")],
        title="Save scraped results",
        parent=root
    )
    root.destroy()
    if file_path:
        df = pd.read_csv("csv/combined_news.csv")
        df.to_csv(file_path, index=False)
        print(f"✅ Saved to {file_path}")
    return file_path
    
    # return root
# if __name__ == "__main__":
#     launch_dialog()