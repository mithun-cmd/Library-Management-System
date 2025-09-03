# 📚 Library Management System

A mini project using **Python flask + MySQL + HTML/CSS** that demonstrates core DBMS concepts like tables, relationships, and logs.

---

## 🚀 Setup Instructions

1. Clone the repository:

```bash

git clone https://github.com/mithun-cmd/Library-Management-System.git
cd Library-Management-System

2.Install dependencies:

bash

pip install -r requirements.txt

3.Create the database in MySQL:

sql

CREATE DATABASE library_db;

4.Import schema:

bash

mysql -u root -p library_db < database/schema.sql

5.Update database password in app/library.py:

python

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_mysql_password",   # 🔑 Change here
    "database": "library_db"
}

6.Run the app:

bash

python app/library.py
Open browser: http://127.0.0.1:5000/