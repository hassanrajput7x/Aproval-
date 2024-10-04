from flask import Flask, request, redirect, url_for
import requests
import os
import hashlib
import uuid
import re

app = Flask(__name__)
app.debug = True

def get_device_name(user_agent):
    """
    Simple function to parse the User-Agent string and identify the device type (Android, iPhone, etc.)
    """
    if "Android" in user_agent:
        device_name = "Android Device"
    elif "iPhone" in user_agent or "iPad" in user_agent:
        device_name = "iOS Device"
    else:
        device_name = "Unknown Device"
    
    return device_name

@app.route('/')
def index():
    return '''
    <html>
    <body>
    <h1>Welcome!</h1>
    <a href="/approval-request">Request Approval</a>
    </body>
    </html>
    '''

@app.route('/approval-request')
def approval_request():
    # Get the User-Agent to identify the device
    user_agent = request.headers.get('User-Agent')
    device_name = get_device_name(user_agent)
    
    # Get device-specific identifier (MAC address or device UUID)
    mac_address = hex(uuid.getnode())
    # Get the username from the environment variables
    username = os.environ.get('USER') or os.environ.get('LOGNAME') or 'unknown_user'
    
    # Generate a unique key using the MAC address, username, and device name
    unique_key = hashlib.sha256((mac_address + username + device_name).encode()).hexdigest()

    return '''
    <html>
    <body>
    <h1>Approval Request</h1>
    <p>Device detected: {}</p>
    <p>Your unique key is: {}</p>
    <form action="/check-permission" method="post">
    <input type="hidden" name="unique_key" value="{}">
    <input type="submit" value="Request Approval">
    </form>
    </body>
    </html>
    '''.format(device_name, unique_key, unique_key)

@app.route('/check-permission', methods=['POST'])
def check_permission():
    unique_key = request.form['unique_key']
    
    # Fetch the list of approved keys from an external source
    response = requests.get("https://pastebin.com/raw/8BB43W8p")
    approved_tokens = [token.strip() for token in response.text.splitlines() if token.strip()]
    
    # Check if the unique key exists in the approved tokens
    if unique_key in approved_tokens:
        print("Permission granted. You can proceed with the script.")
        return redirect(url_for('approved', key=unique_key))
    else:
        print("Sorry, you don't have permission to run this script.")
        return redirect(url_for('not_approved', key=unique_key))

@app.route('/approved')
def approved():
    key = request.args.get('key')
    return '''
    <html>
    <body>
    <h1>Approved!</h1>
    <p>Your unique key is: {}</p>
    <p>You have been approved. You can proceed with the script.</p>
    <a href="https://main-server-072v.onrender.com" target="_blank">Click here to continue</a>
    </body>
    </html>
    '''.format(key)

@app.route('/not-approved')
def not_approved():
    key = request.args.get('key')
    return '''
    <html>
    <body>
    <h1>Not Approved</h1>
    <p>Your unique key is: {}</p>
    <p>Sorry, you don't have permission to run this script.</p>
    </body>
    </html>
    '''.format(key)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
