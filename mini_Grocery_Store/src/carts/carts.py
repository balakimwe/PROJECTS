from flask import (render_template, session, request, redirect, url_for,
                   flash, Blueprint)

from src.models import ProductModel
from src.products.routes import categories
from flask_login import login_required

cart_bp = Blueprint("cart_bp", __name__)


def MagerDicts(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    if isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))


@cart_bp.route('/addcart', methods=['POST'])
@login_required
def AddCart():
    try:
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity'))
        product = ProductModel.query.filter_by(id=product_id).first()

        if request.method == "POST":
            DictItems = {product_id: {'name': product.name, 'price': float(product.price),
                                      'discount': product.discount,
                                      'quantity': quantity, 'image': product.image_1,
                                        }}
            if 'Shoppingcart' in session:
                print(session['Shoppingcart'])
                if product_id in session['Shoppingcart']:
                    for key, item in session['Shoppingcart'].items():
                        if int(key) == int(product_id):
                            session.modified = True
                            item['quantity'] += 1
                else:
                    session['Shoppingcart'] = MagerDicts(session['Shoppingcart'], DictItems)
                    return redirect(request.referrer)
            else:
                session['Shoppingcart'] = DictItems
                return redirect(request.referrer)

    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)


@cart_bp.route('/carts')
@login_required
def getCart():
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('products_bp.all_products'))
    subtotal = 0
    grand_total = 0
    tax = 0
    for key, product in session['Shoppingcart'].items():
        discount = (product['discount'] / 100) * float(product['price'])
        subtotal += float(product['price']) * int(product['quantity'])
        subtotal -= discount
        tax = ("%.2f" % (.06 * float(subtotal)))
        grand_total = float("%.2f" % (1.06 * subtotal))
    return render_template('products/carts.html', tax=tax, grandtotal=grand_total,
                           categories=categories())


@cart_bp.route('/updatecart/<int:code>', methods=['POST'])
@login_required
def updatecart(code):
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    if request.method == "POST":
        quantity = request.form.get('quantity')
        try:
            session.modified = True
            for key, item in session['Shoppingcart'].items():
                if int(key) == code:
                    item['quantity'] = quantity
                    flash('Item is updated!')
                    return redirect(url_for('cart_bp.getCart'))
        except Exception as e:
            print(e)
            return redirect(url_for('cart_bp.getCart'))


@cart_bp.route('/deleteitem/<int:id>')
@login_required
def deleteitem(id):
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('products_bp.home'))
    try:
        session.modified = True
        for key, item in session['Shoppingcart'].items():
            if int(key) == id:
                session['Shoppingcart'].pop(key, None)
                return redirect(url_for('cart_bp.getCart'))
    except Exception as e:
        print(e)
        return redirect(url_for('cart_bp.getCart'))


@cart_bp.route('/clearcart')
def clearcart():
    try:
        session.pop('Shoppingcart', None)
    except Exception as e:
        print(e)
    return redirect(url_for('products_bp.all_products'))
