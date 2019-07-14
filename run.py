# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 15:36:26 2019

@author: AbhilashSrivastava
"""

from application import app

if __name__=='__main__':
    #app.secret_key='4dd89dffe2f2954605c7f1d6e2d0f2d4'
    app.run(debug=True,host='127.0.0.1',port=2040)