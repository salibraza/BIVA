# BIVA-Bussiness Insight and Visualization Assistant
It is a web-based portal dedicated to data analysis and visualization, based on the data warehouse of a superstore

### Load Raw transactional data into Database
1)import DB/transactionsDump.sql in a mysql connection
it'll create a schema with raw data tables and popullate them with data 
**Data source** : *https://data.world/irvinpalacios21/final-data-set-global-sales/workspace/file?filename=Global+Superstore.xls*
**MySQL is used for all the database creation and management is** 
### Create and Popullate Warehouse
This can be done in two ways
1) Clean raw data, create warehouse and popullate it
	1.1) Run cleaning1.py (provide your local mysql connection credentials in the code)
	1.2) Run cleaning2.py (provide your local mysql connection credentials in the code)
	1.3) Run warehouseddl.sql in the same mysql connection where transactional data was imported
 
2) Import already popullated warehouse dump
		 Using all the procedures in previous approach, a ready-to-use warehouse dump is created
		 simply use the dump file.

The first approach was originally used to create the warehouse dump mentioned in second approach, so we suggest you
to use warehouseDump.ddl to directly import ready-to-use warehouse database.

### Create Materialized Views
Run querying/materializedViews.sql in the same schema as the warehouse to
create materialized views used in analysis

### OLAP
all the analytical processing queries used are contained in querying/queries.sql

### Django Web Project
The crm folder in project folder contains django project.For making a design consistent and clean we have used google material design in it as well. Following libraries in python virtual environment are needed to be installed to 
run the django project.
##### Bokeh
	pip install bokeh
##### NetworkX
	pip install networkx
##### Pandas
	pip install pandas
##### Mysql-Connector 
	pip install mysql-connector-python
##### Numpy
	pip install numpy
