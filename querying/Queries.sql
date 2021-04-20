##### EXPLORATION #####
### Category Dimension
#1
select c.category, c.subcategory, count(product_id) as product_count from category_dim c
inner join product_dim p on c.category_id = p.category_id
group by c.category, c.subcategory;

#2 Product Dimension
select p.product_name, c.category, c.subcategory, p.unit_price from category_dim c
inner join product_dim p on c.category_id = p.category_id;

### Location Dimension
#3 Location Hierarchies
select 'market','region','country','state','city';
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
select format(t.sales,2) as today, format(y.sales,2) as yesterday, format((((t.sales-y.sales)/y.sales)*100), 1) difference from 
(select sum(s.sales) sales from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id
where d.date = (select max(date) from dateorder_dim)) as t join
(select sum(s.sales) sales from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id
where d.date = (select max(date)-1 from dateorder_dim)) as y;

#10
select format(t.sales,2) as this_week, format(y.sales,2) as prev_week, format((((t.sales-y.sales)/y.sales)*100),2) difference from 
(select sum(s.sales) sales from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id
where d.year = (select max(year) from dateorder_dim) and d.week = 52) as t join
(select sum(s.sales) sales from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id
where d.year = (select max(year) from dateorder_dim) and d.week = 51) as y;

#11
select format(t.sales,2) as this_month, format(y.sales,2) as prev_month, format((((t.sales-y.sales)/y.sales)*100),2) difference from 
(select sum(s.sales) sales from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id
where d.year = 2014 and d.month = 12) as t join
(select sum(s.sales) sales from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id
where d.year = 2014 and d.month = 11) as y;

#12 #13 #14
select format(sum(s.profit),2) profit, format(sum(s.discount),2) discount, format(sum(s.shipping_cost),2) shipping 
from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id
where d.year = 2014 and d.week = 52;

#15
select format(avg(sales),2) from sales_fact;
#16
select format(avg(sales),2) from order_fact;
#17
select format(avg(sales),2) from mv_customer_sales;

#18
select a.market, round(a.sales, 2) this_month, round(b.sales, 2) prev_month from 
(select market, sum(sales) sales from mv_location_time_sales
where year=2014 and month=12 group by market) a 
inner join
(select market, sum(sales) sales from mv_location_time_sales
where year=2014 and month=11 group by market) b on a.market = b.market;
#19
select cd.category, sum(pj.quantity) quantity from category_dim cd
inner join pj_sales_product_date pj on cd.category_id = pj.category_id
where pj.year = (select max(year) from pj_sales_product_date) 
and pj.month = (select max(month) from pj_sales_product_date)
group by cd.category;

#20
select convert(total.year,char) year, total.total_customers, newc.new_customers from 
(select b.year, count(*) as total_customers from (
select distinct dd.year, od.customer_id from order_fact od
inner join dateorder_dim dd on od.dateOrder_id = dd.dateOrder_id) b
group by year) total
inner join 
(select a.year, count(*) as new_customers from (
select distinct dd.year, ordf.customer_id from order_fact ordf
inner join dateorder_dim dd on dd.dateOrder_id = ordf.dateOrder_id
where dd.year = 2011
union
select distinct dd.year, ordf.customer_id from order_fact ordf
inner join dateorder_dim dd on dd.dateOrder_id = ordf.dateOrder_id
where dd.year = 2012
and ordf.customer_id not in (
select distinct ordf.customer_id from order_fact ordf
inner join dateorder_dim dd on dd.dateOrder_id = ordf.dateOrder_id
where dd.year = 2011)
union
select distinct dd.year, ordf.customer_id from order_fact ordf
inner join dateorder_dim dd on dd.dateOrder_id = ordf.dateOrder_id
where dd.year = 2013
and ordf.customer_id not in (
select distinct ordf.customer_id from order_fact ordf
inner join dateorder_dim dd on dd.dateOrder_id = ordf.dateOrder_id
where dd.year = 2011 or dd.year = 2012)
union
select distinct dd.year, ordf.customer_id from order_fact ordf
inner join dateorder_dim dd on dd.dateOrder_id = ordf.dateOrder_id
where dd.year = 2014
and ordf.customer_id not in (
select distinct ordf.customer_id from order_fact ordf
inner join dateorder_dim dd on dd.dateOrder_id = ordf.dateOrder_id
where dd.year != 2014)) a
group by year) newc on total.year = newc.year;

#21
select a.month, ((a.returns/b.total)*100) percentage_returns from
(select monthname(dd.date) month, count(*) returns from order_fact od 
inner join dateorder_dim dd on dd.dateOrder_id = od.dateOrder_id
where od.returned = 1 and dd.year = 2014
group by month order by dd.month) a
inner join 
(select monthname(dd.date) month, count(*) total from order_fact od 
inner join dateorder_dim dd on dd.dateOrder_id = od.dateOrder_id
where dd.year = 2014
group by month order by dd.month) b on a.month = b.month;

#22
select monthname(date) monthname, segment, sum(sales) from pj_sales_customer_date
where year = (select max(year) from pj_sales_customer_date)
group by month, segment order by month;

#23
select country, convert(sum(profit),signed) as profit from mv_location_time_sales 
where year=2014 and month=12 
group by country order by profit desc limit 10;

#24
select product_name, convert(sum(quantity),signed) as quantity from pj_sales_product_date
where year = (select max(year) from pj_sales_customer_date)
and week = (select max(week) from pj_sales_customer_date where 
			year = (select max(year) from pj_sales_customer_date))
group by product_id order by quantity desc limit 10;

#25
select c.*, (c.S2014 - c.S2013) diff from (
select a.week, sum(a.sales) over(order by week) as S2014, sum(b.sales) over(order by week) as S2013 from 
(select week, sum(sales) sales
from mv_location_time_sales where year = 2014 group by week) a 
inner join 
(select week, sum(sales) sales
from mv_location_time_sales where year = 2013 group by week) b on a.week = b.week) c;

##### Dimension Analysis Reports #####
## Category Dimension Report ##
#26
select a.week, sum(a.sales) over(order by week) as Technology, 
sum(b.sales) over(order by week) as Office_Supplies, 
sum(c.sales) over(order by week) as Furniture from 
(select category, week, sum(sales) sales from pj_sales_category_date
where year = (select max(year) from pj_sales_category_date) 
and category = 'Technology'
group by category, week
order by category, week) a
inner join
(select category, week, sum(sales) sales from pj_sales_category_date
where year = (select max(year) from pj_sales_category_date) 
and category = 'Office Supplies'
group by category, week
order by category, week) b on a.week = b.week 
inner join
(select category, week, sum(sales) sales from pj_sales_category_date
where year = (select max(year) from pj_sales_category_date) 
and category = 'Furniture'
group by category, week
order by category, week) c on c.week = b.week;

#27
select category, year, format(sum(sales),2) sales, format(sum(profit),2) revenue from pj_sales_category_date
group by category, year
order by category, year;
#28
select a.*, b.sales_prev, format((((a.sales_now-b.sales_prev)/b.sales_prev)*100),2) percent_diff from
(select category, format(sum(sales),2) sales_now from pj_sales_category_date pj
where year = 2014 and pj.month = 12 group by category) a
inner join
(select category, format(sum(sales),2) sales_prev from pj_sales_category_date pj
where year = 2014 and pj.month = 11 group by category) b on a.category = b.category;

select a.*, b.profit_prev, format((((a.profit_now-b.profit_prev)/b.profit_prev)*100),2) percent_diff from
(select category, format(sum(profit),2) profit_now from pj_sales_category_date pj
where year = 2014 and pj.month = 12 group by category) a
inner join
(select category, format(sum(profit),2) profit_prev from pj_sales_category_date pj
where year = 2014 and pj.month = 11 group by category) b on a.category = b.category;

#29
select category, convert(sum(sales),signed) this_quarter_sales from pj_sales_category_date
where year = 2014 and quarter = 4 group by category;
#30
select concat(concat(category, ', '), subcategory)subcategory, convert(sum(sales),signed) this_quarter_sales from pj_sales_category_date
where year = 2014 and quarter = 4 group by category, subcategory;
#31
select category, sum(quantity) units_sold_this_month from pj_sales_category_date
where year = 2014 and month = 12 group by category;
#32
select c.subcategory, sum(s.quantity) quantity from 
category_dim c inner join product_dim p on c.category_id = p.category_id
inner join sales_fact s on p.product_id = s.product_id 
inner join dateorder_dim d on s.dateOrder_id = d.dateOrder_id
where d.year = 2014 and d.month = 12
group by c.category_id order by c.category_id;

#33
select c.category, c.subcategory, sum(sales) sales from 
category_dim c inner join mv_product_sales m on c.category_id = m.category_id 
group by c.category, c.subcategory;

## Considering category 'Furniture'
#34
select c.category, count(*) prodcuts_count, avg(p.unit_price) average_product_price from category_dim c
inner join product_dim p on p.category_id = c.category_id
where c.category = 'Furniture'
group by c.category;

#35
select a.day, sum(a.sales) over(order by day) as sales_now, 
sum(b.sales) over(order by day) as sales_prev from
(select day, sum(sales) sales from pj_sales_category_date
where year = (select max(year) from pj_sales_category_date)
and month = 11 
and category = 'Furniture'
group by category, day
order by category, day) a 
left join
(select day, sum(sales) sales from pj_sales_category_date
where year = (select max(year) from pj_sales_category_date)
and month = 12 
and category = 'Furniture'
group by category, day
order by category, day) b on a.day = b.day;

#36
select a.month month_q1, a.revenue revenue_q1, 
b.month month_q2, b.revenue revenue_q2, 
c.month month_q3, b.revenue revenue_q3,
a.month month_q4, a.revenue revenue_q4 from  
(select mod(pj.month,3) m, monthname(date) month, sum(profit) revenue from pj_sales_category_date pj
where  year = 2014 and quarter = 1 and category = 'Furniture' 
group by pj.month order by pj.month) a 
inner join 
(select mod(pj.month,3) m, monthname(date) month, sum(profit) revenue from pj_sales_category_date pj
where  year = 2014 and quarter = 2 and category = 'Furniture'
group by pj.month order by pj.month) b on a.m = b.m 
inner join 
(select mod(pj.month,3) m, monthname(date) month, sum(profit) revenue from pj_sales_category_date pj
where  year = 2014 and quarter = 3 and category = 'Furniture'
group by pj.month order by pj.month) c on b.m = c.m 
inner join 
(select mod(pj.month,3) m, monthname(date) month, sum(profit) revenue from pj_sales_category_date pj
where  year = 2014 and quarter = 4 and category = 'Furniture'
group by pj.month order by pj.month) d on c.m = d.m; 

#37
select a.mname month, a.quantity this_year, b.quantity prev_year from
(select monthname(date) mname, sum(quantity) quantity from pj_sales_category_date
where year = (select max(year) from pj_sales_category_date)
and category = 'Furniture' 
group by month order by month) a 
inner join 
(select monthname(date) mname, sum(quantity) quantity from pj_sales_category_date
where year = (select max(year)-1 from pj_sales_category_date)
and category = 'Furniture' 
group by month order by month) b on a.mname = b.mname;

#38
select l.market, sum(s.sales) sales, sum(s.discount) discount from 
(select * from category_dim where category = 'Furniture') c 
inner join product_dim p on c.category_id = p.category_id
inner join sales_fact s on p.product_id = s.product_id 
inner join location_dim l on s.location_id = l.location_id
group by l.market;

## Considering category 'Furnishings'
#39
select year, month, sum(quantity) quantity from pj_sales_category_date
group by year, month order by year, month;

#40
select c.subcategory, count(*) prodcuts_count, avg(p.unit_price) average_product_price from category_dim c
inner join product_dim p on p.category_id = c.category_id
where c.subcategory = 'Furnishings'
group by c.subcategory;

#41
select a.day, sum(a.sales) over(order by day) as sales_now, 
sum(b.sales) over(order by day) as sales_prev from
(select day, sum(sales) sales from pj_sales_category_date
where year = (select max(year) from pj_sales_category_date)
and month = 11 
and subcategory = 'Furnishings'
group by subcategory, day
order by subcategory, day) a 
left join
(select day, sum(sales) sales from pj_sales_category_date
where year = (select max(year) from pj_sales_category_date)
and month = 12 
and subcategory = 'Furnishings'
group by subcategory, day
order by subcategory, day) b on a.day = b.day;

#42
select a.month month_q1, a.revenue revenue_q1, 
b.month month_q2, b.revenue revenue_q2, 
c.month month_q3, b.revenue revenue_q3,
a.month month_q4, a.revenue revenue_q4 from  
(select mod(pj.month,3) m, monthname(date) month, sum(profit) revenue from pj_sales_category_date pj
where  year = 2014 and quarter = 1 and subcategory = 'Furnishings' 
group by pj.month order by pj.month) a 
inner join 
(select mod(pj.month,3) m, monthname(date) month, sum(profit) revenue from pj_sales_category_date pj
where  year = 2014 and quarter = 2 and subcategory = 'Furnishings'
group by pj.month order by pj.month) b on a.m = b.m 
inner join 
(select mod(pj.month,3) m, monthname(date) month, sum(profit) revenue from pj_sales_category_date pj
where  year = 2014 and quarter = 3 and subcategory = 'Furnishings'
group by pj.month order by pj.month) c on b.m = c.m 
inner join 
(select mod(pj.month,3) m, monthname(date) month, sum(profit) revenue from pj_sales_category_date pj
where  year = 2014 and quarter = 4 and subcategory = 'Furnishings'
group by pj.month order by pj.month) d on c.m = d.m; 

#43
select a.mname month, a.quantity this_year, b.quantity prev_year from
(select monthname(date) mname, sum(quantity) quantity from pj_sales_category_date
where year = (select max(year) from pj_sales_category_date)
and subcategory = 'Furnishings' 
group by month order by month) a 
inner join 
(select monthname(date) mname, sum(quantity) quantity from pj_sales_category_date
where year = (select max(year)-1 from pj_sales_category_date)
and subcategory = 'Furnishings' 
group by month order by month) b on a.mname = b.mname;

#44
select l.market, sum(s.sales) sales, sum(s.discount) discount from 
(select * from category_dim where subcategory = 'Furnishings') c 
inner join product_dim p on c.category_id = p.category_id
inner join sales_fact s on p.product_id = s.product_id 
inner join location_dim l on s.location_id = l.location_id
group by l.market;
#45
(select pj.year, l.country, sum(quantity) quantity from pj_sales_category_date pj 
inner join location_dim l on pj.location_id = l.location_id 
where pj.subcategory = 'Furnishings' and pj.year = 2011 
group by l.country order by quantity desc limit 10) 
union
(select pj.year, l.country, sum(quantity) quantity from pj_sales_category_date pj 
inner join location_dim l on pj.location_id = l.location_id 
where pj.subcategory = 'Furnishings' and pj.year = 2012 
group by l.country order by quantity desc limit 10) 
union
(select pj.year, l.country, sum(quantity) quantity from pj_sales_category_date pj 
inner join location_dim l on pj.location_id = l.location_id 
where pj.subcategory = 'Furnishings' and pj.year = 2013 
group by l.country order by quantity desc limit 10) 
union
(select pj.year, l.country, sum(quantity) quantity from pj_sales_category_date pj 
inner join location_dim l on pj.location_id = l.location_id 
where pj.subcategory = 'Furnishings' and pj.year = 2014 
group by l.country order by quantity desc limit 10);

## Project Dimension Report ##
#46
select product_name, weekday from pj_sales_product_date 
where product_id in 
(select product_id from
(select product_id, count(*) count from pj_sales_product_date
group by product_id order by count desc limit 10) a);

#47

#48
#49
#50
#51
#52
#53
#54
#55
#56
#57
#58
#59
#60

##____________________________________________________________##
## Product combinations that were sold more than 1 times together?
select product1, product2, counts from 
(select a.product_name product1, b.product_name product2, count(*) counts 
from (select s.order_id, p.product_name from sales_fact s 
inner join product_dim p on s.product_id = p.product_id) a 
inner join (select s.order_id, p.product_name from sales_fact s 
inner join product_dim p on s.product_id = p.product_id) b on a.order_id = b.order_id 
where a.product_name != b.product_name
group by a.product_name, b.product_name
order by counts desc) b 
where counts > 1;


## Products that were sold with Product X
select product1, product2, counts from 
(select a.product_name product1, b.product_name product2, count(*) counts 
from (select s.order_id, p.product_name from sales_fact s 
inner join product_dim p on s.product_id = p.product_id) a 
inner join (select s.order_id, p.product_name from sales_fact s 
inner join product_dim p on s.product_id = p.product_id) b on a.order_id = b.order_id 
where a.product_name != b.product_name
group by a.product_name, b.product_name
order by counts desc) b 
where product1 = 'Staples' and counts>1;

## Product combinations that were sold more than 1 times together
## and their combined profit (profit is negative if any discount was offered)
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
group by a.product_name, b.product_name) c on c.product1 = p.product1 and c.product2 = p.product2 
where c.counts > 1
order by c.counts desc;

## Products that were sold with Product X more than one time
## and their combined profit
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
group by a.product_name, b.product_name) c on c.product1 = p.product1 and c.product2 = p.product2
where c.counts > 1 and p.product1 = 'Staples'
order by c.counts desc;

## using the materialized view
select * from mv_product_association
                  where counts > 1 and product1 = 'Staples';
select * from mv_product_association where product1 = 'Staples' and counts>1 
order by counts desc;
select * from mv_product_association where counts>1 order by counts desc;

##____________________________________________________________________________________________
## Data Mining Datasets
select ld.region, ld.country, cd.segment, c.subcategory, pd.product_id, sum(quantity)/4 quantity, sum(profit)/4 profit
from customer_dim cd inner join sales_fact sf on cd.customer_id = sf.customer_id
inner join location_dim ld on ld.location_id = sf.location_id
inner join product_dim pd on pd.product_id = sf.product_id
inner join category_dim c on c.category_id = pd.category_id
group by ld.country, cd.segment, c.subcategory, pd.product_id
order by profit desc;

select min(quantity), avg(quantity), max(quantity), min(profit), avg(profit), max(profit) from 
(select ld.region, ld.country, cd.segment, c.subcategory, pd.product_id, sum(quantity)/4 quantity, sum(profit)/4 profit
from customer_dim cd inner join sales_fact sf on cd.customer_id = sf.customer_id
inner join location_dim ld on ld.location_id = sf.location_id
inner join product_dim pd on pd.product_id = sf.product_id
inner join category_dim c on c.category_id = pd.category_id
group by ld.country, cd.segment, c.subcategory, pd.product_id
order by profit desc) a;

## Classified Results
select ld.region, ld.country, cd.segment, c.subcategory, pd.product_id, 
if((sum(profit)/4)<0,'Loss', if((sum(profit)/4)<1000,'GP','HP')) profit, 
if((sum(quantity)/4)<10,'Low','Good') quantity
from customer_dim cd inner join sales_fact sf on cd.customer_id = sf.customer_id
inner join location_dim ld on ld.location_id = sf.location_id
inner join product_dim pd on pd.product_id = sf.product_id
inner join category_dim c on c.category_id = pd.category_id 
group by ld.country, cd.segment, c.subcategory, pd.product_id;
