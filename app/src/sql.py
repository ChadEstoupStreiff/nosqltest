import logging
import time

import mysql.connector
import streamlit as st
from dotenv import dotenv_values


def connect_mysql():
    config = dotenv_values(".env")

    attempts = 0
    while attempts < 20:
        try:
            st.session_state.conn = mysql.connector.connect(
                host="mariadb",
                port=3306,
                user=config["SQL_USER"],
                password=config["SQL_PWD"],
                database=config["SQL_DB"],
                charset="utf8mb4",
                collation="utf8mb4_unicode_ci",
            )
            break
        except mysql.connector.Error as err:
            logging.error(f"Attempt {attempts + 1}: Could not connect to MySQL - {err}")
            attempts += 1
            time.sleep(5)
    else:
        logging.critical("Failed to connect to MySQL after 20 attempts")
        raise SystemExit("Exiting due to repeated connection failures")
    logging.info("Connected to MySQL")


if "conn" not in st.session_state:
    connect_mysql()


def sql_request(request: str, params: list):
    if "conn" not in st.session_state:
        connect_mysql()
    cursor = st.session_state.conn.cursor()
    cursor.execute(request, params)
    return cursor.fetchall()
