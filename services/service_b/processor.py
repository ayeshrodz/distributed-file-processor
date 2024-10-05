import os
import csv
import json
import pika
from flask import Flask, request, jsonify

# Get folder path from environment variables
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/app/process_files')

app = Flask(__name__)

@app.route('/process_file', methods=['POST'])
def process_file():
    data = request.json
    file_path = data.get('file_path')

    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 400

    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='csv_queue')

    # Read the CSV file and send each row as a JSON message to RabbitMQ
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                # Format data before sending
                json_message = {
                    'file_name': os.path.basename(file_path),
                    'transaction_id': row['transaction_id'],
                    'customer_id': str(row['customer_id']),  # Ensure this is a string
                    'product_id': str(row['product_id']),    # Ensure this is a string
                    'product_name': row['product_name'],
                    'quantity': int(row['quantity']),         # Convert to integer
                    'unit_price': float(row['unit_price']),   # Convert to float
                    'total_price': float(row['total_price']), # Convert to float
                    'transaction_date': row['transaction_date'],  # Keep as is for now
                    'payment_method': row['payment_method'],
                    'shipping_address': row['shipping_address'],
                    'status': row['status']
                }
                
                # Send to RabbitMQ
                channel.basic_publish(exchange='', routing_key='csv_queue', body=json.dumps(json_message))
                print(f"Sent message: {json_message}")

            except Exception as e:
                print(f"Error processing row: {row}. Error: {e}")

    connection.close()

    return jsonify({'status': 'File processed and messages sent to queue'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
