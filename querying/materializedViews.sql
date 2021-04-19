#### Materialized Views
## Product Sales Summary
create table mv_product_sales
select p.*, sum(s.profit) Profit, 
	sum(s.quantity) Quantity, sum(s.sales) Sales, sum(s.discount) discount 
	from sales_fact s join product_dim p on (s.product_id = p.product_id)
    group by product_id;

## Customer Sales Summary
create table mv_customer_sales
select c.*, sum(s.profit) Profit, 
	sum(s.sales) Sales, sum(s.discount) discount 
	from sales_fact s join customer_dim c on (s.customer_id = c.customer_id)
    group by customer_id;

## Market Region Sales Summary
create table mv_market_region_sales
select l.market, l.region, sum(s.profit) Profit, 
	sum(s.sales) Sales, sum(s.discount) discount 
	from sales_fact s join location_dim l on (s.location_id = l.location_id)
    group by l.market, l.region;

## Market region country sales summary
create table mv_market_region_country_sales
select l.market, l.region, l.country, sum(s.profit) Profit, 
	sum(s.sales) Sales, sum(s.discount) discount 
	from sales_fact s join location_dim l on (s.location_id = l.location_id)
    group by l.market, l.region, l.country order by l.country;

## country city sales summary
create table mv_country_city_sales
select l.country, l.city, sum(s.profit) Profit, 
	sum(s.sales) Sales, sum(s.discount) discount 
	from sales_fact s join location_dim l on (s.location_id = l.location_id)
    group by l.country, l.city order by l.country;

## year month sales summary
create table mv_year_month_sales
select d.year, d.month, sum(s.sales) sales, sum(s.profit) profit
	from sales_fact s join dateorder_dim d on (d.dateOrder_id = s.dateOrder_id)
    group by d.year, d.month order by d.year, d.month;
    
#### Pre-calculated Joins
## Sales Product Date join
create table pj_sales_product_date
select sf.*, pd.category_id, pd.product_name, pd.unit_price, 
dd.date, dd.day, dd.half, dd.month, dd.quarter, dd.week, dd.weekday, dd.year
from sales_fact sf 
inner join dateorder_dim dd on sf.dateOrder_id = dd.dateOrder_id
inner join product_dim pd on sf.product_id = pd.product_id;

## Sales Customer Date join
create table pj_sales_customer_date
select sf.*, cd.customer_name, cd.segment,
dd.date, dd.day, dd.half, dd.month, dd.quarter, dd.week, dd.weekday, dd.year
from sales_fact sf 
inner join dateorder_dim dd on sf.dateOrder_id = dd.dateOrder_id
inner join customer_dim cd on sf.customer_id = cd.customer_id;

## Sales Category Date Join
create table pj_sales_category_date
select sf.*, cd.category_id, cd.category, cd.subcategory, 
dd.date, dd.day, dd.half, dd.month, dd.quarter, dd.week, dd.weekday, dd.year
from sales_fact sf 
inner join dateorder_dim dd on sf.dateOrder_id = dd.dateOrder_id
inner join product_dim pd on sf.product_id = pd.product_id
inner join category_dim cd on cd.category_id = pd.category_id;

## Product Association View
create table mv_product_association 
select p.product1, p.product2, c.counts, p.sales, p.profit, p.quantity1, p.quantity2 from 
(select a.product_name product1, b.product_name product2, sum((a.sales + b.sales)) sales, sum(a.quantity) quantity1, sum(b.quantity) quantity2, sum((a.profit + b.profit)) profit 
from (select s.order_id, p.product_name, sales, quantity, profit from sales_fact s 
inner join product_dim p on s.product_id = p.product_id) a 
inner join (select s.order_id, p.product_name, sales, quantity, profit from sales_fact s 
inner join product_dim p on s.product_id = p.product_id) b on a.order_id = b.order_id 
where a.product_name != b.product_name
group by a.product_name, b.product_name) p
inner join
(select a.product_name product1, b.product_name product2, count(*) counts 
from (select s.order_id, p.product_name from sales_fact s 
inner join product_dim p on s.product_id = p.product_id) a 
inner join (select s.order_id, p.product_name from sales_fact s 
inner join product_dim p on s.product_id = p.product_id) b on a.order_id = b.order_id 
where a.product_name != b.product_name
group by a.product_name, b.product_name) c on c.product1 = p.product1 and c.product2 = p.product2;
