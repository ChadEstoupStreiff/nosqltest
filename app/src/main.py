import logging

import streamlit as st
import time

logging.basicConfig(level=logging.INFO)
st.set_page_config(page_title="SQLvsNOSQL", page_icon="⌚", layout="wide")

with st.spinner("Connecting to databases"):
    from sql import sql_request
    from nosql import nosql_request


with st.sidebar:
    request_type = st.selectbox(
        "Select type of request", ["Follows", "Purchases", "Products", "Users"]
    )
    st.divider()

    st.write(f"{request_type} request parameters:")
    if request_type == "Follows":
        nbr_follows = st.number_input(
            "Number of follows", min_value=1, max_value=100000, value=1000
        )

    run_request = st.button("Run request")

if run_request:
    st.session_state.result = {}

    time_start = time.time()
    st.session_state.result['sql'] = sql_request("SELECT * FROM Follows LIMIT %s", [nbr_follows])
    time_end = time.time()
    st.session_state.result['time_sql'] = time_end - time_start
    
    time_start = time.time()
    st.session_state.result['no_sql'] = nosql_request(
        "MATCH (:User)-[f:FOLLOWS]->(:User) RETURN f LIMIT $nbr_follows",
        {"nbr_follows": nbr_follows},
    )
    time_end = time.time()
    st.session_state.result['time_no_sql'] = time_end - time_start

if "result" in st.session_state:
    winner = "SQL" if st.session_state.result['time_sql'] < st.session_state.result['time_no_sql'] else "NoSQL"
    st.title("Results:")
    st.write(f"{winner} wins by {abs(st.session_state.result['time_sql'] - st.session_state.result['time_no_sql']):.4f} seconds !")
    st.write(f"{winner} is {(st.session_state.result['time_sql'] / st.session_state.result['time_no_sql'] * 100):.3f}% faster !")
    with st.expander("Show results"):
        colsql, colnosql = st.columns(2)
    with colsql:
        st.title("SQL results")
        st.write(f"Time taken: {st.session_state.result['time_sql']} seconds")
        st.write("Result content:")
        st.write(st.session_state.result['sql'])

    with colnosql:
        st.title("NoSQL results")
        st.write(f"Time taken: {st.session_state.result['time_no_sql']} seconds")
        st.write("Result content:")
        st.write(st.session_state.result['no_sql'])
else:
    st.write("No results to display")