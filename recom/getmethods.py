
import recom 
from recom.config import GETOS
z=GETOS()


def get_rec_list(category ,user,books_data=z.get_books() ):
  z.refresh_value() #to get new rating matrice & nb rating
  if(int(user["nb_ratings"])<10):
    #demarage froid 
    return z.demarage_froid(category,user).sample(frac=1)

  elif(int(user["nb_ratings"])<15):

    return z.wrdvec(user).sample(frac=1)

  else:
    return z.getsvd(category,user).sample(frac=1)

def get_sim(book):
  return z.get_five_sim(book).sample(frac=1)

def log_out_ref():
  z.refresh_value_logout()







