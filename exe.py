import streamlit as st
import requests
import json
import pandas as pd
import time
import threading
from flask import Flask, request, jsonify

# Flask app setup
flask_app = Flask(__name__)
data_storage = {}  # Simple in-memory storage for demonstration

@flask_app.route('/post_data', methods=['POST'])
def post_data():
    data = request.json
    # Print the received data to the console
    print("Received data:", data)
    # Assuming you want to store each piece of data separately in the data_storage
    data_storage['headers'] = data.get('headers')
    data_storage['table'] = data.get('table')
    data_storage['total_bids_traversed'] = data.get('total_bids_traversed')
    data_storage['total_bids_matched'] = data.get('total_bids_matched')
    return jsonify({"message": "Data stored successfully."}), 200

@flask_app.route('/get_data', methods=['GET'])
def get_data():
# Check if the required data is available in data_storage
    if 'table' in data_storage:
        # Prepare the response data structure
        response_data = {
            "headers": data_storage.get('headers', []),
            "table": data_storage.get('table', ''),
            "total_bids_traversed": data_storage.get('total_bids_traversed', 0),
            "total_bids_matched": data_storage.get('total_bids_matched', 0)
        }
        return jsonify(response_data), 200
    else:
        return jsonify({"message": "No data available."}), 404

def run_flask_app():
    # Flask will run on port 5001 to avoid conflicts with Streamlit's default port
    flask_app.run(port=5001, debug=True, use_reloader=False)

# Function placeholders for authentication and bot deployment
def generate_api_key():
    return "Your API Key"

def authenticate_user(username, api_key):
    url = "Your URL for creating token"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "username": username,
        "apiKey": api_key
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    #st.success(response)
    if response.status_code == 200:
        token = response.json().get('token', None)
        if token:
            #st.success("Token successfully extracted and saved.")
            return token
        else:
            st.error("Token extraction failed.")
            return None
    else:
        st.error(f"Failed to authenticate. Status code: {response.status_code}")
        return None

def deploy_bot(token, URL, keywords, modelname):
    url = "Your URL to deploy bot"
    headers = {
        'Content-Type': 'application/json',
        'X-Authorization': token
    }
    payload = {
        "fileId": 37128,
        "runAsUserIds": [214],
        "poolIds": [4],
        "overrideDefaultDevice": False,
        "callbackInfo": {
            "url": "https://callbackserver.com/storeBotExecutionStatus",
            "headers": {
                "X-Authorization": token  
            }
        },
        "botInput": {
            "istrurl": {
                "type": "STRING",
                "string": URL
            },
            "istrkeywords": {
                "type": "STRING",
                "string": keywords
                },
            "istrmodelname": {
                "type": "STRING",
                "string": modelname
                }
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code in [200, 202]:
        #st.success("Bot deployment initiated successfully.")
        return response.json()
    else:
        st.error(f"Failed to deploy bot. Status code: {response.status_code}, Response: {response.text}")
        return None

    pass

def run_api(URL, keywords, modelname):

    username = "USERNAME"
    api_key = generate_api_key()
    token = authenticate_user(username, api_key)
    if token:
        deploy_bot_response = deploy_bot(token, URL, keywords, modelname)
        #st.json(deploy_bot_response)
    else:
        st.error("Authentication failed, cannot deploy bot")
    # Your existing API run function
    pass

FLASK_API_URL = "http://127.0.0.1:5001/get_data"

def fetch_bot_results():
    # Modified to match Flask's running port
    response = requests.get('http://127.0.0.1:5001/get_data')
    if response.status_code == 200:
        return response.json()
    return None

# Streamlit app setup
def main():
    st.title('Semantic Search System')

    URL = st.text_input('Enter the URL:')
    
    Keyphrases = ['Machine Learning', 'Artificial Intelligence', 'Data Science', 'Robotics', 'Natural Language Processing']

    if 'custom_keywords' not in st.session_state:
        st.session_state.custom_keywords = []
        
    if 'selected_keywords' not in st.session_state:
        st.session_state.selected_keywords = []

    col1, col2 = st.columns([3,1])

    with col1:
        new_keyword = st.text_input('Enter a new keyword:', key='new_keyword')

    with col2:
        st.write("\n\n")
        if st.button('Add Keyword'):
            if new_keyword and new_keyword not in Keyphrases + st.session_state.custom_keywords:
                st.session_state.custom_keywords.append(new_keyword)
                # Only add the new keyword to the selection
                if new_keyword not in st.session_state.selected_keywords:
                    st.session_state.selected_keywords.append(new_keyword)
                st.success(f'Added "{new_keyword}" to keywords.')

    all_keywords = Keyphrases + st.session_state.custom_keywords
    with col1:
        # Update the multiselect widget with the current state of selected keywords
        selected_keywords = st.multiselect(
            'Select keywords:', 
            options=all_keywords, 
            default=st.session_state.selected_keywords, 
            key='keyword_selector'
        )
        # Update the session state based on user selection
        st.session_state.selected_keywords = selected_keywords
    
    models = ['GPT-3.5 turbo']
    with col2:
        model = st.selectbox('Select model:', options=models, index=0, help="Select your model of choice")
        
    option = st.radio(
    'Choose bids based on pulished date:',
    ('Since Last Run', 'Today'))
        
    if st.button('Start Searching'):
        selected_keywords = ', '.join(selected_keywords)
        run_api(URL, selected_keywords, model)
        
        # Placeholder for the results
        results_placeholder = st.empty()
        results_placeholder.info('Waiting for bot results...')

         # Initialize progress bar
        progress_bar = st.progress(0)
        

        # Polling interval (in seconds)
        POLLING_INTERVAL = 5  # Example: check every 5 seconds
        MAX_WAIT_TIME = 12000  # Maximum wait time in seconds, for example, 3 hrs
        elapsed_time = 0

        # Loop to continuously poll the Flask API for results
        while elapsed_time < MAX_WAIT_TIME:
            results = fetch_bot_results()
            if results:
                # Clear the placeholders
                results_placeholder.empty()
                progress_bar.empty()

                # Assuming the results are in a format that can be directly converted to a DataFrame
                columns = results['headers'].split(',')
                rows = results["table"].strip()[1:-1].split("}, {")
                rows = [row.split(',') for row in rows]
                df = pd.DataFrame(rows, columns=columns)
                st.write(df)
                st.write('Total Bids Traversed: ',results["total_bids_traversed"])
                st.write('Total Bids Matched: ' ,results["total_bids_matched"])
                break  # Exit the loop if results are found
            else:
                # Update the placeholder with a loading message
                results_placeholder.info('Bot is still running. Waiting for results...')
                
                # Update progress bar based on elapsed time
                progress = (elapsed_time / MAX_WAIT_TIME) * 100
                progress_bar.progress(min(int(progress), 100))
                
                time.sleep(POLLING_INTERVAL)  # Wait before the next check
                elapsed_time += POLLING_INTERVAL

        if elapsed_time >= MAX_WAIT_TIME:
            results_placeholder.error('Bot did not return results in the expected time.')


# Starting the Flask app in a background thread
threading.Thread(target=run_flask_app, daemon=True).start()

if __name__ == "__main__":
    main()
