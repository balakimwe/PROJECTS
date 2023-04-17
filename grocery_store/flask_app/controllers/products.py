from flask_app import app, render_template, redirect, session, request
from flask_app.models.product import Product

# @app.route('/products')
# def products():
#     if 'user_id' not in session:
#         return redirect('/logout')
#     return render_template('products.html', products = Product.get_all())

@app.route('/products')
def products():
    if 'user_id' not in session:
        return redirect('/logout')
    return render_template('main_page.html', products = Product.get_all())

@app.route('/products/new')
def new_product():
    if 'user_id' not in session:
        return redirect('/logout')
    return render_template('new_product.html')

@app.route('/products/create', methods = ['POST'])
def create_product():
    print(request.form)
    if not Product.validate_product(request.form):
        return redirect('/products/new')
    Product.save(request.form)
    return redirect('/products')

@app.route('/products/<int:id>')
def show_product(id):
    data = {'id': id}
    return render_template("show_product.html", product = Product.get_one(data))

@app.route("/products/edit/<int:id>")
def edit_product(id):
    data = {'id': id}
    return render_template("edit.html", product = Product.get_one(data))

@app.route('/products/update', methods = ["POST"])
def update_product():
    print(request.form)
    if not Product.validate_product(request.form):
        return redirect(f"/products/edit/{request.form['id']}")
    Product.update(request.form)
    return redirect('/products') 

@app.route('/products/delete/<int:id>')
def delete_product(id):
    data = {'id': id}
    Product.delete(data)
    return redirect('/products')
