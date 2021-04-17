from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User,auth

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
    #------------------------------------------------------
    #20
    

    script20, div20 = components(p)
    #------------------------------------------------------
    #21

    script20, div20 = components(p)
    #------------------------------------------------------
    #22

    script20, div20 = components(p)
    #------------------------------------------------------
    #23

    script20, div20 = components(p)
    #------------------------------------------------------
    #24

    script20, div20 = components(p)
    #------------------------------------------------------
    #25
    #------------------------------------------------------
    #26
    #------------------------------------------------------
    #27





    #***************************************************#
    if (request.method == 'POST' ):
        username =  request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username = username,password = password)
        if user is not None:
            auth.login(request,user)
            return render(request,'dashboard.html')
        else:
            messages.info(request,'Invalid credentials')
            return redirect('/')
    else:
        return render(request,'dashboard.html')

def decision(request):
    return render(request,'decision.html')


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
    #------------------------------------------------------
    #20
    

    script20, div20 = components(p)
    #------------------------------------------------------
    #21

    script20, div20 = components(p)
    #------------------------------------------------------
    #22

    script20, div20 = components(p)
    #------------------------------------------------------
    #23

    script20, div20 = components(p)
    #------------------------------------------------------
    #24

    script20, div20 = components(p)
    #------------------------------------------------------
    #25
    #------------------------------------------------------
    #26
    #------------------------------------------------------
    #27


    # first_graph = "Chal Para"
    return render(request, 'home.html', {'script18':script18, 'div18':div18, 'script19':script19, 'div19':div19})



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