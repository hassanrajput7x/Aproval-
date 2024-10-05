from flask import Flask, request, redirect, url_for, session
import requests
import os
import hashlib
import uuid
import re  # For parsing the model from User-Agent

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.debug = True

APPROVED_KEYS_FILE = 'approved_keys.txt'  # File to store approved keys

# Function to parse mobile name and model from User-Agent
def get_device_name_and_model(user_agent):
    if "Android" in user_agent:
        match = re.search(r'\b(\w+\s?\w+)\sBuild', user_agent)  # Extract model name
        device_model = match.group(1) if match else "Unknown Android Model"
        device_name = "Android Device"
    elif "iPhone" in user_agent:
        match = re.search(r'\biPhone\s?(\w+)?', user_agent)
        device_model = f"iPhone {match.group(1)}" if match else "iPhone"
        device_name = "iOS Device"
    elif "iPad" in user_agent:
        device_name = "iOS Device"
        device_model = "iPad"
    else:
        device_name = "Unknown Device"
        device_model = "Unknown Model"

    return device_name, device_model

# Check if the key is already approved
def is_key_approved(unique_key):
    if os.path.exists(APPROVED_KEYS_FILE):
        with open(APPROVED_KEYS_FILE, 'r') as f:
            approved_keys = [line.strip() for line in f.readlines()]
        return unique_key in approved_keys
    return False

# Save the approved key
def save_approved_key(unique_key):
    with open(APPROVED_KEYS_FILE, 'a') as f:
        f.write(unique_key + '\n')

@app.route('/')
def index():
    return '''
    <html>
    <head>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f4f9;
            text-align: center;
            margin-top: 50px;
        }
        h1 {
            color: #333;
            font-size: 65px;
        }
        a {
            text-decoration: none;
            color: #007bff;
            font-weight: bold;
            padding: 10px 20px;
            border: 2px solid #007bff;
            border-radius: 5px;
            transition: background-color 0.3s, color 0.3s;
        }
        a:hover {
            background-color: #007bff;
            color: white;
        }
    </style>
    </head>
    <body>
    <h1>♛WELCOME TO HASSAN♛</h1>
    <a href="/approval-request">Request Approval</a>
    </body>
    </html>
    '''

@app.route('/approval-request')
def approval_request():
    user_agent = request.headers.get('User-Agent')
    device_name, device_model = get_device_name_and_model(user_agent)

    if 'device_id' not in session:
        session['device_id'] = str(uuid.uuid4())

    device_id = session['device_id']
    username = os.environ.get('USER') or os.environ.get('LOGNAME') or 'unknown_user'

    unique_key = hashlib.sha256((device_id + username + device_name + device_model).encode()).hexdigest()

    if is_key_approved(unique_key):
        return redirect(url_for('approved', key=unique_key))

    return f'''
    <html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #dff0d8;
            text-align: center;
            margin-top: 50px;
        }}
        h1 {{
            color: #3c763d;
            font-size: 65px;
        }}
        p {{
            color: #333;
            font-size: 20px;
        }}
        a {{
            text-decoration: none;
            color: #007bff;
            font-weight: bold;
        }}
        a:hover {{
            color: #0056b3;
        }}
        .key-box {{
            display: inline-block;
            border: 2px solid #3c763d;
            padding: 20px;
            background-color: #ffffff;
            color: #333;
            font-size: 22px;
            font-weight: bold;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <h1>Approved!</h1>
    <div class="key-box">Your unique key is: {unique_key}</div>
    <p>You have been approved. You can proceed with the script.</p>
    <a href="https://main-server-072v.onrender.com" target="_blank">Click here to continue</a>
</body>
</html>
    '''

@app.route('/check-permission', methods=['POST'])
def check_permission():
    unique_key = request.form['unique_key']

    try:
        # Fetch the list of approved tokens (could be an external API or database)
        response = requests.get("https://pastebin.com/raw/8BB43W8p")
        response.raise_for_status()  # Raise an error for bad responses
        approved_tokens = [token.strip() for token in response.text.splitlines() if token.strip()]
    except requests.RequestException as e:
        return f"Error fetching approved tokens: {e}", 500  # Return an error message

    # If the unique key is approved, save it locally and allow the device
    if unique_key in approved_tokens:
        save_approved_key(unique_key)
        return redirect(url_for('approved', key=unique_key))
    else:
        return redirect(url_for('not_approved', key=unique_key))

@app.route('/approved')
def approved():
    key = request.args.get('key')
    return f'''
    <html>
    <head>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #dff0d8;
            text-align: center;
            margin-top: 50px;
        }}
        h1 {{
            color: #3c763d;
            font-size: 65px;
        }}
        p {{
            color: #333;
            font-size: 20px;
        }}
        a {{
            text-decoration: none;
            color: #007bff;
            font-weight: bold;
        }}
        a:hover {{
            color: #0056b3;
        }}
    </style>
    </head>
    <body>
    <h1>Approved!</h1>
    <div class="key-box">Your unique key is: {key}</div>
    <p>You have been approved. You can proceed with the script.</p>
    <a href="https://main-server-072v.onrender.com" target="_blank">Click here to continue</a>
    </body>
    </html>
    '''

@app.route('/not-approved')
def not_approved():
    key = request.args.get('key')
    return f'''
    <html>
    <head>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f2dede;
            text-align: center;
            margin-top: 50px;
        }}
        h1 {{
            color: #a94442;
            font-size: 65px;
        }}
        p {{
            color: #333;
            font-size: 20px;
        }}
    </style>
    </head>
    <body>
    <h1>Not Approved</h1>
    <div class="key-box">Your unique key is: {key}</div>
    <p>Sorry, you don't have permission to run. Contact owner on WhatsApp +923417885339.</p>
    </body>
    </html>
    '''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
