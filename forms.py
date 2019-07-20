# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 11:28:09 2019

@author: AbhilashSrivastava
"""
from flask_wtf import FlaskForm
from wtforms import SelectField,IntegerField,StringField,PasswordField,SubmitField , BooleanField
from wtforms.validators import DataRequired, Length, Email,EqualTo

class RegistrationForm(FlaskForm):
        count=0
        username=StringField('Username',validators=[DataRequired(),Length(min=2,max=30)])
        email=StringField('Email', validators=[DataRequired(),Email()])
        choices = [('1001', 'full stack dev'), ('1002', 'ui/ux dev'), ('1003', 'data engineer'), ('1004', 'data scientist')]
        jobId=SelectField('select job',choices=choices)
        #image=StringField('image',validators=[DataRequired()])
        resume=StringField('resume',validators=[DataRequired()])
        notice=StringField('notice',validators=[DataRequired()])
        phno=StringField('phno',validators=[DataRequired()])
        skills=StringField('skills',validators=[DataRequired()])
        source=StringField('source',validators=[DataRequired()])
        password=PasswordField('password',validators=[DataRequired()])
        confirm_password=PasswordField('confirm_password',validators=[DataRequired(),EqualTo('password')])
        submit=SubmitField('sign up')
        
class LoginForm(FlaskForm):
        #username=StringField('Username',validators=[DataRequired(),Length(min=2,max=30)])
        email=StringField('Email', validators=[DataRequired(),Email()])
        password=PasswordField('password',validators=[DataRequired()])
        #confirm_password=PasswordField('confirm_password',validators=[DataRequired(),EqualTo('password')])
        remember=BooleanField('Remember me')
        submit=SubmitField('Login')
        
class AdminLoginForm(FlaskForm):
        adminId=StringField('adminId', validators=[DataRequired()])
        password=PasswordField('password',validators=[DataRequired()])
        remember=BooleanField('Remember me')
        submit=SubmitField('login')
class SearchForm(FlaskForm):
        #choices = [('Skill', 'Skill'), ('Stages', 'Stages'), ('Notice Period', 'Notice Period')]
        choice1 = [('NULL','NULL'),('scheduled', 'scheduled'), ('Selected', 'Selected'), ('Rejected', 'Rejected'), ('On Hold', 'On Hold')]
        choice2 = [('NULL','NULL'),('r1','1'),('r2','2'),('r3','3'),('r4','4'),('hr','hr'),('os','offer status'),('joined','joined')]
        choice3 = [('NULL','NULL'),('1001', 'full stack dev'), ('1002', 'ui/ux dev'), ('1003', 'data engineer'), ('1004', 'data scientist')]
        stages=SelectField('stages',choices=choice1)
        rounds=SelectField('rounds',choices=choice2)
        s = StringField('Notice Period')
        e = StringField('skills')
        jobid=SelectField('jobId',choices=choice3)
        submit = SubmitField('Go')
class jobVacancy(FlaskForm):
        jobId=StringField('JobID',validators=[DataRequired()])
        job=StringField('job',validators=[DataRequired()])
        no=IntegerField('noOfVac',validators=[DataRequired()])
        submit = SubmitField('Go')
        
class StatusForm(FlaskForm):
    Id=StringField('id',validators=[DataRequired()])
    dd = [('scheduled', 'scheduled'), ('Selected', 'Selected'), ('Rejected', 'Rejected'), ('On Hold', 'On Hold')]
    dd1= [('r1','1'),('r2','2'),('r3','3'),('r4','4'),('hr','hr'),('os','offer status'),('joined','joined')]
    rounds=SelectField('rounds',choices=dd1)
    stat=SelectField('status',choices=dd)
    submit = SubmitField('Submit')