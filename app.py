from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3
from sqlalchemy import orm

app = Flask(__name__)
# postgress
db = SQLAlchemy()

#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost:3307/dt"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///backup.db"
app.config['SECRET_KEY'] = "random string"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "abcabc"
db.init_app(app)


class Feed(db.Model):
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    order = db.Column(db.Text(500), nullable=False)
    rate = db.Column(db.String(30)) 
    date_created = db.Column(db.DATE, default=datetime.now(), nullable=False)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    date_created = db.Column(db.DATE, default=datetime.now(), nullable=False)

@app.route("/", methods=['GET','POST'])
def home():
      return render_template("index.html",isIndex=True)


@app.route("/order", methods=['GET','POST'])
def order():
    if not session.get('username'):
        flash('Please login first','warning')
        return render_template("login.html")
    else:
        
        if request.method=='POST':
            exp = request.form['exp']
            com = request.form['ord']
            uid = session['id']
            
            
            feed = Feed(order=com, rate=exp,user_id=uid )
            db.session.add(feed)
            db.session.commit()

            

            flash('Your order Successfully submit !','success') 
            return render_template("order.html")
        
    return render_template("order.html")


@app.route("/reg", methods=['GET', 'POST'])
def reg():

    if request.method == "POST":
        name = request.form.get("name").lower()
        email = request.form.get("email")
        password = request.form.get("password")
        phone = request.form.get("phone")

        user = User.query.filter_by(email=email).first()
        if not user:
            # Creat new record

            usere = User(name=name, email=email,
                         password=password, phone=phone)

            db.session.add(usere)
            db.session.commit()
            flash('Successfully register!','success')
            return render_template("login.html")

        else:
            flash('Username or Email already exists','danger')
            return render_template("reg.html")

    return render_template("reg.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    session.clear()
    if request.method == "POST":

        email = request.form.get("email1")
        password = request.form.get("password1")
        
       

        user = User.query.filter_by(email=email, password=password).first()
        
    
        if user :
            session['username'] = email
            session['name'] = user.name
            session['id'] = user.id
            session['phone'] = user.phone
            
            if not session['username']=='yousafzai612@gmail.com':
                flash('Wellcome in ','inf')
                return redirect(url_for("order"))
                
            else:
                session['admin']= user.email
                flash('Wellcome!','success')
                return redirect(url_for("table"))
            

        else:
            flash('Username and password doesnot match','warning')

    return render_template("login.html")

@app.route("/delete/user/<id>", methods=['GET', 'POST'])
def delete_user(id):
    if not session.get('admin') :
        session.clear()
        flash('Unauthorized access login correctly! ','danger')
        return render_template("login.html")
    else:
       
        duser = User.query.filter(User.id==id).first()

        db.session.delete(duser)
        db.session.commit()
        flash('Successfully Deleted!','success')
        return redirect(url_for('user'))

@app.route("/delete/order/<id>", methods=['GET', 'POST'])
def delete_ord(id):
    if not session.get('admin') :
        session.clear()
        flash('Unauthorized access login correctly! ','danger')
        return render_template("login.html")
    
    else:
        fe = Feed.query.filter(Feed.id==id).first()

        db.session.delete(fe)
        db.session.commit()
        flash('Successfully Deleted!','success')
        return redirect(url_for('table'))

@app.route("/table", methods=['GET','POST'])
def table():
    feed = db.session.query(User, Feed).\
    filter(Feed.user_id == User.id).order_by(Feed.date_created.desc()).all()
    
    if request.method == 'POST' and 'tag' in request.form:
        name = request.form.get("name")
        
        tag = request.form["tag"]
        search = "%{}%".format(tag) 


        feed = db.session.query(User, Feed).\
        filter(Feed.user_id == User.id).order_by(
        Feed.date_created.desc()).filter(User.name.like(search)).all()
        return render_template('table.html', feed=feed , tag=tag)

    return render_template("table.html",feed=feed)

@app.route("/table/users",methods=['GET', 'POST'])
def user():

    if session.get('admin') :
        user = User.query.all()
        
        feed = db.session.query(User, Feed).\
        filter(Feed.user_id == User.id).order_by(Feed.date_created.desc()).all()
        
        if request.method == 'POST' and 'tag' in request.form:
            name = request.form.get("name")
       
       
            tag = request.form["tag"]
            search = "%{}%".format(tag) 

            user = User.query.filter(User.name.like(search)) 
       

            return render_template('user.html', user=user,tag=tag, feed=feed)
        
        else:
            return render_template('user.html', user=user,feed=feed )
    else:
        session.clear()
        flash('Unauthorized access login correctly! ','danger')
        return render_template("login.html")

@app.route("/update/user/<id>", methods=['GET', 'POST'])
def update_user(id):
    if not session.get('admin') :
        session.clear()
        flash('Unauthorized access login correctly! ','danger')
        return render_template("login.html")
    else:
        user = User.query.all()
        feed = db.session.query(User, Feed).\
        filter(Feed.user_id == User.id).order_by(Feed.date_created.desc()).all()
    
        if request.method=="POST":
            name = request.form.get("name").lower()
            email = request.form.get("email")
            password = request.form.get("password")
            phone = request.form.get("phone")
            
            serv = db.session.query(User).filter_by(id=id).first()
            useru = User.query.filter_by(id = id).first()
            useru.name = name
            useru.email = email
            useru.password = password
            useru.phone= phone
            db.session.commit()
            flash('Successfully Updated!','success')
            return redirect(url_for('user'))

        else:
            serv = User.query.filter(User.id == id).first()
            return render_template("upus.html", feed=feed,user=user,serv=serv)

@app.route("/add/user", methods=['GET', 'POST'])
def adduser():
    
    if not session.get('admin') :
        session.clear()
        flash('Unauthorized access login correctly! ','danger')
        return render_template("login.html")
    else:
        user = User.query.all()
        feed = db.session.query(User, Feed).\
        filter(Feed.user_id == User.id).order_by(Feed.date_created.desc()).all()
        
        if request.method == "POST":
            name = request.form.get("name").lower()
            email = request.form.get("email")
            password = request.form.get("password")
            phone = request.form.get("phone")

            user = User.query.filter_by(email=email).first()
            if not user:
            # Creat new record
                usere = User(name=name, email=email,password=password, phone=phone)

                db.session.add(usere)
                db.session.commit()
                flash('Successfully added!','success')
                return redirect(url_for('user'))

            else:
                flash('Username or Email already exists','danger')
                return redirect (url_for(('adduser')))
 
        return render_template('addus.html', user=user,feed=feed)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
   app.run(debug=True)
