import pandas as pd
import os
import sys
from tabulate import tabulate


class InventoryDataLoader:
    
    def __init__(self, csv_file='IT_Inventory.csv'):
        self.csv_file = csv_file
        self.df = None
        self._validate_and_load()
    
    def _validate_and_load(self):
        if not os.path.exists(self.csv_file):
            raise FileNotFoundError(
                f"ERROR: {self.csv_file} not found!\n"
                f"Please run 'python generate_data.py' first to create the dataset."
            )
        
        self.df = pd.read_csv(self.csv_file)
    
    def get_data(self):
        return self.df
    
    def get_asset_count(self):
        return len(self.df)


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
        print("INVENTORY SUMMARY")
        print("=" * 80)
        
        stats = self.get_total_stats()
        print(f"\nTotal Assets: {stats['total_assets']:,}")
        print(f"Total Asset Value: ₹{stats['total_value']:,.2f}")
        print(f"Average Asset Cost: ₹{stats['average_cost']:,.2f}")
        
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
        printers = self.get_printers()
        return printers['Status'].value_counts()
    
    def get_printers_by_location(self):
        printers = self.get_printers()
        return printers['Location'].value_counts()
    
    def display(self):
        print("=" * 80)
        print("PRINTER INVENTORY")
        print("=" * 80)
        
        printers = self.get_printers()
        print(f"\nTotal Printers: {self.get_printer_count():,}\n")
        
        if len(printers) > 0:
            printer_display = printers[['Asset_ID', 'Manufacturer', 'Model', 'Location', 
                                       'Status', 'Owner_Name', 'Department', 'Cost_INR']].reset_index(drop=True)
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
        """Display category report"""
        print("=" * 80)
        print("ASSET CATEGORIES")
        print("=" * 80)
        
        category_counts = self.get_category_counts()
        print(f"\nTotal Categories: {self.get_category_count()}\n")
        
        total_assets = len(self.df)
        
        print("Category Breakdown:")
        print("-" * 50)
        
        for category, count in category_counts.items():
            percentage = (count / total_assets) * 100
            bar_length = int(percentage / 2)
            bar = "█" * bar_length
            print(f"{category:<20} {count:>6,}  ({percentage:>5.1f}%)  {bar}")
        
        print("-" * 50)
        print(f"{'TOTAL':<20} {total_assets:>6,}  (100.0%)")
        
        print("\n--- Category Details ---")
        print(tabulate(self.get_category_details(), headers='keys', tablefmt='grid'))
        
        print("\n")


class MenuView:
    
    @staticmethod
    def display_menu():
        print("\n" + "=" * 80)
        print("IT ASSETS INVENTORY MANAGEMENT SYSTEM")
        print("=" * 80)
        print("\nSelect an option:")
        print("  1. Display Inventory Summary")
        print("  2. List All Printers")
        print("  3. Display Asset Categories")
        print("  4. Run All Reports")
        print("  5. Exit")
        print("\n" + "=" * 80)
    
    @staticmethod
    def get_choice():
        try:
            choice = input("Enter your choice (1-5): ").strip()
            return choice
        except EOFError:
            return '5'


class ITInventoryManagement:
    
    def __init__(self):
        try:
            self.loader = InventoryDataLoader()
            self.df = self.loader.get_data()
            self.summary_report = SummaryReport(self.df)
            self.printer_report = PrinterReport(self.df)
            self.category_report = CategoryReport(self.df)
        except FileNotFoundError as e:
            print(f"ERROR: {e}")
            sys.exit(1)
    
    def display_summary(self):
        self.summary_report.display()
    
    def display_printers(self):
        self.printer_report.display()
    
    def display_categories(self):
        self.category_report.display()
    
    def display_all_reports(self):
        self.display_summary()
        self.display_categories()
        self.display_printers()
    
    def run_interactive(self):
        menu_view = MenuView()
        
        while True:
            menu_view.display_menu()
            choice = menu_view.get_choice()
            
            if choice == '1':
                self.display_summary()
            elif choice == '2':
                self.display_printers()
            elif choice == '3':
                self.display_categories()
            elif choice == '4':
                self.display_all_reports()
            elif choice == '5':
                print("\nThank you for using IT Assets Inventory Management System!")
                break
            else:
                print("\n❌ Invalid choice! Please enter a number between 1 and 5.\n")
    
    def run_command_line(self, report_type):
        report_type = report_type.lower()
        
        if report_type == 'summary':
            self.display_summary()
        elif report_type == 'printers':
            self.display_printers()
        elif report_type == 'categories':
            self.display_categories()
        elif report_type == 'all':
            self.display_all_reports()
        else:
            print("Invalid report type!")
            print("Usage: python dashboard.py [summary|printers|categories|all]")


if __name__ == "__main__":
    try:
        system = ITInventoryManagement()
        
        if len(sys.argv) > 1:
            # Command-line mode
            report_type = sys.argv[1]
            system.run_command_line(report_type)
        else:
            # Interactive mode
            system.run_interactive()
    except Exception as e:
        print(f"ERROR: {e}")
