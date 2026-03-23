import sqlite3
import os

# Path to database (one level up from src)
db_path = os.path.join(os.path.dirname(os.getcwd()), 'mediguard.db')
print(f"Database path: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get existing columns
cols = [row[1] for row in cursor.execute('PRAGMA table_info(users)')]
print(f"Existing columns: {cols}")

# Columns to add
to_add = {
    'security_question_1': 'TEXT',
    'security_answer_1': 'TEXT',
    'security_question_2': 'TEXT',
    'security_answer_2': 'TEXT',
    'reset_token': 'TEXT',
    'reset_token_expiry': 'DATETIME',
    'password_reset_requested_at': 'DATETIME'
}

for col, dtype in to_add.items():
    if col not in cols:
        cursor.execute(f'ALTER TABLE users ADD COLUMN {col} {dtype}')
        print(f'Added: {col}')
    else:
        print(f'Already exists: {col}')

conn.commit()
conn.close()
print('Done! Database updated successfully.')
