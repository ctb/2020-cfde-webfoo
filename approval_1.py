from flask import request, make_response, redirect, url_for
from flask import Flask
app = Flask(__name__)

datasets = [
    dict(id=1, program="LINCS", name="data set name", user="user uploaded", date="date uploaded", status="available", nwarnings=5),
    dict(id=2, program="IDG", name="data set 2 name", user="user 2 uploaded", date="date 2 uploaded", status="available", nwarnings=0),
    ]

logfiles = { 1: open('log_files/log-1.txt', 'rt').read(),
             2: open('log_files/log-2.txt', 'rt').read()
           }
    
@app.route('/')
def index():
    username = request.cookies.get('username')
    is_superuser = request.cookies.get('superuser', '0')
    try:
        is_superuser = int(is_superuser)
    except ValueError:
        is_superuser = 0

    superuser_text = '(mode: dcc viewer)'
    if is_superuser:
        superuser_text = '(mode: final approver)'

    if not username:
        username = '** none **'
        logout_text = """<a href="/login">Log in.</a><p>"""
    else:
        logout_text = f"You are logged in as {username} {superuser_text}. <a href='/logout'>log out</a>"
        
    return f"""
App: {__name__}
<p>
{logout_text}
<p>

<p>
<a href="/uploaded_datasets">See uploaded data sets</a>

"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', 'default')
        is_superuser = request.form.get('superuser', 0)
        if is_superuser:
            is_superuser = 1              # enforce it to a particular value

        text = f"logged in as {username}, approver mode {is_superuser}.<p><a href='/'>return to front page.</a>"
        resp = make_response(text)
        resp.set_cookie('username', username)
        resp.set_cookie('superuser', str(is_superuser))
        return resp
    else:
        return f"""
<form method="post" action="/login">
globus username: <input type="text" name="username">
final approver today? <input type="checkbox" name="superuser">
<p>
<input type="submit">
</form>
"""

@app.route('/logout')
def logout():
    resp = make_response(f"""logging you out. <a href='/'>return to front page.</a>""")
    resp.set_cookie('username', '')
    resp.set_cookie('superuser', '')
    return resp


@app.route('/uploaded_datasets')
def uploaded_datasets():
    username = request.cookies.get('username')
    if not username:
        return "you are not logged in. <A href='/login'>go log in.</a>"

    is_superuser = request.cookies.get('superuser', '0')
    try:
        is_superuser = int(is_superuser)
    except ValueError:
        is_superuser = 0

    superuser_text = '(mode: dcc viewer)'
    if is_superuser:
        superuser_text = '(mode: final approver)'

    rows = []
    for ds in datasets:
        ident = ds['id']
        status = ds['status']

        approve_link = f"""<a href='/approve_dataset?id={ident}'>approve for merge</a>"""
        validate_link = f"""<a href='/validate_dataset?id={ident}'>validate</a>"""
        invalidate_link = f"""<a href='/invalidate_dataset?id={ident}'>invalidate</a>"""
        delete_link = f"""<a href='/delete_dataset?id={ident}'>delete</a>"""

        links = []
        
        if is_superuser:
            if status == 'available':
                links.append(validate_link)
                links.append(delete_link)
            elif status.startswith('validated by'):
                links.append(approve_link)
                links.append(invalidate_link)
        else:
            if status == 'available':
                links.append(validate_link)
                links.append(delete_link)
            elif status.startswith('validated by'):
                links.append(invalidate_link)

        links = " | ".join(links)
            
        rows.append(f"""
<tr>
 <td>{ds['program']}</td>
 <td><a href='/explore_ds?id={ident}'>explore dataset {ident}</a>
 <td>{ds['user']}</td>
 <td>{ds['date']}</td>
 <td>{status}</td>
 <td>{links} </td>
 <td><a href='/view_log?id={ident}'>{ds['nwarnings']} warnings</a></td>
</tr>
""")
    rows = "\n".join(rows)

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

username: {username} {superuser_text}
<p>

<h2>Review catalog</h2>

<table class="center">
  <tr>
   <td>program</td>
   <td></td>
   <td>username</td>
   <td>date</td><td>status</td>
   <td>actions</td>
   <td>log info</td></tr>
  {rows}
</table>
<p>
<a href='/'>index</a>

<h2>Discussion for CFDE-CC implementers</h2>

On this page, data sets can be inspected by their relevant DCC users.
<P>
Here, a DCC user is someone who has access to see, explore, and validate
a data set. They do not necessarily have final approver status, although
the final approver is a DCC user.
<p>
The outcomes of this should be that a data set first gets validated by
a DCC user, and then approved by a final approver.
<p>
Any DCC user can validate a data set. There can be at most one validated data
set at a time.
<p>
There is only one final approver for each DCC, in general.
Once a data set is validated, final approvers can approve it for merge.
<p>
Once a data set is approved, someone at the CFDE-CC does the backend stuff to
put it in a queue to be merged into the release catalog.
That can change the status on this page to "Waiting for release."
"""


@app.route('/approve_dataset')
def approve_dataset():
    username = request.cookies.get('username')
    ident = request.args.get('id')
    try:
        ident = int(ident)
    except:
        ident = None

    for ds in datasets:
        if ds['id'] == ident:
            ds['status'] = f'APPROVED by {username} at time XXX'
            print('APPROVING:', ident)

    return redirect(url_for('uploaded_datasets'))

@app.route('/validate_dataset')
def validate_dataset():
    username = request.cookies.get('username')
    ident = request.args.get('id')
    try:
        ident = int(ident)
    except:
        ident = None

    for ds in datasets:
        if ds['id'] != ident:
            if ds['status'].startswith('validated by'):
                return f"ERROR. There can only be one validated data set. dataset id {ds['id']} is already validated."

    for ds in datasets:
        if ds['id'] == ident:
            ds['status'] = f'validated by {username} at time XXX'
            print('VALIDATING:', ident)

    return redirect(url_for('uploaded_datasets'))


@app.route('/invalidate_dataset')
def invalidate_dataset():
    ident = request.args.get('id')
    try:
        ident = int(ident)
    except:
        ident = None

    for ds in datasets:
        if ds['id'] == ident:
            ds['status'] = 'available'
            print('INVALIDATING:', ident)

    return redirect(url_for('uploaded_datasets'))


@app.route('/delete_dataset')
def delete_dataset():
    username = request.cookies.get('username')
    ident = request.args.get('id')
    try:
        ident = int(ident)
    except:
        ident = None

    for ds in datasets:
        if ds['id'] == ident:
            ds['status'] = f'DELETED by {username} at time XXX'
            print('DELETING:', ident)

    return redirect(url_for('uploaded_datasets'))


@app.route('/view_log')
def view_log():
    ident = request.args.get('id')
    ident = int(ident)
        
    return f"""
Log for {ident}
---

<pre>
{logfiles[ident]}
</pre>
<p>
<a href='/uploaded_datasets'>go back to uploaded data sets</a>
"""


@app.route('/explore_ds')
def explore_ds():
    ident = request.args.get('id')
    ident = int(ident)
        
    return f"""
<h2>Exploring data set {ident}</h2>

<img src='{ url_for('static', filename='chase-catalog-summary.png') }' width=40%>

<p>

<a href='/uploaded_datasets'>go back to review catalog</a>

<h2>Discussion for CFDE-CC implementers</h2>

This is literally the review page, sayeth Amanda.

Here should be a variety of ways to slice and dice the data, including
* interactive summary figures
* a link to the chase catalog for this uploaded data set
"""
