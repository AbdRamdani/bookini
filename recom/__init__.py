"""
import pandas as pd
import numpy as np 
from surprise import Reader, Dataset, SVD  
import gensim 
import pickle 
from main import mongo 
"""

"""
books_data=pd.DataFrame.from_dict(mongo.db.books.find())
users=pd.DataFrame.from_dict(mongo.db.users.find())
books_rating=pd.DataFrame.from_dict(mongo.db.ratings.find())
user_category=mongo.db.categories.find()
docsim_index = pickle.load(open('SoftCosineSimilarity_final_WES2.pickle','rb'))
reader = Reader(rating_scale=(1, 10))
data = Dataset.load_from_df(books_rating[['User-ID', 'ISBN', 'Book-Rating']], reader)
trainset = data.build_full_trainset()
algo = SVD()
algo.fit(trainset)
print("done2 ")

"""



"""
def demarage_froid(category , books_data ):
  books_data_df=books_data[books_data["Category"].isin(category)]
  average_all=books_data_df["average_rating"].mean()
  nb_vote_min=books_data_df["SommeRating"].quantile(0.99)
  def weighted_rating(data,min=nb_vote_min,aver=average_all):
    ar=data["average_rating"]
    vc=data["SommeRating"]
    return (vc/(vc+min)*ar) + (min/(min+vc)*aver)
  books_data_df["weighted_score"]=books_data_df.apply(weighted_rating,axis=1)
  books_data_df=books_data_df.sort_values("weighted_score",ascending=False)
  #on retour par exemple 10 livre
  return books_data_df[0:5]
"""
"""
def recommender(book_id):

    col=("ISBN","rat","sim")
    array = np.empty((0,3)) 

    test=(books_data[books_data["ISBN"]==book_id]).squeeze()

    sim=docsim_index[test["Text"]]
    for i in range(1,11): # car le 0 cest notre livre donc 
        row=books_data.iloc[sim[i][0]]
        array = np.append(array, np.array([[row["ISBN"],row["average_rating"],sim[i][1]]]), axis=0)
    df = pd.DataFrame(data=array, columns=col)
    df=df.sort_values("sim",ascending=False)
    return df


"""
"""
def testsvd():




docsim_index = pickle.load(open('SoftCosineSimilarity_final_WES2.pickle','rb'))
print(books_data.head())

col=("ISBN","rat","sim")
array = np.empty((0,3)) 

test=(books_data[books_data["ISBN"]=="0425176428" ]).squeeze()

sim=docsim_index[test["Text"]]
for i in range(1,11): # car le 0 cest notre livre donc 
    row=books_data.iloc[sim[i][0]]
    array = np.append(array, np.array([[row["ISBN"],row["average_rating"],sim[i][1]]]), axis=0)
df = pd.DataFrame(data=array, columns=col)
df=df.sort_values("sim",ascending=False)
"""

