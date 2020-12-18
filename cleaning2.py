import pandas as pd
import mysql.connector

# Changes the order id
def change_id(g):
    old = int(g[7:])
    new = str(old-1)
    old = str(old)
    g = g.replace(old, new)
    return g

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="s@qiekausarali5",
  database="fypdata"
)
mycursor = mydb.cursor()

# Obtaining repeating orders
mycursor.execute("select distinct a.product_id, a.product_name from orders a left join (select distinct product_id, product_name from orders group by product_id) b using (product_id, product_name) where b.product_name is null;")
df = pd.DataFrame(mycursor.fetchall())
dfn = df.copy()
# Obtaining all orders
mycursor.execute("select distinct product_id from orders;")
df2 = pd.DataFrame(mycursor.fetchall())

print (df)
print ("lolololo")
print (df2)

# Changing repeating order IDs in the dataframe
for i in range(len(df)) :
  product_id = df.loc[i, 0]
  while product_id in df2.iloc[:, 0].values :
    product_id = change_id(product_id)
  df.loc[i,0] = product_id

count = 0
# Updating transaction table with new IDs
for i in range(len(df)) :
  sql = "update orders set product_id = '"+ df.loc[i,0] +"' where row_id <= 51290 and product_name = '"+ dfn.loc[i,1] +"' and product_id = '"+ dfn.loc[i,0] +"';"
  mycursor.execute(sql)
  mydb.commit()
  print (count, "  ", mycursor.rowcount, "record(s) affected")
  count += 1