from flask import Flask, render_template, redirect, session, url_for, request


user_list = [
        (1, 'john.doe@def.com', '123456', 'John Doe'),
        (2, 'jane.doe@def.com', '654321', 'Jane Doe'),
        (3, 'john.smith@def.com', 'abcabc', 'John Smith'),
        (4, 'mike.malloy@def.com', 'defdef', 'Mike Malloy'),
        (5, 'aileen.chen@def.com', '123123', 'Aileen Chen'),
        (6, 'violet.minh@def.com', '456456', 'Violet Minh'),
        (7, 'lucy.anderson@def.com', 'qwerty', 'Lucy Anderson'),
        (8, 'lisa.dinstill@def.com', 'aaabbb', 'Lisa Dinstill'),
        (9, 'katie.sanero@def.com', 'cccddd', 'Katie Sanero'),
        (10, 'sam.teller@def.com', 'efefef', 'Sam Teller'),
    ]

app = Flask(__name__)
app.secret_key = '123456789'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']

            for user in user_list:
                if not username or not password:
                    return 'Username or password cannot be blank'
                if username == user[1] and password == user[2]:
                    session['loginSuccess'] = True
                    return redirect(url_for('profile'))
            else:
                return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/new', methods=['GET', 'POST'])
def new_user():
    if request.method == 'POST':
        if 'one' in request.form and 'two' in request.form and 'three' in request.form:
            name = request.form['one']
            username = request.form['two']  # this is the email address of the user
            password = request.form['three']
            user_list.append((len(user_list)+1, username, password, name))
            return redirect(url_for('index'))
        else:
            return 'Missing information!'
    return render_template('register.html')


@app.route('/new/profile')
def profile():
    if session['loginSuccess']:
        return render_template('profile.html')


@app.route('/new/logout')
def logout():
    session.pop('loginSuccess', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)  # Default port is at 5000
