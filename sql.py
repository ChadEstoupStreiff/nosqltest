import random
import string
from faker import Faker
import mysql.connector
from dotenv import dotenv_values
import logging
from tqdm import tqdm
import uuid

logging.basicConfig(level=logging.INFO)
config = dotenv_values(".env")
fake = Faker()
logging.info(config)

PORT = int(config["SQL_PORT"])
PORT = 3306 # WTF it ignores dockercompose port config ???

conn = mysql.connector.connect(
    host="127.0.0.1",
    port=PORT,
    user=config["SQL_USER"],
    password=config["SQL_PWD"],
    database=config["SQL_DB"],
    charset='utf8mb4',
    collation='utf8mb4_unicode_ci'
)
cursor = conn.cursor()
logging.info("Connected to MySQL")

logging.info("Creating tables")
# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS User (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255),
    hashed_password VARCHAR(255),
    full_name VARCHAR(255),
    role VARCHAR(255)
) COLLATE utf8mb4_unicode_ci
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Product (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    price REAL,
    description TEXT,
    image TEXT
) COLLATE utf8mb4_unicode_ci
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Purchase (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    product_id VARCHAR(255),
    quantity INTEGER,
    total_price REAL,
    FOREIGN KEY(user_id) REFERENCES User(id),
    FOREIGN KEY(product_id) REFERENCES Product(id)
) COLLATE utf8mb4_unicode_ci
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Follows (
    follower_id VARCHAR(255),
    followee_id VARCHAR(255),
    PRIMARY KEY (follower_id, followee_id),
    FOREIGN KEY(follower_id) REFERENCES User(id),
    FOREIGN KEY(followee_id) REFERENCES User(id)
) COLLATE utf8mb4_unicode_ci
''')

# Insert random data
def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Insert 10000 random users
logging.info("Inserting random users")
for _ in tqdm(range(10000)):
    cursor.execute('''
    INSERT INTO User (id, email, hashed_password, full_name, role)
    VALUES (%s, %s, %s, %s, %s)
    ''', (str(uuid.uuid4()), fake.email(), random_string(), fake.name(), random.choice(['user', 'admin'])))

# Insert 1000 random products
logging.info("Inserting random products")
for _ in tqdm(range(1000)):
    cursor.execute('''
    INSERT INTO Product (id, name, price, description, image)
    VALUES (%s, %s, %s, %s, %s)
    ''', (str(uuid.uuid4()), fake.word(), round(random.uniform(1.0, 100.0), 2), fake.text(), fake.image_url()))

# Insert 100000 random purchases
logging.info("Inserting random purchases")
cursor.execute('SELECT id FROM User')
user_ids = [row[0] for row in cursor.fetchall()]
cursor.execute('SELECT id FROM Product')
product_ids = [row[0] for row in cursor.fetchall()]

for _ in tqdm(range(100000)):
    user_id = random.choice(user_ids)
    product_id = random.choice(product_ids)
    quantity = random.randint(1, 10)
    total_price = round(quantity * random.uniform(1.0, 100.0), 2)
    cursor.execute('''
    INSERT INTO Purchase (id, user_id, product_id, quantity, total_price)
    VALUES (%s, %s, %s, %s, %s)
    ''', (str(uuid.uuid4()), user_id, product_id, quantity, total_price))

# Insert 100000 random follows
logging.info("Inserting random follows")
follows_set = set()
for _ in tqdm(range(100000)):
    follower_id = random.choice(user_ids)
    followee_id = random.choice(user_ids)
    if follower_id != followee_id and (follower_id, followee_id) not in follows_set:
        cursor.execute('''
        INSERT INTO Follows (follower_id, followee_id)
        VALUES (%s, %s)
        ''', (follower_id, followee_id))
        follows_set.add((follower_id, followee_id))

# Commit and close
conn.commit()
conn.close()
logging.info("Ok.")