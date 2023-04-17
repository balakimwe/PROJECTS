from flask_app import app, render_template, redirect, request, bcrypt, session, flash
from flask_app.models.customer import Customer

@app.route('/')
def main_page():
    return render_template('main_page.html')

#! CREATE AKA REGISTER

@app.route("/register", methods = ['post'])
def register():
    print(request.form)

    # TODO validate our customer
    if not Customer.validate_customer(request.form):
        return redirect('/')
    # TODO hash the password
    hashed_pw = bcrypt.generate_password_hash(request.form['password'])
    print(hashed_pw)
    # TODO save the customer to the database
    customer_data = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'password': hashed_pw
    }
    customer_id = Customer.save(customer_data)
    # TODO log in the customer
    session['customer_id'] = customer_id
    session['first_name'] = request.form['first_name']
    session['last_name'] = request.form['last_name']
    # TODO redirect customer to app
    return redirect('/products')

#! READ and VERIFY AKA LOGIN

@app.route('/login', methods=['post'])
def login():
    print(request.form)
    # TODO see if the email is in our DB
    customer = Customer.get_by_email(request.form)
    if not customer:
        flash("invalid credentials")
        return redirect("/")
    # TODO check to see of the password provided matches the password in our DB
    password_valid = bcrypt.check_password_hash(customer.password, request.form['password'])
    print(password_valid)
    if not password_valid:
        flash("invalid credentials")
        return redirect('/')
    # TODO log in the customer
    session['customer_id'] = customer.id
    session['first_name'] = customer.first_name
    session['last_name'] = customer.last_name
    # TODO redirect customer to app
    return redirect('/products')

#! LOGOUT

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')