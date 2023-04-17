from flask import (render_template, session, request,
                   redirect, url_for, flash,
                   Blueprint)
from flask_login import login_required, current_user, logout_user, login_user
from src import db, bcrypt
from .forms import UserRegisterForm, UserLoginFrom, CustomerProfileForm
from src.models import UserModel, CustomerOrderModel, OrderProductModel,ProductModel
import secrets


customer_bp = Blueprint("customer_bp", __name__, template_folder="templates/customer")


@customer_bp.route('/register', methods=['GET', 'POST'])
def customer_register():
    if current_user.is_authenticated:
        return redirect(url_for('products_bp.all_products'))
    form = UserRegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        username = form.username.data
        hash_password = bcrypt.generate_password_hash(password)
        gender = form.gender.data
        birthday = form.birthday.data

        user = UserModel(name=name, username=username,
                         email=email, password=hash_password,
                         gender=gender, birthday=birthday)
        db.session.add(user)
        flash(f'Welcome {form.name.data} Thank you for registering', 'success')
        db.session.commit()
        return redirect(url_for('customer_bp.login'))
    return render_template('customer/register.html', form=form)


# customer profile page
@customer_bp.route('/profile')
@login_required
def profile():
    return render_template('customer/profile.html')


# for updating customer profile
@customer_bp.route('/update-profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    user = current_user
    form = CustomerProfileForm(
        country=user.country,
        city=user.city,
        contact=user.contact,
        address=user.address,
        zipcode=user.zipcode
    )
    if form.validate_on_submit():
        user.country = form.country.data
        user.city = form.city.data
        user.contact = form.contact.data
        user.address = form.address.data
        user.zipcode = form.zipcode.data
        db.session.commit()
        return redirect(url_for('customer_bp.profile'))
    return render_template('customer/profile-update.html', form=form)


# for login for customer and admin
@customer_bp.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('products_bp.all_products'))
    form = UserLoginFrom()
    if form.validate_on_submit():
        user = UserModel.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('You are login now!', 'success')
            next_url = request.args.get('next')
            if current_user.is_admin:
                return redirect(next_url or url_for('admin_bp.admin'))
            return redirect(next_url or url_for('products_bp.all_products'))
        flash('Incorrect email and password', 'danger')
        return redirect(url_for('customer_bp.login'))

    return render_template('customer/login.html', form=form)


# for logout
@customer_bp.route('/logout')
@login_required
def customer_logout():
    logout_user()
    flash('Sign out successful', 'success')
    return redirect(url_for('customer_bp.login'))


# this is just normal function used for updating shopping cart
def updateshoppingcart():
    for key, shopping in session['Shoppingcart'].items():
        session.modified = True
        del shopping['image']
    return updateshoppingcart


# when a user go from cart to order page this function will add the card items info from session
# and create a entry in the order model and order product model database.
@customer_bp.route('/getorder')
@login_required
def get_order():
    if current_user.is_authenticated:
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        # updateshoppingcart
        try:
            order = CustomerOrderModel(invoice=invoice, customer_id=customer_id)
            db.session.add(order)
            db.session.commit()
            for key, product in session['Shoppingcart'].items():
                print(key, product)
                get_product = ProductModel.query.get(key)
                get_product.stock = get_product.stock - 1
                print(
                    f"{order.id} {customer_id} {get_product.name} {int(product['quantity'])} {float(product['price'])}"
                    f"{int(product['discount'])}")
                order_product = OrderProductModel(customer_id=customer_id, order=order,
                                                  product=get_product,
                                                  quantity=int(product['quantity']),
                                                  product_price=float(product['price']),
                                                  discount=int(product['discount']))
                db.session.add(order_product)
                db.session.commit()
            session.pop('Shoppingcart')
            flash('Your order has been sent successfully', 'success')
            return redirect(url_for('customer_bp.orders', invoice=invoice))
        except Exception as e:
            print(e)
            flash('Some thing went wrong while get order', 'danger')
            return redirect(url_for('cart_bp.getCart'))


# this one you call when you wan to view the order page
@customer_bp.route('/orders/<invoice>')
@login_required
def orders(invoice):
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        tax = 0
        customer_id = current_user.id
        customer = UserModel.query.filter_by(id=customer_id).first()
        customer_order = CustomerOrderModel.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(
            CustomerOrderModel.id.desc()).first()
        for order in customer_order.orders:
            discount = (order.discount / 100) * float(order.product_price)
            subTotal += float(order.product_price) * order.quantity
            subTotal -= discount
            tax = ("%.2f" % (.06 * float(subTotal)))
            grandTotal = ("%.2f" % (1.06 * float(subTotal)))

    else:
        return redirect(url_for('customer_bp.login'))
    return render_template('customer/order.html', invoice=invoice, tax=tax, subTotal=subTotal,
                           grandTotal=grandTotal,
                           customer=customer, customer_order=customer_order)

