# **Github link: https://github.com/ChadEstoupStreiff/nosqltest** 
# SQL vs NoSQL
This project aims to time request with same objectives between a sql database (mariadb) and a nosql database (neo4j).  

## 1. Modèles de Données:  

Nous allons définir trois collections :  
	•	users : Gère les utilisateurs et leurs relations de followers.  
	•	products : Gère les produits disponibles.  
	•	purchases : Gère les achats effectués par les utilisateurs.  
 
![entites uml](diagrams/entities.png)

<div style="display: flex; justify-content: space-between;">
	<div style="flex: 1; margin-right: 10px;">
		<h3>SQL diagram:</h3>
		<img src="diagrams/sql.png" alt="sql uml">
	</div>
	<div style="flex: 1; margin-left: 10px;">
		<h3>NOSQL diagram:</h3>
		<img src="diagrams/nosql.png" alt="nosql uml">
	</div>
</div>

## 2. Init databases:  
**Make sure to have docker, docker-compose, python and pypi installed!**  
Then launch installation with this command:
```bash
./install.sh
```
This will creates tables and entitites, create 10000 users, 1000 products, 100000 purchases and 100000 follows on both databases.  
All your containers will be started.

## 3. Use application
You can now access to the web application at this url: http://localhost:3793/

## 4. Results:
Test table
| Test Case       | SQL (MariaDB) Time | NoSQL (Neo4j) Time | Difference |
|-----------------|--------------------|--------------------|--------------------|
| Search for 1000 users    | 0.0080s              | 0.2232s               | 2689%               |
| Search for 1000 products    | 0.0182s              | 0.1075s               | 490%               |
| Search for 1000 purchases    | 0.0159              | 0.1938               | 1118%               |
| Search for 1000 follows    | 0.0164s              | 0.2733s               | 1567%               |
| Search for 1000 users with at least 20 relations    | 0.0616s              | 0.0410s               | 50%               |
| Search for 1000 users with at least 20 relations and at least 50 purchases    | 0.0547s              | 0.3919s               | 615%               |

Conclusion: Regular SQL seems a lot faster on any requests.