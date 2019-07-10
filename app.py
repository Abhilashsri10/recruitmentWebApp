# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 11:41:56 2019

@author: AbhilashSrivastava
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 11:03:59 2019

@author: AbhilashSrivastava
"""
from flask import Flask,render_template,url_for,request,flash,redirect,session,logging
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session,sessionmaker
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL
import yaml
from forms import RegistrationForm, LoginForm
import random


app=Flask(__name__)


db=yaml.load(open('db.yaml','r'))

app.config['MYSQL_HOST']=db['mysql_host']
app.config['MYSQL_USER']=db['mysql_user']
app.config['MYSQL_PASSWORD']=db['mysql_password']
app.config['MYSQL_DB']=db['mysql_db']

app.config['SECRET_KEY']='4dd89dffe2f2954605c7f1d6e2d0f2d4'

engine=create_engine("mysql+pymysql://root:lapulga@10@localhost/flaskapp")
db=scoped_session(sessionmaker(bind=engine))
mysql=MySQL(app)

    
@app.route('/')
def home():
    return render_template('home.html',title='HomePage')

@app.route('/register',methods=['GET','POST'])
def registration():
    form=RegistrationForm()
    if request.method=='POST':
        name=request.form.get("username")
        email=request.form.get("email")
        jId=request.form.get("jobId")
        password=request.form.get("password")
        confirm=request.form.get("confirm_password")
        secure_password=sha256_crypt.encrypt(str(form.password))
        
        if password==confirm:
            db.execute(f"INSERT INTO candid(name,email,jobId,password) VALUES(:name,:email,:jId,:password)",
                                           {"name":name,"email":email,"jId":jId,"password":secure_password})
            db.commit()
            return redirect(url_for('Login'))
        else:
            return render_template("register.html")
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!','success')
        return redirect(url_for('home'))
    return render_template('register.html',title='Register',form=form)
    
@app.route('/login',methods=['GET','POST'])
def Login():
    form=LoginForm()
    if form.validate_on_submit():
        flash(f'Logged in!','success')
        return redirect(url_for('home'))
    return render_template('login.html',title='Login',form=form)

@app.route('/enter', methods=['GET','POST'])
def index():
    if request.method=='POST':
        userDetails=request.form
        name=userDetails['name']
        email=userDetails['email']
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO users(name,email) VALUES(%s,%s)",(name,email))
        mysql.connection.commit()
        cur.close()
        return 'success'
    return render_template("form.html")

@app.route('/users')
def info():
    cur=mysql.connection.cursor()
    resultValue=cur.execute("select * from users")
    if resultValue>0:
        userDetails=cur.fetchall()
        return render_template('users.html',userDetails=userDetails)

        
if __name__=='__main__':
    app.run(debug=True,host='127.0.0.1',port=2000)
    
    
    
    
    
"""
if request.method=='POST':
        userDetails=request.form
        cur=mysql.connection.cursor()
        cur.execute("CREATE table [if not exits] {}(status1,status2,status3,status4,hr,offer,joined)".format(form.username))
        mysql.connection.commit()
        cur.close()
        """