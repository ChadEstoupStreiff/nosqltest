1. Modèles de Données  

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

2. Init databases:
**Make sure to have docker, docker-compose, python and pypi installed**
