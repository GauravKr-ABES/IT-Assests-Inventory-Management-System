import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
import pandas as pd
from db_config import DB_CONFIG

class InventoryDataLoaderDB:
    def __init__(self):
        conn_str = f"Driver={DB_CONFIG['driver']};Server={DB_CONFIG['server']};Database={DB_CONFIG['database']};Trusted_Connection={DB_CONFIG['trusted_connection']};"
        try:
            conn = pyodbc.connect(conn_str)
            self.df = pd.read_sql("SELECT * FROM Assets", conn)
            conn.close()
        except Exception as e:
            raise FileNotFoundError(f"ERROR: Database connection failed!\n{e}\nPlease run 'python setup_database.py' first.")
    def get_data(self):
        return self.df

class SummaryReport:
    def __init__(self, df):
        self.df = df
    def get_total_stats(self):
        return {'total_assets': len(self.df), 'total_value': self.df['Cost_INR'].sum(), 'average_cost': self.df['Cost_INR'].mean()}
    def get_status_distribution(self):
        return self.df['Status'].value_counts()
    def get_top_departments(self, limit=5):
        return self.df['Department'].value_counts().head(limit)
    def get_top_manufacturers(self, limit=5):
        return self.df['Manufacturer'].value_counts().head(limit)
    def get_location_distribution(self):
        return self.df['Location'].value_counts()

class PrinterReport:
    def __init__(self, df):
        self.df = df
    def get_printers(self):
        return self.df[self.df['Category'] == 'Printer'].copy()
    def get_printer_status_distribution(self):
        return self.get_printers()['Status'].value_counts()
    def get_printers_by_location(self):
        return self.get_printers()['Location'].value_counts()

class CategoryReport:
    def __init__(self, df):
        self.df = df
    def get_category_counts(self):
        return self.df['Category'].value_counts().sort_values(ascending=False)
    def get_category_details(self):
        details = self.df.groupby('Category').agg({'Asset_ID': 'count', 'Cost_INR': ['sum', 'mean']}).round(2)
        details.columns = ['Count', 'Total_Cost', 'Average_Cost']
        return details.sort_values('Count', ascending=False)

class ModernInventoryGUI:
    def __init__(self, root):
        try:
            loader = InventoryDataLoaderDB()
            self.data = loader.get_data()
            self.sr = SummaryReport(self.data)
            self.pr = PrinterReport(self.data)
            self.cr = CategoryReport(self.data)
        except FileNotFoundError as e:
            messagebox.showerror("Error", str(e))
            root.destroy()
            return
        
        self.root = root
        self.root.title("IT Inventory Management System")
        self.root.geometry("1400x800")
        
        self.bg_dark = "#f5f5f5"
        self.bg_darker = "#ffffff"
        self.accent1 = "#0066cc"
        self.accent2 = "#cc0033"
        self.accent3 = "#ff9900"
        self.accent4 = "#6600cc"
        self.text_light = "#000000"
        self.text_muted = "#555555"
        
        self.root.configure(bg=self.bg_dark)
        self.setup_styles()
        self.setup_ui()
        self.center_window()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Dark.TNotebook', background=self.bg_dark, borderwidth=0)
        style.configure('Dark.TNotebook.Tab', padding=[20, 10])
        style.map('Dark.TNotebook.Tab', background=[('selected', self.accent1)], foreground=[('selected', self.bg_dark)])
        
        style.configure('Dark.TFrame', background=self.bg_dark)
        style.configure('Dark.TLabel', background=self.bg_dark, foreground=self.text_light)
    
    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        header = tk.Frame(self.root, bg="#ffffff", height=80)
        header.pack(fill=tk.X)
        
        title = tk.Label(header, text="IT INVENTORY MANAGEMENT", font=("Segoe UI", 24, "bold"), 
                        bg="#ffffff", fg="#0066cc")
        title.pack(pady=15)
        
        subtitle = tk.Label(header, text="SQL Server Database | Real-time Analytics", 
                           font=("Segoe UI", 10), bg="#ffffff", fg="#666666")
        subtitle.pack()
        
        notebook = ttk.Notebook(self.root, style='Dark.TNotebook')
        notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        notebook.add(self.build_summary_tab(), text="⚡ Summary")
        notebook.add(self.build_category_tab(), text="📊 Categories")
        notebook.add(self.build_printer_tab(), text="🖨️  Printers")
    
    def create_stat_card(self, parent, title, value, color, icon=""):
        card = tk.Frame(parent, bg=color, highlightbackground="#cccccc", highlightthickness=1, relief=tk.FLAT)
        card.pack(fill=tk.X, pady=8, padx=0)
        
        inner = tk.Frame(card, bg=color)
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)
        
        tk.Label(inner, text=icon, font=("Arial", 28), bg=color, fg="#333333").pack(anchor=tk.W)
        tk.Label(inner, text=title, font=("Segoe UI", 11), bg=color, fg="#666666").pack(anchor=tk.W)
        tk.Label(inner, text=value, font=("Segoe UI", 20, "bold"), bg=color, fg="#333333").pack(anchor=tk.W, pady=(5, 0))
    
    def build_summary_tab(self):
        f = tk.Frame(self.root, bg=self.bg_dark)
        
        mf = tk.Frame(f, bg=self.bg_dark)
        mf.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        stats = self.sr.get_total_stats()
        self.create_stat_card(mf, "Total Assets", f"{stats['total_assets']:,}", "#e3f2fd", "📦")
        self.create_stat_card(mf, "Total Value", f"INR {stats['total_value']:,.0f}", "#e8f5e9", "💰")
        self.create_stat_card(mf, "Average Cost", f"INR {stats['average_cost']:,.2f}", "#fff3e0", "📈")
        
        sep = tk.Frame(mf, bg=self.text_muted, height=1)
        sep.pack(fill=tk.X, pady=15)
        
        for title, data, icon in [("Status", self.sr.get_status_distribution(), "🔄"), 
                                   ("Departments", self.sr.get_top_departments(), "👥"),
                                   ("Manufacturers", self.sr.get_top_manufacturers(), "🏢"),
                                   ("Locations", self.sr.get_location_distribution(), "📍")]:
            self.create_data_section(mf, title, data, icon)
        
        return f
    
    def create_data_section(self, parent, title, data, icon=""):
        section = tk.Frame(parent, bg=self.bg_darker, relief=tk.FLAT, highlightthickness=0)
        section.pack(fill=tk.X, pady=10, padx=0)
        
        header_frame = tk.Frame(section, bg=self.bg_darker)
        header_frame.pack(fill=tk.X, padx=15, pady=(10, 5))
        tk.Label(header_frame, text=f"{icon} {title}", font=("Segoe UI", 12, "bold"), 
                bg=self.bg_darker, fg="#0066cc").pack(anchor=tk.W)
        
        for label, value in data.items():
            row = tk.Frame(section, bg=self.bg_darker)
            row.pack(fill=tk.X, padx=15, pady=4)
            tk.Label(row, text=label, font=("Segoe UI", 10), bg=self.bg_darker, 
                    fg="#333333", width=25, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row, text=f"{value:,}", font=("Segoe UI", 10, "bold"), bg=self.bg_darker, 
                    fg=self.accent3).pack(side=tk.LEFT, fill=tk.X, expand=True, anchor=tk.W)
    
    def build_category_tab(self):
        f = tk.Frame(self.root, bg=self.bg_dark)
        mf = tk.Frame(f, bg=self.bg_dark)
        mf.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        counts = self.cr.get_category_counts()
        
        chart_frame = tk.Frame(mf, bg=self.bg_darker, relief=tk.FLAT, highlightthickness=0)
        chart_frame.pack(fill=tk.BOTH, expand=False, pady=10)
        
        tk.Label(chart_frame, text="📊 Distribution Chart", font=("Segoe UI", 12, "bold"), 
                bg=self.bg_darker, fg="#0066cc").pack(anchor=tk.W, padx=15, pady=10)
        
        for cat, cnt in counts.items():
            bar_frame = tk.Frame(chart_frame, bg=self.bg_darker)
            bar_frame.pack(fill=tk.X, padx=15, pady=5)
            
            tk.Label(bar_frame, text=cat, font=("Segoe UI", 9), bg=self.bg_darker, 
                    fg="#333333", width=18, anchor=tk.W).pack(side=tk.LEFT)
            
            bar_length = int((cnt / counts.max()) * 30)
            bar = "█" * bar_length
            tk.Label(bar_frame, text=bar, font=("Courier", 8), bg=self.bg_darker, 
                    fg=self.accent1).pack(side=tk.LEFT, padx=10)
            
            tk.Label(bar_frame, text=f"{cnt:,} ({(cnt/counts.sum()*100):.1f}%)", 
                    font=("Segoe UI", 9, "bold"), bg=self.bg_darker, fg=self.accent3).pack(side=tk.LEFT)
        
        tk.Label(mf, text="📋 Category Details", font=("Segoe UI", 12, "bold"), 
                bg=self.bg_dark, fg="#0066cc").pack(anchor=tk.W, pady=(15, 5))
        
        tf = tk.Frame(mf, bg=self.bg_darker, relief=tk.FLAT, highlightthickness=1)
        tf.pack(fill=tk.BOTH, expand=True, pady=10)
        
        sb = ttk.Scrollbar(tf)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        
        cols = ("Category", "Count", "Total Cost", "Avg Cost")
        tree = ttk.Treeview(tf, columns=cols, height=8, yscrollcommand=sb.set, show='headings')
        tree.pack(fill=tk.BOTH, expand=True)
        sb.config(command=tree.yview)
        
        for col, width in zip(cols, [150, 100, 150, 120]):
            tree.column(col, anchor=tk.CENTER, width=width)
            tree.heading(col, text=col, anchor=tk.CENTER)
        
        for idx, (cat, row) in enumerate(self.cr.get_category_details().iterrows()):
            tag = 'oddrow' if idx % 2 else 'evenrow'
            tree.insert("", tk.END, values=(cat, f"{int(row['Count']):,}", 
                       f"INR {row['Total_Cost']:,.0f}", f"INR {row['Average_Cost']:,.2f}"), tags=(tag,))
        
        tree.tag_configure('oddrow', background="#f9f9f9", foreground="#333333")
        tree.tag_configure('evenrow', background="#ffffff", foreground="#333333")
        
        return f
    
    def build_printer_tab(self):
        f = tk.Frame(self.root, bg=self.bg_dark)
        mf = tk.Frame(f, bg=self.bg_dark)
        mf.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        printers = self.pr.get_printers()
        
        search_frame = tk.Frame(mf, bg=self.bg_darker)
        search_frame.pack(fill=tk.X, pady=10)
        tk.Label(search_frame, text="🔍 Search:", font=("Segoe UI", 10), 
                bg=self.bg_darker, fg="#333333").pack(side=tk.LEFT, padx=10, pady=8)
        self.printer_search = tk.Entry(search_frame, font=("Segoe UI", 10), bg="#e8e8e8", 
                                       fg="#333333", borderwidth=1, relief=tk.FLAT)
        self.printer_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), pady=8)
        self.printer_search.bind('<KeyRelease>', lambda e: self.filter_printers())
        
        info_frame = tk.Frame(mf, bg=self.bg_darker)
        info_frame.pack(fill=tk.X, pady=10)
        tk.Label(info_frame, text=f"🖨️  Total Printers: {len(printers):,}", font=("Segoe UI", 11, "bold"), 
                bg=self.bg_darker, fg="#0066cc").pack(anchor=tk.W, padx=15, pady=5)
        
        tf = tk.Frame(mf, bg=self.bg_darker, relief=tk.FLAT, highlightthickness=1)
        tf.pack(fill=tk.BOTH, expand=True, pady=10)
        
        sb_y = ttk.Scrollbar(tf, orient=tk.VERTICAL)
        sb_y.pack(side=tk.RIGHT, fill=tk.Y)
        sb_x = ttk.Scrollbar(tf, orient=tk.HORIZONTAL)
        sb_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        cols = ("ID", "Manufacturer", "Model", "Location", "Status", "Owner", "Department", "Cost")
        self.printer_tree = ttk.Treeview(tf, columns=cols, height=12, yscrollcommand=sb_y.set, 
                                        xscrollcommand=sb_x.set, show='headings')
        self.printer_tree.pack(fill=tk.BOTH, expand=True)
        sb_y.config(command=self.printer_tree.yview)
        sb_x.config(command=self.printer_tree.xview)
        
        for col, width in zip(cols, [100, 100, 120, 130, 100, 120, 100, 100]):
            self.printer_tree.column(col, anchor=tk.CENTER if col in ["ID", "Cost"] else tk.W, width=width)
            self.printer_tree.heading(col, text=col, anchor=tk.CENTER if col in ["ID", "Cost"] else tk.W)
        
        self.populate_printer_tree(printers)
        
        return f
    
    def populate_printer_tree(self, printers):
        for item in self.printer_tree.get_children():
            self.printer_tree.delete(item)
        
        for idx, (_, row) in enumerate(printers.iterrows()):
            tag = 'oddrow' if idx % 2 else 'evenrow'
            self.printer_tree.insert("", tk.END, values=(row['Asset_ID'], row['Manufacturer'], 
                                    row['Model'], row['Location'], row['Status'], row['Owner_Name'], 
                                    row['Department'], f"INR {row['Cost_INR']:,.0f}"), tags=(tag,))
        
        self.printer_tree.tag_configure('oddrow', background="#f9f9f9", foreground="#333333")
        self.printer_tree.tag_configure('evenrow', background="#ffffff", foreground="#333333")
    
    def filter_printers(self):
        search_term = self.printer_search.get().lower()
        filtered = self.pr.get_printers()
        if search_term:
            filtered = filtered[
                (filtered['Asset_ID'].str.lower().str.contains(search_term)) |
                (filtered['Manufacturer'].str.lower().str.contains(search_term)) |
                (filtered['Model'].str.lower().str.contains(search_term)) |
                (filtered['Location'].str.lower().str.contains(search_term))
            ]
        self.populate_printer_tree(filtered)

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernInventoryGUI(root)
    root.mainloop()
