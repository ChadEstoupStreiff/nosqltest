import logging
import time

import streamlit as st
from dotenv import dotenv_values
from neo4j import GraphDatabase


def connect_neo4j():
    config = dotenv_values(".env")

    attempts = 0
    while attempts < 20:
        try:
            st.session_state.driver = GraphDatabase.driver(
                uri="bolt://neo4j:7687", auth=("neo4j", config["NOSQL_PWD"])
            )
            with st.session_state.driver.session() as session:
                session.run("RETURN 1")
            break
        except Exception as err:
            logging.error(f"Attempt {attempts + 1}: Could not connect to Neo4j - {err}")
            attempts += 1
            time.sleep(5)
    else:
        logging.critical("Failed to connect to Neo4j after 20 attempts")
        raise SystemExit("Exiting due to repeated connection failures")

    logging.info("Connected to Neo4j")


if "driver" not in st.session_state:
    connect_neo4j()


def nosql_request(request: str, params: dict):
    if "driver" not in st.session_state:
        connect_neo4j()
    with st.session_state.driver.session() as session:
        result = session.run(request, **params)
        return [record for record in result]
