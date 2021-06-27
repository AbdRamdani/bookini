import os 
from os import error
from flask import Flask,render_template,url_for,request,redirect, session , jsonify
from flask_pymongo import PyMongo
import pandas as pd 
import numpy as np
import pickle
from bson.json_util import dumps
import recom 
from recom import getmethods 
from flask_bcrypt import Bcrypt



app = Flask(__name__)
app.config['MONGO_URI'] ='mongodb://localhost:27017/dataset'
SECRET_KEY = os.urandom(16).hex()
app.config['SECRET_KEY'] = SECRET_KEY
mongo = PyMongo(app)
#to crypt pwd 
bcrypt=Bcrypt(app)




@app.route('/')
def dashboard():
    if 'u_id' in session:
        
        #books = mongo.db.books.find()
        category = mongo.db.users.find_one({'User-ID':session['u_id']})['Liked_categories']
        category = ['[\''+x+'\']' for x in category]
        #books_data = pd.DataFrame.from_dict(books)
        
        #recommendation = demarage_froid(category,books_data)
        #recommendation = getmethods.demarage_froid(category,books_data)
        user_id=(mongo.db.users.find_one({'User-ID':session['u_id']}))
        user_rat_nb=int( mongo.db.users.find_one({'User-ID':session['u_id']})["nb_ratings"] )
        books = getmethods.get_last_five_rated(user_id)

        
        print("\n\t*********************************\n nombre de ratting pour l'utilisateur est :",user_id["nb_ratings"])
        recommendation = getmethods.get_rec_list(category,user_id)
        
        
        # last_rated_book = mongo.db.users.find_one({"User-ID" : session['u_id']})['last_rated']

        return render_template('final.html',nb=user_rat_nb,books = books,recommendation = recommendation)
    return redirect('/login')

@app.route('/search',methods = ['GET','POST'])
def search():
    if request.method =='POST':
        query = request.form['query']
        mongo.db.books.ensure_index([('book_title',"text"),('book_author',"text"),('publisher',"text"),('Summary',"text"),('Category',"text")])
        
        recommendation = mongo.db.books.find( { "$text": { "$search": query } } )
        return render_template('search.html',recommendation = recommendation,query=query)
        


@app.route('/<id>',methods = ['GET','POST'])  #<int:id>
def book(id):
    if 'u_id' in session:
            
            result = mongo.db.books.find_one_or_404({"ISBN":id})
            res_rat= round(result["average_rating"],2)
            print(res_rat)
            rating = mongo.db.ratings.find_one({"ISBN":id,"User-ID":session['u_id']})
            return render_template('book.html',res = result,res_rat=res_rat,rating=rating)
    return redirect('/login')

@app.route('/login',methods= ['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        res = {
            'email':email,
            'password':password
        }
        user =  mongo.db.users.find_one({'email':email})
        if not user == None:
            if bcrypt.check_password_hash(user['password'],password) :
            #if password == user['password']:
                u_id =  mongo.db.users.find_one({'email':email})['User-ID']
                session['u_id'] = u_id
                return redirect('/')
            else:
                return render_template('login.html',error="Password incorrect")
                
        else:
            return render_template('login.html',error="User does not exist")

    else:
        session.pop('u_id',None)
        return render_template('login.html',error=None)

@app.route('/signup',methods = ['GET','POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        name = firstname + lastname
        age = request.form['Age']
        password = request.form['password']
        password=bcrypt.generate_password_hash(password).decode("utf-8")
        u_id =278635 + mongo.db.users.count() + 1
        content = {
            'email':email,
            'name' : name,
            'firstname':firstname,
            'lastname':lastname,
            'User-ID' : u_id,
            'age':age,
            'password':password
        }
        user = mongo.db.users.find_one({'email':email})
        if user == None:
            mongo.db.users.insert_one(content)
            session['u_id'] = u_id
            return redirect('/categories')
        else:
            return render_template('signup.html',error ='user already exists')
    else:
        session.pop('u_id',None)
        return render_template('signup.html',error = None)

@app.route('/categories',methods =['GET','POST'])
def cats():
    if request.method == 'POST':
        cat =  request.form.getlist('cat')
        mongo.db.users.find_one_and_update({"User-ID" : session['u_id']},{"$set": {"Liked_categories": cat,'nb_ratings':0}})
        return redirect('/')
    else:
        #36 categories 
        categories = mongo.db.categories.find({}) #.sort([('nb',-1)])
        
        return render_template('categories.html',categories = categories)


@app.route('/similair',methods =['POST','GET'])
def sim():
    if request.method == 'POST':
        res = mongo.db.books.find()
        
        #work fine
        newrating = {
                'User-ID' : session['u_id'],
                'ISBN' : (request.form['book_id']),
                'Book-Rating' : int(request.form['rating'])
            }
            
        mongo.db.ratings.insert_one(newrating)

        current_book = mongo.db.books.find_one({'ISBN':newrating['ISBN']})

        average = ((current_book['SommeRating'] * current_book['average_rating']) + newrating['Book-Rating']) / (current_book['SommeRating'] + 1)
        current_book['average_rating'] = average              
        current_book['SommeRating'] = current_book['SommeRating'] + 1
        mongo.db.books.update_one({'ISBN' : newrating['ISBN']}, {"$set" : current_book})
        mongo.db.users.update_one({'User-ID':session['u_id']},{"$set":{'last_rated' : request.form['book_id']}})

        #pour calculer le nombre des ratings par l'utilisateur : 
        mongo.db.users.update_one({'User-ID':session['u_id']},{"$inc":{'nb_ratings' : 1}})
        

        list_res = getmethods.get_sim(current_book)
        
        list_res=list_res[["img_l","book_title","Summary","ISBN"]]
        #json to send it to book.html
        list_json=list_res.to_json(orient = 'records')
        return list_json



@app.route('/logout')
def logout():
   
    session.pop('u_id',None)

    #refresh svd matrice value with new rating 
    getmethods.log_out_ref()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)

