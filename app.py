from flask import Flask, jsonify, render_template, send_from_directory
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import os
from dotenv import load_dotenv

app = Flask(__name__,template_folder='.',static_folder='static/')

# Load environment variables from .env file
load_dotenv()

# Database connection configuration from environment variables
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn

@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/get_data', methods=['GET'])
def get_data():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM players")
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    # Save data to a JSON file
    with open('static/data.json', 'w') as f:
        json.dump(data, f, indent=4)

    return jsonify(data)

@app.route('/snapshot')
def generate_snapshot():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT * FROM players')
        data = cursor.fetchall()
        cursor.close()
        conn.close()

        html_content = '<!DOCTYPE html><html><head><title>Snapshot</title></head><body><h1>Player Scores</h1><ul></html>'
        for player in data:
            html_content += f'<li>{player["name"]}: {player["game"]}</li>'
        html_content += '</ul></body></html>'

        with open('snapshot.html', 'w') as f:
            f.write(html_content)

        return html_content
    except Exception as e:
        return str(e)

@app.route('/snapshot.html')
def get_snapshot():
    return send_from_directory('.', 'snapshot.html')

if __name__ == '__main__':
    app.run(debug=True)
