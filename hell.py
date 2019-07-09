# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 11:03:59 2019

@author: AbhilashSrivastava
"""
from flask import Flask,render_template,request
from flask_mysqldb import MySQL
import yaml
app=Flask(__name__)


db=yaml.load(open('db.yaml','r'))

app.config['MYSQL_HOST']=db['mysql_host']
app.config['MYSQL_USER']=db['mysql_user']
app.config['MYSQL_PASSWORD']=db['mysql_password']
app.config['MYSQL_DB']=db['mysql_db']

mysql=MySQL(app)

@app.route('/', methods=['GET','POST'])
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
"""
@app.route('/information/<name>')
def info(name):
    if(name[-1]!='y'):
        return "user:{}".format(name+'y')
    else:
        name=name[:-1]+'iful'
        return "user:{}".format(name)
"""
if __name__=='__main__':
    app.run(debug=True)