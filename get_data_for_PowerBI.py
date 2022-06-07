# pip install pymongo pymongo[srv] pandas matplotlib
# PowerBI - Python script as datasource

import pymongo
import pandas as pd

login = ""
password = ""
url = "mongodb+srv://{}:{}@cluster0.k1skitd.mongodb.net/?retryWrites=true&w=majority".format(login, password)
client = pymongo.MongoClient(url)
db = client.test
mongo = db.mieszkania
cursor = mongo.find({})
df =  pd.DataFrame(list(cursor))
df = df.drop(columns=['_id'])
print(df)