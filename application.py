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
from flask import jsonify,Flask,render_template,url_for,request,flash,redirect,session,logging,Response
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session,sessionmaker
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL
import yaml
from forms import jobVacancy,StatusForm,SearchForm,RegistrationForm, LoginForm ,AdminLoginForm
import random
import os
import urllib.request
import profile
from flask_login import LoginManager,login_user,current_user,logout_user,login_required
import sys,json
from google_drive_downloader import GoogleDriveDownloader as gdd
from realApp import download

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

#HOME pages    
@app.route('/')
def home():
    return render_template('home.html',title='Home')
@app.route('/adminHome')
def adminHome():
    data=db.execute("SELECT jobId,count(jobId) FROM candid GROUP BY jobId;")
    #data=db.execute("SELECT j.job,count(c.jobId) FROM candid as c RIGHT JOIN jobVac as j ON c.jobId=j.jobId GROUP BY c.jobId;")
    fetchData=data.fetchall();
    graphdata=[]
    for ele in fetchData:
        graphdata.append([str(ele[0]),ele[1]])
    data1=db.execute("SELECT jobId,job,noOfVac FROM jobVac;")
    fetchData1=data1.fetchall()
    graphdata1=[]
    for ele in fetchData1:
        graphdata1.append(['('+str(ele[0])+')'+ele[1],ele[2]])
    return render_template('mainDashboard.html', title='adminHome',graphdata=graphdata,graphdata1=graphdata1)


#Registration Page
@app.route('/register',methods=['GET','POST'])
def registration():
    form=RegistrationForm()
    if request.method=='POST':
        name=request.form.get("username")
        email=request.form.get("email")
        jId=request.form.get("jobId")
        notice=request.form.get("notice")
        #image_file=request.form.get("image")
        resume=request.form.get("resume")
        phno=request.form.get("phno")
        source=request.form.get("source")
        skills=request.form.get("skills")
        password=request.form.get("password")
        confirm=request.form.get("confirm_password")
        secure_password=sha256_crypt.encrypt(str(password))
        
        if password==confirm:
            db.execute(f"INSERT INTO candid(name,email,jobId,phno,password,resume,noticep,skills,source) VALUES(:name,:email,:jId,:phno,:password,:resume,:noticep,:skills,:source)",
                                           {"name":name,"email":email,"jId":jId,"phno":phno,"password":secure_password,"resume":resume,"noticep":notice,"skills":skills,"source":source})
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
        #imagedata=db.execute("SELECT image FROM candid WHERE email=:email",{"email":email}).fetchone()[0]
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


#HR login with graph data
@app.route('/adminlogin',methods=['GET','POST'])
def AdLogin():
    form=AdminLoginForm()
    if request.method=='POST':
        adminId=request.form.get("adminId")
        password=request.form.get("password")
        adIddata=db.execute("SELECT adminId FROM admins WHERE adminId=:adminId",{"adminId":adminId}).fetchone()
        passworddata=db.execute("SELECT password FROM admins WHERE adminId=:adminId",{"adminId":adminId}).fetchone()[0]
        #for applied
        data=db.execute("SELECT jobId,count(jobId) FROM candid GROUP BY jobId;")
        fetchData=data.fetchall()
        graphdata=[]
        for ele in fetchData:
            graphdata.append([str(ele[0]),ele[1]])
            
        #for vacancy
        data1=db.execute("SELECT jobId,job,noOfVac FROM jobVac;")
        fetchData1=data1.fetchall()
        graphdata1=[]
        for ele in fetchData1:
            graphdata1.append(['('+str(ele[0])+')'+ele[1],ele[2]])
        if adIddata is None:
            flash("No adminId","danger")
            return render_template("adminlogin.html",form=form)
        else:
            if sha256_crypt.verify(password,passworddata):
                session['loggedin']=True
                session['admin']=request.form['adminId']
                flash("You are now logged in",'success')
                return render_template("mainDashboard.html",graphdata=json.dumps(graphdata),graphdata1=json.dumps(graphdata1))
            else:
                flash("incorrect password","danger")
                return render_template("adminlogin.html",form=form)
    return render_template('adminlogin.html',title='Login',form=form)

#dashboard to enter the status.
@app.route('/dashboard')
def dashboard():
    return render_template('profilePage.html', title='dashboard')
@app.route('/users')
def info():
    #cur=mysql.connection.cursor()
    resultValue=db.execute("select * from candid;")
    userDetails=resultValue.fetchall()
    db.commit()
    if(userDetails[0][7].endswith('/view?usp=sharing')):
        userR=userDetails[0][7][:-17]+'?export=download'
        return render_template('users.html',userDetails=userDetails,userR=userR)
    return render_template('users.html',userDetails=userDetails)
    #return redirect(url_for('adminHome'))
#logins
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
        flash("You have been logged out!",'success')
    #gc.collect()
    return redirect(url_for('AdLogin'))



@app.route('/prof')
#@login_required
def prof():
    if 'logged_in' in session:
        flash("logged",'success')
        userDetails=db.execute("SELECT * from candid where email=:email;",{"email":session['id']}).fetchone()
        statDetails=db.execute("SELECT * from candidStat where id=:id;",{"id":userDetails[0]}).fetchone()
        #file_name=profile.randomString(4)
        file_name='messi'
        #download(userDetails[4],file_name)
        if(statDetails==None):
            statDetails=['NULL','NULL','NULL','NULL','NULL','NULL','NULL','NULL']
            return render_template('profilePage.html',userDetails=userDetails,statDetails=statDetails,file_name=file_name)
        return render_template('profilePage.html',userDetails=userDetails,statDetails=statDetails,file_name=file_name)

#profile list and resume download
@app.route('/adprof',methods=['POST'])
def adprof():
    form=StatusForm()
    if 'loggedin' in session:
        rf=request.get_json(silent=True)
        userDetails=db.execute("SELECT * from candid where id=:id;",{"id":rf['val']}).fetchone()
        statDetails=db.execute("SELECT * from candidStat where id=:id;",{"id":userDetails[0]}).fetchone()
        
        return render_template('profilePageadm.html',userDetails=userDetails,statDetails=statDetails,form=form)
    #return render_template('profilePage.html',userDetails=userDetails,statDetails=statDetails)

           
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
            result=db.execute(f"SELECT c.id,c.name,c.email,c.phno,s.r1,s.r2,s.r3,s.r4,s.hr,s.os,s.joined FROM candid as c RIGHT JOIN candidStat as s ON c.id=s.id WHERE c.id={int(idc)};")
            details=result.fetchall()
            db.commit()
            flash(f'Entry done!','success')
            return render_template('dashboard.html',details=details)
        elif(result2==1 and result1!=0):
            db.execute(f"UPDATE candidStat SET {rd}=:st WHERE id={int(idc)};",{"st":st})
            result=db.execute(f"SELECT c.id,c.name,c.email,c.phno,s.r1,s.r2,s.r3,s.r4,s.hr,s.os,s.joined FROM candid as c RIGHT JOIN candidStat as s ON c.id=s.id WHERE c.id={int(idc)};")
            details=result.fetchall()
            db.commit()
            flash(f'Update done!','success')
            return render_template('dashboard.html',details=details)
    return render_template('statent.html',form=form)

#vacancy entry
@app.route("/vac",methods=['GET','POST'])
def jobVac():
    form=jobVacancy()
    if request.method=='POST':
        jobId=request.form.get("jobId")
        job=request.form.get("job")
        no=request.form.get("no")
        count=db.execute("SELECT COUNT(jobId) from jobVac WHERE jobId=:jobId;",{"jobId":jobId}).fetchone()[0]
        if(count==0):
            db.execute("INSERT INTO jobVac(jobId,job,noOfVac) VALUES(:jobId,:job,:no);",{"jobId":jobId,"job":job,"no":int(no)})
            db.commit()
            flash("Entry Done!",'success')
        else:
            db.execute("UPDATE jobVac SET noOfVac=:no WHERE jobId=:jobId;",{"no":no,"jobId":jobId})
            flash("updated",'success')
        #userDetails=db.execute("SELECT * from candid where id=:id;",{"id":id}).fetchone()
        #statDetails=db.execute("SELECT * from candidStat where id=:id;",{"id":userDetails[0]}).fetchone()
        return redirect(url_for('adminHome'))#render_template('profilePageadm.html')#,userDetails=userDetails,statDetails=statDetails)
    return render_template('jobVc.html',form=form)


#filters
@app.route("/ihome", methods=['GET', 'POST'])
def search():
    form = SearchForm()
    result = None
    if form.validate_on_submit():
        #curs = db.connection.cursor()
        #notice = request.form.get('s')
        skills = request.form.get('e')
        jobId=request.form.get('jobid')
        rounds=request.form.get('rounds')
        stages=request.form.get('stages')
        if(skills!=None and jobId=="NULL" and stages=="NULL" and rounds=="NULL"):
            result=db.execute(f"SELECT c.id,c.name,c.email,c.phno,s.r1,s.r2,s.r3,s.r4,s.hr,s.os,s.joined FROM candid as c RIGHT JOIN candidStat as s ON c.id=s.id WHERE c.skills like :skills;",{"skills":'%'+skills+'%'})
            details=result.fetchall()
            return render_template('dashboard.html',details=details)
        elif(skills!=None and jobId=="NULL" and stages!="NULL" and rounds!="NULL"):
            result=db.execute(f"SELECT c.id,c.name,c.email,c.phno,s.r1,s.r2,s.r3,s.r4,s.hr,s.os,s.joined FROM candid as c RIGHT JOIN candidStat as s ON c.id=s.id WHERE c.skills like :skills AND s.{rounds}=:stages;",{"skills":'%'+skills+'%',"stages":stages})
            details=result.fetchall()
            return render_template('dashboard.html',details=details)
        elif(skills!=None and jobId!="NULL" and stages=="NULL" and rounds=="NULL"):
            result=db.execute(f"SELECT c.id,c.name,c.email,c.phno,s.r1,s.r2,s.r3,s.r4,s.hr,s.os,s.joined FROM candid as c RIGHT JOIN candidStat as s ON c.id=s.id WHERE c.skills like :skills AND c.jobId={jobId};",{"skills":'%'+skills+'%'})
            details=result.fetchall()
            return render_template('dashboard.html',details=details)
        elif(skills!=None and jobId!="NULL" and stages!="NULL" and rounds!="NULL"):
            result=db.execute(f"SELECT c.id,c.name,c.email,c.phno,s.r1,s.r2,s.r3,s.r4,s.hr,s.os,s.joined FROM candid as c RIGHT JOIN candidStat as s ON c.id=s.id WHERE c.skills like :skills AND s.{rounds}=:stages AND c.jobId={jobId};",{"skills":'%'+skills+'%',"stages":stages})
            details=result.fetchall()
            return render_template('dashboard.html',details=details)
        elif(skills==None and jobId!="NULL" and stages=="NULL" and rounds=="NULL"):
            result=db.execute(f"SELECT c.id,c.name,c.email,c.phno,s.r1,s.r2,s.r3,s.r4,s.hr,s.os,s.joined FROM candid as c RIGHT JOIN candidStat as s ON c.id=s.id WHERE c.jobId={jobId};")
            details=result.fetchall()
            return render_template('dashboard.html',details=details)
        elif(skills==None and jobId!="NULL" and stages!="NULL" and rounds!="NULL"):
            result=db.execute(f"SELECT c.id,c.name,c.email,c.phno,s.r1,s.r2,s.r3,s.r4,s.hr,s.os,s.joined FROM candid as c RIGHT JOIN candidStat as s ON c.id=s.id WHERE s.{rounds}=:stages AND c.jobId={jobId};",{"stages":stages})
            details=result.fetchall()
            return render_template('dashboard.html',details=details)
    return render_template('searchBar.html', form=form, result=result)

#graph clickable functionality
@app.route('/graphFilters',methods=['POST'])
def graphFilters():
    data=request.get_json(silent=True)
    #data=data['val'][6:]
    dataId=data['val']
    result=db.execute(f"SELECT c.id,c.name,c.email,c.phno,s.r1,s.r2,s.r3,s.r4,s.hr,s.os,s.joined FROM candid as c RIGHT JOIN candidStat as s ON c.id=s.id WHERE c.jobId={int(dataId)};")
    details=result.fetchall()
    db.commit()
    return render_template('dashboard.html',details=details)
    
@app.route('/graphFiltersav',methods=['POST'])
def graphFiltersav():
    data=request.get_json(silent=True)
    dataId=data['val'][1:5]
    result1=db.execute(f"SELECT noOfVac FROM jobVac WHERE jobId={int(dataId)};")
    
    #result=db.execute(f"SELECT c.id,c.name,c.email,c.phno,s.r1,s.r2,s.r3,s.r4,s.hr,s.os,s.joined FROM candid as c RIGHT JOIN candidStat as s ON c.id=s.id WHERE c.jobId={int(dataId)};")
    details=result1.fetchall()
    db.commit()
    return render_template('jobProf.html',details=details)
        
    
    
    
