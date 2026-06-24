from flask import Blueprint, render_template, session, request 
from utils.codeforces_api import verify_and_get_user

# Creating blueprint object to connect it with app.py
auth_bp = Blueprint('auth',__name__)

@auth_bp.route('/login',methods = ['POST'])
def login():
    # Get the handle of the user 
    handle = request.form.get('handle')

    user_data, error = verify_and_get_user(handle)
    # print("this is the user data :",user_data, end='------------------')


    if user_data :
        if 'rank' not in user_data.keys():
            user_data['rank']  = 'No Rank'
        session['user']= user_data
        return render_template('index.html',user=user_data,show_form=False)
    else:
        return render_template('index.html',error=error,show_form=True)
    
@auth_bp.route('/logout')
def logout():
    #Clear all user data and logout
    session.pop('user',None)
    return render_template('index.html',show_form=True)
