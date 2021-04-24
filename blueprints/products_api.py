from flask import Blueprint, abort, render_template, redirect, url_for
from flask_login import current_user

from data import db_session
from forms.products import ProductForm
from data.products import Product

products = Blueprint('products', __name__)


@products.route('/')
def index():
    db_sess = db_session.create_session()
    all_products = db_sess.query(Product).all()
    return render_template('products/show.html', products=all_products)


@products.route('/products_list')
def products_list():
    db_sess = db_session.create_session()
    all_products = db_sess.query(Product).all()
    return render_template('products/products.html', products=all_products)


@products.route('/<int:product_id>')
def details(product_id):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.id == product_id).first()
    return render_template('products/details.html', product=product)


@products.route('/create', methods=['GET', 'POST'])
def create():
    if current_user.is_admin:
        form = ProductForm()
        if form.validate_on_submit():
            product = Product(name=form.name.data,
                              description=form.description.data,
                              price_cents=int(form.price.data * 100),
                              picture_url=form.picture_url.data)
            db_sess = db_session.create_session()
            db_sess.add(product)
            db_sess.commit()
            return redirect(url_for('.details', product_id=product.id))
        return render_template('products/new.html', form=form)
    return redirect('/')


@products.route('/<int:product_id>/edit', methods=['GET', 'POST'])
def edit(product_id):
    if current_user.is_admin:
        db_sess = db_session.create_session()
        product = db_sess.query(Product).filter(Product.id == product_id).first()
        form = ProductForm(obj=product, price=product.price_cents / 100)
        if form.validate_on_submit():
            product.name = form.name.data
            product.description = form.description.data
            product.price_cents = int(form.price.data * 100)
            product.picture_url = form.picture_url.data
            db_sess.commit()
            return redirect(url_for('.details', product_id=product.id))
        return render_template('products/edit.html', product=product, form=form)
    return redirect('/')


@products.route('/product_delete/<int:product_id>', methods=['GET', 'POST'])
def delete(product_id):
    if current_user.is_admin:
        db_sess = db_session.create_session()
        product = db_sess.query(Product).filter(Product.id == product_id).first()
        if not product:
            abort(404)
        product_name = product.name
        db_sess.delete(product)
        db_sess.commit()
        return render_template('products/deleted.html', product_name=product_name)
    return redirect('/')
