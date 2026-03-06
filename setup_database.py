import pandas as pd
import pyodbc
import os
from db_config import DB_CONFIG

def setup_database():
    try:
        print("[INFO] Connecting to SQL Server (master database)...")
        master_conn_str = f"Driver={DB_CONFIG['driver']};Server={DB_CONFIG['server']};Database=master;Trusted_Connection={DB_CONFIG['trusted_connection']};"
        master_conn = pyodbc.connect(master_conn_str)
        master_conn.autocommit = True
        master_cursor = master_conn.cursor()
        
        db_name = DB_CONFIG['database']
        print(f"[INFO] Creating database '{db_name}'...")
        try:
            master_cursor.execute(f"CREATE DATABASE [{db_name}]")
            print(f"[OK] Database '{db_name}' created")
        except:
            print(f"[INFO] Database already exists or error - continuing...")
        
        master_cursor.close()
        master_conn.close()
        
        conn_str = f"Driver={DB_CONFIG['driver']};Server={DB_CONFIG['server']};Database={db_name};Trusted_Connection={DB_CONFIG['trusted_connection']};"
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        print("[INFO] Creating table...")
        cursor.execute("IF OBJECT_ID('Assets', 'U') IS NOT NULL DROP TABLE Assets")
        cursor.execute("""
        CREATE TABLE Assets (
            Asset_ID NVARCHAR(50) PRIMARY KEY,
            Category NVARCHAR(100),
            Manufacturer NVARCHAR(100),
            Model NVARCHAR(100),
            Location NVARCHAR(100),
            Status NVARCHAR(50),
            Purchase_Date DATE,
            Warranty_Expiry DATE,
            Department NVARCHAR(100),
            Owner_Name NVARCHAR(100),
            Cost_INR FLOAT
        )
        """)
        conn.commit()
        print("[OK] Table 'Assets' created")
        
        csv_file = 'IT_Inventory.csv'
        if not os.path.exists(csv_file):
            print(f"ERROR: {csv_file} not found!")
            return
        
        df = pd.read_csv(csv_file)
        print(f"[INFO] Loading {len(df):,} records...")
        
        for idx, (_, row) in enumerate(df.iterrows()):
            sql = """
            INSERT INTO Assets (Asset_ID, Category, Manufacturer, Model, Location, Status, 
                              Purchase_Date, Warranty_Expiry, Department, Owner_Name, Cost_INR)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(sql, (row['Asset_ID'], row['Category'], row['Manufacturer'], row['Model'],
                                row['Location'], row['Status'], row['Purchase_Date'], row['Warranty_Expiry'],
                                row['Department'], row['Owner_Name'], row['Cost_INR']))
            if (idx + 1) % 1000 == 0:
                print(f"  Loaded {idx + 1:,} records...")
        
        conn.commit()
        print(f"[OK] Loaded {len(df):,} records to database")
        cursor.close()
        conn.close()
        print("[OK] Database setup complete!")
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    print("Setting up SQL Server database from CSV...\n")
    setup_database()
