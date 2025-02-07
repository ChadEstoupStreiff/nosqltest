import random
from neo4j import GraphDatabase
from dotenv import dotenv_values

class Neo4jDatabase:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def setup_database(self):
        with self.driver.session() as session:
            session.write_transaction(self.create_constraints)

    @staticmethod
    def create_constraints(tx):
        tx.run("CREATE CONSTRAINT ON (u:User) ASSERT u.id IS UNIQUE")
        tx.run("CREATE CONSTRAINT ON (p:Product) ASSERT p.id IS UNIQUE")
        tx.run("CREATE CONSTRAINT ON (pu:Purchase) ASSERT pu.id IS UNIQUE")

    def create_user(self, user_id, email, hashed_password, full_name, role):
        with self.driver.session() as session:
            session.write_transaction(self._create_user, user_id, email, hashed_password, full_name, role)

    @staticmethod
    def _create_user(tx, user_id, email, hashed_password, full_name, role):
        tx.run("CREATE (u:User {id: $user_id, email: $email, hashed_password: $hashed_password, full_name: $full_name, role: $role})",
               user_id=user_id, email=email, hashed_password=hashed_password, full_name=full_name, role=role)

    def create_product(self, product_id, name, price, description, image):
        with self.driver.session() as session:
            session.write_transaction(self._create_product, product_id, name, price, description, image)

    @staticmethod
    def _create_product(tx, product_id, name, price, description, image):
        tx.run("CREATE (p:Product {id: $product_id, name: $name, price: $price, description: $description, image: $image})",
               product_id=product_id, name=name, price=price, description=description, image=image)

    def create_purchase(self, purchase_id, user_id, product_id, quantity, total_price):
        with self.driver.session() as session:
            session.write_transaction(self._create_purchase, purchase_id, user_id, product_id, quantity, total_price)

    @staticmethod
    def _create_purchase(tx, purchase_id, user_id, product_id, quantity, total_price):
        tx.run("CREATE (pu:Purchase {id: $purchase_id, user_id: $user_id, product_id: $product_id, quantity: $quantity, total_price: $total_price})",
               purchase_id=purchase_id, user_id=user_id, product_id=product_id, quantity=quantity, total_price=total_price)

if __name__ == "__main__":
    config = dotenv_values(".env")
    db = Neo4jDatabase("neo4j://localhost:7687", "neo4j", config["NOSQL_PWD"])
    db.setup_database()

    # Insert 10,000 users
    for i in range(1, 10001):
        db.create_user(str(i), f"user{i}@example.com", "hashed_password", f"User {i}", "user")

    # Insert 10,000 products
    for i in range(1, 10001):
        db.create_product(str(i), f"Product {i}", round(random.uniform(10.0, 100.0), 2), f"Description of product {i}", f"image{i}.jpg")

    # Insert 100,000 purchases
    for i in range(1, 100001):
        user_id = str(random.randint(1, 10000))
        product_id = str(random.randint(1, 10000))
        quantity = random.randint(1, 10)
        total_price = round(quantity * random.uniform(10.0, 100.0), 2)
        db.create_purchase(str(i), user_id, product_id, quantity, total_price)

    db.close()