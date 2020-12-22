#### Materialized Views
## Product Sales Summary
create table product_sales_mv
select p.*, sum(s.profit) Profit, 
	sum(s.quantity) Quantity, sum(s.sales) Sales, sum(s.discount) discount 
	from sales_fact s join product_dim p on (s.product_id = p.product_id)
    group by product_id;

## Customer Sales Summary
create table customer_sales_mv
select c.*, sum(s.profit) Profit, 
	sum(s.sales) Sales, sum(s.discount) discount 
	from sales_fact s join customer_dim c on (s.customer_id = c.customer_id)
    group by customer_id;
select * from _sales_mv;
## Market Region Sales Summary
create table market_region_sales_mv
select l.market, l.region, sum(s.profit) Profit, 
	sum(s.sales) Sales, sum(s.discount) discount 
	from sales_fact s join location_dim l on (s.location_id = l.location_id)
    group by l.market, l.region;

## Market region country sales summary
create table market_region_country_sales_mv
select l.market, l.region, l.country, sum(s.profit) Profit, 
	sum(s.sales) Sales, sum(s.discount) discount 
	from sales_fact s join location_dim l on (s.location_id = l.location_id)
    group by l.market, l.region, l.country order by l.country;

## country city sales summary
create table country_city_sales_mv
select l.country, l.city, sum(s.profit) Profit, 
	sum(s.sales) Sales, sum(s.discount) discount 
	from sales_fact s join location_dim l on (s.location_id = l.location_id)
    group by l.country, l.city order by l.country;

## year month sales summary
create table year_month_sales_mv
select d.year, d.month, sum(s.sales) sales, sum(s.profit) profit
	from sales_fact s join dateorder_dim d on (d.dateOrder_id = s.dateOrder_id)
    group by d.year, d.month order by d.year, d.month;
    




select * from product_sales_mv