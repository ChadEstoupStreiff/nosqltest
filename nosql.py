import logging
import random
import time

from dotenv import dotenv_values
from neo4j import GraphDatabase
from tqdm import tqdm


class Neo4jDatabase:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def setup_database(self):
        with self.driver.session() as session:
            session.execute_write(self.create_constraints)

    @staticmethod
    def create_constraints(tx):
        tx.run("CREATE CONSTRAINT FOR (u:User) REQUIRE u.id IS UNIQUE")
        tx.run("CREATE CONSTRAINT FOR (p:Product) REQUIRE p.id IS UNIQUE")
        tx.run("CREATE CONSTRAINT FOR (pu:Purchase) REQUIRE pu.id IS UNIQUE")

    def create_user(self, user_id, email, hashed_password, full_name, role):
        with self.driver.session() as session:
            session.execute_write(
                self._create_user, user_id, email, hashed_password, full_name, role
            )

    @staticmethod
    def _create_user(tx, user_id, email, hashed_password, full_name, role):
        tx.run(
            "CREATE (u:User {id: $user_id, email: $email, hashed_password: $hashed_password, full_name: $full_name, role: $role})",
            user_id=user_id,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
        )

    def create_product(self, product_id, name, price, description, image):
        with self.driver.session() as session:
            session.execute_write(
                self._create_product, product_id, name, price, description, image
            )

    @staticmethod
    def _create_product(tx, product_id, name, price, description, image):
        tx.run(
            "CREATE (p:Product {id: $product_id, name: $name, price: $price, description: $description, image: $image})",
            product_id=product_id,
            name=name,
            price=price,
            description=description,
            image=image,
        )

    def create_purchase(self, purchase_id, user_id, product_id, quantity, total_price):
        with self.driver.session() as session:
            session.execute_write(
                self._create_purchase,
                purchase_id,
                user_id,
                product_id,
                quantity,
                total_price,
            )

    @staticmethod
    def _create_purchase(tx, purchase_id, user_id, product_id, quantity, total_price):
        tx.run(
            "CREATE (pu:Purchase {id: $purchase_id, user_id: $user_id, product_id: $product_id, quantity: $quantity, total_price: $total_price})",
            purchase_id=purchase_id,
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            total_price=total_price,
        )

    def create_follow(self, follower_id, followee_id):
        with self.driver.session() as session:
            session.execute_write(self._create_follow, follower_id, followee_id)

    @staticmethod
    def _create_follow(tx, follower_id, followee_id):
        tx.run(
            "MATCH (follower:User {id: $follower_id}), (followee:User {id: $followee_id}) "
            "CREATE (follower)-[:FOLLOWS]->(followee)",
            follower_id=follower_id,
            followee_id=followee_id,
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    config = dotenv_values(".env")
    PORT = int(config["NOSQL_PORT"])

    logging.info("Config: %s", config)

    logging.info("Connecting to Neo4j")
    db = Neo4jDatabase(f"bolt://localhost:{PORT}", "neo4j", config["NOSQL_PWD"])
    total_time_start = time.time()
    logging.info("Connected to Neo4j")
    logging.info("Setting up database")
    db.setup_database()

    # Insert 10,000 users
    time_start = time.time()
    logging.info("Inserting 10,000 users")
    for i in tqdm(range(1, 10001)):
        db.create_user(
            str(i), f"user{i}@example.com", "hashed_password", f"User {i}", "user"
        )
    logging.info("Inserted 10,000 users in %s seconds", time.time() - time_start)

    # Insert 10,000 products
    time_start = time.time()
    logging.info("Inserting 1,000 products")
    for i in tqdm(range(1, 1001)):
        db.create_product(
            str(i),
            f"Product {i}",
            round(random.uniform(10.0, 100.0), 2),
            f"Description of product {i}",
            f"image{i}.jpg",
        )
    logging.info("Inserted 10,000 products in %s seconds", time.time() - time_start)

    # Insert 100,000 purchases
    time_start = time.time()
    logging.info("Inserting 100,000 purchases")
    for i in tqdm(range(1, 100001)):
        user_id = str(random.randint(1, 10000))
        product_id = str(random.randint(1, 10000))
        quantity = random.randint(1, 10)
        total_price = round(quantity * random.uniform(10.0, 100.0), 2)
        db.create_purchase(str(i), user_id, product_id, quantity, total_price)
    logging.info("Inserted 100,000 purchases in %s seconds", time.time() - time_start)

    # Insert follows
    time_start = time.time()
    logging.info("Inserting 100,000 follows")
    follows_set = set()
    for i in tqdm(range(1, 100001)):
        follower_id = str(random.randint(1, 10000))
        followee_id = str(random.randint(1, 10000))
        if follower_id != followee_id and (follower_id, followee_id) not in follows_set:
            db.create_follow(follower_id, followee_id)
            follows_set.add((follower_id, followee_id))
    logging.info("Inserted follows in %s seconds", time.time() - time_start)

    db.close()
    logging.info("Total time: %s seconds", time.time() - total_time_start)
