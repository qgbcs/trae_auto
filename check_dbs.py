#!/usr/bin/env python3
import sqlite3
import os

dbs = [
    r'C:\Users\Administrator\AppData\Roaming\Trae CN\Local Storage\config.db',
    r'C:\Users\Administrator\AppData\Roaming\Trae CN\ModularData\ckg_server\env_codekg.db',
    r'C:\Users\Administrator\AppData\Roaming\Trae CN\ModularData\ai-agent\database.db',
]

for db_path in dbs:
    if not os.path.exists(db_path):
        continue
    print(f'\n=== {os.path.basename(db_path)} ===')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print('Tables:', [t[0] for t in tables])

        # Search for checkin/credits related tables
        for table in tables:
            tname = table[0]
            if any(kw in tname.lower() for kw in ['checkin', 'credit', 'activity', 'commerce', 'icube']):
                cursor.execute(f'SELECT * FROM [{tname}] LIMIT 3')
                rows = cursor.fetchall()
                print(f'\n{tname}:')
                for row in rows:
                    print(f'  {row}')
        conn.close()
    except Exception as e:
        print(f'Error: {e}')
