import pandas as pd
import numpy as np 
from surprise import Reader, Dataset, SVD  
import gensim 
import pickle 
from main import mongo 



class GETOS: 
    #it takes 20s , but it will work fine later 
    def __init__(self):
        self.books_data=pd.DataFrame.from_dict(mongo.db.books.find())
        self.users=pd.DataFrame.from_dict(mongo.db.users.find())
        self.books_rating=pd.DataFrame.from_dict(mongo.db.ratings.find())
        self.user_category=mongo.db.categories.find()
        self.docsim_index = pickle.load(open('SoftCosineSimilarity_final_WES2.pickle','rb'))
        reader = Reader(rating_scale=(1, 10))
        data = Dataset.load_from_df(self.books_rating[['User-ID', 'ISBN', 'Book-Rating']], reader)
        trainset = data.build_full_trainset()
        algo = SVD()
        algo.fit(trainset)
        self.algo=algo
    def refresh_value(self):
        #self.books_data=pd.DataFrame.from_dict(mongo.db.books.find())
        self.users=pd.DataFrame.from_dict(mongo.db.users.find())
        self.books_rating=pd.DataFrame.from_dict(mongo.db.ratings.find())

        """reader = Reader(rating_scale=(1, 10))
        data = Dataset.load_from_df(self.books_rating[['User-ID', 'ISBN', 'Book-Rating']], reader)
        trainset = data.build_full_trainset()
        algo = SVD()
        algo.fit(trainset)
        self.algo=algo"""

    def refresh_value_logout(self):
        #to get new value in algo matrice (svd matrice)
        self.books_data=pd.DataFrame.from_dict(mongo.db.books.find())

        reader = Reader(rating_scale=(1, 10))
        data = Dataset.load_from_df(self.books_rating[['User-ID', 'ISBN', 'Book-Rating']], reader)
        trainset = data.build_full_trainset()
        algo = SVD()
        algo.fit(trainset)
        self.algo=algo


    def get_books(self):
        return self.books_data

    def get_users(self):
        return self.users

    def get_user_books_rated(self,user_id):
        
        usr_rat=self.books_rating[self.books_rating["User-ID"]==user_id["User-ID"]]
        
        #from the highest to the lowest
        usr_rat=usr_rat.sort_values(by="Book-Rating",ascending=False)

        z=pd.merge(usr_rat["ISBN"],self.books_data,on="ISBN",how="inner")
        
        return z

    def get_user_rating(self,user_id):
        return self.books_rating[self.books_rating["User-ID"]==user_id]

    def demarage_froid(self,category,user):
        print(" *&$ now you are using demarage_froid method *&$")
        books_data_df=self.books_data[self.books_data["Category"].isin(category)]
        average_all=books_data_df["average_rating"].mean()
        nb_vote_min=books_data_df["SommeRating"].quantile(0.99)
        #on calcule les poids de chaque livre (qui depend de nombre des ratting et de la somme des rating)
        def weighted_rating(data,min=nb_vote_min,aver=average_all):
            ar=data["average_rating"]
            vc=data["SommeRating"]
            return (vc/(vc+min)*ar) + (min/(min+vc)*aver)
        books_data_df["weighted_score"]=books_data_df.apply(weighted_rating,axis=1)
        books_data_df=books_data_df.sort_values("weighted_score",ascending=False)
        
        print("-----------",books_data_df.shape,"-------- ")
        #remove already rated books
        user_rat_bfr=(self.get_user_books_rated(user))["ISBN"]
        user_rat_bfr=user_rat_bfr.tolist()
        print(len(user_rat_bfr))
        books_data_df = books_data_df[~books_data_df['ISBN'].isin(user_rat_bfr)]
        
        return books_data_df[0:300]
    
    def wrdvec(self,user):
        print(" *&$ now you are using word2vec method *&$")
        bo=self.get_user_books_rated(user)
        user_rat_bfr=bo
        bo=bo[0:5]
        
        col=("ISBN","rat","sim")
        array = np.empty((0,3)) 
        for i,ro in bo.iterrows():
            test=(self.books_data[self.books_data["ISBN"]==ro["ISBN"]]).squeeze()
            sim=self.docsim_index[test["Text"]]
            
            for i in range(1,11): # car le 0 cest notre livre donc 
                row=self.books_data.iloc[sim[i][0]]
                array = np.append(array, np.array([[row["ISBN"],row["average_rating"],sim[i][1]]]), axis=0)
                
        df = pd.DataFrame(data=array, columns=col)
        df=df.sort_values("sim",ascending=False)
        
        bb=pd.merge(df["ISBN"],self.books_data,on="ISBN",how="inner")
        print(bb.shape)
        user_rat_bfr=(user_rat_bfr["ISBN"]).tolist()
        bb = bb[~bb['ISBN'].isin(user_rat_bfr)]
        print(bb.shape)
        return bb
    
    def getsvd(self,category,user):

        print(" *&$ now you are using svd method *&$")
        col=("ISBN","note")
        books_data_cb=self.books_data[self.books_data["Category"].isin(category)]
        array = np.empty((0,2))
        for i,row in books_data_cb.iterrows():
            pred = (self.algo.predict(user["User-ID"],row["ISBN"]))
            array = np.append(array, np.array([[row["ISBN"],pred[3]]]), axis=0)  
        df = pd.DataFrame(data=array, columns=col)
        df = df.sort_values("note",ascending=False)
        bb=pd.merge(df["ISBN"],self.books_data,on="ISBN",how="inner")
        print(bb.shape)
        user_rat_bfr=(self.get_user_books_rated(user))["ISBN"]
        user_rat_bfr=user_rat_bfr.tolist()
        #to remove already rated books from rec
        bb = bb[~bb['ISBN'].isin(user_rat_bfr)]
        print(bb.shape)
        return bb[0:300]

    def get_five_sim(self,book):

        """col=("ISBN","rat","sim")
        array = np.empty((0,3)) 
            
        for i in range(1,6): # car le 0 cest notre livre donc 
            row=self.books_data.iloc[sim[i][0]]
            array = np.append(array, np.array([[row["ISBN"],row["average_rating"],sim[i][1]]]), axis=0)
        df = pd.DataFrame(data=array, columns=col)
        df=df.sort_values("sim",ascending=False)
        bb=pd.merge(self.books_data,df["ISBN"],on="ISBN",how="inner")
        return bb"""

        col=("ISBN","rat","sim")
        array = np.empty((0,3)) 

        test=(self.books_data[self.books_data["ISBN"]==book["ISBN"]]).squeeze()
        print(type(test),"      ",test)
        sim=self.docsim_index[test["Text"]]
            
        for i in range(1,11): # car le 0 cest notre livre donc 
            row=self.books_data.iloc[sim[i][0]]
            array = np.append(array, np.array([[row["ISBN"],row["average_rating"],sim[i][1]]]), axis=0)
                
        df = pd.DataFrame(data=array, columns=col)
        df=df.sort_values("sim",ascending=False)
        
        bb=pd.merge(df["ISBN"],self.books_data,on="ISBN",how="inner")
        
        print(bb.shape)
        print(bb["ISBN"].head())
        return bb[:5]

    def combine_svd_w2vc(self,category,user):
        res1=self.getsvd(category,user)
        res2=self.wrdvec(user)
        resultat=pd.merge(res1,res2,on="ISBN")
        #resultat=resultat.drop_duplicates(subset="ISBN")
        print("$$$$$$",resultat.shape)
        print(resultat.head(5))
        return resultat

        
