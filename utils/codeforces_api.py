import requests
import pandas as pd 

# Verify and get user's data

def verify_and_get_user(handle):
    # Check if user's handle is exist already and return user's data -- returns (user_data,error_message) tuple
    if not handle or not handle.strip():
        return None, 'Please enter you handle'
    #url api for requesting the data using the requests function 
    api_url = f"https://codeforces.com/api/user.info?handles={handle}"

    try:
        # request data with timeout 10 
        res = requests.get(api_url,timeout=10)
        # Convert the data to JSON form 
        data = res.json()
        # If the response returned with data return the data with no error 
        if data['status']=='OK':
            return data['result'][0],None
        else:
            return None,'Not Found'
    except requests.RequestException:
        return None , "Could not connect to Codeforces"
    except Exception as e:
        return None, f"An error occurred: {str(e)}"

# Get all the problemset from Codeforces

def get_all_problems():
    """
        Get all the problems of codeforces and return it as dataframe
    """
    api_url = "https://codeforces.com/api/problemset.problems"
    try : 
        res = requests.get(api_url,timeout=10)
        data = res.json()
        if data['status'] == 'OK':
            df = pd.DataFrame(data['result']['problems'])
            return df,None
        else:
            return None, f"Could not fetch problemset from Codeforces"
    except requests.Timeout:
            return None, "Request timed out"
    except Exception as e:
            return None, f"Error fetching problems: {str(e)}"
    
# Get all user's submissions 

def get_user_submissions(handle):
    """
    Return user's submissions as DataFrame.
    """
    api_url = f"https://codeforces.com/api/user.status?handle={handle}" 
    try:
        res = requests.get(api_url,timeout=10)
        data = res.json()
        if data['status']=='OK':
            submissions=[]
            for p in data['result']:

                problem = p.get("problem",{})

                submissions.append({
                    "contestId":problem.get('contestId'),
                    "index":problem.get('index'),
                    "rating":problem.get('rating'),
                    "tags":problem.get('tags'),
                    "verdict":p.get('verdict')
                }) 
            df = pd.DataFrame(submissions)
            return df , None
        else:
             return None,"Could not fetch user's submissions"
    except requests.Timeout:
            return None, 'Requests timeout'
    except Exception as e :
        return None, f"Error fetching submissions: {str(e)}"