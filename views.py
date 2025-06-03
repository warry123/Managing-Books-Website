from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from .models import User, Books, Genre, Authors, BooknGenre, Favourites, BestAuthors, Recommend, Alabels
from . import db
import json

views = Blueprint('views', __name__)


# ------- USER PAGES --------
#----------------------------

#home page
@views.route('/', methods=['GET','POST'])
@login_required
def home():

    #defining variables
    no_authors = 5 
    aname = []           #stores the names of authors     
    books = []           #2d array for books where each row is by an author
    total = []           #2d array for books where each column is an author
    max = 0              #maximum number of books from each author    
    allow = 1           #check for allow recommendations    

    #POST request
    if request.method == "POST":
        forms = request.form.get("formhome")

        #to delete authors
        if forms == "formdelete":
            delhome = request.form.get("delete")
            delauthor = Authors.query.filter_by(name = delhome).first()

            #for books
            delbooks = Books.query.filter_by(authorid = delauthor.authorid).all()
            delbooks_id = [b.authorid for b in delbooks]

            #for alabels
            alabel = Alabels.query.filter(Alabels.authorid == delauthor.authorid, Alabels.userid == current_user.userid).first()
            db.session.delete(alabel)
            db.session.commit()

            if len(delbooks_id) > 0:
                #for bookngenre
                delbookgenre = BooknGenre.query.filter(BooknGenre.bookid.in_(delbooks_id), BooknGenre.userid == current_user.userid).all()
                delbookgenre_ids = [bg.bookngenre_id for bg in delbookgenre]
                print(delbookgenre_ids)
                for bg in delbookgenre:
                    db.session.delete(bg)
                    db.session.commit()

                #for favourites
                delfavourite = Favourites.query.filter(Favourites.bookngenre_id.in_(delbookgenre_ids)).all()
                for f in delfavourite:
                    db.session.delete(f)
                    db.session.commit()

                #for best authors
                delbestauthor = BestAuthors.query.filter(BestAuthors.authorid == delauthor.authorid, BestAuthors.userid == current_user.userid)
                for b in delbestauthor:
                    db.session.delete(b)
                    db.session.commit()
        
        #to add to favourites
        elif forms == "formstar":
            titled = request.form.get("fav")
            favbook = Books.query.filter_by(title = titled).first()
            favbookngenre = BooknGenre.query.filter_by(bookid = favbook.booksid).first()
            favourite = Favourites(bookngenre_id = favbookngenre.bookngenre_id, userid = current_user.userid)
            db.session.add(favourite)
            db.session.commit()
        
        #to add to best authors
        elif forms == "formbestauthor":
            bestauthor = request.form.get("bestauthor")
            bestauthored = Authors.query.filter_by(name = bestauthor).first()
            bestauthors = BestAuthors(authorid = bestauthored.authorid, userid = current_user.userid)
            db.session.add(bestauthors)
            db.session.commit()

        #manage toggle button for allow recommend page
        elif forms == "formallowrecommend":
            check = request.form.get("allowrecommend")
            if check:
                allow = 1
            else:
                allow = 0

    #extracting all authors belonging to a user
    alabels = Alabels.query.filter_by(userid = current_user.userid).all()
    authorids = [a.authorid for a in alabels]

    #checking number of authors
    authors = Authors.query.filter(Authors.authorid.in_(authorids)).limit(no_authors).all()
    for a in authors:
        if a.name:
            aname.append(a.name)
    if len(aname) < 5:
        no_authors = len(aname)

    #Searching for the authors
    authors = Authors.query.filter(Authors.authorid.in_(authorids)).limit(no_authors).all()

    for a in authors:
        book = Books.query.filter_by(authorid = a.authorid)
        bookids = [b.booksid for b in book]
        bookngenre = BooknGenre.query.filter(BooknGenre.bookid.in_(bookids), BooknGenre.userid == current_user.userid).all()

        bookids = [bg.bookid for bg in bookngenre]
        book = Books.query.filter(Books.booksid.in_(bookids)).all()
        book = [b.title for b in book]
        books.append(book)

        #finding which author has largest book count
        if len(book) > max:
            max = len(book)


    #to create memory spaces for total table first
    for i in range(max):
        temp = []
        for j in range(len(authors)):
            temp.append("")
        total.append(temp)

    #to fill in total table
    for i, a in enumerate(authors):
        for j, t in enumerate(books[i]):
            total[j][i] = t
            

    #for recommend page
    title = ""        
    author = "" 

    recommend = Recommend.query.filter_by(userid = current_user.userid).first()
    if recommend:
        title = recommend.title
        author = recommend.author

    return render_template("home.html", user = current_user, total = total, authors = authors, title = title, author = author, length=no_authors, allow = allow)

#addbook page
@views.route('/addbook', methods = ['GET', 'POST'])
@login_required
def addbook():
    if request.method == "POST":
        #get form data
        title = request.form.get("title")
        author = request.form.get("author")
        date = request.form.get("date")
        genre = request.form.get("genre")

        if len(title) < 1:
            flash("title should be at least one character.", category="error")
        elif len(author) < 1:
            flash("author should be at least one character.", category="error")
        elif len(date) < 8:
            flash("date needs to be in the form of dd/mm/yy", category="error")
            if "/" not in date:
                flash("date needs to have / in it.", category="error")
        elif len(genre) < 1:
            flash("Genre should be at least one character.", category="error")
        else:
            #check for title
            bookngenre = None

            book = Books.query.filter_by(title = title).first()
            if book:
                bookngenre = BooknGenre.query.filter(BooknGenre.bookid == book.booksid, BooknGenre.userid == current_user.userid).first()          
            if bookngenre:
                flash("book already exists!", category="error")

            else:
                new_author = Authors.query.filter_by(name = author).first()
                if not new_author:
                    new_author = Authors(name = author)
                    db.session.add(new_author)
                    db.session.commit()

                    #add Alabel
                    alabels = Alabels(authorid = new_author.authorid, userid = current_user.userid)
                    db.session.add(alabels)
                    db.session.commit()
                
                else:
                    alabels = Alabels.query.filter(Alabels.authorid == new_author.authorid, Alabels.userid == current_user.userid).first()
                    if not alabels:
                        #add Alabel
                        alabels = Alabels(authorid = new_author.authorid, userid = current_user.userid)
                        db.session.add(alabels)
                        db.session.commit()
                
                #add genre
                new_genre = Genre.query.filter_by(genre = genre).first()
                if not new_genre:
                    new_genre = Genre(genre = genre)
                    db.session.add(new_genre)
                    db.session.commit()
                
                #add book
                new_book = Books.query.filter_by(title = title).first()
                if not new_book:
                    new_book = Books(title = title, authorid = new_author.authorid, publish_date = date)
                    db.session.add(new_book)
                    db.session.commit()
                
                #add bookngenre
                new_bookngenre = BooknGenre.query.filter(BooknGenre.bookid == new_book.booksid, BooknGenre.userid == current_user.userid).first()
                if not new_bookngenre:
                    new_bookngenre = BooknGenre(genreid = new_genre.genreid, bookid = new_book.booksid, userid = current_user.userid)
                    db.session.add(new_bookngenre)
                    db.session.commit()
                
                flash("book added successfully!", category="success")
                return redirect(url_for('views.home'))
   
    return render_template("addbook.html")


#search by author page
@views.route('/searchauthor')
@login_required
def searchauthor():
    return render_template("searchbyauthor.html")
 
#route to do active search using htmx for search by author
@views.route('/search')
@login_required
def search():
    title = []
    authors = []
    genres = []
    q = request.args.get("q")
    if q:
        alabels = Alabels.query.filter_by(userid = current_user.userid).all()
        alabelids = [a.authorid for a in alabels]
        id = []

        search = Authors.query.filter(Authors.name.ilike(f"%{q}%")).all()
        searchids = [author.authorid for author in search]
        
        for ids in searchids:
            if ids in alabelids:
                id.append(ids)

        books = Books.query.filter(Books.authorid.in_(id)).all()
        #t = [t.title for t in books]

        booksid = [book.booksid for book in books]
        bookngenre = BooknGenre.query.filter(BooknGenre.bookid.in_(booksid), BooknGenre.userid == current_user.userid).all()


        for b in bookngenre:
            book = Books.query.filter_by(booksid = b.bookid).first()
            title.append(book.title)


            author = Authors.query.filter_by(authorid = book.authorid).first()
            authors.append(author.name)


            genre = Genre.query.filter_by(genreid = b.genreid).first()
            genres.append(genre.genre)


    return render_template("search.html", title = title, authors = authors, genres = genres)


#search by book page
@views.route('/searchbook')
@login_required
def searchbook():
    return render_template("searchbybook.html")


#route to do active search using htmx for search by book
@views.route('/search2')
@login_required
def search2():
    title = []
    genres = []
    authors = []
   
    q = request.args.get("q")
    if q:
        search = Books.query.filter(Books.title.ilike(f"%{q}%")).all()
        booksid = [book.booksid for book in search]
        bookngenre = BooknGenre.query.filter(BooknGenre.bookid.in_(booksid), BooknGenre.userid == current_user.userid).all()

        for b in bookngenre:
            book = Books.query.filter_by(booksid = b.bookid).first()
            title.append(book.title)

            author = Authors.query.filter_by(authorid = book.authorid).first()
            authors.append(author.name)

            genre = Genre.query.filter_by(genreid = b.genreid).first()
            genres.append(genre.genre)

    return render_template("search2.html", title = title, authors = authors, genres = genres)


'''
#search internet page
@views.route('/searchinternet')
@login_required
def searchinternet():
    return render_template("searchinternet.html")
'''


#favourites page
@views.route('/favourites', methods=['GET','POST'])
@login_required
def favourites():
    #variables
    title = []
    authors = []
    genres = []

    #for deleting from a favourites section
    if request.method == "POST":
        titled = request.form.get("title")


        booked = Books.query.filter_by(title = titled)
        bookedids = [b.booksid for b in booked]


        bookngenre = BooknGenre.query.filter(BooknGenre.bookid.in_(bookedids)).all()
        bookngenre_ids = [b.bookngenre_id for b in bookngenre]


        favourites = Favourites.query.filter(Favourites.bookngenre_id.in_(bookngenre_ids)).all()
        for f in favourites:
            if f:
                if f.userid == current_user.userid:
                    db.session.delete(f)
                    db.session.commit()
                    flash("book deleted successfully!", category="success")
            else:
                print("none")


    #fetching all favourites from a user
    fav = Favourites.query.filter(Favourites.userid == current_user.userid).all()
    bookngenre_id = [b.bookngenre_id for b in fav]
    bookngenre = BooknGenre.query.filter(BooknGenre.bookngenre_id.in_(bookngenre_id)).all()


    #creating the lists for title, authors, and genres
    for b in bookngenre:
            book = Books.query.filter_by(booksid = b.bookid).first()
            title.append(book.title)


            author = Authors.query.filter_by(authorid = book.authorid).first()
            authors.append(author.name)


            genre = Genre.query.filter_by(genreid = b.genreid).first()
            genres.append(genre.genre)


    return render_template("favourite.html", title = title, authors = authors, genres = genres)


#best authors page
@views.route('/bestauthors', methods=['GET','POST'])
@login_required
def bestauthors():
    #for delete from bestauthors page
    if request.method == "POST":
        author = request.form.get("author")
        authored = Authors.query.filter_by(name = author).first()
        bestauthor = BestAuthors.query.filter(BestAuthors.authorid == authored.authorid, BestAuthors.userid == current_user.userid).first()
        if bestauthor:
            db.session.delete(bestauthor)
            db.session.commit()
        flash("author deleted successfully!", category="success")

    #extracting the authors for best authors page
    best = BestAuthors.query.filter(BestAuthors.userid == current_user.userid).all()
    bestids = [b.authorid for b in best]
    authors = Authors.query.filter(Authors.authorid.in_(bestids)).all()


    return render_template("bestauthor.html", authors = authors)




   


   
       


#----------------------------------------------------------------------------------------------------------------------


# ------- Employee PAGES --------
#----------------------------


#home page
@views.route('/ehome')
@login_required
def ehome():
    return render_template("ehome.html")


#Search by Email
@views.route('/eclientEmail')
@login_required
def eclientEmail():
    return render_template("eclientEmail.html")


@views.route('/esearchemail')
@login_required
def esearchemail():
    q = request.args.get("email")
    if q:
        user = User.query.filter(User.email.ilike(f"%{q}%"), User.person == "user").all()
    else:
        user = []
    return render_template("esearchemail.html", users = user)


#Search by Name
@views.route('/eclientName')
@login_required
def eclientName():
    return render_template("eclientName.html")


@views.route('/esearchname')
@login_required
def esearchname():
    q = request.args.get("name")
    if q:
        user = User.query.filter(User.name.ilike(f"%{q}%"), User.person == "user").all()
    else:
        user = []
    return render_template("esearchname.html", users = user)


#add client
@views.route('/addclient', methods=['GET','POST'])
@login_required
def addclient():
    if request.method == "POST":
        #getting requested data
        email = request.form.get("email")
        password = request.form.get("password")
        name = request.form.get("name")
        genres = []

        for i in range(3):
            if len(request.form.get("genre"+str(i+1))) > 0:
                genres.append(request.form.get("genre"+str(i+1)))
            else:
                flash("Genres needs to be filled in.", category="error")


        #conditionals
        if len(email) < 4:
            flash("email has to be at least 4 characters!", category="error")
        elif len(password) < 8:
            flash("password has to be at least 8 characters!", category="error")
        elif len(name) < 1:
            flash("name has to be at least 1 character")
        else:
            #add new user to database
            user = User.query.filter_by(email = email).first()
            if not user:
                user = User(email = email, password = generate_password_hash(password), name = name, person="user")
                db.session.add(user)
                db.session.commit()


                #check if genres already exist
                for g in genres:
                    genre = Genre.query.filter_by(genre = g).first()
                    if not genre:
                        genre = Genre(genre = g)
                        db.session.add(genre)
                        db.session.commit()

            else:
                flash("user already exists")
                return render_template("addclient.html")


            flash("user added successfully!", category="success")
            return redirect(url_for("views.eclientEmail"))


    return render_template("addclient.html")


#edit client
@views.route('/editclient', methods=['GET','POST'])
@login_required
def editclient():
    if request.method == "POST":
        #getting form data
        userid = request.form.get("userid")
        email = request.form.get("email")
        name = request.form.get("name")


        #conditionals
        if len(email) < 4:
            flash("email has to be at least 4 characters!", category="error")
        elif len(name) < 1:
            flash("name has to be at least 1 character")
        else:
            #searching for existing user
            user = User.query.filter_by(userid = userid).first()

            if user:
                #editing the data in database
                user.email = email
                user.name = name
                db.session.commit()
                return redirect(url_for("views.eclientEmail"))
            else:
                flash("userid invalid")
   
    return render_template("editclient.html")


#books by title
@views.route('/ebooksTitle')
@login_required
def ebooksTitle():
    return render_template("ebooksTitle.html")


#search book by title
@views.route('/esearchtitle')
@login_required
def esearchtitle():
    q = request.args.get("title")
    if q:
       authors = []
       book = Books.query.filter(Books.title.ilike(f"%{q}%")).all()
       for b in book:
           author = Authors.query.filter_by(authorid = b.authorid).first()
           authors.append(author.name)

    else:
        book = []
        authors = []
    return render_template("esearchtitle.html", books = book, authors = authors)


#books by author
@views.route('/ebooksAuthor')
@login_required
def ebooksAuthor():
    return render_template("ebooksAuthor.html")


#search book by author
@views.route('/esearchauthor')
@login_required
def esearchauthor():
    q = request.args.get("author")
    if q:
       authors = []
       author = Authors.query.filter(Authors.name.ilike(f"%{q}%")).all()
       authorids = [a.authorid for a in author]
       book = Books.query.filter(Books.authorid.in_(authorids)).all()

       for b in book:
           author = Authors.query.filter_by(authorid = b.authorid).first()
           authors.append(author.name)
    else:
        book = []
        authors = []
    return render_template("esearchauthor.html", books = book, authors = authors)


#books by date
@views.route('/ebooksDate')
@login_required
def ebooksDate():
    return render_template("ebooksDate.html")


#search book by Date
@views.route('/esearchdate')
@login_required
def esearchdate():
    q = request.args.get("date")
    if q:
       authors = []
       book = Books.query.filter(Books.publish_date.ilike(f"%{q}%")).all()
       for b in book:
           author = Authors.query.filter_by(authorid = b.authorid).first()
           authors.append(author.name)
    else:
        book = []
        authors = []
    return render_template("esearchdate.html", books = book, authors = authors)


#employee add book
@views.route('/eaddbook', methods=['GET','POST'])
@login_required
def eaddbook():
    if request.method == "POST":
        #getting requested data
        title = request.form.get("title")
        author = request.form.get("author")
        date = request.form.get("date")

        #conditionals
        if len(title) < 1:
            flash("Title has to be at least 1 characters!", category="error")
        elif len(author) < 1:
            flash("Author has to be at least 1 characters!", category="error")
        elif len(date) < 1 or "/" not in date:
            flash("name has to be at least 1 character and has to be in dd/mm/yy format", category="error")
        else:
            #put in database
            author = Authors.query.filter_by(name = author).first()
            if not author:
                author = Authors(name = author)
                db.session.add(author)
                db.session.commit()

            book = Books.query.filter_by(title = title).first()
            if not book:
                book = Books(title = title, authorid = author.authorid, publish_date = date)
                db.session.add(book)
                db.session.commit()
            else:
                flash("book already exists.", category="error")
                return render_template("eaddbook.html")

            flash("Book added successfully!", category="success")
            return redirect(url_for("views.ebooksTitle"))


    return render_template("eaddbook.html")


#employee edit book
@views.route('/eeditbook', methods=['GET','POST'])
@login_required
def eeditbook():
    if request.method == "POST":
        bookid = request.form.get("bookid")
        title = request.form.get("title")
        author = request.form.get("author")
        date = request.form.get("date")

        #conditionals
        if len(bookid) > 0:
            flash("bookid must be at least a number", category="error")
            if not isinstance(bookid, int): 
                flash("bookid must be an integer", category="error")
        elif len(title) < 4:
            flash("title has to be at least 1 characters!", category="error")
        elif len(author) < 1:
            flash("name has to be at least 1 character")
        elif len(date) < 1 or "/" not in date:
            flash("name has to be at least 1 character and has to be in dd/mm/yy format", category="error")
        else:
            book = Books.query.filter_by(booksid = bookid).first()

            if book:
                book.title = title
                book.publish_date = date
                db.session.commit()

                authors = Authors.query.filter_by(authorid = book.authorid)
                authors.name = author
                db.session.commit()
                return redirect(url_for("views.ebooksTitle"))

            else:
                flash("bookid invalid!", category="error")
   
    return render_template("eeditbook.html")


#employee delete book
@views.route('/edeletebook', methods=['GET','POST'])
@login_required
def edeletebook():
    pass


#trends
@views.route('/etrends')
@login_required
def etrends():
    return render_template("etrends.html")


#display trends by Genre
@views.route('/etrendGenre', methods=['GET','POST'])
@login_required
def etrendGenre():
    #initialise variables
    num = 0            # number of rows / genres
    genres = []        # list of all genres
    users = []         # list of all the user_counts, each index is for each genre
    books = []         # list of all the book_counts, each index is for each genre
    authors = []       # list of all the author_counts, each index is for each genre


    labels = []        # list for x-axis
    values = []        # list for y-axis
    yaxis = "data point"


    if request.method == "POST":
        #get request data
        yaxis = request.form.get("yaxis")
        topbottom = request.form.get("topbottom")   # whether want top or bottom
        num = request.form.get("genre")        # number of rows / genres

        #conditional
        if num:
            if isinstance(num, int):
                pass
            else:
                flash("number of genres has to be an integer.", category="error")
        
        else:
            flash("number of genres has to be filled in.", category="error")


        #whether want top or bottom
        if topbottom == "top":
            genred = Genre.query.limit(num).all()
        else:
            genred = Genre.query.order_by(Genre.genreid.desc()).limit(num).all()


        #add all the genres in the genres list
        for g in genred:
            if g.genre not in genres:
                genres.append(g.genre)


        for g in genred:
            #variables
            user = []       # list to store all users for genre g
            book = []       # list to store all books for genre g
            author = []     # list to store all authors for genre g


            user_count = 0
            book_count = 0
            author_count = 0


            bookngenre = BooknGenre.query.filter_by(genreid = g.genreid).all()
           
            #for users and books
            for b in bookngenre:
                if b.userid not in user:
                    user.append(b.userid)
                    user_count += 1
                if b.bookid not in book:
                    book.append(b.bookid)
                    book_count += 1


            #for authors
            booked = Books.query.filter(Books.booksid.in_(book)).all()
            for b in booked:
                if b.authorid not in author:
                    author.append(b.authorid)
                    author_count += 1
           
            #add to users, books, authors array
            users.append(user_count)
            books.append(book_count)
            authors.append(author_count)
       
        #chart
        labels = genres
        if yaxis == "NoofUsers":
            values = users
        elif yaxis == "NoofBooks":
            values = books
        elif yaxis == "NoofAuthors":
            values = authors




    return render_template("etrendGenre.html", num = num, genres = genres, users = users, books = books, authors = authors, labels = labels, values = values, yaxis = yaxis)


#book trends
@views.route('/etrendBook', methods=['GET','POST'])
@login_required
def etrendBook():
    #initialise variables
    num = 0            # number of rows / genres
    books = []         # list of all the books
    users = []         # list of all the user_counts, each index is for each book
    genres = []        # list of all the genre_counts, each index is for each book


    labels = []        # list for x-axis
    values = []        # list for y-axis
    yaxis = "data point"


    if request.method == "POST":
        #get request data
        yaxis = request.form.get("yaxis")
        topbottom = request.form.get("topbottom")       # whether want top or bottom
        num = int(request.form.get("book"))             # number of rows / books

        #conditional
        if num:
            if isinstance(num, int):
                pass
            else:
                flash("number of books has to be an integer.", category="error")
        
        else:
            flash("number of books has to be filled in.", category="error")


        #whether want top or bottom
        if topbottom == "top":
            booked = Books.query.limit(num).all()
        else:
            booked = Books.query.order_by(Books.booksid.desc()).limit(num).all()


        #add all the books in the books list
        for b in booked:
            if b.title not in books:
                books.append(b.title)


        for b in booked:
            #variables
            user = []
            genre = []


            user_count = 0
            genre_count = 0


            bookngenre = BooknGenre.query.filter_by(bookid = b.booksid).all()


            #for users and genres
            for bg in bookngenre:
                if bg.userid not in user:
                    user.append(bg.userid)
                    user_count += 1
                if bg.genreid not in genre:
                    genre.append(bg.genreid)
                    genre_count += 1
           
            #add to users, books, authors array
            users.append(user_count)
            genres.append(genre_count)
       
        #chart
        labels = books
        if yaxis == "NoofUsers":
            values = users
        elif yaxis == "NoofGenres":
            values = genres


    return render_template("etrendBook.html", num = num, genres = genres, users = users, books = books, labels = labels, values = values, yaxis = yaxis)


#trends for Authors
@views.route('/etrendAuthor', methods=['GET','POST'])
@login_required
def etrendAuthor():

    #initialise variables
    num = 0            # number of rows / genres
    authors = []       # list of all the authors
    users = []         # list of all the user_counts, each index is for each author
    books = []         # list of all the book_counts, each index is for each author


    labels = []        # list for x-axis
    values = []        # list for y-axis
    yaxis = "data point"


    if request.method == "POST":
        #get request data
        yaxis = request.form.get("yaxis")
        topbottom = request.form.get("topbottom")   # whether want top or bottom
        num = int(request.form.get("author"))       # number of rows / authors

        #conditional
        if num:
            if isinstance(num, int):
                pass
            else:
                flash("number of authors has to be an integer.", category="error")
        
        else:
            flash("number of authors has to be filled in.", category="error")


        #whether want top or bottom
        if topbottom == "top":
            authored = Authors.query.limit(num).all()
        else:
            authored = Authors.query.order_by(Authors.authorid.desc()).limit(num).all()


        #add all the authors in the authors list
        for a in authored:
            if a.name not in authors:
                authors.append(a.name)


        for a in authored:
            #search all bookngenres by an author
            booking = Books.query.filter_by(authorid = a.authorid)
            bookids = [b.booksid for b in booking]
            bookngenre = BooknGenre.query.filter(BooknGenre.bookid.in_(bookids)).all()


            #variables
            user = []
            user_count = 0
            book_count = len(bookids)


            #for users and genres
            for bg in bookngenre:
                if bg.userid not in user:
                    user.append(bg.userid)
                    user_count += 1
           
            #add to users, books, authors array
            users.append(user_count)
            books.append(book_count)
       
        #chart
        labels = authors
        if yaxis == "NoofUsers":
            values = users
        elif yaxis == "NoofBooks":
            values = books


    return render_template("etrendAuthor.html", num = num, authors = authors, users = users, books = books, labels = labels, values = values, yaxis = yaxis)




@views.route('/erecommendpage', methods=['GET','POST'])
@login_required
def erecommendpage():
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")

        #conditionals
        if len(title) < 1:
            flash("title has to be at least one character.", category="error")
        elif len(author) < 1:
            flash("author has to be at least one character.", category="error")
        else:
            for i in range(3):
                userid = request.form.get("userid"+str(i+1))

                #conditional
                if len(userid) < 1:
                    flash("userid must be more than one digit.", category="error")
                else:
                    #if not isinstance(userid, int):
                        #flash("userid must be an integer", category="error")
                    check_user = User.query.filter_by(userid = userid).first()
                    if not check_user:
                        flash("user does not exist.", category="error")

                delrecom = Recommend.query.filter_by(userid = userid).first()
                if delrecom:
                    db.session.delete(delrecom)
                    db.session.commit()
                recommend = Recommend(title = title, author = author, userid = userid)
                db.session.add(recommend)
                db.session.commit()

    return render_template("erecommendpage.html")


