import os
import urlparse
import psycopg2
from flask import Flask, request, redirect, url_for, make_response
from functools import wraps

app = Flask(__name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.cookies.get('user_id')
        app.logger.error(user_id)
        if not user_id:
            return redirect(url_for('register', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def get_connection():
    """
    """
    result = urlparse.urlparse(os.environ['DATABASE_URL'])
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    connection = psycopg2.connect(
        database=database,
        user=username,
        host=hostname,
        password=password
    )
    connection.autocommit = True
    return connection


conn = get_connection()


@app.route("/")
def hello():
    return 'Hello World! Come <a href="/register">Register</a>'


@app.route("/comments", methods=["GET"])
@login_required
def comments():
    statement = 'SELECT * FROM comments;'
    cur = conn.cursor()
    cur.execute(statement)
    result = cur.fetchall()
    comments_list = '<ul>'
    for comment in result:
        comments_list += '<li>' + comment[1] + '</li>'
    comments_list += '</ul>'

    response_body = '''
    <!DOCTYPE html>
    <html>
        <body>
            <h1>Comments</h1>
    ''' + comments_list + '''
            <form method="POST">
                <input name="comment" type="text">
                <br>
                <input type="submit">
            </form>
        </body>
    </html>
    '''
    # Browsers will now try to prevent XSS. Let's turn that
    # feature off to make our app vulnerable.
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-XSS-Protection
    response = make_response(response_body)
    response.headers['X-XSS-Protection'] = 0
    return response


@app.route("/comments", methods=["POST"])
def comment():
    comment = request.form['comment']
    cur = conn.cursor()
    user_id = request.cookies.get('user_id')
    if user_id:
        user_id = int(user_id)
        query = 'INSERT INTO comments (user_id, text) VALUES ({0}, \'{1}\');'
        statement = query.format(user_id, comment)
    else:
        query = 'INSERT INTO comments (text) VALUES (\'{0}\');'
        statement = query.format(comment)

    if 'drop' in statement.lower():
        return redirect('/comments')

    cur.execute(statement)
    conn.commit()
    return redirect("/comments")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        statement = (
            'INSERT INTO users (username, password) '
            'VALUES (\'{0}\', \'{1}\') RETURNING id;'
        ).format(username, password)
        if 'drop' in statement.lower():
            return redirect("/register")

        cur = conn.cursor()
        print(statement)
        cur.execute(statement)
        user_id = cur.fetchone()[0]
        response = redirect('/comments')
        response.set_cookie('user_id', str(user_id))
        return response

    return '''
<!DOCTYPE html>
<html>
<body>
Hello! Please register for my awesome, totally secure site
<form method="POST">
<input name="username" type="text" placeholder="username" pattern=".{3,}">
<br>
<input name="password" type="password" placeholder="password" pattern=".{3,}">
<br>
<input type="submit">
</form>
</body>
</html>
'''


if __name__ == "__main__":
    host = os.getenv('IP', '0.0.0.0')
    port = int(os.getenv('PORT', 8080))
    app.run(debug=True, host=host, port=port)
