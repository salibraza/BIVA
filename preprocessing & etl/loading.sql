use fypdata;
#drop table if exists orders;
#truncate table orders;
create table orders (
	row_id int primary key,
    order_id varchar(20),
    order_date varchar(12),
    ship_date varchar(12),
    ship_mode varchar(20),
    customer_id varchar(10),
    customer_name varchar(30),
    segment varchar(20),
    city varchar(40),
    state varchar(40),
    country varchar(40),
    postal_code int,
    market varchar(10),
    region varchar(20),
    product_id varchar(20),
    category varchar(20),
    subcategory varchar(20),
    product_name varchar(130),
    sales decimal(15,4),
    quantity int,
    discount decimal(5,2),
    profit decimal(10,4),
    shipping_cost decimal(15,4),
    order_priority varchar(10)
);

# returns all the repeating products
#select distinct a.product_id, a.product_name from orders a
#left join 
#(select distinct product_id, product_name from orders group by product_id) b 
#using (product_id, product_name) where b.product_name is null;
#returns repeating orders
#select distinct a.order_id, a.order_date from orders a
#left join 
#(select distinct order_id, order_date, city, state, country from fypdata.orders group by order_id) b 
#using (order_id, order_date, city, state, country) where b.order_date is null;