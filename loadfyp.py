import pandas as pd
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="s@qiekausarali5",
  database="fypdata"
)
mycursor = mydb.cursor()

df = pd.read_csv("E:\Work\FYP\FYP 1\Business Insight and Visualization Assistant\data\Orders.csv")

values = []
j = 0
k = 1
for i in range(len(df)) :
  #print (i, end =" ")
  row_id = int(df.loc[i, "Row ID"])
  #print (row_id, type(row_id), end =" "
  order_id = df.loc[i, "Order ID"]
  #print (order_id, type(order_id), end =" ")
  order_date = df.loc[i, "Order Date"]
  #print (order_date, type(order_date), end =" ")
  ship_date = df.loc[i, "Ship Date"]
  #print (ship_date, type(ship_date), end =" ")
  ship_mode = df.loc[i, "Ship Mode"]
  #print (ship_mode, type(ship_mode), end =" ")
  customer_id = df.loc[i, "Customer ID"]
  #print (customer_id, type(customer_id), end =" ")
  customer_name = df.loc[i, "Customer Name"]
  #print (customer_name, type(customer_name), end =" ")
  segment = df.loc[i, "Segment"]
  #print (segment, type(segment), end =" ")
  city = df.loc[i, "City"]
  #print (city, type(city), end =" ")
  state = df.loc[i, "State"]
  #print (state, type(state), end =" ")
  country = df.loc[i, "Country"]
  #print (country, type(country), end =" ")
  postal_code = int(df.loc[i, "Postal Code"].astype('Int64'))
  if postal_code < 0:
    postal_code = None
  #print (postal_code, type(postal_code), end =" ")
  market = df.loc[i, "Market"]
  #print (market, type(market), end =" ")
  region = df.loc[i, "Region"]
  #print (region, type(region), end =" ")
  product_id = df.loc[i, "Product ID"]
  #print (product_id, type(product_id), end =" ")
  category = df.loc[i, "Category"]
  #print (category, type(category), end =" ")
  subcategory = df.loc[i, "Sub-Category"]
  #print (subcategory, type(subcategory), end =" ")
  product_name = df.loc[i, "Product Name"]
  #print (product_name, type(product_name), end =" ")
  sales = float(df.loc[i, "Sales"])
  #print (sales, type(sales), end =" ")
  quantity = int(df.loc[i, "Quantity"])
  #print (quantity, type(quantity), end =" ")
  discount = float(df.loc[i, "Discount"])
  #print (discount, type(discount), end =" ")
  profit = float(df.loc[i, "Profit"])
  #print (profit, type(profit), end =" ")
  shipping_cost = float(df.loc[i, "Shipping Cost"])
  #print (shipping_cost, type(shipping_cost), end =" ")
  order_priority = df.loc[i, "Order Priority"]
  #print (order_priority, type(order_priority))
  val = (row_id, order_id, order_date, ship_date, ship_mode, customer_id, customer_name, segment, 
        city, state, country, postal_code, market, region, product_id, category, subcategory, 
        product_name, sales, quantity, discount, profit, shipping_cost, order_priority)
  values.append(val)
  j += 1
  if j == 46:
    sql = "INSERT IGNORE INTO fypdata.orders VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    mycursor.executemany(sql, values)
    mydb.commit()
    print (k, ": inserted ", j, " rows")
    values.clear()
    k += 1
    j = 0
print (j, " inserted")
