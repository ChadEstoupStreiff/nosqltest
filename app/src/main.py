import logging
import time

import streamlit as st

logging.basicConfig(level=logging.INFO)
st.set_page_config(page_title="SQLvsNOSQL", page_icon="⌚", layout="wide")

with st.spinner("Connecting to databases"):
    from nosql import nosql_request
    from sql import sql_request


with st.sidebar:
    min_relations = 0
    min_purchases = 0
    request_type = st.selectbox(
        "Select type of request", ["Activity", "Relation", "Follows", "Purchases", "Products", "Users",]
    )
    st.divider()

    st.write(f"{request_type} request parameters:")
    nbr_entities = st.number_input(
        "Number of entities", min_value=1, max_value=100000, value=1000
    )

    if request_type == "Relation" or request_type == "Activity":
        min_relations = st.number_input(
            "Minimum number of relations", min_value=1, max_value=1000, value=1
        )
    if request_type == "Activity":
        min_purchases = st.number_input(
            "Minimum number of purchases", min_value=1, max_value=1000, value=1
        )

    run_request = st.button("Run request")
    st.divider()

if run_request:
    sql_request_string = {
        "Follows": "SELECT * FROM Follows LIMIT %s",
        "Purchases": "SELECT * FROM Purchase LIMIT %s",
        "Products": "SELECT * FROM Product LIMIT %s",
        "Users": "SELECT * FROM User LIMIT %s",
        "Relation": """
            SELECT u1.id, COUNT(*) as relation_count
            FROM User u1
            JOIN Follows f ON u1.id = f.follower_id
            GROUP BY u1.id
            HAVING relation_count >= %s
            LIMIT %s
        """,
        "Activity": """
            SELECT u.id, COUNT(*) as relation_count, COUNT(p.id) as purchase_count
            FROM User u
            LEFT JOIN Follows f ON u.id = f.follower_id
            LEFT JOIN Purchase p ON u.id = p.user_id
            GROUP BY u.id
            HAVING relation_count >= %s AND purchase_count >= %s
            LIMIT %s
        """
    }.get(request_type)
    sql_request_params = {
        "Follows": [nbr_entities],
        "Purchases": [nbr_entities],
        "Products": [nbr_entities],
        "Users": [nbr_entities],
        "Relation": [min_relations, nbr_entities],
        "Activity": [min_relations, min_purchases, nbr_entities]
    }.get(request_type)

    no_sql_request_string = {
        "Follows": "MATCH (:User)-[f:FOLLOWS]->(:User) RETURN f LIMIT $nbr_follows",
        "Purchases": "MATCH (p:Purchase) RETURN p LIMIT $nbr_purchases",
        "Products": "MATCH (p:Product) RETURN p LIMIT $nbr_products",
        "Users": "MATCH (u:User) RETURN u LIMIT $nbr_users",
        "Relation": """
            MATCH (u:User)-[r:FOLLOWS]->()
            WITH u, COUNT(r) as relation_count
            WHERE relation_count >= $n_relations
            RETURN u, relation_count
            LIMIT $nbr_entities
        """,
        "Activity": """
            MATCH (u:User)
            OPTIONAL MATCH (u)-[r:FOLLOWS]->()
            OPTIONAL MATCH (u)-[:PURCHASED]->(p:Purchase)
            WITH u, COUNT(r) as relation_count, COUNT(p) as purchase_count
            WHERE relation_count >= $min_relations AND purchase_count >= $min_purchases
            RETURN u, relation_count, purchase_count
            LIMIT $nbr_entities
        """
    }.get(request_type)
    no_sql_request_params = {
        "Follows": {"nbr_follows": nbr_entities},
        "Purchases": {"nbr_purchases": nbr_entities},
        "Products": {"nbr_products": nbr_entities},
        "Users": {"nbr_users": nbr_entities},
        "Relation": {"n_relations": min_relations, "nbr_entities": nbr_entities},
        "Activity": {"min_relations": min_relations, "min_purchases": min_purchases, "nbr_entities": nbr_entities}
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
    st.write(f"{looser} is {(faster_by):.3f}% slower than {winner}")

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
