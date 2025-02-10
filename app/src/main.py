import logging
import time

import streamlit as st

logging.basicConfig(level=logging.INFO)
st.set_page_config(page_title="SQLvsNOSQL", page_icon="⌚", layout="wide")

with st.spinner("Connecting to databases"):
    from nosql import nosql_request
    from sql import sql_request


with st.sidebar:
    request_type = st.selectbox(
        "Select type of request", ["Follows", "Purchases", "Products", "Users"]
    )
    st.divider()

    st.write(f"{request_type} request parameters:")
    nbr_entities = st.number_input(
        "Number of entities", min_value=1, max_value=100000, value=1000
    )

    run_request = st.button("Run request")
    st.divider()

if run_request:
    sql_request_string = {
        "Follows": "SELECT * FROM Follows LIMIT %s",
        "Purchases": "SELECT * FROM Purchase LIMIT %s",
        "Products": "SELECT * FROM Product LIMIT %s",
        "Users": "SELECT * FROM User LIMIT %s",
    }.get(request_type)
    sql_request_params = {
        "Follows": [nbr_entities],
        "Purchases": [nbr_entities],
        "Products": [nbr_entities],
        "Users": [nbr_entities],
    }.get(request_type)

    no_sql_request_string = {
        "Follows": "MATCH (:User)-[f:FOLLOWS]->(:User) RETURN f LIMIT $nbr_follows",
        "Purchases": "MATCH (p:Purchase) RETURN p LIMIT $nbr_purchases",
        "Products": "MATCH (p:Product) RETURN p LIMIT $nbr_products",
        "Users": "MATCH (u:User) RETURN u LIMIT $nbr_users",
    }.get(request_type)
    no_sql_request_params = {
        "Follows": {"nbr_follows": nbr_entities},
        "Purchases": {"nbr_purchases": nbr_entities},
        "Products": {"nbr_products": nbr_entities},
        "Users": {"nbr_users": nbr_entities},
    }.get(request_type)

    with st.sidebar:
        st.title("SQL request:")
        st.write(sql_request_string)
        st.write(sql_request_params)
        st.title("NoSQL request:")
        st.write(no_sql_request_string)
        st.write(no_sql_request_params)
    with st.spinner("Running requests"):
        st.session_state.result = {}

        time_start = time.time()
        st.session_state.result["sql"] = sql_request(
            sql_request_string, sql_request_params
        )
        time_end = time.time()
        st.session_state.result["time_sql"] = time_end - time_start

        time_start = time.time()
        st.session_state.result["no_sql"] = nosql_request(
            no_sql_request_string,
            no_sql_request_params,
        )
        time_end = time.time()
        st.session_state.result["time_no_sql"] = time_end - time_start

if "result" in st.session_state:
    winner = (
        "SQL"
        if st.session_state.result["time_sql"] < st.session_state.result["time_no_sql"]
        else "NoSQL"
    )
    looser = "NoSQL" if winner == "SQL" else "SQL"
    st.title("Results:")
    st.write(
        f"{winner} wins by {abs(st.session_state.result['time_sql'] - st.session_state.result['time_no_sql']):.4f} seconds !"
    )
    faster_by = (
        st.session_state.result["time_no_sql" if winner == "SQL" else "time_sql"]
        / st.session_state.result["time_no_sql" if looser == "SQL" else "time_sql"]
        * 100
        - 100
    )
    st.write(f"{looser} is {(faster_by):.3f}% slower !")

    with st.expander("Show results"):
        colsql, colnosql = st.columns(2)
    with colsql:
        st.title("SQL results")
        st.write(f"Time taken: {st.session_state.result['time_sql']} seconds")
        st.write("Result content:")
        st.write(st.session_state.result["sql"])

    with colnosql:
        st.title("NoSQL results")
        st.write(f"Time taken: {st.session_state.result['time_no_sql']} seconds")
        st.write("Result content:")
        st.write(st.session_state.result["no_sql"])
else:
    st.write("No results to display")
