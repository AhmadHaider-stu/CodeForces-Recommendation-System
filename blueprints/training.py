from flask import Blueprint, render_template, session
from models.predictor import predictions
from utils.codeforces_api import get_all_problems, get_user_submissions

# Creating blueprint object to connect it with app.py
training_bp = Blueprint('training', __name__)


@training_bp.route('/model')
def model():

    # Auth check 
    if session.get('user') is None:
        return render_template('index.html', error="Please enter your handle", show_form=True)

    user   = session.get('user')
    # print(user)
    handle = user.get('handle')
    rating = user.get('rating')
    
    # ─── Fetch problems ──────
    problems, problems_err = get_all_problems()
    if problems_err:
        return render_template(
            'training.html',
            user=user,
            error=f"Could not load problem set: {problems_err}"
        )

    # ─── Fetch user submissions ────
    user_sub, sub_err = get_user_submissions(handle)
    if sub_err:
        return render_template(
            'training.html',
            user=user,
            error=f"Could not load submissions for '{handle}': {sub_err}"
        )

    # ─── Generate recommendations ────
    try:
        recommendations = predictions(
            problems=problems,      
            userSub=user_sub,       
            userRating=rating     
        )
    except ValueError as e:
        return render_template(
            'training.html',
            user=user,
            error=str(e)
        )

    return render_template('training.html', user=user, recommendations=recommendations)