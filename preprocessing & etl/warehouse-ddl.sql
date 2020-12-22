create schema biva;
use biva;

drop table if exists category_dim;
create table category_dim (
	category_id varchar(30) primary key, # "category-subcategory"
    category varchar(20),
    subcategory varchar(20)
);

drop table if exists product_dim;
create table product_dim (
	product_id varchar(20) primary key,
    product_name varchar(130),
    unit_price decimal(15,4),
    category_id varchar(30) not null,
    foreign key (category_id) references category_dim(category_id)
);
 

drop table if exists customer_dim;
create table customer_dim (
	customer_id varchar(10) primary key,
    customer_name varchar(30),
    segment varchar(20)
);

drop table if exists location_dim;
create table location_dim (
	location_id varchar(80) primary key, # "market-country-state-city"
	market varchar(10),
    region varchar(20),
	country varchar(40),
	state varchar(40),
	city varchar(40)
);

drop table if exists dateOrder_dim;
create table dateOrder_dim (
	dateOrder_id varchar(12) primary key, # "date"
    year int,
    half int,
    quarter int,
    month int,
    day int,
    weekday varchar(15),
    date date
);

drop table if exists order_fact;
create table order_fact (
    order_id varchar(20) not null,
    customer_id varchar(10) not null,
    location_id varchar(80) not null,
    dateOrder_id varchar(12) not null,
    dateShip date,
    sales decimal(15,4),
    products_quantity int,
    discount decimal,
    profit decimal(10,4),
    shipping_cost decimal(15,4),
    ship_mode varchar(20),
    order_priority varchar(10),
    primary key (order_id, customer_id, location_id, dateOrder_id),
    foreign key (customer_id) references customer_dim(customer_id),
    foreign key (location_id) references location_dim(location_id),
    foreign key (dateOrder_id) references dateOrder_dim(dateOrder_id)
);

drop table if exists sales_fact;
create table sales_fact (
	order_id varchar(20) not null,
    product_id varchar(20) not null,
    customer_id varchar(10) not null,
    location_id varchar(80) not null,
    dateOrder_id varchar(12) not null,
    dateShip date,
    sales decimal(15,4),
    quantity int,
    discount decimal,
    profit decimal(10,4),
    shipping_cost decimal(15,4),
    ship_mode varchar(20),
    order_priority varchar(10),
    primary key (order_id, product_id, customer_id, location_id, dateOrder_id),
    foreign key (customer_id) references customer_dim(customer_id),
    foreign key (product_id) references product_dim(product_id),
    foreign key (location_id) references location_dim(location_id),
    foreign key (dateOrder_id) references dateOrder_dim(dateOrder_id),
    foreign key (order_id) references order_fact(order_id)
);

use biva;
# Populating the customer dimension table
insert ignore into customer_dim select DISTINCT customer_id, customer_name, segment from fypdata.orders;

# Populating the category dimension table
insert ignore into category_dim select DISTINCT concat_ws("-", category, subcategory), category, subcategory from fypdata.orders;

# Populating the location dimension table
insert ignore into location_dim 
	select DISTINCT concat_ws("-", market, country, state, city), market, region, country, state, city from fypdata.orders;

# Populating the dateOrder dimension table
insert ignore into dateOrder_dim select distinct order_date, 
	year(STR_TO_DATE(order_date,'%m/%d/%Y')) year, IF(quarter(STR_TO_DATE(order_date,'%m/%d/%Y')) < 3, 1, 2) half,
	quarter(STR_TO_DATE(order_date,'%m/%d/%Y')) quarter, month(STR_TO_DATE(order_date,'%m/%d/%Y')) month,
    day(STR_TO_DATE(order_date,'%m/%d/%Y')) day, dayname(STR_TO_DATE(order_date,'%m/%d/%Y')) dayname, 
    (STR_TO_DATE(order_date,'%m/%d/%Y')) date
    from fypdata.orders;

# Populating the product dimension
insert ignore into biva.product_dim
	select product_id, product_name, sales/quantity, concat_ws("-", category, subcategory) catrgoryID 
	from orders group by product_id;

# Populating the order fact table
insert ignore into biva.order_fact
	select order_id, customer_id, concat_ws("-", market, country, state, city) location_id,
	order_date, STR_TO_DATE(ship_date,'%m/%d/%Y') dateship, sum(sales) sales, sum(quantity) products_quantity,
    Round(sum((sales/(1-discount))*discount), 4) discount,
    sum(profit), sum(shipping_cost), ship_mode, order_priority from orders group by order_id order by order_id;

# Populating the sales fact table
insert ignore into biva.sales_fact
	select order_id, product_id, customer_id, concat_ws("-", market, country, state, city) location_id, order_date,
	STR_TO_DATE(ship_date,'%m/%d/%Y') dateship, sales, quantity, Round(((sales/(1-discount))*discount),4) discount, 
    profit, shipping_cost, ship_mode, order_priority from orders 
    group by order_id, product_id, customer_id, location_id, order_date;

