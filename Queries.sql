##### EXPLORATION #####
### Category Dimension
#1
select c.category, c.subcategory, count(product_id) as product_count from category_dim c
inner join product_dim p on c.category_id = p.category_id
group by c.category, c.subcategory;

### Product Dimension
#2
select p.product_name, c.category, c.subcategory, p.unit_price from category_dim c
inner join product_dim p on c.category_id = p.category_id;

### Location Dimension
#4
select market, count(*) from 
(select distinct market, region from location_dim) a group by a.market;
#5
select region, count(*) from 
(select distinct region, country from location_dim) a group by a.region;
#6
select state, count(city) from 
(select distinct country, state, city from location_dim where country = 'China') a group by a.state;
#7
select city from location_dim where state = 'Ontario' order by city;

### Customer Dimension
#8
select segment, count(*) from customer_dim group by segment;

##### GENERAL SALES DASHBORD #####
#9
select t.sales as today, y.sales as yesterday, (((t.sales-y.sales)/y.sales)*100) difference from 
(select sum(s.sales) sales from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id
where d.date = '2014-12-31') as t join
(select sum(s.sales) sales from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id
where d.date = '2014-12-30') as y;

#10
select t.sales as this_week, y.sales as prev_week, (((t.sales-y.sales)/y.sales)*100) difference from 
(select sum(s.sales) sales from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id
where d.year = 2014 and d.week = 52) as t join
(select sum(s.sales) sales from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id
where d.year = 2014 and d.week = 51) as y;

#11
select t.sales as this_week, y.sales as prev_week, (((t.sales-y.sales)/y.sales)*100) difference from 
(select sum(s.sales) sales from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id
where d.year = 2014 and d.month = 12) as t join
(select sum(s.sales) sales from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id
where d.year = 2014 and d.month = 11) as y;

#12
select sum(s.profit) profit from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id
where d.year = 2014 and d.week = 52;
#13
select sum(s.discount) discount from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id
where d.year = 2014 and d.week = 52;
#14
select sum(s.shipping_cost) shipping from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id
where d.year = 2014 and d.week = 52;
#15
select avg(sales) from sales_fact;
#16
select avg(sales) from order_fact;
#17
select avg(sales) from mv_customer_sales;
#18
select a.market, a.sales this_month, b.sales prev_month from 
(select market, sum(sales) sales from mv_location_time_sales
where year=2014 and month=12 group by market) a 
inner join
(select market, sum(sales) sales from mv_location_time_sales
where year=2014 and month=11 group by market) b on a.market = b.market;

#23
select country, sum(sales) as sales from mv_location_time_sales 
where year=2014 and month=12 
group by country order by sales desc limit 10;

#25
select a.week, sum(a.sales) over(order by week) as S2014, sum(b.sales) over(order by week) as S2013 from 
(select week, sum(sales) sales
from mv_location_time_sales where year = 2014 group by week) a 
inner join 
(select week, sum(sales) sales
from mv_location_time_sales where year = 2013 group by week) b on a.week = b.week;
#32
select c.subcategory, sum(s.quantity) quantity from 
category_dim c inner join product_dim p on c.category_id = p.category_id
inner join sales_fact s on p.product_id = s.product_id 
inner join dateorder_dim d on s.dateOrder_id = d.dateOrder_id
where d.year = 2014 and d.month = 12
group by c.category_id;

#33
select c.category, c.subcategory, sum(sales) sales from 
category_dim c inner join mv_product_sales m on c.category_id = m.category_id 
group by c.category, c.subcategory;

#38
select l.market, sum(s.sales) sales, sum(s.discount) discount from 
(select * from category_dim where category = 'Furniture') c 
inner join product_dim p on c.category_id = p.category_id
inner join sales_fact s on p.product_id = s.product_id 
inner join location_dim l on s.location_id = l.location_id
group by l.market;

#39
select b.product_name, b.product_name, b.mname, b.month, b.quantity from 
(select p.product_id, p.product_name, sum(s.quantity) as quantity from product_dim p 
inner join sales_fact s on p.product_id = s.product_id 
inner join dateorder_dim d on s.dateOrder_id = d.dateOrder_id
where d.year = 2014 and p.category_id in (select category_id from category_dim where subcategory = 'Labels') 
group by p.product_id order by quantity desc limit 100) a inner join 

(select p.product_id, p.product_name, monthname(d.date) mname, d.month, sum(s.quantity) as quantity from product_dim p 
inner join sales_fact s on p.product_id = s.product_id 
inner join dateorder_dim d on s.dateOrder_id = d.dateOrder_id
where d.year = 2014 and p.category_id in (select category_id from category_dim where subcategory = 'Labels') 
group by p.product_id, d.month order by d.month) b on a.product_id = b.product_id;

select d.year, monthname(d.date) mname, sum(s.quantity) as quantity from 
product_dim p 
inner join sales_fact s on p.product_id = s.product_id 
inner join dateorder_dim d on s.dateOrder_id = d.dateOrder_id
where p.category_id = (select category_id from category_dim where subcategory = 'Labels')
group by d.year, d.month
order by d.year, d.month


