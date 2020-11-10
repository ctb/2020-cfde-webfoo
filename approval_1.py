from flask import request, make_response, redirect, url_for
from flask import Flask
app = Flask(__name__)

datasets = [
    dict(id=1, name="data set name", user="user uploaded", date="date uploaded", status="not yet approved"),
    dict(id=2, name="data set 2 name", user="user 2 uploaded", date="date 2 uploaded", status="not yet approved"),
    ]
    
@app.route('/')
def index():
    username = request.cookies.get('username')
    if not username:
        username = '** none **'
        logout_text = ''
    else:
        logout_text = f"<a href='/logout'>log out</a>"
        
    return f"""
App: {__name__}
<p>
You are logged in as: {username}.
{logout_text}
<p>

<p>
<a href="/login">Log in.</a><p>
<a href="/uploaded_datasets">See uploaded data sets</a>

"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', 'default')
        text = f"logged in as {username}.<p><a href='/'>return to front page.</a>"
        resp = make_response(text)
        resp.set_cookie('username', username)
        return resp
    else:
        return f"""<form method="post" action="/login">globus username: <input type="text" name="username"></form>"""

@app.route('/logout')
def logout():
    resp = make_response(f"""logging you out. <a href='/'>return to front page.</a>""")
    resp.set_cookie('username', '')
    return resp


@app.route('/uploaded_datasets')
def uploaded_datasets():
    username = request.cookies.get('username')
    if not username:
        return "you are not logged in. <A href='/login'>go log in.</a>"

    x = []
    for ds in datasets:
        x.append(f"""<tr><td>{ds['id']}</td><td>{ds['user']}</td><td>{ds['date']}</td><td>{ds['status']}</td><td><a href='/approve_dataset?id={ds['id']}'>approve</a> | <a href='/delete_dataset?id={ds['id']}'>delete</a></tr>""")
    x = "\n".join(x)

    return f"""
<head>
<style>
table, th, td {{
  border: 1px solid black;
}}
table.center {{
  margin-left: auto; 
  margin-right: auto;
}}
</style>
</head>

<table class="center"><tr><td>id</td><td>username</td><td>date</td><td>status</td></tr>{x}</table>
<p>
<a href='/'>index</a>
"""


@app.route('/approve_dataset')
def approve_dataset():
    ident = request.args.get('id')
    try:
        ident = int(ident)
    except:
        ident = None

    for ds in datasets:
        if ds['id'] == ident:
            ds['status'] = 'APPROVED'
            print('APPROVING:', ident)

    return redirect(url_for('uploaded_datasets'))


@app.route('/delete_dataset')
def delete_dataset():
    ident = request.args.get('id')
    try:
        ident = int(ident)
    except:
        ident = None

    for ds in datasets:
        if ds['id'] == ident:
            ds['status'] = 'DELETED'
            print('DELETING:', ident)

    return redirect(url_for('uploaded_datasets'))
