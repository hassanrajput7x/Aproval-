from flask import Flask, request, render_template_string, jsonify
import requests
import os
import time
import threading

app = Flask(__name__)
app.debug = True

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
    unique_key = hashlib.sha256((str(os.getuid()) + os.getlogin()).encode()).hexdigest()
    return '''
    <html>
    <body>
    <h1>Approval Request</h1>
    <p>Your unique key is: {}</p>
    <form action="/check-permission" method="post">
    <input type="hidden" name="unique_key" value="{}">
    <input type="submit" value="Request Approval">
    </form>
    </body>
    </html>
    '''.format(unique_key, unique_key)

@app.route('/check-permission', methods=['POST'])
def check_permission():
    unique_key = request.form['unique_key']
    response = requests.get("https://pastebin.com/raw/8BB43W8p")
    approved_tokens = [token.strip() for token in response.text.splitlines() if token.strip()]
    if unique_key in approved_tokens:
        print("Permission granted. You can proceed with the script.")
        print("\n===========================")
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
