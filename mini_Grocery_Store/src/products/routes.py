from flask import (render_template, session, request, redirect,
                   url_for, flash, current_app, Blueprint)

from src import db, photos, search
from src.models import CategoryModel, ProductModel
from .forms import AddProductForm
import secrets
import os
from src.admin.utils import admin_only
from sqlalchemy.exc import IntegrityError

products_bp = Blueprint("products_bp", __name__, template_folder="templates/products")


# return all the save category
def categories():
    all_categories = CategoryModel.query.join(ProductModel, (CategoryModel.id == ProductModel.category_id)).all()
    return all_categories


# this view returns all the products in the store page
@products_bp.route('/products')
def all_products():
    page = request.args.get('page', 1, type=int)
    products = ProductModel.query.filter(ProductModel.stock > 0).order_by(ProductModel.id.desc()).paginate(
        page=page,
        per_page=8)
    return render_template('products/index.html', products=products, categories=categories())


# this view returns all the search products that are searched from the search bar of navbar.
@products_bp.route('/result')
def result():
    searchword = request.args.get('q')
    products = ProductModel.query.msearch(searchword, fields=['name', 'description'], limit=6)
    return render_template('products/result.html', products=products, categories=categories())


# this view will show single product in page with all the details.
@products_bp.route('/product/<int:product_id>')
def single_page(product_id):
    product = ProductModel.query.get_or_404(product_id)
    return render_template('products/single_page.html', product=product, categories=categories())


# this view will return all the products in specific category
@products_bp.route('/categories/<int:category_id>')
def get_category(category_id):
    page = request.args.get('page', 1, type=int)
    get_cat = CategoryModel.query.filter_by(id=category_id).first_or_404()
    get_cat_prod = ProductModel.query.filter_by(category=get_cat).paginate(page=page, per_page=8)
    return render_template('products/index.html', get_cat_prod=get_cat_prod, categories=categories(),
                           get_cat=get_cat)


# for adding category to the database
@products_bp.route('/add-category', methods=['GET', 'POST'])
@admin_only
def add_category():
    if request.method == "POST":
        get_cat = request.form.get('category')
        category = CategoryModel(name=get_cat)
        db.session.add(category)
        try:
            db.session.commit()
            flash(f'The category {get_cat} was added to your database', 'success')
            return redirect(url_for('admin_bp.categories'))
        except IntegrityError:
            db.session.rollback()
            flash(f'The category {get_cat} was already exists in your database', 'danger')
    return render_template('products/add-category.html', title='Add category')


# for updating category to the database
@products_bp.route('/update-category/<int:category_id>', methods=['GET', 'POST'])
@admin_only
def update_category(category_id):
    update_cat = CategoryModel.query.get_or_404(category_id)
    category = request.form.get('category')
    if request.method == "POST":
        update_cat.name = category
        flash(f'The category {update_cat.name} was changed to {category}', 'success')
        db.session.commit()
        return redirect(url_for('admin_bp.categories'))
    category = update_cat.name
    return render_template('products/add-category.html', title='Update cat', updatecat=update_cat)


# for deleting category from the database
@products_bp.route('/delete-category/<int:category_id>', methods=['GET', 'POST'])
@admin_only
def delete_category(category_id):
    category = CategoryModel.query.get_or_404(category_id)
    if request.method == "POST":
        db.session.delete(category)
        flash(f"The brand {category.name} was deleted from your database", "success")
        db.session.commit()
        return redirect(url_for('admin_bp.admin'))
    flash(f"The brand {category.name} can't be  deleted from your database", "warning")
    return redirect(url_for('admin_bp.admin'))


# for adding product to the database
@products_bp.route('/add-product', methods=['GET', 'POST'])
@admin_only
def add_product():
    form = AddProductForm(request.form)
    all_categories = CategoryModel.query.all()
    if request.method == "POST" and 'image_1' in request.files:
        name = form.name.data
        price = form.price.data
        discount = form.discount.data
        stock = form.stock.data
        description = form.description.data
        category = request.form.get('category')
        image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
        image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
        product = ProductModel(name=name, price=price, discount=discount, stock=stock,
                               description=description, category_id=category,
                               image_1=image_1, image_2=image_2, image_3=image_3)
        db.session.add(product)
        flash(f'The product {name} was added in database', 'success')
        db.session.commit()
        return redirect(url_for('admin_bp.admin'))
    return render_template('products/add-product.html', form=form, title='Add a Product',
                           categories=all_categories)


# for updating product to the database
@products_bp.route('/update-product/<int:product_id>', methods=['GET', 'POST'])
@admin_only
def update_product(product_id):
    form = AddProductForm(request.form)
    product = ProductModel.query.get_or_404(product_id)
    all_categories = CategoryModel.query.all()
    brand = request.form.get('brand')
    category = request.form.get('category')
    if request.method == "POST":
        product.name = form.name.data
        product.price = form.price.data
        product.discount = form.discount.data
        product.stock = form.stock.data
        product.description = form.description.data
        product.category_id = category
        product.brand_id = brand
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
            except:
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
            except:
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
            except:
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")

        flash('The product was updated', 'success')
        db.session.commit()
        return redirect(url_for('admin_bp.admin'))
    form.name.data = product.name
    form.price.data = product.price
    form.discount.data = product.discount
    form.stock.data = product.stock
    form.description.data = product.description
    category = product.category.name
    return render_template('products/add-product.html', form=form, title='Update Product',
                           getproduct=product, categories=all_categories)


# for deleting product from the database
@products_bp.route('/delete-product/<int:product_id>', methods=['POST'])
@admin_only
def delete_product(product_id):
    product = ProductModel.query.get_or_404(product_id)
    if request.method == "POST":
        try:
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
        except Exception as e:
            print(e)
        db.session.delete(product)
        db.session.commit()
        flash(f'The product {product.name} was delete from your record', 'success')
        return redirect(url_for('admin_bp.admin'))
    flash(f'Can not delete the product', 'success')
    return redirect(url_for('admin_bp.admin'))
