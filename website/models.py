from . import db
from flask_login import UserMixin


#user database
class User(db.Model, UserMixin):
    userid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    person = db.Column(db.String(150))


    #connections with other classes
    bookngenre = db.relationship('BooknGenre')
    favourites = db.relationship('Favourites')
    recommend = db.relationship('Recommend')
    alabels = db.relationship('Alabels')


    #get_id method for login_user
    def get_id(self):
        return self.userid

#genre database  
class Genre(db.Model):
    genreid = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(150))


#authors database
class Authors(db.Model):
    authorid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))

#labels database
class Alabels(db.Model):
    alabelid = db.Column(db.Integer, primary_key=True)
    authorid = db.Column(db.Integer)

    #connections with other classes
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'))


#books database
class Books(db.Model):
    booksid = db.Column(db.Integer, primary_key=True)
    #img = db.Column(db.String(150))  #needs to know the exact file format
    title = db.Column(db.String(150))
    authorid = db.Column(db.Integer)
    publish_date = db.Column(db.String(150))


#database to connect books and genre, and user
class BooknGenre(db.Model):
    bookngenre_id = db.Column(db.Integer, primary_key=True)  #non-existant in crit b
    genreid = db.Column(db.Integer)
    bookid = db.Column(db.Integer)


    #connections with other classes
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'))


#favourite books database
class Favourites(db.Model):
    favourites_id = db.Column(db.Integer, primary_key=True)
    bookngenre_id = db.Column(db.Integer)


    #connections with other classes
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'))


#best authors database
class BestAuthors(db.Model):
    bestauthors_id = db.Column(db.Integer, primary_key=True)
    authorid = db.Column(db.Integer)


    #connections with other classes
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'))

#recommend page database
class Recommend(db.Model):
    recommend_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    author = db.Column(db.String(150))

    #connections with other classes
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'))