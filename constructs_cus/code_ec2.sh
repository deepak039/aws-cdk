#!/bin/bash
# Update and install necessary packages
sudo yum update -y
sudo yum install -y python3 pip git

# Install Flask and other Python dependencies
pip3 install flask pymysql

# Create application directory
APP_DIR="/home/ec2-user/flaskapp"
sudo mkdir -p $APP_DIR
cd $APP_DIR

# Flask application code
cat << EOF > app.py
from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)

# Database configuration (replace placeholders with actual values)
DB_HOST = "${db_host}"
DB_PORT = int("${db_port}")
DB_USER = "yourdbuser"
DB_PASSWORD = "yourdbpassword"
DB_NAME = "yourdbname"

# Database connection helper
def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

# Insert data into database
@app.route('/insert', methods=['POST'])
def insert_data():
    try:
        data = request.json
        key = data.get("key")
        value = data.get("value")

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "INSERT INTO my_table (key_column, value_column) VALUES (%s, %s)"
        cursor.execute(sql, (key, value))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success", "message": f"Inserted key={key}, value={value}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# Retrieve data from database
@app.route('/get', methods=['GET'])
def get_data():
    try:
        key = request.args.get("key")

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "SELECT value_column FROM my_table WHERE key_column = %s"
        cursor.execute(sql, (key,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            return jsonify({"status": "success", "key": key, "value": result[0]})
        else:
            return jsonify({"status": "error", "message": "Key not found."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# Health check route
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
EOF

# Set up the database schema
cat << EOF > setup_db.py
import pymysql

DB_HOST = "${db_host}"
DB_PORT = int("${db_port}")
DB_USER = "admin1"
DB_PASSWORD = "password123"
DB_NAME = "testdb"

def setup_database():
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()

    # Create database
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    conn.commit()

    # Connect to the newly created database
    conn.select_db(DB_NAME)

    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS my_table (
            key_column VARCHAR(255) PRIMARY KEY,
            value_column VARCHAR(255)
        )
    """)
    conn.commit()

    cursor.close()
    conn.close()

if __name__ == "__main__":
    setup_database()
EOF

# Run database setup
python3 setup_db.py

# Launch Flask app
nohup python3 app.py > app.log 2>&1 &