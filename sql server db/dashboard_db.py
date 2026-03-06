import pyodbc
import pandas as pd
import sys
from tabulate import tabulate
from db_config import DB_CONFIG

class InventoryDataLoaderDB:
    def __init__(self):
        self.conn_str = f"Driver={DB_CONFIG['driver']};Server={DB_CONFIG['server']};Database={DB_CONFIG['database']};Trusted_Connection={DB_CONFIG['trusted_connection']};"
        self.df = None
        self._connect_and_load()
    
    def _connect_and_load(self):
        try:
            conn = pyodbc.connect(self.conn_str)
            self.df = pd.read_sql("SELECT * FROM Assets", conn)
            conn.close()
        except Exception as e:
            raise ConnectionError(f"ERROR: Database connection failed!\n{e}\nPlease run 'python setup_database.py' first.")
    
    def get_data(self):
        return self.df

class SummaryReport:
    def __init__(self, dataframe):
        self.df = dataframe
    
    def get_total_stats(self):
        return {
            'total_assets': len(self.df),
            'total_value': self.df['Cost_INR'].sum(),
            'average_cost': self.df['Cost_INR'].mean()
        }
    
    def get_status_distribution(self):
        return self.df['Status'].value_counts()
    
    def get_top_departments(self, limit=5):
        return self.df['Department'].value_counts().head(limit)
    
    def get_top_manufacturers(self, limit=5):
        return self.df['Manufacturer'].value_counts().head(limit)
    
    def get_location_distribution(self):
        return self.df['Location'].value_counts()
    
    def display(self):
        print("=" * 80)
        print("INVENTORY SUMMARY (From Database)")
        print("=" * 80)
        
        stats = self.get_total_stats()
        print(f"\nTotal Assets: {stats['total_assets']:,}")
        print(f"Total Asset Value: INR {stats['total_value']:,.2f}")
        print(f"Average Asset Cost: INR {stats['average_cost']:,.2f}")
        
        print("\n--- Asset Status Distribution ---")
        for status, count in self.get_status_distribution().items():
            percentage = (count / len(self.df)) * 100
            print(f"  {status}: {count:,} ({percentage:.1f}%)")
        
        print("\n--- Top Departments by Asset Count ---")
        for dept, count in self.get_top_departments().items():
            print(f"  {dept}: {count:,}")
        
        print("\n--- Top Manufacturers ---")
        for mfr, count in self.get_top_manufacturers().items():
            print(f"  {mfr}: {count:,}")
        
        print("\n--- Location Distribution ---")
        for loc, count in self.get_location_distribution().items():
            percentage = (count / len(self.df)) * 100
            print(f"  {loc}: {count:,} ({percentage:.1f}%)")
        print("\n")

class PrinterReport:
    def __init__(self, dataframe):
        self.df = dataframe
    
    def get_printers(self):
        return self.df[self.df['Category'] == 'Printer'].copy()
    
    def get_printer_count(self):
        return len(self.get_printers())
    
    def get_printer_status_distribution(self):
        return self.get_printers()['Status'].value_counts()
    
    def get_printers_by_location(self):
        return self.get_printers()['Location'].value_counts()
    
    def display(self):
        print("=" * 80)
        print("PRINTER INVENTORY (From Database)")
        print("=" * 80)
        print(f"\nTotal Printers: {self.get_printer_count():,}\n")
        
        if len(self.get_printers()) > 0:
            printer_display = self.get_printers()[['Asset_ID', 'Manufacturer', 'Model', 'Location', 'Status', 'Owner_Name', 'Department', 'Cost_INR']].reset_index(drop=True)
            printer_display.index = printer_display.index + 1
            print(tabulate(printer_display, headers='keys', tablefmt='grid', maxcolwidths=[15, 12, 20, 15, 15, 15, 15, 12]))
            
            print(f"\n--- Printer Status ---")
            for status, count in self.get_printer_status_distribution().items():
                print(f"  {status}: {count}")
            
            print(f"\n--- Printers by Location ---")
            for loc, count in self.get_printers_by_location().items():
                print(f"  {loc}: {count}")
        print("\n")

class CategoryReport:
    def __init__(self, dataframe):
        self.df = dataframe
    
    def get_category_counts(self):
        return self.df['Category'].value_counts().sort_values(ascending=False)
    
    def get_category_details(self):
        category_details = self.df.groupby('Category').agg({
            'Asset_ID': 'count',
            'Cost_INR': ['sum', 'mean']
        }).round(2)
        category_details.columns = ['Count', 'Total_Cost', 'Average_Cost']
        return category_details.sort_values('Count', ascending=False)
    
    def get_category_count(self):
        return len(self.get_category_counts())
    
    def display(self):
        print("=" * 80)
        print("ASSET CATEGORIES (From Database)")
        print("=" * 80)
        print(f"\nTotal Categories: {self.get_category_count()}\n")
        
        counts = self.get_category_counts()
        max_count = counts.max()
        
        for category, count in counts.items():
            bar_length = int((count / max_count) * 40)
            bar = "█" * bar_length
            percentage = (count / len(self.df)) * 100
            print(f"  {category:<20} {count:>6,} ({percentage:>5.1f}%) {bar}")
        
        print("\n--- Category Details ---\n")
        details_table = self.get_category_details().reset_index()
        details_table.columns = ['Category', 'Count', 'Total Cost', 'Avg Cost']
        print(tabulate(details_table, headers='keys', tablefmt='grid', showindex=False))
        print("\n")

class ITInventoryManagementDB:
    def __init__(self):
        try:
            self.loader = InventoryDataLoaderDB()
            data = self.loader.get_data()
            self.sr = SummaryReport(data)
            self.pr = PrinterReport(data)
            self.cr = CategoryReport(data)
        except ConnectionError as e:
            print(str(e))
            sys.exit(1)
    
    def display_summary(self):
        self.sr.display()
    
    def display_printers(self):
        self.pr.display()
    
    def display_categories(self):
        self.cr.display()
    
    def display_all_reports(self):
        self.sr.display()
        self.pr.display()
        self.cr.display()
    
    def run_command_line(self):
        if len(sys.argv) < 2:
            self.display_all_reports()
            return
        
        command = sys.argv[1].lower()
        
        if command == 'summary':
            self.display_summary()
        elif command == 'printers':
            self.display_printers()
        elif command == 'categories':
            self.display_categories()
        elif command == 'all':
            self.display_all_reports()
        else:
            print(f"Unknown command: {command}")

if __name__ == "__main__":
    app = ITInventoryManagementDB()
    app.run_command_line()
