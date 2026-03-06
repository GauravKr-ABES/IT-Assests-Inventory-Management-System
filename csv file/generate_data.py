import pandas as pd
import random
from datetime import datetime, timedelta


class AssetConfig:
    
    CATEGORIES = {
        'Laptop': 3050,
        'Server': 1546,
        'Printer': 368,
        'Monitor': 2100,
        'Network Switch': 1200,
        'Router': 800,
        'Storage Device': 600,
        'Mouse/Keyboard': 200,
        'Headset': 136
    }
    
    LOCATIONS = ['On-Prem', 'Cloud', 'Branch Office 1', 'Branch Office 2', 'Data Center', 'Cloud AWS']
    
    STATES = ['Active', 'Inactive', 'Under Maintenance', 'Decommissioned']
    
    DEPARTMENTS = ['IT', 'HR', 'Finance', 'Operations', 'Sales', 'Marketing', 'Support']
    
    MANUFACTURERS = {
        'Laptop': ['Dell', 'HP', 'Lenovo', 'Apple', 'ASUS'],
        'Server': ['Dell', 'HP', 'Lenovo', 'IBM', 'Oracle'],
        'Printer': ['HP', 'Canon', 'Brother', 'Xerox', 'Ricoh'],
        'Monitor': ['Dell', 'LG', 'ASUS', 'Samsung', 'BenQ'],
        'Network Switch': ['Cisco', 'Juniper', 'Arista', 'Dell'],
        'Router': ['Cisco', 'Juniper', 'Arista', 'TP-Link'],
        'Storage Device': ['Dell', 'NetApp', 'HPE', 'EMC'],
        'Mouse/Keyboard': ['Logitech', 'Microsoft', 'Corsair', 'Razer'],
        'Headset': ['Plantronics', 'Jabra', 'Sennheiser', 'Corsair']
    }
    
    COST_RANGE = (200, 5000)
    WARRANTY_RANGE = (365, 1825)
    PURCHASE_DAYS_RANGE = (0, 1825)


class Asset:
    
    def __init__(self, asset_id, category, manufacturer, model, location, 
                 status, purchase_date, warranty_expiry, department, owner_name, cost_inr):
        self.asset_id = asset_id
        self.category = category
        self.manufacturer = manufacturer
        self.model = model
        self.location = location
        self.status = status
        self.purchase_date = purchase_date
        self.warranty_expiry = warranty_expiry
        self.department = department
        self.owner_name = owner_name
        self.cost_inr = cost_inr
    
    def to_dict(self):
        return {
            'Asset_ID': self.asset_id,
            'Category': self.category,
            'Manufacturer': self.manufacturer,
            'Model': self.model,
            'Location': self.location,
            'Status': self.status,
            'Purchase_Date': self.purchase_date,
            'Warranty_Expiry': self.warranty_expiry,
            'Department': self.department,
            'Owner_Name': self.owner_name,
            'Cost_INR': self.cost_inr
        }


class AssetDataGenerator:
    
    def __init__(self, config=None):
        self.config = config or AssetConfig()
        self.assets = []
        self.asset_id_counter = 1000
    
    def generate_purchase_date(self):
        days_ago = random.randint(*self.config.PURCHASE_DAYS_RANGE)
        return (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
    
    def generate_warranty_date(self):
        warranty_days = random.randint(*self.config.WARRANTY_RANGE)
        return (datetime.now() + timedelta(days=warranty_days)).strftime('%Y-%m-%d')
    
    def generate_manufacturer(self, category):
        manufacturers = self.config.MANUFACTURERS.get(category, ['Unknown'])
        return random.choice(manufacturers)
    
    def generate_cost(self):
        return random.randint(*self.config.COST_RANGE)
    
    def generate_asset(self, category):
        self.asset_id_counter += 1
        
        asset = Asset(
            asset_id=f'AST-{self.asset_id_counter}',
            category=category,
            manufacturer=self.generate_manufacturer(category),
            model=f'{category}-Model-{random.randint(100, 999)}',
            location=random.choice(self.config.LOCATIONS),
            status=random.choice(self.config.STATES),
            purchase_date=self.generate_purchase_date(),
            warranty_expiry=self.generate_warranty_date(),
            department=random.choice(self.config.DEPARTMENTS),
            owner_name=f'Employee-{random.randint(1, 5000)}',
            cost_inr=self.generate_cost()
        )
        
        self.assets.append(asset)
        return asset
    
    def generate_all(self):
        for category, count in self.config.CATEGORIES.items():
            for _ in range(count):
                self.generate_asset(category)
    
    def get_dataframe(self):
        data = [asset.to_dict() for asset in self.assets]
        return pd.DataFrame(data)


class DataRepository:
    
    def __init__(self, filename='IT_Inventory.csv'):
        self.filename = filename
    
    def save(self, dataframe):
        dataframe.to_csv(self.filename, index=False)
        return True
    
    def print_summary(self, dataframe):
        print(f"Dataset created successfully!")
        print(f"Total records: {len(dataframe)}")
        print(f"\nAsset Categories:")
        print(dataframe['Category'].value_counts().to_string())
        print(f"\nFile saved as: {self.filename}")


class DataGeneratorApp:
    
    def __init__(self):
        self.generator = AssetDataGenerator()
        self.repository = DataRepository()
    
    def run(self):
        print("Generating IT inventory data...")
        self.generator.generate_all()
        
        df = self.generator.get_dataframe()
        self.repository.save(df)
        self.repository.print_summary(df)


if __name__ == "__main__":
    app = DataGeneratorApp()
    app.run()
