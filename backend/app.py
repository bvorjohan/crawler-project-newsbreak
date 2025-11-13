from flask import Flask, jsonify, send_from_directory
import pandas as pd
import threading
import os
from datetime import datetime

app = Flask(__name__, static_folder="../frontend/build", static_url_path="/")

def run_crawler():
    from crawler.main import run
    run()

@app.route('/api/results')
def get_results():
    csv_path = os.path.join('output', 'results.csv')
    if not os.path.exists(csv_path):
        return jsonify({"error": "No data yet"}), 404
    df = pd.read_csv(csv_path)
    return jsonify(df.to_dict(orient='records'))

@app.route('/api/re-crawl', methods=['POST'])
def recrawl():
    lock_path = 'crawler.lock'
    if os.path.exists(lock_path):
        return jsonify({"status": "busy"}), 429
    open(lock_path, 'w').close()
    threading.Thread(target=_async_crawl).start()
    return jsonify({"status": "started"})

def _async_crawl():
    try:
        run_crawler()
        with open('output/last_run.txt', 'w') as f:
            f.write(datetime.now().isoformat())
    finally:
        os.remove('crawler.lock')

@app.route('/')
@app.route('/<path:path>')
def serve_react(path=""):
    build_dir = os.path.join(app.static_folder)
    if path != "" and os.path.exists(os.path.join(build_dir, path)):
        return send_from_directory(build_dir, path)
    return send_from_directory(build_dir, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
