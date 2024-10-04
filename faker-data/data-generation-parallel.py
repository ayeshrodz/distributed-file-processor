import csv
import uuid
from faker import Faker # type: ignore
import random
from multiprocessing import Pool, cpu_count
import faker_commerce

fake = Faker()
fake.add_provider(faker_commerce.Provider)

# Function to generate a chunk of rows
def generate_chunk(chunk_size, file_name):
    rows = []
    for _ in range(chunk_size):
        transaction_id = str(uuid.uuid4())
        customer_id = random.randint(1000, 9999)
        product_id = random.randint(5000, 5999)
        product_name = fake.ecommerce_name()
        quantity = random.randint(1, 10)
        unit_price = round(random.uniform(10.00, 100.00), 2)
        total_price = round(quantity * unit_price, 2)
        transaction_date = fake.date_time_this_year()
        payment_method = random.choice(['Credit Card', 'PayPal', 'Bank Transfer'])
        shipping_address = fake.address().replace("\n", ", ")
        status = random.choice(['Completed', 'Pending', 'Canceled'])
        
        rows.append([
            file_name, transaction_id, customer_id, product_id, product_name, 
            quantity, unit_price, total_price, transaction_date, 
            payment_method, shipping_address, status
        ])
    return rows

# Function to write a chunk of rows to the CSV
def write_to_csv(file_name, rows):
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

# Generate the CSV using multiprocessing
def generate_csv_parallel(file_name, num_rows, num_workers=None):
    chunk_size = num_rows // num_workers if num_workers else num_rows // cpu_count()

    if not num_workers:
        num_workers = cpu_count()  # Use all available CPU cores

    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow([
            'file_name', 'transaction_id', 'customer_id', 'product_id', 'product_name', 
            'quantity', 'unit_price', 'total_price', 'transaction_date', 
            'payment_method', 'shipping_address', 'status'
        ])

    with Pool(num_workers) as pool:
        results = [pool.apply_async(generate_chunk, (chunk_size, file_name)) for _ in range(num_workers)]

        for result in results:
            chunk = result.get()  # Get the generated rows from the pool
            write_to_csv(file_name, chunk)  # Write the chunk to the file


if __name__ == '__main__':
    # Generate large files with parallel processing
    for i in range(1, 4):
        generate_csv_parallel(f'test_file_{i}.csv', 100000, num_workers=8)  # Generate files with 10,000 rows each