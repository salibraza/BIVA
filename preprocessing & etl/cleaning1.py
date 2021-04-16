import pandas as pd
import mysql.connector

# Changes the order id
def change_id(g):
  old = int(g[8:])
  new = str(old-1)
  old = str(old)
  g = g.replace(old, new)
  return g

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="password here",
  database="fypdata"
)
mycursor = mydb.cursor()

# Obtaining repeating orders
mycursor.execute("select distinct a.order_id, a.order_date, a.city, a.state, a.country from orders a left join (select distinct order_id, order_date, city, state, country from fypdata.orders group by order_id) b using (order_id, order_date, city, state, country) where b.order_date is null;")
df = pd.DataFrame(mycursor.fetchall())
dfn = df.copy()
# Obtaining all orders
mycursor.execute("select distinct order_id from orders;")
df2 = pd.DataFrame(mycursor.fetchall())

print (df)
#print ("lol")
print (df2)

# Changing repeating order IDs in the dataframe
for i in range(len(df)) :
  order_id = df.loc[i, 0]
  while order_id in df2.iloc[:, 0].values :
    order_id = change_id(order_id)
  df.loc[i,0] = order_id

count = 0
# Updating transaction table with new IDs
for i in range(len(df)) :
  sql = "update orders set order_id = '"+ df.loc[i,0] +"' where row_id <= 51290 and order_date = '"+ dfn.loc[i,1] +"' and city = '" + dfn.loc[i,2] + "' and order_id = '"+ dfn.loc[i,0] +"';"
  mycursor.execute(sql)
  mydb.commit()
  print (count, "  ", mycursor.rowcount, "record(s) affected")
  count += 1