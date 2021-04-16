from django.http import HttpResponse
from django.shortcuts import render
from bokeh.plotting import figure, from_networkx
from bokeh.embed import components

from bokeh.layouts import column, row, gridplot
from bokeh.palettes import Category20c, Spectral10, Spectral4
from bokeh.transform import cumsum, factor_cmap, dodge
from bokeh.models import ColumnDataSource
from bokeh.models import (BoxSelectTool, Circle, EdgesAndLinkedNodes, HoverTool,
                          MultiLine, NodesAndLinkedEdges, Plot, Range1d, TapTool,)
from math import pi
import mysql.connector
import pandas as pd

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1214",
    database="biva"
    )

# Create your views here.

def home(request):
    #### View on Cards_________________________________________________________________________________
    ## 9
    mycursor.execute("select t.sales as today, y.sales as yesterday, format((((t.sales-y.sales)/y.sales)*100), 1) difference from \
    (select sum(s.sales) sales from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id \
    where d.date = (select max(date) from dateorder_dim)) as t join \
    (select sum(s.sales) sales from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id \
    where d.date = (select max(date)-1 from dateorder_dim)) as y;")
    df = pd.DataFrame(mycursor.fetchall())
    today = df[0][0] #sales
    yesterday = df[1][0]
    percentage_diff = df[2][0]

    ## 10
    mycursor.execute("select format(t.sales,2) as this_week, format(y.sales,2) as prev_week, format((((t.sales-y.sales)/y.sales)*100),2) difference from \
    (select sum(s.sales) sales from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id \
    where d.year = (select max(year) from dateorder_dim) and d.week = 52) as t join \
    (select sum(s.sales) sales from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id \
    where d.year = (select max(year) from dateorder_dim) and d.week = 51) as y;")
    df = pd.DataFrame(mycursor.fetchall())
    this_week = df[0][0] #sales
    prev_week = df[1][0]
    percentage_diff = df[2][0]

    ## 11
    mycursor.execute("select format(t.sales,2) as this_month, format(y.sales,2) as prev_month, format((((t.sales-y.sales)/y.sales)*100),2) difference from \
    (select sum(s.sales) sales from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id \
    where d.year = 2014 and d.month = 12) as t join \
    (select sum(s.sales) sales from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id \
    where d.year = 2014 and d.month = 11) as y;")
    df = pd.DataFrame(mycursor.fetchall())
    this_month = df[0][0] #sales
    prev_month = df[1][0]
    percentage_diff = df[2][0]

    ## 12, 13, 14
    mycursor.execute("select format(sum(s.profit),2) profit, format(sum(s.discount),2) discount, format(sum(s.shipping_cost),2) shipping \
    from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id \
    where d.year = 2014 and d.week = 52;")
    df = pd.DataFrame(mycursor.fetchall())
    week_profit = df[0][0] #this week
    week_discount = df[1][0]
    week_shipping = df[2][0]

    ## 
    #15
    mycursor.execute("select format(avg(sales),2) from sales_fact;")
    df = pd.DataFrame(mycursor.fetchall())
    avg_transaction = df[0][0] #avg transaction size

    #16
    mycursor.execute("select format(avg(sales),2) from order_fact;")
    df = pd.DataFrame(mycursor.fetchall())
    avg_order = df[0][0] #average order size

    #17
    mycursor.execute("select format(avg(sales),2) from mv_customer_sales;")
    df = pd.DataFrame(mycursor.fetchall())
    avg_value = df[0][0] #average customer value

    #18
    

    first_graph = "Chal Para"
    return HttpResponse(first_graph)


def category(request):
    mycursor = mydb.cursor()
    
    #Pie chart to show all regions and measuring country instances in them
    mycursor.execute("select region, count(*) from (select distinct region, country from location_dim) a group by a.region;")
    df = pd.DataFrame(mycursor.fetchall())
    df = df.rename(columns = {0:'region', 1:'count'})

    
    script, div = components(plot)
    return render(request, 'category.html', {'script':script, 'div':div, 'script2':script, 'div2':div})


def product(request):
    first_graph = "Product wise performance"
    return HttpResponse(first_graph)

def customer(request):
    first_graph = "Customer Wise Performance"
    return HttpResponse(first_graph)

def returns(request):
    first_graph = "Returns Data"
    return HttpResponse(first_graph)

def graph(request):
    first_graph = "Network Graph"
    return HttpResponse(first_graph)