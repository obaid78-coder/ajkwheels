from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3, os, hashlib, json
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'ajkwheels_secret_key_2024'
DB_PATH = os.path.join(os.path.dirname(__file__), 'db', 'ajkwheels.db')

# ─── Database ─────────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone TEXT,
            city TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            make TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER NOT NULL,
            price INTEGER NOT NULL,
            mileage INTEGER,
            fuel_type TEXT,
            transmission TEXT,
            engine_cc INTEGER,
            color TEXT,
            city TEXT,
            condition TEXT,
            description TEXT,
            image_url TEXT,
            views INTEGER DEFAULT 0,
            is_featured INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS bikes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            make TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER NOT NULL,
            price INTEGER NOT NULL,
            mileage INTEGER,
            fuel_type TEXT,
            engine_cc INTEGER,
            color TEXT,
            city TEXT,
            condition TEXT,
            description TEXT,
            image_url TEXT,
            views INTEGER DEFAULT 0,
            is_featured INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_type TEXT,
            item_id INTEGER,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user_id INTEGER,
            to_user_id INTEGER,
            car_id INTEGER,
            message TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)
    # Seed sample data
    c.execute("SELECT COUNT(*) FROM cars")
    if c.fetchone()[0] == 0:
        seed_data(c)
    conn.commit()
    conn.close()

def seed_data(c):
    # Create demo user
    pw = hashlib.sha256("demo123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users(name,email,password,phone,city) VALUES(?,?,?,?,?)",
              ("Demo User","demo@ajkwheels.com",pw,"0300-1234567","Lahore"))
    
    cars_data = [
        (1,"Toyota Corolla 2022 GLi","Toyota","Corolla",2022,3200000,15000,"Petrol","Automatic",1800,"White","Lahore","Used","Excellent condition, single owner, all documents clear. Full original paint, no accident history.",
         "https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?w=600&q=80",1,1),
        (1,"Honda Civic 2023 Turbo","Honda","Civic",2023,5800000,8000,"Petrol","Automatic",1500,"Red","Karachi","Used","Just 8000km driven. Turbo variant with all features. Immaculate condition.",
         "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=600&q=80",1,1),
        (1,"Suzuki Alto 2023 VXL","Suzuki","Alto",2023,1750000,5000,"Petrol","Automatic",660,"Silver","Islamabad","Used","AGS automatic variant. Factory fitted CNG not done. Genuine 5000km.",
         "https://images.unsplash.com/photo-1549924231-f129b911e442?w=600&q=80",0,0),
        (1,"Toyota Fortuner 2022 Sigma 4","Toyota","Fortuner",2022,9500000,22000,"Diesel","Automatic",2800,"Black","Lahore","Used","Sigma 4 full option. 4x4 variant. All genuine. Black interior.",
         "https://images.unsplash.com/photo-1574179893384-7b8ea5d0f3c8?w=600&q=80",1,1),
        (1,"Honda BRV 2022 S CVT","Honda","BRV",2022,4200000,18000,"Petrol","Automatic",1500,"Blue","Peshawar","Used","S variant CVT. 7 seater. All original, no repaint.",
         "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=600&q=80",0,0),
        (1,"Toyota Yaris 2023 ATIV","Toyota","Yaris",2023,3100000,12000,"Petrol","Automatic",1300,"Gray","Multan","Used","ATIV variant. Single owner. All genuine paint.",
         "https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?w=600&q=80",0,1),
        (1,"KIA Sportage 2023 AWD","KIA","Sportage",2023,7800000,9000,"Petrol","Automatic",2000,"Pearl White","Lahore","Used","AWD full option. Panoramic roof. All features.",
         "https://images.unsplash.com/photo-1583121274602-3e2820c69888?w=600&q=80",1,1),
        (1,"Suzuki Cultus 2022 VXL","Suzuki","Cultus",2022,2150000,28000,"Petrol","Manual",1000,"Red","Faisalabad","Used","VXL top variant. Well maintained. Power windows, power mirrors.",
         "https://images.unsplash.com/photo-1553440569-bcc63803a83d?w=600&q=80",0,0),
    ]
    c.executemany("""INSERT INTO cars(user_id,title,make,model,year,price,mileage,fuel_type,transmission,
                  engine_cc,color,city,condition,description,image_url,is_featured,status) 
                  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", cars_data)
    
    bikes_data = [
        (1,"Honda CB150F 2023","Honda","CB150F",2023,320000,3000,"Petrol",150,"Red","Lahore","Used",
         "Just 3 months used. All genuine. No modification.",
         "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=80",1,1),
        (1,"Yamaha YBR 125G 2022","Yamaha","YBR 125G",2022,210000,15000,"Petrol",125,"Black","Karachi","Used",
         "Good condition. All documents complete.",
         "https://images.unsplash.com/photo-1568772585407-9361f9bf3a87?w=600&q=80",0,0),
        (1,"Honda Pridor 2023","Honda","Pridor",2023,185000,2000,"Petrol",100,"Blue","Islamabad","Used",
         "Like new condition. 2 months used only.",
         "https://images.unsplash.com/photo-1449426468159-d96dbf08f19f?w=600&q=80",0,1),
    ]
    c.executemany("""INSERT INTO bikes(user_id,title,make,model,year,price,mileage,fuel_type,engine_cc,color,
                  city,condition,description,image_url,is_featured,status)
                  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", bikes_data)

# ─── Helpers ──────────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def hash_password(pw): return hashlib.sha256(pw.encode()).hexdigest()

def fmt_price(p):
    if p >= 10000000: return f"{p/10000000:.1f} Crore"
    if p >= 100000: return f"{p/100000:.1f} Lakh"
    return f"{p:,}"

app.jinja_env.filters['fmt_price'] = fmt_price
app.jinja_env.filters['fmt_num'] = lambda n: f"{n:,}" if n else "N/A"

# ─── Routes ───────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    db = get_db()
    featured_cars = db.execute("SELECT * FROM cars WHERE is_featured=1 AND status='active' ORDER BY created_at DESC LIMIT 8").fetchall()
    featured_bikes = db.execute("SELECT * FROM bikes WHERE is_featured=1 AND status='active' ORDER BY created_at DESC LIMIT 4").fetchall()
    stats = {
        'cars': db.execute("SELECT COUNT(*) FROM cars WHERE status='active'").fetchone()[0],
        'bikes': db.execute("SELECT COUNT(*) FROM bikes WHERE status='active'").fetchone()[0],
        'users': db.execute("SELECT COUNT(*) FROM users").fetchone()[0],
    }
    db.close()
    return render_template('index.html', featured_cars=featured_cars, featured_bikes=featured_bikes, stats=stats)

@app.route('/cars')
def cars():
    db = get_db()
    q = request.args.get('q','')
    make = request.args.get('make','')
    city = request.args.get('city','')
    min_price = request.args.get('min_price','')
    max_price = request.args.get('max_price','')
    year_from = request.args.get('year_from','')
    transmission = request.args.get('transmission','')
    sort = request.args.get('sort','newest')
    page = int(request.args.get('page', 1))
    per_page = 12

    sql = "SELECT * FROM cars WHERE status='active'"
    params = []
    if q: sql += " AND (title LIKE ? OR make LIKE ? OR model LIKE ?)"; params += [f'%{q}%']*3
    if make: sql += " AND make=?"; params.append(make)
    if city: sql += " AND city=?"; params.append(city)
    if min_price: sql += " AND price>=?"; params.append(int(min_price))
    if max_price: sql += " AND price<=?"; params.append(int(max_price))
    if year_from: sql += " AND year>=?"; params.append(int(year_from))
    if transmission: sql += " AND transmission=?"; params.append(transmission)

    order = {'newest':'created_at DESC','oldest':'created_at ASC','price_low':'price ASC','price_high':'price DESC','mileage':'mileage ASC'}.get(sort,'created_at DESC')
    sql += f" ORDER BY {order}"

    all_cars = db.execute(sql, params).fetchall()
    total = len(all_cars)
    cars_list = all_cars[(page-1)*per_page : page*per_page]
    makes = db.execute("SELECT DISTINCT make FROM cars WHERE status='active' ORDER BY make").fetchall()
    cities = db.execute("SELECT DISTINCT city FROM cars WHERE status='active' ORDER BY city").fetchall()
    db.close()
    return render_template('cars.html', cars=cars_list, total=total, page=page, per_page=per_page,
                           makes=makes, cities=cities, args=request.args)

@app.route('/car/<int:car_id>')
def car_detail(car_id):
    db = get_db()
    db.execute("UPDATE cars SET views=views+1 WHERE id=?", (car_id,))
    db.commit()
    car = db.execute("SELECT c.*, u.name as seller_name, u.phone as seller_phone, u.city as seller_city, u.created_at as member_since FROM cars c JOIN users u ON c.user_id=u.id WHERE c.id=?", (car_id,)).fetchone()
    if not car: db.close(); return redirect(url_for('cars'))
    similar = db.execute("SELECT * FROM cars WHERE make=? AND id!=? AND status='active' LIMIT 4", (car['make'], car_id)).fetchall()
    db.close()
    return render_template('car_detail.html', car=car, similar=similar)

@app.route('/bikes')
def bikes():
    db = get_db()
    q = request.args.get('q','')
    make = request.args.get('make','')
    city = request.args.get('city','')
    page = int(request.args.get('page',1))
    per_page = 12
    sql = "SELECT * FROM bikes WHERE status='active'"
    params = []
    if q: sql += " AND (title LIKE ? OR make LIKE ? OR model LIKE ?)"; params += [f'%{q}%']*3
    if make: sql += " AND make=?"; params.append(make)
    if city: sql += " AND city=?"; params.append(city)
    sql += " ORDER BY created_at DESC"
    all_bikes = db.execute(sql, params).fetchall()
    total = len(all_bikes)
    bikes_list = all_bikes[(page-1)*per_page : page*per_page]
    makes = db.execute("SELECT DISTINCT make FROM bikes ORDER BY make").fetchall()
    cities = db.execute("SELECT DISTINCT city FROM bikes ORDER BY city").fetchall()
    db.close()
    return render_template('bikes.html', bikes=bikes_list, total=total, page=page, per_page=per_page,
                           makes=makes, cities=cities, args=request.args)

@app.route('/bike/<int:bike_id>')
def bike_detail(bike_id):
    db = get_db()
    db.execute("UPDATE bikes SET views=views+1 WHERE id=?", (bike_id,))
    db.commit()
    bike = db.execute("SELECT b.*, u.name as seller_name, u.phone as seller_phone FROM bikes b JOIN users u ON b.user_id=u.id WHERE b.id=?", (bike_id,)).fetchone()
    if not bike: db.close(); return redirect(url_for('bikes'))
    similar = db.execute("SELECT * FROM bikes WHERE make=? AND id!=? AND status='active' LIMIT 4", (bike['make'], bike_id)).fetchall()
    db.close()
    return render_template('bike_detail.html', bike=bike, similar=similar)

@app.route('/post-ad', methods=['GET','POST'])
@login_required
def post_ad():
    if request.method == 'POST':
        ad_type = request.form.get('ad_type', 'car')
        db = get_db()
        if ad_type == 'car':
            db.execute("""INSERT INTO cars(user_id,title,make,model,year,price,mileage,fuel_type,transmission,
                       engine_cc,color,city,condition,description,image_url) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                      (session['user_id'],
                       f"{request.form['make']} {request.form['model']} {request.form['year']}",
                       request.form['make'], request.form['model'], int(request.form['year']),
                       int(request.form['price']), int(request.form.get('mileage',0)),
                       request.form['fuel_type'], request.form['transmission'],
                       int(request.form.get('engine_cc',0)), request.form['color'],
                       request.form['city'], request.form['condition'],
                       request.form['description'],
                       request.form.get('image_url','https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?w=600&q=80')))
        else:
            db.execute("""INSERT INTO bikes(user_id,title,make,model,year,price,mileage,fuel_type,engine_cc,
                       color,city,condition,description,image_url) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                      (session['user_id'],
                       f"{request.form['make']} {request.form['model']} {request.form['year']}",
                       request.form['make'], request.form['model'], int(request.form['year']),
                       int(request.form['price']), int(request.form.get('mileage',0)),
                       request.form['fuel_type'], int(request.form.get('engine_cc',0)),
                       request.form['color'], request.form['city'], request.form['condition'],
                       request.form['description'],
                       request.form.get('image_url','https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=80')))
        db.commit(); db.close()
        flash('Ad posted successfully!', 'success')
        return redirect(url_for('my_ads'))
    return render_template('post_ad.html')

@app.route('/my-ads')
@login_required
def my_ads():
    db = get_db()
    my_cars = db.execute("SELECT * FROM cars WHERE user_id=? ORDER BY created_at DESC", (session['user_id'],)).fetchall()
    my_bikes = db.execute("SELECT * FROM bikes WHERE user_id=? ORDER BY created_at DESC", (session['user_id'],)).fetchall()
    db.close()
    return render_template('my_ads.html', my_cars=my_cars, my_bikes=my_bikes)

@app.route('/delete-ad/<string:type>/<int:ad_id>', methods=['POST'])
@login_required
def delete_ad(type, ad_id):
    db = get_db()
    table = 'cars' if type == 'car' else 'bikes'
    db.execute(f"DELETE FROM {table} WHERE id=? AND user_id=?", (ad_id, session['user_id']))
    db.commit(); db.close()
    flash('Ad deleted.', 'info')
    return redirect(url_for('my_ads'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email=? AND password=?",
                         (request.form['email'], hash_password(request.form['password']))).fetchone()
        db.close()
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('index'))
        flash('Invalid email or password', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        db = get_db()
        try:
            db.execute("INSERT INTO users(name,email,password,phone,city) VALUES(?,?,?,?,?)",
                      (request.form['name'], request.form['email'],
                       hash_password(request.form['password']),
                       request.form.get('phone',''), request.form.get('city','')))
            db.commit()
            user = db.execute("SELECT * FROM users WHERE email=?", (request.form['email'],)).fetchone()
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            db.close()
            flash('Account created successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.close()
            flash('Email already registered', 'error')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id=?", (session['user_id'],)).fetchone()
    total_ads = db.execute("SELECT COUNT(*) FROM cars WHERE user_id=?", (session['user_id'],)).fetchone()[0]
    total_ads += db.execute("SELECT COUNT(*) FROM bikes WHERE user_id=?", (session['user_id'],)).fetchone()[0]
    db.close()
    return render_template('profile.html', user=user, total_ads=total_ads)

@app.route('/compare')
def compare():
    return render_template('compare.html')

@app.route('/api/car-compare')
def api_compare():
    ids = request.args.get('ids','').split(',')
    db = get_db()
    cars = [dict(db.execute("SELECT * FROM cars WHERE id=?", (i,)).fetchone()) for i in ids if i]
    db.close()
    return jsonify(cars)

@app.route('/api/search-suggestions')
def search_suggestions():
    q = request.args.get('q','')
    db = get_db()
    cars = db.execute("SELECT title, 'car' as type FROM cars WHERE title LIKE ? LIMIT 5", (f'%{q}%',)).fetchall()
    bikes = db.execute("SELECT title, 'bike' as type FROM bikes WHERE title LIKE ? LIMIT 3", (f'%{q}%',)).fetchall()
    db.close()
    return jsonify([{'title': r['title'], 'type': r['type']} for r in list(cars)+list(bikes)])

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5050))
app.run(host='0.0.0.0', port=port)
