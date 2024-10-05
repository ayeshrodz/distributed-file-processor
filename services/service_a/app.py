from flask import Flask, request
import os
import requests

# Get folder path from environment variables
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/app/process_files')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <h1>Upload CSV</h1>
    <form action="/upload" method="POST" enctype="multipart/form-data">
        <input type="file" name="file" accept=".csv">
        <button type="submit">Upload</button>
    </form>
    '''

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Notify Service B to start processing
    webhook_url = 'http://service_b:5001/process_file'
    data = {'file_path': file_path}
    response = requests.post(webhook_url, json=data)

    if response.status_code == 200:
        return f'File {file.filename} uploaded and processing started.'
    else:
        return 'Error starting file processing', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
