#how to upload it to mongo
from pymongo import MongoClient
import pandas 






import pickle 
pickle_in=open("booksdata_final_WES.pickle","rb") #csv dataset
books=pickle.load(pickle_in)
print(books["Summary"])



client = MongoClient('localhost', 27017)
db = client['dataset']  #data name
coll = db["books"] #collection name
books=books.to_dict(orient="records")
coll.insert_many(books)





