from flask import Flask, render_template, request, session, redirect, url_for, flash, send_file
import os
import json
import qrcode
from io import BytesIO
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'gupta_cloth_house_global_24_7_secret')
UPLOAD_FOLDER = 'static/images'
DB_FILE = 'products.json'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def load_products():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return [
        {"id": 1, "name": "Premium Silk Ladies Suit", "price": 1800, "category": "Ladies Suite", "image": "ladies_suit.jpg", "description": "Elegant silk wear."},
        {"id": 2, "name": "Designer Banarasi Saree", "price": 3500, "category": "Sarees", "image": "banarasi.jpg", "description": "Traditional gold zari work."},
        {"id": 3, "name": "Men's Night Suit", "price": 750, "category": "Men Night Suite", "image": "mens_night.jpg", "description": "Cotton comfort."},
        {"id": 4, "name": "Woolen Winter Cardigan", "price": 1500, "category": "Winter Wear", "image": "cardigan.jpg", "description": "Warm & stylish."}
    ]

def save_products(products):
    with open(DB_FILE, 'w') as f:
        json.dump(products, f, indent=4)

@app.route('/')
def index():
    return render_template('index.html', products=load_products())

@app.route('/category/<cat_name>')
def category(cat_name):
    products = [p for p in load_products() if p['category'] == cat_name]
    return render_template('category.html', products=products, category=cat_name)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/poster')
def poster():
    # Use request.host_url to automatically detect the cloud link
    return render_template('poster.html', shop_url=request.host_url)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        category = request.form.get('category')
        description = request.form.get('description')
        file = request.files.get('file')
        if name and price and category and file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            products = load_products()
            new_id = max([p['id'] for p in products]) + 1 if products else 1
            products.append({"id": new_id, "name": name, "price": int(price), "category": category, "image": filename, "description": description})
            save_products(products)
            flash("Product Added Successfully!")
            return redirect(url_for('index'))
    return render_template('admin.html', shop_url=request.host_url)

@app.route('/qr_code')
def generate_qr():
    # Automatically creates QR for the current website address
    shop_url = request.host_url
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(shop_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#9b0000", back_color="white")
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session: session['cart'] = []
    product = next((p for p in load_products() if p['id'] == product_id), None)
    if product:
        session['cart'].append(product)
        session.modified = True
        flash(f"Added {product['name']} to cart!")
    return redirect(request.referrer or url_for('index'))

@app.route('/cart')
def cart():
    items = session.get('cart', [])
    total = sum(item['price'] for item in items)
    return render_template('cart.html', items=items, total=total)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        session.pop('cart', None)
        return render_template('success.html', order_id="GCH-"+os.urandom(3).hex().upper())
    items = session.get('cart', [])
    total = sum(item['price'] for item in items)
    return render_template('checkout.html', total=total)

@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('cart'))

if __name__ == '__main__':
    # Local fallback
    from waitress import serve
    print(f"\nGUAPTA CLOTH HOUSE LOCAL: http://127.0.0.1:5000")
    serve(app, host='0.0.0.0', port=5000)
