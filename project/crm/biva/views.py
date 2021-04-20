from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User,auth

import networkx as nx
from .models import Cards
from bokeh.plotting import figure, from_networkx
from bokeh.embed import components
from bokeh.layouts import column, row, gridplot
from bokeh.palettes import Category20c, Spectral10, Spectral4, Spectral5
from bokeh.transform import cumsum, factor_cmap, dodge
from bokeh.models import ColumnDataSource,  LabelSet
from bokeh.models import (BoxSelectTool, Circle, EdgesAndLinkedNodes, HoverTool,
                          MultiLine, NodesAndLinkedEdges, Plot, Range1d, TapTool,)
from math import pi
import mysql.connector
import pandas as pd

#sql connector
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="biva"
    )
mycursor =  mydb.cursor()


# Create your views here.
def index(request): #Login page
    
    return render(request,'index.html')

def logout(request): 
    auth.logout(request)
    return redirect('/')
def register(request):
    if request.method == 'POST':
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        usename = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        print(password1,password2)
        if(password1 == password2):
            if User.objects.filter(username = usename).exists():
                messages.info(request,'Username taken')
                return render(request,'signup.html')
            elif User.objects.filter(email = email).exists():
                messages.info(request,'Email already taken')
                return render(request,'signup.html')
            else:
                user =  User.objects.create_user(username = usename,
                password = password1,
                email=email,
                first_name = firstname,
                last_name = lastname)
                user.save()
                return redirect('/')
        else:
            messages.info(request,'Passwords not matching')
            return render(request,'signup.html')
    messages.info(request,'Register a new user')
    return render(request,'signup.html')

def dashboard(request):
    
    #### View on Cards_________________________________________________________________________________
    ## 9
    # mycursor.execute("select t.sales as today, y.sales as yesterday, format((((y.sales-t.sales)/y.sales)*100), 1) difference from \
    mycursor.execute("select format(t.sales,2) as today, format(y.sales,2) as yesterday, format((((t.sales-y.sales)/y.sales)*100), 1) difference from \
    (select sum(s.sales) sales from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id \
    where d.date = (select max(date) from dateorder_dim)) as t join \
    (select sum(s.sales) sales from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id \
    where d.date = (select max(date)-1 from dateorder_dim)) as y;")
    df = pd.DataFrame(mycursor.fetchall())
    dashcard1 = Cards()
    dashcard1.assign("Daily",df[0][0],df[1][0],df[2][0])

    ## 10
    mycursor.execute("select format(t.sales,2) as this_week, format(y.sales,2) as prev_week, format((((t.sales-y.sales)/y.sales)*100),2) difference from \
    (select sum(s.sales) sales from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id \
    where d.year = (select max(year) from dateorder_dim) and d.week = 52) as t join \
    (select sum(s.sales) sales from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id \
    where d.year = (select max(year) from dateorder_dim) and d.week = 51) as y;")
    df = pd.DataFrame(mycursor.fetchall())
    # this_week = df[0][0] #sales
    # prev_week = df[1][0]
    # percentage_diff = df[2][0]
    dashcard2 = Cards()
    dashcard2.assign("Weekly",df[0][0],df[1][0],df[2][0])

    ## 11
    mycursor.execute("select format(t.sales,2) as this_month, format(y.sales,2) as prev_month, format((((t.sales-y.sales)/y.sales)*100),2) difference from \
    (select sum(s.sales) sales from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id \
    where d.year = 2014 and d.month = 12) as t join \
    (select sum(s.sales) sales from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id \
    where d.year = 2014 and d.month = 11) as y;")
    df = pd.DataFrame(mycursor.fetchall())
    # this_month = df[0][0] #sales
    # prev_month = df[1][0]
    # percentage_diff = df[2][0]
    dashcard3 = Cards()
    dashcard3.assign("Monthly",df[0][0],df[1][0],df[2][0])

    ## 12, 13, 14
    mycursor.execute("select format(sum(s.profit),2) profit, format(sum(s.discount),2) discount, format(sum(s.shipping_cost),2) shipping \
    from sales_fact s inner join dateorder_dim d on d.dateOrder_id = s.dateOrder_id \
    where d.year = 2014 and d.week = 52;")
    df = pd.DataFrame(mycursor.fetchall())
    # week_profit = df[0][0] #this week
    # week_discount = df[1][0]
    # week_shipping = df[2][0]
    dashcard4 = Cards()
    dashcard4.assign("Weekly Stats",df[0][0],df[1][0],df[2][0]) 

    ## 
    dashcard5 = Cards()
    dashcard5.type = "Average Stats"
    #15
    mycursor.execute("select format(avg(sales),2) from sales_fact;")
    df = pd.DataFrame(mycursor.fetchall())
    # avg_transaction = df[0][0] #avg transaction size
    dashcard5.now = df[0][0] # average transaction size

    #16
    mycursor.execute("select format(avg(sales),2) from order_fact;")
    df = pd.DataFrame(mycursor.fetchall())
    # avg_order = df[0][0] #average order size
    dashcard5.previous = df[0][0] # average order size


    #17
    mycursor.execute("select format(avg(sales),2) from mv_customer_sales;")
    df = pd.DataFrame(mycursor.fetchall())
    # avg_value = df[0][0] #average customer value
    dashcard5.percentage = df[0][0] # average customer value


    #### View on bars_________________________________________________________________________________
    #18
    mycursor.execute("select a.market, round(a.sales, 2) this_month, round(b.sales, 2) prev_month from \
    (select market, sum(sales) sales from mv_location_time_sales \
    where year=2014 and month=12 group by market) a \
    inner join \
    (select market, sum(sales) sales from mv_location_time_sales \
    where year=2014 and month=11 group by market) b on a.market = b.market;")
    df = pd.DataFrame(mycursor.fetchall())
    df = df.rename(columns = {0:'0', 1:'1', 2:'2'}) # renaming dataframe columns
    p = figure(x_range = df['0'], 
                plot_width=400, 
                plot_height=400,
                title="Current and Previous month sales by market", 
                y_axis_label = "Sales Amount", 
                tools="box_select,tap,save,reset", 
                tooltips=[("Market", "@0"), ("Dec 2014", "@1"), ("Nov 2014", "@2")])
    p.vbar(x=dodge('0', -0.15, range=p.x_range), 
            top = '1', # y-axis values column of source
            width = 0.3, 
            source = df, 
            line_color="white", 
            color = '#3182bd', 
            fill_alpha = 0.8,
            legend_label='Dec 2014')
    p.vbar(x=dodge('0', +0.15, range=p.x_range), 
            top = '2', # y-axis values column of source
            width = 0.3, 
            source = df, 
            line_color="white", 
            color = '#e6550d', 
            fill_alpha = 0.8,
            legend_label='Nov 2014')
    p.xaxis.axis_label = "Sales in USD"
    #p.xaxis.major_label_orientation = 0.9
    p.x_range.range_padding = 0.05
    p.y_range.start = 0
    p.toolbar.logo = None
    script18, div18 = components(p)
    #------------------------------------------------------
    #19
    mycursor.execute("select cd.category, sum(pj.quantity) quantity from category_dim cd \
    inner join pj_sales_product_date pj on cd.category_id = pj.category_id \
    where pj.year = (select max(year) from pj_sales_product_date) \
    and pj.month = (select max(month) from pj_sales_product_date) \
    group by cd.category;")
    df = pd.DataFrame(mycursor.fetchall())
    df = df.rename(columns = {0:'0', 1:'1'}) # renaming dataframe columns

    p = figure(x_range = df['0'], 
                plot_width=300, 
                plot_height=400,
                title="Items Sold per Category this Month", 
                y_axis_label = "Quantity Sold", 
                x_axis_label = "Category", 
                tools="box_select,tap,save,reset", 
                tooltips=[("Category", "@0"), ("Quantity", "@1")])
    p.vbar(x=dodge('0', 0, range=p.x_range), 
            top = '1', # y-axis values column of source
            width = 0.5, 
            source = df, 
            line_color="white", 
            color = '#3182bd', 
            fill_alpha = 0.8)
    p.x_range.range_padding = 0.05
    p.y_range.start = 0
    p.toolbar.logo = None
    script19, div19 = components(p)
    #------------------------------------------------------
    #20
    mycursor.execute("select convert(total.year,char) year, total.total_customers, newc.new_customers from \
    (select b.year, count(*) as total_customers from ( \
    select distinct dd.year, od.customer_id from order_fact od \
    inner join dateorder_dim dd on od.dateOrder_id = dd.dateOrder_id) b \
    group by year) total \
    inner join \
    (select a.year, count(*) as new_customers from ( \
    select distinct dd.year, ordf.customer_id from order_fact ordf \
    inner join dateorder_dim dd on dd.dateOrder_id = ordf.dateOrder_id \
    where dd.year = 2011 \
    union \
    select distinct dd.year, ordf.customer_id from order_fact ordf \
    inner join dateorder_dim dd on dd.dateOrder_id = ordf.dateOrder_id \
    where dd.year = 2012 \
    and ordf.customer_id not in ( \
    select distinct ordf.customer_id from order_fact ordf \
    inner join dateorder_dim dd on dd.dateOrder_id = ordf.dateOrder_id \
    where dd.year = 2011) \
    union \
    select distinct dd.year, ordf.customer_id from order_fact ordf \
    inner join dateorder_dim dd on dd.dateOrder_id = ordf.dateOrder_id \
    where dd.year = 2013 \
    and ordf.customer_id not in ( \
    select distinct ordf.customer_id from order_fact ordf \
    inner join dateorder_dim dd on dd.dateOrder_id = ordf.dateOrder_id \
    where dd.year = 2011 or dd.year = 2012) \
    union \
    select distinct dd.year, ordf.customer_id from order_fact ordf \
    inner join dateorder_dim dd on dd.dateOrder_id = ordf.dateOrder_id \
    where dd.year = 2014 \
    and ordf.customer_id not in ( \
    select distinct ordf.customer_id from order_fact ordf \
    inner join dateorder_dim dd on dd.dateOrder_id = ordf.dateOrder_id \
    where dd.year != 2014)) a \
    group by year) newc on total.year = newc.year;")
    df = pd.DataFrame(mycursor.fetchall())
    df = df.rename(columns = {0:'0', 1:'1', 2:'2'}) # renaming dataframe columns
    p = figure(x_range = df['0'], 
                plot_width=400, 
                plot_height=400,
                title="Total and New Customers Every Year", 
                y_axis_label = "Customers", 
                x_axis_label = "Years",
                tools="box_select,tap,save,reset", 
                tooltips=[("Year", "@0"), ("Total Customers", "@1"), ("New Customers", "@2")])
    p.vbar(x=dodge('0', -0.15, range=p.x_range), 
            top = '1', # y-axis values column of source
            width = 0.3, 
            source = df, 
            line_color="white", 
            color = '#3182bd', 
            fill_alpha = 0.8,
            legend_label='Total Customers')
    p.vbar(x=dodge('0', +0.15, range=p.x_range), 
            top = '2', # y-axis values column of source
            width = 0.3, 
            source = df, 
            line_color="white", 
            color = '#e6550d', 
            fill_alpha = 0.9,
            legend_label='New Customers')
    #p.xaxis.major_label_orientation = 0.9
    p.x_range.range_padding = 0.05
    p.y_range.start = 0
    p.toolbar.logo = None
    script20, div20 = components(p)

    #------------------------------------------------------
    #21
    mycursor.execute("select a.month, ((a.returns/b.total)*100) percentage_returns from \
    (select monthname(dd.date) month, count(*) returns from order_fact od \
    inner join dateorder_dim dd on dd.dateOrder_id = od.dateOrder_id \
    where od.returned = 1 and dd.year = 2014 \
    group by month order by dd.month) a \
    inner join \
    (select monthname(dd.date) month, count(*) total from order_fact od \
    inner join dateorder_dim dd on dd.dateOrder_id = od.dateOrder_id \
    where dd.year = 2014 \
    group by month order by dd.month) b on a.month = b.month;")
    df = pd.DataFrame(mycursor.fetchall())
    df = df.rename(columns = {0:'0', 1:'1'}) # renaming dataframe columns

    p = figure(x_range = df['0'], 
                plot_width=500, 
                plot_height=400,
                title="Percentage of Total Orders Returned this Year", 
                y_axis_label = "% Returns", 
                x_axis_label = "Months", 
                tools="box_select,tap,save,reset", 
                tooltips=[("Month", "@0"), ("% return", "@1")])
    p.vbar(x=dodge('0', 0, range=p.x_range), 
            top = '1', # y-axis values column of source
            width = 0.5, 
            source = df, 
            line_color="white", 
            color = '#3182bd', 
            fill_alpha = 0.9)
    p.xaxis.major_label_orientation = 0.9
    p.x_range.range_padding = 0.05
    p.y_range.start = 0
    p.toolbar.logo = None 
    script21, div21 = components(p)
    
    #------------------------------------------------------
    #22
    mycursor.execute("select monthname(date) monthname, segment, sum(sales) from pj_sales_customer_date \
    where year = (select max(year) from pj_sales_customer_date) \
    group by month, segment order by month;")
    df = pd.DataFrame(mycursor.fetchall())
    df = df.rename(columns = {0:'month', 1:'segment', 2: 'sales'})

    group = df.groupby(by=['segment', 'month'])
    index_cmap = factor_cmap('segment_month', palette=Spectral4, factors=sorted(df.segment.unique()), end=1)

    p = figure(plot_width=800, 
                plot_height=400, 
                x_axis_label = "Segment X Month", 
                y_axis_label = "Sales (x 100,000 USD)", 
                title="Total Monthly sales of Customer Segments", 
                x_range=group, 
                tools="box_select,tap,save,reset", 
                tooltips=[("segment_month: ", "@segment_month"), ("sales: ", "@sales_top")])

    p.vbar(x='segment_month', 
            top='sales_top', width=1, 
            source=group, 
            line_color="white", 
            fill_color=index_cmap)

    p.y_range.start = 0
    p.x_range.range_padding = 0.05
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = 0.8
    p.outline_line_color = 'black'
    p.toolbar.logo = None 
    script22, div22 = components(p)
    #------------------------------------------------------
    #23 pie chart
    mycursor.execute("select country, convert(sum(profit),signed) as profit from mv_location_time_sales \
    where year=2014 and month=12 \
    group by country order by profit desc limit 10;")
    df = pd.DataFrame(mycursor.fetchall())
    df = df.rename(columns = {0:'0', 1:'1'})

    df['angle'] = df['1']/df['1'].sum() *2* pi
    df['color'] = Category20c[len(df)]

    p = figure(plot_height=400,
                plot_width=450,
                title="10 Most Profitable Countries this Month",
                tools="hover,tap,reset,save", 
                tooltips=[("Country", "@0"), ("Profit this Month", "@1")], 
                x_range=(-0.5, 1.0))
    p.wedge(x=0, y=1, 
            radius=0.4, 
            start_angle=cumsum('angle', include_zero=True), 
            end_angle=cumsum('angle'),
            line_color="white", 
            fill_color='color', 
            legend_field='0', 
            source=df)
    p.axis.axis_label=None
    p.axis.visible=False
    p.grid.grid_line_color = None
    p.toolbar.logo = None
    script23, div23 = components(p)
    
    # script20, div20 = components(p)
    #------------------------------------------------------
    #24 pie chart
    mycursor.execute("select product_name, convert(sum(quantity),signed) as quantity from pj_sales_product_date \
    where year = (select max(year) from pj_sales_customer_date) \
    and week = (select max(week) from pj_sales_customer_date where \
                year = (select max(year) from pj_sales_customer_date)) \
    group by product_id order by quantity desc limit 10;")
    df = pd.DataFrame(mycursor.fetchall())
    df = df.rename(columns = {0:'0', 1:'1'})

    df['angle'] = df['1']/df['1'].sum() *2* pi
    df['color'] = Category20c[len(df)]

    p = figure(plot_height=400,
                plot_width=650,
                title="10 Most Sold Products this Week",
                tools="hover,save,tap,reset", 
                tooltips=[("Product", "@0"), ("Units Sold", "@1")], 
                x_range=(-0.5, 1.0))
    p.wedge(x=-0.15, y=1, 
            radius=0.3, 
            start_angle=cumsum('angle', include_zero=True), 
            end_angle=cumsum('angle'),
            line_color="white", 
            fill_color='color', 
            legend_field='0', 
            source=df)
    p.axis.axis_label=None
    p.axis.visible=False
    p.grid.grid_line_color = None
    p.toolbar.logo = None 
    script24, div24 = components(p)
    
    #------------------------------------------------------
    #25 
    mycursor.execute("select c.*, (c.S2014 - c.S2013) diff from ( \
    select a.week, sum(a.sales) over(order by week) as S2014, sum(b.sales) over(order by week) as S2013 from \
    (select week, sum(sales) sales \
    from mv_location_time_sales where year = 2014 group by week) a \
    inner join \
    (select week, sum(sales) sales \
    from mv_location_time_sales where year = 2013 group by week) b on a.week = b.week) c;") 
    df = pd.DataFrame(mycursor.fetchall()) 
    df = df.rename(columns = {0:'week', 1:'2014',2:'2013',3:'diff'})

    sc = ColumnDataSource(df)
    p = figure(plot_width=900, plot_height=400, title="Weekly Sales Comparison(This year vs Prev Year)", 
                y_axis_label = "Sales (in Million USD)", 
                x_axis_label = "Week Number",
                tools="box_select,zoom_in,zoom_out,save,reset", 
                tooltips=[("Week: ", "@week"), ("2014: ", "@2014"), ("2013: ", "@2013"), ("Difference: ", "@diff")])

    # add a line renderer
    p.line('week', '2014', source = df, line_width=3, color = '#3182bd', legend_label='2014')
    p.line('week', '2013', source = df, line_width=3, color = '#e6550d', legend_label='2013') 
    p.legend.location = "top_left"
    p.toolbar.logo = None
    script25, div25 = components(p)

    #------------------------------------------------------
    #26
    #------------------------------------------------------
    #27



    #********************************************#
    # dashcards1 = Cards()
    dashcards1 = [dashcard1,dashcard2,dashcard3]
    dashcards2 = [dashcard4,dashcard5]

    divlist =    [div18,div19,div20,div25,div24,div22,div23,div21]
    scriptlist = [script18,script19,script20,script25,script24,script22,script23,script21]
    
    #***************************************************#
    if (request.method == 'POST' ):
        username =  request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username = username,password = password)
        if user is not None:
            auth.login(request,user)
            return render(request,'dashboard.html',
            {'scriptlist':scriptlist, 'divlist':divlist,
            'dashcards1': dashcards1, 'dashcards2':dashcards2,
            'name':"BIVA",'dashboard': True}
            )
        else:
            messages.info(request,'Invalid credentials')
            return redirect('/')
    else:
        return render(request,'dashboard.html',
         {'scriptlist':scriptlist, 'divlist':divlist,
         'dashcards1': dashcards1, 'dashcards2' : dashcards2,
         'name':"Dashbobard",'dashboard': True}
         )

def decision(request):
    return render(request,'decision.html',{'name':"Decision Support",'decision' : True,})
def explore(request):
    return render(request,'decision.html',{'name':"Explore",'explore' : True,})
def graph(request):
    return render(request,'decision.html',{'name':"Graph",'graph' : True,})
def customQuery(request):
    return render(request,'decision.html',{'name':"Custom Query",'query' : True,})


#additional files 


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

    #### View on bars_________________________________________________________________________________
    #18
    mycursor.execute("select a.market, round(a.sales, 2) this_month, round(b.sales, 2) prev_month from \
    (select market, sum(sales) sales from mv_location_time_sales \
    where year=2014 and month=12 group by market) a \
    inner join \
    (select market, sum(sales) sales from mv_location_time_sales \
    where year=2014 and month=11 group by market) b on a.market = b.market;")
    df = pd.DataFrame(mycursor.fetchall())
    df = df.rename(columns = {0:'0', 1:'1', 2:'2'}) # renaming dataframe columns
    p = figure(x_range = df['0'], 
                plot_width=400, 
                plot_height=400,
                title="Current and Previous month sales by market", 
                y_axis_label = "Sales Amount", 
                tools="box_select,zoom_in,zoom_out,reset", 
                tooltips=[("Market", "@0"), ("Dec 2014", "@1"), ("Nov 2014", "@2")])
    p.vbar(x=dodge('0', -0.15, range=p.x_range), 
            top = '1', # y-axis values column of source
            width = 0.3, 
            source = df, 
            line_color="white", 
            color = '#3182bd', 
            fill_alpha = 0.8,
            legend_label='Dec 2014')
    p.vbar(x=dodge('0', +0.15, range=p.x_range), 
            top = '2', # y-axis values column of source
            width = 0.3, 
            source = df, 
            line_color="white", 
            color = '#e6550d', 
            fill_alpha = 0.8,
            legend_label='Nov 2014')
    p.xaxis.axis_label = "Sales in USD"
    #p.xaxis.major_label_orientation = 0.9
    p.x_range.range_padding = 0.05
    p.y_range.start = 0
    p.toolbar.logo = None
    script18, div18 = components(p)
    #====================================================================================================
    #19
    mycursor.execute("select cd.category, sum(pj.quantity) quantity from category_dim cd \
    inner join pj_sales_product_date pj on cd.category_id = pj.category_id \
    where pj.year = (select max(year) from pj_sales_product_date) \
    and pj.month = (select max(month) from pj_sales_product_date) \
    group by cd.category;")
    df = pd.DataFrame(mycursor.fetchall())
    df = df.rename(columns = {0:'0', 1:'1'}) # renaming dataframe columns

    p = figure(x_range = df['0'], 
                plot_width=300, 
                plot_height=400,
                title="Items Sold per Category this Month", 
                y_axis_label = "Quantity Sold", 
                x_axis_label = "Category", 
                tools="box_select,zoom_in,zoom_out,reset", 
                tooltips=[("Category", "@0"), ("Quantity", "@1")])
    p.vbar(x=dodge('0', 0, range=p.x_range), 
            top = '1', # y-axis values column of source
            width = 0.5, 
            source = df, 
            line_color="white", 
            color = '#3182bd', 
            fill_alpha = 0.8)
    p.x_range.range_padding = 0.05
    p.y_range.start = 0
    p.toolbar.logo = None
    script19, div19 = components(p)
    #====================================================================================================
    #20
    mycursor.execute("select convert(total.year,char) year, total.total_customers, newc.new_customers from \
    (select b.year, count(*) as total_customers from ( \
    select distinct dd.year, od.customer_id from order_fact od \
    inner join dateorder_dim dd on od.dateOrder_id = dd.dateOrder_id) b \
    group by year) total \
    inner join \
    (select a.year, count(*) as new_customers from ( \
    select distinct dd.year, ordf.customer_id from order_fact ordf \
    inner join dateorder_dim dd on dd.dateOrder_id = ordf.dateOrder_id \
    where dd.year = 2011 \
    union \
    select distinct dd.year, ordf.customer_id from order_fact ordf \
    inner join dateorder_dim dd on dd.dateOrder_id = ordf.dateOrder_id \
    where dd.year = 2012 \
    and ordf.customer_id not in ( \
    select distinct ordf.customer_id from order_fact ordf \
    inner join dateorder_dim dd on dd.dateOrder_id = ordf.dateOrder_id \
    where dd.year = 2011) \
    union \
    select distinct dd.year, ordf.customer_id from order_fact ordf \
    inner join dateorder_dim dd on dd.dateOrder_id = ordf.dateOrder_id \
    where dd.year = 2013 \
    and ordf.customer_id not in ( \
    select distinct ordf.customer_id from order_fact ordf \
    inner join dateorder_dim dd on dd.dateOrder_id = ordf.dateOrder_id \
    where dd.year = 2011 or dd.year = 2012) \
    union \
    select distinct dd.year, ordf.customer_id from order_fact ordf \
    inner join dateorder_dim dd on dd.dateOrder_id = ordf.dateOrder_id \
    where dd.year = 2014 \
    and ordf.customer_id not in ( \
    select distinct ordf.customer_id from order_fact ordf \
    inner join dateorder_dim dd on dd.dateOrder_id = ordf.dateOrder_id \
    where dd.year != 2014)) a \
    group by year) newc on total.year = newc.year;")
    df = pd.DataFrame(mycursor.fetchall())
    df = df.rename(columns = {0:'0', 1:'1', 2:'2'}) # renaming dataframe columns
    p = figure(x_range = df['0'], 
                plot_width=400, 
                plot_height=400,
                title="Total and New Customers Every Year", 
                y_axis_label = "Customers", 
                x_axis_label = "Years",
                tools="box_select,zoom_in,zoom_out,reset", 
                tooltips=[("Year", "@0"), ("Total Customers", "@1"), ("New Customers", "@2")])
    p.vbar(x=dodge('0', -0.15, range=p.x_range), 
            top = '1', # y-axis values column of source
            width = 0.3, 
            source = df, 
            line_color="white", 
            color = '#3182bd', 
            fill_alpha = 0.8,
            legend_label='Total Customers')
    p.vbar(x=dodge('0', +0.15, range=p.x_range), 
            top = '2', # y-axis values column of source
            width = 0.3, 
            source = df, 
            line_color="white", 
            color = '#e6550d', 
            fill_alpha = 0.9,
            legend_label='New Customers')
    #p.xaxis.major_label_orientation = 0.9
    p.x_range.range_padding = 0.05
    p.y_range.start = 0
    p.toolbar.logo = None
    script20, div20 = components(p)
    #====================================================================================================
    #21
    mycursor.execute("select a.month, ((a.returns/b.total)*100) percentage_returns from \
    (select monthname(dd.date) month, count(*) returns from order_fact od \
    inner join dateorder_dim dd on dd.dateOrder_id = od.dateOrder_id \
    where od.returned = 1 and dd.year = 2014 \
    group by month order by dd.month) a \
    inner join \
    (select monthname(dd.date) month, count(*) total from order_fact od \
    inner join dateorder_dim dd on dd.dateOrder_id = od.dateOrder_id \
    where dd.year = 2014 \
    group by month order by dd.month) b on a.month = b.month;")
    df = pd.DataFrame(mycursor.fetchall())
    df = df.rename(columns = {0:'0', 1:'1'}) # renaming dataframe columns

    p = figure(x_range = df['0'], 
                plot_width=500, 
                plot_height=400,
                title="Percentage of Total Orders Returned this Year", 
                y_axis_label = "% Returns", 
                x_axis_label = "Months", 
                tools="box_select,zoom_in,zoom_out,reset", 
                tooltips=[("Month", "@0"), ("% return", "@1")])
    p.vbar(x=dodge('0', 0, range=p.x_range), 
            top = '1', # y-axis values column of source
            width = 0.5, 
            source = df, 
            line_color="white", 
            color = '#3182bd', 
            fill_alpha = 0.9)
    p.xaxis.major_label_orientation = 0.9
    p.x_range.range_padding = 0.05
    p.y_range.start = 0
    p.toolbar.logo = None 
    script21, div21 = components(p)
    #====================================================================================================
    #22
    mycursor.execute("select monthname(date) monthname, segment, sum(sales) from pj_sales_customer_date \
    where year = (select max(year) from pj_sales_customer_date) \
    group by month, segment order by month;")
    df = pd.DataFrame(mycursor.fetchall())
    df = df.rename(columns = {0:'month', 1:'segment', 2: 'sales'})

    group = df.groupby(by=['segment', 'month'])
    index_cmap = factor_cmap('segment_month', palette=Spectral4, factors=sorted(df.segment.unique()), end=1)

    p = figure(plot_width=800, 
                plot_height=400, 
                x_axis_label = "Segment X Month", 
                y_axis_label = "Sales (x 100,000 USD)", 
                title="Total Monthly sales of Customer Segments", 
                x_range=group, 
                tools="box_select,zoom_in,zoom_out,reset", 
                tooltips=[("segment_month: ", "@segment_month"), ("sales: ", "@sales_top")])

    p.vbar(x='segment_month', 
            top='sales_top', width=1, 
            source=group, 
            line_color="white", 
            fill_color=index_cmap)

    p.y_range.start = 0
    p.x_range.range_padding = 0.05
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = 0.8
    p.outline_line_color = 'black'
    p.toolbar.logo = None 
    script22, div22 = components(p)
    #====================================================================================================
    #### View on Pie Charts______________________________________________________________________________
    #23
    mycursor.execute("select country, convert(sum(profit),signed) as profit from mv_location_time_sales \
    where year=2014 and month=12 \
    group by country order by profit desc limit 10;")
    df = pd.DataFrame(mycursor.fetchall())
    df = df.rename(columns = {0:'0', 1:'1'})

    df['angle'] = df['1']/df['1'].sum() *2* pi
    df['color'] = Category20c[len(df)]

    p = figure(plot_height=400,
                plot_width=500,
                title="10 Most Profitable Countries this Month",
                tools="hover", 
                tooltips=[("Country", "@0"), ("Profit this Month", "@1")], 
                x_range=(-0.5, 1.0))
    p.wedge(x=0, y=1, 
            radius=0.4, 
            start_angle=cumsum('angle', include_zero=True), 
            end_angle=cumsum('angle'),
            line_color="white", 
            fill_color='color', 
            legend_field='0', 
            source=df)
    p.axis.axis_label=None
    p.axis.visible=False
    p.grid.grid_line_color = None
    p.toolbar.logo = None
    script23, div23 = components(p)
    #====================================================================================================
    #24
    mycursor.execute("select product_name, convert(sum(quantity),signed) as quantity from pj_sales_product_date \
    where year = (select max(year) from pj_sales_customer_date) \
    and week = (select max(week) from pj_sales_customer_date where \
                year = (select max(year) from pj_sales_customer_date)) \
    group by product_id order by quantity desc limit 10;")
    df = pd.DataFrame(mycursor.fetchall())
    df = df.rename(columns = {0:'0', 1:'1'})

    df['angle'] = df['1']/df['1'].sum() *2* pi
    df['color'] = Category20c[len(df)]

    p = figure(plot_height=400,
                plot_width=650,
                title="10 Most Sold Products this Week",
                tools="hover", 
                tooltips=[("Product", "@0"), ("Units Sold", "@1")], 
                x_range=(-0.5, 1.0))
    p.wedge(x=-0.15, y=1, 
            radius=0.3, 
            start_angle=cumsum('angle', include_zero=True), 
            end_angle=cumsum('angle'),
            line_color="white", 
            fill_color='color', 
            legend_field='0', 
            source=df)
    p.axis.axis_label=None
    p.axis.visible=False
    p.grid.grid_line_color = None
    p.toolbar.logo = None 
    script24, div24 = components(p)
    #====================================================================================================
    #### View on Line Plot______________________________________________________________________________
    #25
    mycursor.execute("select c.*, (c.S2014 - c.S2013) diff from ( \
    select a.week, sum(a.sales) over(order by week) as S2014, sum(b.sales) over(order by week) as S2013 from \
    (select week, sum(sales) sales \
    from mv_location_time_sales where year = 2014 group by week) a \
    inner join \
    (select week, sum(sales) sales \
    from mv_location_time_sales where year = 2013 group by week) b on a.week = b.week) c;") 
    df = pd.DataFrame(mycursor.fetchall()) 
    df = df.rename(columns = {0:'week', 1:'2014',2:'2013',3:'diff'})

    sc = ColumnDataSource(df)
    p = figure(plot_width=900, plot_height=400, title="Weekly Sales Comparison(This year vs Prev Year)", 
                y_axis_label = "Sales (in Million USD)", 
                x_axis_label = "Week Number",
                tools="box_select,zoom_in,zoom_out,reset", 
                tooltips=[("Week: ", "@week"), ("2014: ", "@2014"), ("2013: ", "@2013"), ("Difference: ", "@diff")])

    # add a line renderer
    p.line('week', '2014', source = df, line_width=3, color = '#3182bd', legend_label='2014')
    p.line('week', '2013', source = df, line_width=3, color = '#e6550d', legend_label='2013') 
    p.legend.location = "top_left"
    p.toolbar.logo = None
    script25, div25 = components(p)

    # first_graph = "Chal Para"
    return render(request, 'home.html', {'script18':script18, 'div18':div18, 'script19':script19, 'div19':div19, 
                                        'script20':script20, 'div20':div20, 'script21':script21, 'div21':div21, 
                                        'script22':script22, 'div22':div22, 'script23':script23, 'div23':div23, 
                                        'script24':script24, 'div24':div24, 'script25':script25, 'div25':div25})



def category(request):
    ## GENERAL STATS OF CATEGORY DIMENSION
    # 26
    mycursor.execute("select a.week, sum(a.sales) over(order by week) as Technology, \
    sum(b.sales) over(order by week) as Office_Supplies, \
    sum(c.sales) over(order by week) as Furniture from \
    (select category, week, sum(sales) sales from pj_sales_category_date \
    where year = (select max(year) from pj_sales_category_date) \
    and category = 'Technology' \
    group by category, week \
    order by category, week) a \
    inner join \
    (select category, week, sum(sales) sales from pj_sales_category_date \
    where year = (select max(year) from pj_sales_category_date) \
    and category = 'Office Supplies' \
    group by category, week \
    order by category, week) b on a.week = b.week \
    inner join \
    (select category, week, sum(sales) sales from pj_sales_category_date \
    where year = (select max(year) from pj_sales_category_date) \
    and category = 'Furniture' \
    group by category, week \
    order by category, week) c on c.week = b.week;") 
    df = pd.DataFrame(mycursor.fetchall())
    df = df.rename(columns = {0:'week', 1:'1', 2:'2', 3:'3'})

    sc = ColumnDataSource(df)
    p = figure(plot_width=900, plot_height=400, title="Weekly Commulative Sales Of All Categories This Year", 
                y_axis_label = "Sales (in Million USD)", 
                x_axis_label = "Week Number",
                tools="box_select,zoom_in,zoom_out,save,reset", 
                tooltips=[("Week", "@week"), ("Technology", "@1"), ("Office Supplies", "@2"), ("Furniture", "@3")])

    # add a line renderer
    p.line('week', '1', source = df, line_width=3, color = Spectral4[0], legend_label='Technology')
    p.line('week', '2', source = df, line_width=3, color = Spectral4[1], legend_label='Office Supplies')
    p.line('week', '3', source = df, line_width=3, color = Spectral4[2], legend_label='Furniture') 
    p.legend.location = "top_left"
    p.toolbar.logo = None
    script26, div26 = components(p)
    #====================================================================================================
    # 27
    mycursor.execute("select category, year, format(sum(sales),2) sales, format(sum(profit),2) revenue from pj_sales_category_date \
    group by category, year \
    order by category, year;")
    df = pd.DataFrame(mycursor.fetchall())
    df = df.rename(columns = {0:'0', 1:'1', 2:'2', 3:'3'})
    # Furniture sales and profit for all years
    f_2011_sales = df.at[0,'2']
    f_2011_profit = df.at[0,'3']
    f_2012_sales = df.at[1,'2']
    f_2012_profit = df.at[1,'3']
    f_2013_sales = df.at[2,'2']
    f_2013_profit = df.at[2,'3']
    f_2014_sales = df.at[3,'2']
    f_2014_profit = df.at[3,'3']

    # Office Supplies' sales and profit for all years
    o_2011_sales = df.at[4,'2']
    o_2011_profit = df.at[4,'3']
    o_2012_sales = df.at[5,'2']
    o_2012_profit = df.at[5,'3']
    o_2013_sales = df.at[6,'2']
    o_2013_profit = df.at[6,'3']
    o_2014_sales = df.at[7,'2']
    o_2014_profit = df.at[7,'3']

    # Technology sales and profit for all years
    t_2011_sales = df.at[8,'2']
    t_2011_profit = df.at[8,'3']
    t_2012_sales = df.at[9,'2']
    t_2012_profit = df.at[9,'3']
    t_2013_sales = df.at[10,'2']
    t_2013_profit = df.at[10,'3']
    t_2014_sales = df.at[11,'2']
    t_2014_profit = df.at[11,'3']
    #====================================================================================================
    # 28
    mycursor.execute("select a.*, b.sales_prev, format((((a.sales_now-b.sales_prev)/b.sales_prev)*100),2) percent_diff from \
    (select category, format(sum(sales),2) sales_now from pj_sales_category_date pj \
    where year = 2014 and pj.month = 12 group by category) a \
    inner join \
    (select category, format(sum(sales),2) sales_prev from pj_sales_category_date pj \
    where year = 2014 and pj.month = 11 group by category) b on a.category = b.category;")
    df = pd.DataFrame(mycursor.fetchall())
    df = df.rename(columns = {0:'0', 1:'1', 2:'2', 3:'3'})
    # Sales in current month vs previous month 
    # Furniture
    f_sale_now = df.at[0,'1']
    f_sale_prev = df.at[0,'2']
    f_sale_diff = df.at[0,'3']

    # Office Supplies
    o_sale_now = df.at[1,'1']
    o_sale_prev = df.at[1,'2']
    o_sale_diff = df.at[1,'3']

    # Technology
    t_sale_now = df.at[2,'1']
    t_sale_prev = df.at[2,'2']
    t_sale_diff = df.at[2,'3']

    mycursor.execute("select a.*, b.profit_prev, format((((a.profit_now-b.profit_prev)/b.profit_prev)*100),2) percent_diff from \
    (select category, format(sum(profit),2) profit_now from pj_sales_category_date pj \
    where year = 2014 and pj.month = 12 group by category) a \
    inner join \
    (select category, format(sum(profit),2) profit_prev from pj_sales_category_date pj \
    where year = 2014 and pj.month = 11 group by category) b on a.category = b.category;")
    df = pd.DataFrame(mycursor.fetchall())
    df = df.rename(columns = {0:'0', 1:'1', 2:'2', 3:'3'})
    # Profit in current month vs previous month
    # Furniture
    f_prof_now = df.at[0,'1']
    f_prof_prev = df.at[0,'2']
    f_prof_diff = df.at[0,'3']

    # Office Supplies
    o_prof_now = df.at[1,'1']
    o_prof_prev = df.at[1,'2']
    o_prof_diff = df.at[1,'3']

    # Technology
    t_prof_now = df.at[2,'1']
    t_prof_prev = df.at[2,'2']
    t_prof_diff = df.at[2,'3']
    #====================================================================================================
    # 29
    mycursor.execute("select category, convert(sum(sales),signed) this_quarter_sales from pj_sales_category_date \
    where year = 2014 and quarter = 4 group by category;")
    df = pd.DataFrame(mycursor.fetchall())
    df = df.rename(columns = {0:'0', 1:'1'})

    df['angle'] = df['1']/df['1'].sum() *2* pi
    df['color'] = Category20c[len(df)]

    p = figure(plot_height=400,
                plot_width=400,
                title="Category Wise Sales In Current Quarter",
                tools="hover,save,tap,reset",
                tooltips=[("Category", "@0"), ("Sales Amount", "@1")], 
                x_range=(-0.5, 1.0))
    p.wedge(x=-0.05, y=1, 
            radius=0.4, 
            start_angle=cumsum('angle', include_zero=True), 
            end_angle=cumsum('angle'),
            line_color="white", 
            fill_color='color', 
            legend_field='0', 
            source=df)
    p.axis.axis_label=None
    p.axis.visible=False
    p.grid.grid_line_color = None
    p.toolbar.logo = None
    script29, div29 = components(p)
    #====================================================================================================
    # 30
    mycursor.execute("select concat(concat(category, ', '), subcategory)subcategory, convert(sum(sales),signed) this_quarter_sales from pj_sales_category_date \
    where year = 2014 and quarter = 4 group by category, subcategory;")
    df = pd.DataFrame(mycursor.fetchall())
    df = df.rename(columns = {0:'0', 1:'1'})

    df['angle'] = df['1']/df['1'].sum() *2* pi
    df['color'] = Category20c[len(df)]

    p = figure(plot_height=400,
                plot_width=600,
                title="Subcategory Wise Sales In Current Quarter",
                tools="hover,save,tap,reset", 
                tooltips=[("Subcategory", "@0"), ("Sales Amount", "@1")], 
                x_range=(-0.5, 1.0))
    p.wedge(x=-0.05, y=1, 
            radius=0.4, 
            start_angle=cumsum('angle', include_zero=True), 
            end_angle=cumsum('angle'),
            line_color="white", 
            fill_color='color', 
            legend_field='0', 
            source=df)
    p.axis.axis_label=None
    p.axis.visible=False
    p.grid.grid_line_color = None
    p.toolbar.logo = None
    script30, div30 = components(p)
    #====================================================================================================
    # 31
    mycursor.execute("select category, sum(quantity) units_sold_this_month from pj_sales_category_date \
    where year = 2014 and month = 12 group by category;")
    df = pd.DataFrame(mycursor.fetchall())
    df = df.rename(columns = {0:'0', 1:'1'}) # renaming dataframe columns

    p = figure(x_range = df['0'], 
                plot_width=300, 
                plot_height=400,
                title="Quantity of Items Sold this Month", 
                y_axis_label = "Quantity Sold", 
                x_axis_label = "Category", 
                tools="tap,box_select,save,reset", 
                tooltips=[("Category", "@0"), ("Quantity", "@1")])
    p.vbar(x=dodge('0', 0, range=p.x_range), 
            top = '1', # y-axis values column of source
            width = 0.5, 
            source = df, 
            line_color="white", 
            color = '#3182bd', 
            fill_alpha = 0.9)
    p.x_range.range_padding = 0.05
    p.y_range.start = 0
    p.toolbar.logo = None
    script31, div31 = components(p)
    #====================================================================================================
    # 32
    mycursor.execute("select c.subcategory, sum(s.quantity) quantity from \
    category_dim c inner join product_dim p on c.category_id = p.category_id \
    inner join sales_fact s on p.product_id = s.product_id \
    inner join dateorder_dim d on s.dateOrder_id = d.dateOrder_id \
    where d.year = 2014 and d.month = 12 \
    group by c.category_id order by c.category_id;")
    df = pd.DataFrame(mycursor.fetchall())
    df = df.rename(columns = {0:'0', 1:'1'}) # renaming dataframe columns

    p = figure(x_range = df['0'], 
                plot_height=400,
                plot_width=500,
                title="Quantity of Items Sold This Month", 
                y_axis_label = "Quantity Sold", 
                x_axis_label = "Subcategories", 
                tools="tap,box_select,save,reset,hover", 
                tooltips=[("Subcategory", "@0"), ("Quantity", "@1")])

    p.vbar(x = '0', 
            top = '1', 
            width = 1.0, 
            source = df, 
            line_color="white", 
            color = '#3182bd')
    p.xaxis.major_label_orientation = 0.9
    p.x_range.range_padding = 0.05
    p.toolbar.logo = None
    script32, div32 = components(p)
    #====================================================================================================
    #33
    mycursor.execute("select c.category, c.subcategory, sum(sales) sales from category_dim c inner join mv_product_sales m on c.category_id = m.category_id group by c.category, c.subcategory;")
    df = pd.DataFrame(mycursor.fetchall())
    df = df.rename(columns = {0:'category', 1:'subcategory', 2: 'sales'})

    group = df.groupby(by=['category', 'subcategory'])

    index_cmap = factor_cmap('category_subcategory', palette=Spectral10, factors=sorted(df.category.unique()), end=1)

    p = figure(plot_width=700, 
                plot_height=400, 
                title="Total Sales of Subcategories", 
                x_axis_label = "Subcategories in Categories",
                y_axis_label = "Sales (in Million USD)", 
                x_range=group, 
                tools="tap,box_select,save,reset,hover", 
                tooltips=[("Category_SubCategory: ", "@category_subcategory"), ("sales: ", "@sales_top")])

    p.vbar(x='category_subcategory', 
            top='sales_top', width=1, 
            source=group, 
            line_color="white", 
            fill_color=index_cmap)

    p.y_range.start = 0
    p.x_range.range_padding = 0.05
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = 1.0
    p.outline_line_color = 'black'
    p.toolbar.logo = None
    script33, div33 = components(p)
    #====================================================================================================

    return render(request, 'category.html', {'script26':script26, 'div26':div26, 'script29':script29, 'div29':div29, 
                                                'script30':script30, 'div30':div30, 'script31':script31, 'div31':div31, 
                                                'script32':script32, 'div32':div32, 'script33':script33, 'div33':div33})


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
    
    ## NETWORK GRAPH VISUALIZATION OF PRODUCT ASSOCIATIONS
    # Input Variables
    mycursor.execute("Select distinct product1 from mv_product_association;")
    df2 = pd.DataFrame(mycursor.fetchall())
    df2 = df2.rename(columns = {0:'p1'})
    product_list = df2['p1'].tolist() #list having product names (3742 products)
    
    labelnodes = True
    productname = 'Staples'     # can have any value from product_list, '' is no prodcut selected
    productname2 = ''           # can have any value from product_list, '' is no prodcut selected
    counts = '1'                # can have values 0,1,2,3,4

    # IF the input is: 1) no product specified. 2) one product specified. 3) two products specified 
    if productname == '' and productname2 == '':
        mycursor.execute("select * from mv_product_association \
                        where counts > "+counts+";")
    elif productname != '' and productname2 == '':
        mycursor.execute("select * from mv_product_association \
                        where counts > "+counts+" and product1 = '"+productname+"';")
    else :
        mycursor.execute("select * from mv_product_association \
                        where counts > "+counts+" and product1 = '"+productname+"' \
                        and product2 = '"+productname2+"';")

    df = pd.DataFrame(mycursor.fetchall())
    df = df.rename(columns = {0:'P1', 1:'P2', 2:'Count', 3:'Sales', 4:'Profit', 5:'Q1', 6:'Q2'})
    # Duplicating first two columns (to add them in edge attributes) 
    df['P1dup'] = df['P1']
    df['P2dup'] = df['P2']
    #print(df)

    ## Graph Creation
    # Creating network in networkx by passing data
    G = nx.from_pandas_edgelist(df, source='P1', target='P2', edge_attr = True) # reference: https://networkx.org/documentation/stable/reference/generated/networkx.convert_matrix.from_pandas_edgelist.html
    # Degree is the number of edges of a node
    degrees = dict(nx.degree(G))
    nx.set_node_attributes(G, name='degree', values=degrees)
    # Title of graph
    title = "Product Associations"

    # Defining bokeh plot figure reference: https://melaniewalsh.github.io/Intro-Cultural-Analytics/Network-Analysis/Making-Network-Viz-with-Bokeh.html
    p = figure(title = title, 
                plot_width=800, plot_height=700,
                x_range=Range1d(-12.1, 12.1), y_range=Range1d(-12.1, 12.1), 
                tools="pan,wheel_zoom,tap,reset,save", active_scroll='wheel_zoom') 

    # Creating network graph object in bokeh by using networkx graph object G
    network_graph = from_networkx(G, nx.spring_layout, scale=10, center=(0, 0))

    # Set node size and color, selection and hover functionalities
    network_graph.node_renderer.glyph = Circle(size=20, fill_color=Spectral5[0])
    network_graph.node_renderer.selection_glyph = Circle(size=20, fill_color=Spectral5[4])
    network_graph.node_renderer.hover_glyph = Circle(size=20, fill_color=Spectral5[1])

    # Set edge opacity and width, selection and hover functionalities
    network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=3)
    network_graph.edge_renderer.selection_glyph = MultiLine(line_color=Spectral5[3], line_width=4)
    network_graph.edge_renderer.hover_glyph = MultiLine(line_color=Spectral5[1], line_width=4)

    ## Selection and Hover policies of graph. 
    # Reference: https://docs.bokeh.org/en/latest/docs/user_guide/graph.html
    network_graph.selection_policy = NodesAndLinkedEdges()
    network_graph.inspection_policy = EdgesAndLinkedNodes()

    # Creating seperate edge and node hover tools
    # solution and idea found from source: https://discourse.bokeh.org/t/separate-hovertool-for-nodes-and-edges-in-graph/6282
    hover_edges = HoverTool(
    tooltips=[('Product 1', '@P1dup'), ('Product 2', '@P2dup'), ('No. of Mutual Orders', '@Count'), ('Combined Sales', '@Sales'), ('Combined Profit', '@Profit'), ('Product1 Quantity', '@Q1'), ('Product2 Quantity', '@Q2')],
    renderers=[network_graph.edge_renderer], line_policy="interp"
    )
    hover_nodes = HoverTool(
    tooltips=[("Product Name", "@index"), ("Degree: ", "@degree")],
    renderers=[network_graph.node_renderer], line_policy="interp"
    )
    # Add network graph to the plot
    p.renderers.append(network_graph)

    #Add Labels
    if labelnodes:
        x, y = zip(*network_graph.layout_provider.graph_layout.values())
        node_labels = list(G.nodes())
        source = ColumnDataSource({'x': x, 'y': y, 'product': [node_labels[i] for i in range(len(x))]})
        labels = LabelSet(x='x', y='y', text='product', source=source, background_fill_color='white', text_font_size='10px', background_fill_alpha=.7)
        p.renderers.append(labels)

    # Adding edge hover tool to bokeh plot
    p.add_tools(hover_edges)
    p.add_tools(hover_nodes)

    # removing bokeh logo
    p.axis.visible=False
    p.grid.grid_line_color = None
    p.toolbar.logo = None
    graphscript, graphdiv = components(p)

    return render(request, 'graph.html', {'graphscript':graphscript, 'graphdiv':graphdiv})