from flask import render_template, Blueprint
from src.models import ProductModel, CategoryModel
from .utils import admin_only

admin_bp = Blueprint("admin_bp", __name__, template_folder="templates/admin")


@admin_bp.route('/admin')
@admin_only
def admin():
    products = ProductModel.query.all()
    return render_template('admin/home.html', title='Admin page', products=products)


@admin_bp.route('/categories')
@admin_only
def categories():
    categories = CategoryModel.query.order_by(CategoryModel.id.desc()).all()
    return render_template('admin/categories.html', title='categories', categories=categories)


