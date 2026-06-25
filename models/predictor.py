import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.ensemble import RandomForestRegressor
from lightgbm import LGBMRegressor
from sklearn.model_selection import cross_val_score


# FIX THE ZERO SUBMISSION USERS 
def predictions(problems, userSub, userRating):

    if userRating is None:
        raise ValueError('You have no submissions yet...')
    submissions = pd.DataFrame(userSub)
    # Make the userRating%100 == 0 
    de = userRating%100
    userRating-=de

    # Drop all the null values
    problems = problems.dropna()

    # Remove all the solved problems from the problemset dataset
    solved = (
        submissions[submissions['verdict'] == 'OK']
        [['contestId', 'index']]
        .drop_duplicates()
    )
    unsolved = problems.merge(
        solved,
        on=['contestId', 'index'],
        how='left',
        indicator=True
    )
    unsolved = unsolved[unsolved['_merge'] == 'left_only']
    problems = unsolved.drop(columns='_merge')

    problems = problems.reset_index(drop=True)


    # ------------------------------------------------------------------
    # Preprocessing — Problemset
    # ------------------------------------------------------------------

    # Build link column then drop raw id columns
    problems['link'] = (
        "https://codeforces.com/contest/" +
        problems['contestId'].astype(str) +
        '/' +
        "problem/"+
        problems['index'].astype(str)
    )
    problems = problems.drop(columns=['index', 'contestId', 'name'])

    # ------------------------------------------------------------------
    # Preprocessing — User submissions
    # ------------------------------------------------------------------

    submissions['link'] = (
        "https://codeforces.com/contest/" +
        submissions['contestId'].astype(str) +
        '/' +
        "problem/"+
        submissions['index'].astype(str)
    )
    submissions = submissions.drop(columns=['contestId', 'index'])
    submissions['target'] = (submissions['verdict'] == 'OK').astype(float)

    # Concatenate submissions and problems into one dataset --- Why?
    df = pd.concat([submissions, problems])
    df = df.drop(columns=['verdict'])
    df['gap'] = userRating-df['rating']

    # ------------------------------------------------------------------
    # Encode tags as binary features
    # ------------------------------------------------------------------

    mlb = MultiLabelBinarizer()
    tags_encoded = mlb.fit_transform(df['tags'])
    tags_df = pd.DataFrame(tags_encoded, columns=mlb.classes_)
    tags_df = tags_df.add_prefix('tag_')

    df = df.reset_index(drop=True)
    tags_df = tags_df.reset_index(drop=True)

    df = pd.concat([df, tags_df], axis=1).drop(columns='tags')
    df = df.drop(columns='type')
    
    # ------------------------------------------------------------------
    # Training data
    # ------------------------------------------------------------------


    train_df = df[df['target'].notna()].copy()

    X = train_df.drop(columns=['target', 'link'])
    y = train_df['target']

    # X_train, X_test, y_train, y_test = train_test_split(
    #     X, y,
    #     test_size=0.2,
    #     random_state=42
    # )

    # ------------------------------------------------------------------
    # Model
    # ------------------------------------------------------------------

    model = LGBMRegressor(
        n_estimators=200,
        random_state=42
    )
    model.fit(X, y)
    # ------------------------------------------------------------------
    # Evaluating Model
    # ------------------------------------------------------------------
    
    # from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

    # y_pred = model.predict(X_test)

    # print("MAE:", mean_absolute_error(y_test, y_pred))
    # print("MSE:", mean_squared_error(y_test, y_pred))
    # print("R2 Score:", r2_score(y_test, y_pred))
    # ------------------------------------------------------------------
    # Predict on unsolved problems
    # ------------------------------------------------------------------

    predict_df = df[df['target'].isna()].copy()

    problem_links = predict_df['link']
    problem_ratings = predict_df['rating']

    X_new = predict_df.drop(columns=['target', 'link'])

    predictions = model.predict(X_new)

    results = pd.DataFrame({
    'link': problem_links.values,
    'prediction': predictions,
    'rating': problem_ratings.values
    })

    results = results.sort_values(by='prediction', ascending=False).reset_index(drop=True)

    # ------------------------------------------------------------------
    # Four recommendations
    # ------------------------------------------------------------------

    def safe_sample(df_filtered, label):
        """Pick one row at random from df_filtered and return it as a dict.
        Returns None if no rows match the filter."""
        if df_filtered.empty:
            print(f"[WARNING] No problems found for category: {label}")
            return None
        random_row = df_filtered.sample(1)
        return random_row.to_dict(orient='records')[0]

    easy_pool = results[
        (results['prediction'] >= 0.9)&(results['rating'] <=userRating)&(results['rating'] >=max(userRating-200,800))
    ]
    medium1_pool = results[
        (results['prediction'] < 0.9)&(results['prediction'] >= 0.8)&(results['rating'] <=userRating+100)&(results['rating'] >=userRating-100)
    ]

    medium2_pool = results[
        (results['prediction'] < 0.8)&(results['prediction'] >= 0.5)&(results['rating'] <=userRating+100)&(results['rating'] >=userRating)
    ]

    hard_pool = results[
        (results['prediction'] < 0.5)&(results['prediction'] >= 0.2)&(results['rating'] <=userRating+300)&(results['rating'] >=userRating)
    ]

    easy_problem   = safe_sample(easy_pool,    "easy")
    medium1_problem = safe_sample(medium1_pool, "medium1")
    medium2_problem = safe_sample(medium2_pool, "medium2") 
    hard_problem   = safe_sample(hard_pool,    "hard")  
    
    return easy_problem, medium1_problem, medium2_problem, hard_problem
