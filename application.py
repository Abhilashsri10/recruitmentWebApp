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
from flask import Flask,render_template,url_for,request,flash,redirect,session,logging,Response
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session,sessionmaker
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL
import yaml
from forms import StatusForm,SearchForm,RegistrationForm, LoginForm ,AdminLoginForm
import random
import os
import urllib.request
import profile
from flask_login import LoginManager,login_user,current_user,logout_user,login_required
import sys,json

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

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'Login'
    
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
        notice=request.form.get("notice")
        image_file=request.form.get("image")
        resume=request.form.get("resume")
        phno=request.form.get("phno")
        source=request.form.get("source")
        skills=request.form.get("skills")
        password=request.form.get("password")
        confirm=request.form.get("confirm_password")
        secure_password=sha256_crypt.encrypt(str(password))
        
        if password==confirm:
            db.execute(f"INSERT INTO candid(name,email,jobId,image,phno,password,resume,noticep,skills,source) VALUES(:name,:email,:jId,:image,:phno,:password,:resume,:noticep,:skills,:source)",
                                           {"name":name,"email":email,"jId":jId,"image":image_file,"phno":phno,"password":secure_password,"resume":resume,"noticep":notice,"skills":skills,"source":source})
            db.commit()
            flash(f'Account created for {form.username.data}!','success')
            return redirect(url_for('Login'))
        else:
            flash("password does not match","danger")
            return render_template("register.html",form=form)
    if form.validate_on_submit():
        
        return redirect(url_for('Login'))
    return render_template('register.html',title='Register',form=form)
    
@app.route('/login',methods=['GET','POST'])
def Login():
    form=LoginForm()
    if request.method=='POST':
        email=request.form.get("email")
        password=request.form.get("password")
        emaildata=db.execute("SELECT email FROM candid WHERE email=:email",{"email":email}).fetchone()
        passworddata=db.execute("SELECT password FROM candid WHERE email=:email",{"email":email}).fetchone()[0]
        if emaildata is None:
            flash("No email","danger")
            return render_template("login.html",form=form)
        else:
            if sha256_crypt.verify(password,passworddata):
                session['logged_in']=True
                session['id']=request.form['email']
                flash("You are now logged in",'success')
                #flash(db.execute("Select * from candid WHERE email=:email",{"email":session['username']}).fetchone()[1])
                return redirect(url_for("prof"))
            else:
                flash("incorrect password","danger")
                return render_template("login.html",form=form)
    return render_template('login.html',title='Login',form=form)
@app.route('/adminlogin',methods=['GET','POST'])
def AdLogin():
    form=AdminLoginForm()
    if request.method=='POST':
        adminId=request.form.get("adminId")
        password=request.form.get("password")
        adIddata=db.execute("SELECT adminId FROM admins WHERE adminId=:adminId",{"adminId":adminId}).fetchone()
        passworddata=db.execute("SELECT password FROM admins WHERE adminId=:adminId",{"adminId":adminId}).fetchone()[0]
        if adIddata is None:
            flash("No adminId","danger")
            return render_template("adminlogin.html",form=form)
        else:
            if sha256_crypt.verify(password,passworddata):
                session['loggedin']=True
                session['admin']=request.form['adminId']
                flash("You are now logged in",'success')
                return redirect(url_for('adminHome'))
            else:
                flash("incorrect password","danger")
                return render_template("adminlogin.html",form=form)
    return render_template('adminlogin.html',title='Login',form=form)
@app.route('/adminHome')
def adminHome():
    return render_template('adminHome.html', title='Home')
#dashboard to enter the status.
@app.route('/dashboard')
def dashboard():
    return render_template('profilePage.html', title='dashboard')
@app.route('/users')
def info():
    cur=mysql.connection.cursor()
    resultValue=cur.execute("select * from candid;")
    if resultValue>0:
        userDetails=cur.fetchall()
        if(userDetails[0][7].endswith('/view?usp=sharing')):
            userR=userDetails[0][7][:-17]+'?export=download'
            return render_template('users.html',userDetails=userDetails,userR=userR)


@app.route("/logoutcandid")
def logoutcandid():
    if 'logged_in' in session:
        session.pop('id',None)
        flash("You have been logged out!",'success')
    return redirect(url_for('home'))

@app.route("/logoutadmin")
def logoutadmin():
    if 'loggedin' in session:
        session.pop('admin',None)
        flash("You have been logged out!")
    #gc.collect()
    return redirect(url_for('AdLogin'))
@app.route('/prof')
#@login_required
def prof():
    if 'logged_in' in session:
        flash("logged",'success')
        userDetails=db.execute("SELECT * from candid where email=:email;",{"email":session['id']}).fetchone()
        statDetails=db.execute("SELECT * from candidStat where id=:id;",{"id":userDetails[0]}).fetchone()
        if(statDetails==None):
            statDetails=['NULL','NULL','NULL','NULL','NULL','NULL','NULL','NULL']
            return render_template('profilePage.html',userDetails=userDetails,statDetails=statDetails)
        return render_template('profilePage.html',userDetails=userDetails,statDetails=statDetails)

@app.route('/adprof',methods=['GET','POST'])
def adprof():
    if 'loggedin' in session:
        data=request.get_json()
        flash(data)
        userDetails=db.execute("SELECT * from candid where id=:id;",{"id":data[0]['id']}).fetchone()
        flash(userDetails)
        statDetails=db.execute("SELECT * from candidStat where id=:id;",{"id":userDetails[0]}).fetchone()
        return render_template('profilePage.html',userDetails=userDetails,statDetails=statDetails)


           
@app.route('/stat',methods=['GET','POST'])
def statEnt():
    form=StatusForm()
    if request.method=='POST':
        idc=request.form.get("Id")
        rd=request.form.get("rounds")
        st=request.form.get("stat")
        result1=db.execute("SELECT COUNT(id) FROM candidStat WHERE id=:id;",{"id":idc}).fetchone()[0]
        result2=db.execute("SELECT COUNT(id) FROM candid WHERE id=:id;",{"id":idc}).fetchone()[0]
        
        if(result1==0 and result2==1):
            db.execute(f"INSERT INTO candidStat(id,{rd}) VALUES(:id,:rounds);",
                                           {"id":int(idc),"rounds":st})    
            db.commit()
            flash(f'Entry done!','success')
        elif(result2==1 and result1!=0):
            db.execute(f"UPDATE candidStat SET {rd}=:st WHERE id={int(idc)};",{"st":st})
            db.commit()
            flash(f'Entry done!','success')
        return redirect(url_for('adminHome'))
    return render_template('statent.html',form=form)

#filters
@app.route("/ihome", methods=['GET', 'POST'])
def search():
    form = SearchForm()
    result = None
    if form.validate_on_submit():
        #curs = db.connection.cursor()
        choice = form.s.data
        skills = request.form.get('skills')
        jobId=request.form.get('jobId')
        rounds=request.form.get('rounds')
        stages=request.form.get('stages')
        result=db.execute(f"SELECT c.id,c.name,s.{rounds},c.skills FROM candid as c RIGHT JOIN candidStat as s ON c.id=s.id WHERE c.skills={skills} AND s.{rounds}={stages};")
        flash(result.fetchone())
        return redirect(url_for('adminHome'))
    return render_template('searchBar.html', form=form, result=result)

    
    
    
    
