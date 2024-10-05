import pika
import psycopg2
import json
import os
import time
from datetime import datetime

# PostgreSQL configuration from environment variables
POSTGRES_USER = os.getenv('POSTGRES_USER', 'user')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'password')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'csv_data')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', 5432)

# Function to create the table if it doesn't exist
def create_table_if_not_exists():
    conn = psycopg2.connect(
        host="postgres",
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        port=POSTGRES_PORT
    )
    cursor = conn.cursor()
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS records (
        id SERIAL PRIMARY KEY,
        transaction_id TEXT,
        customer_id TEXT,
        product_id TEXT,
        product_name TEXT,
        quantity INT,
        unit_price FLOAT,
        total_price FLOAT,
        transaction_date TIMESTAMP,
        payment_method TEXT,
        shipping_address TEXT,
        status TEXT
    )
    '''
    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()

# Function to insert a row into the database
def insert_into_db(data):
    conn = psycopg2.connect(
        host="postgres",
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        port=POSTGRES_PORT
    )
    cursor = conn.cursor()
    
    insert_query = '''
    INSERT INTO records (
        transaction_id, customer_id, product_id, product_name, quantity,
        unit_price, total_price, transaction_date, payment_method,
        shipping_address, status
    ) VALUES (%(transaction_id)s, %(customer_id)s, %(product_id)s, %(product_name)s, %(quantity)s,
              %(unit_price)s, %(total_price)s, %(transaction_date)s, %(payment_method)s,
              %(shipping_address)s, %(status)s)
    '''

    # Prepare the values for the SQL statement
    try:

        # Ensure correct data types
        values = {
            'transaction_id': data['transaction_id'],
            'customer_id': str(data['customer_id']),  # Convert to string
            'product_id': str(data['product_id']),     # Convert to string
            'product_name': data['product_name'],
            'quantity': int(data['quantity']),         # Convert to integer
            'unit_price': float(data['unit_price']),   # Convert to float
            'total_price': float(data['total_price']), # Convert to float
        }

        # Handle the transaction_date with proper parsing
        transaction_date_str = data['transaction_date']
        try:
            # Attempt to parse the date with microseconds
            values['transaction_date'] = datetime.strptime(transaction_date_str, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            # If that fails, try parsing without microseconds
            values['transaction_date'] = datetime.strptime(transaction_date_str, '%Y-%m-%d %H:%M:%S')

        # Add the remaining fields to values
        values['payment_method'] = data['payment_method']
        values['shipping_address'] = data['shipping_address']
        values['status'] = data['status']

        # Execute the insert query
        cursor.execute(insert_query, values)
        conn.commit()
        print(f"{data['transaction_id']} - Data inserted successfully.")

    except Exception as e:
        # Print the SQL statement and error message if an error occurs
        formatted_sql = cursor.mogrify(insert_query, values)
        print(f"Error inserting into database: {e}")
        print(f"SQL statement that caused the issue: {formatted_sql.decode()}")
        print(f"Data that caused the issue: {data}")

    finally:
        cursor.close()
        conn.close()



# RabbitMQ message callback function
def callback(ch, method, properties, body):
    # print(f"Received message: {body.decode()}")
    json_data = json.loads(body.decode())
    insert_into_db(json_data)
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Function to establish connection to RabbitMQ with retries
def connect_to_rabbitmq():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            print("RabbitMQ not available yet, retrying in 5 seconds...")
            time.sleep(5)

# Function to consume messages from RabbitMQ
def consume_from_queue():
    connection = connect_to_rabbitmq()
    channel = connection.channel()
    channel.queue_declare(queue='csv_queue')

    # Ensure the table exists
    create_table_if_not_exists()

    channel.basic_consume(queue='csv_queue', on_message_callback=callback)
    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    consume_from_queue()
