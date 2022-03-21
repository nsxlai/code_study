import pandas as pd
from flask import Flask, render_template, redirect, session, url_for, request


user_list = [
    {'name': 'vehicle_01', 'VIN': '111111', 'COMP_ID': 'CPPM', 'SN': '1121225JBL000010', 'TACT': 'ABC-001'},
    {'name': 'vehicle_02', 'VIN': '111222', 'COMP_ID': 'CPPM', 'SN': '1121225JBL000110', 'TACT': 'ABC-005'},
    {'name': 'vehicle_03', 'VIN': '111333', 'COMP_ID': 'CPPM', 'SN': '1121225JBL000210', 'TACT': 'ABC-007'},
    {'name': 'vehicle_04', 'VIN': '111444', 'COMP_ID': 'CPPM', 'SN': '1121225JBL000310', 'TACT': 'ABC-012'},
    {'name': 'vehicle_05', 'VIN': '111555', 'COMP_ID': 'CPPM', 'SN': '1121225JBL000410', 'TACT': 'ABC-025'},
    ]

headings = ['Name', 'VIN', 'COMP_ID', 'SN']
data = [
    ['vehicle_01', '111111', 'CPPM', '1121225JBL000010'],
    ['vehicle_02', '111222', 'CPPM', '1121225JBL000110'],
    ['vehicle_03', '111333', 'CPPM', '1121225JBL000210'],
    ['vehicle_04', '111444', 'CPPM', '1121225JBL000310'],
    ['vehicle_05', '111555', 'CPPM', '1121225JBL000410'],
]
app = Flask(__name__)
app.secret_key = '123456789'


@app.route('/')
def table():
    return render_template("table.html", headings=headings, data=data)


@app.route('/index', methods=['GET', 'POST'])
def index():
    # if request.method == 'POST':
    #     if 'username' in request.form and 'password' in request.form:
    #         username = request.form['username']
    #         password = request.form['password']
    #
    #         for user in user_list:
    #             if not username or not password:
    #                 return 'Username or password cannot be blank'
    #             if username == user[1] and password == user[2]:
    #                 session['loginSuccess'] = True
    #                 return redirect(url_for('profile'))
    #         else:
    #             return redirect(url_for('index'))
    # return render_template('login.html')
    # @app.route("/tables")
    # def show_tables():
    data = pd.DataFrame(user_list)
    # data.set_index(['Name'], inplace=True)
    # data.index.name = None
    # females = data.loc[data.Gender == 'f']
    # males = data.loc[data.Gender == 'm']
    return render_template('login.html', tables=[data.to_html(classes='vehicle_info')], titles=['Vehicle Info'])


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
