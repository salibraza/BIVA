# BIVA-Bussiness Insight and Visualization Assistant
### Load Raw transactional data into Database
1)import transactionsDump.sql in a mysql connection
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
Run materializedViews.sql in the same schema as the warehouse to
create materialized views used in analysis

### Data Visuals
groupVbar.py, multiVbarchar.py, pie.py and templateplots.py contains
codes plots different figures required for analysis

### OLAP
all the analytical processing queries used are contained in queries.sql