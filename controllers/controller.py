from flask import request,render_template,redirect,url_for, session, flash
from flask import current_app as app
import os

from models.model import *
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from datetime import datetime



@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        full_name = request.form['full_name']
        password = request.form['password']
        user = User.query.filter_by(email=full_name, password=password).first()
        if user:
            session['user_id'] = user.id
            session['role'] = user.role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            return render_template('login.html', msg='Invalid user credentials....')
    return render_template('login.html', msg='')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        role = 'user'  
        address = request.form['address']
        pin_code = request.form['pin_code']
        user = User.query.filter_by(email=email).first()
        if user:
            return render_template('register.html', msg='Sorry, this email is already registered. Please use a different email.')
        new_user = User(full_name=full_name, email=email, password=password, role=role, address=address, pin_code=pin_code)
        db.session.add(new_user)
        db.session.commit()
        return render_template('login.html', success='Registration successful, please login.')
    return render_template('register.html',msg='')

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    lots = ParkingLot.query.all()
    return render_template("admin_dashboard.html", lots=lots)

@app.route('/add_lot', methods=['GET', 'POST'])
def add_lot():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        location_name = request.form['location_name']
        address = request.form['address']
        pin_code = request.form['pin_code']
        price_per_unit = float(request.form['price_per_unit'])
        total_spots = int(request.form['total_spots'])
        
        new_lot = ParkingLot(
            location_name=location_name,
            address=address,
            pin_code=pin_code,
            price_per_unit=price_per_unit,
            total_spots=total_spots
        )
        db.session.add(new_lot)
        db.session.commit()
        for _ in range(total_spots):
            spot = ParkingSpot(lot_id=new_lot.id, status='A')
            db.session.add(spot)
        db.session.commit()

        flash('Parking lot added successfully!')
        return redirect(url_for('admin_dashboard'))

    return render_template("add_lot.html")

@app.route('/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)

    if request.method == 'POST':
        lot.location_name = request.form['location_name']
        lot.address = request.form['address']
        lot.pin_code = request.form['pin_code']
        lot.price_per_unit = float(request.form['price_per_unit'])
        lot.total_spots = int(request.form['total_spots'])
        spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
        if len(spots) < lot.total_spots:
            for _ in range(lot.total_spots - len(spots)):
                new_spot = ParkingSpot(lot_id=lot.id, status='A')
                db.session.add(new_spot)
        elif len(spots) > lot.total_spots:
            for spot in spots[lot.total_spots:]:
                db.session.delete(spot)

        db.session.commit()
        flash('Parking lot updated successfully!')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_lot.html', lot=lot)

@app.route('/delete_lot/<int:lot_id>', methods=['POST', 'GET'])
def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    ParkingSpot.query.filter_by(lot_id=lot.id).delete()
    db.session.delete(lot)
    db.session.commit()
    flash('Parking lot deleted successfully!')
    return redirect(url_for('admin_dashboard'))

@app.route('/users')
def users_page():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    all_users = User.query.filter_by(role='user').all()
    return render_template('users.html', users=all_users)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    lots = []
    keyword = ""
    search_by = ""
    if request.method == 'POST':
        search_by = request.form['search_by']
        keyword = request.form['keyword']

        if search_by == "location":
            lots = ParkingLot.query.filter(ParkingLot.location_name.ilike(f"%{keyword}%")).all()
        elif search_by == "user_id":
            user = User.query.filter_by(id=keyword).first()
            if user:
                lots = ParkingLot.query.join(ParkingSpot).join(Reservation).filter(Reservation.user_id == user.id).all()
    return render_template("search.html", lots=lots, keyword=keyword, search_by=search_by)

@app.route('/summary')
def summary():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    lots = ParkingLot.query.all()
    if not lots:
        return render_template("summary.html", pie_chart=None, bar_chart=None)
    lot_names = []
    revenues = []
    occupied_counts = []
    available_counts = []
    for lot in lots:
        lot_names.append(lot.location_name)
        occupied = sum(1 for spot in lot.spots if spot.status == 'O')
        available = sum(1 for spot in lot.spots if spot.status == 'A')
        revenue = occupied * lot.price_per_unit

        revenues.append(revenue)
        occupied_counts.append(occupied)
        available_counts.append(available)
    if all(rev == 0 for rev in revenues):
        revenues = [1 for _ in revenues] 
    # Pie chart ke liye
    plt.figure(figsize=(5, 5))
    plt.pie(revenues, labels=lot_names, autopct='%1.1f%%', startangle=140)
    plt.title("Revenue from each parking lot")
    pie_path = os.path.join('static', 'revenue_pie.png')
    plt.savefig(pie_path)
    plt.close()
    # Bar chart ke liye
    plt.figure(figsize=(6, 5))
    x = range(len(lot_names))
    plt.bar(x, occupied_counts, color='red', label='Occupied')
    plt.bar(x, available_counts, bottom=occupied_counts, color='green', label='Available')
    plt.xticks(x, lot_names, rotation=30)
    plt.ylabel("Number of Spots")
    plt.title("Available vs Occupied Spots per Lot")
    plt.legend()
    bar_path = os.path.join('static', 'occupancy_bar.png')
    plt.savefig(bar_path)
    plt.close()

    return render_template("summary.html", pie_chart='revenue_pie.png', bar_chart='occupancy_bar.png')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    if request.method == 'POST':
        user.full_name = request.form['full_name']
        user.email = request.form['email']
        user.address = request.form['address']
        user.pin_code = request.form['pin_code']
        user.password = request.form['password']

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        if user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    return render_template('edit_profile.html', user=user)

@app.route('/view_spot/<int:spot_id>', methods=['GET', 'POST'])
def view_spot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)
    if request.method == 'POST':
        if spot.status == 'A':
            db.session.delete(spot)
            db.session.commit()
            flash('Spot deleted successfully!')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Cannot delete occupied spot.')
    return render_template('view_spot.html', spot=spot)

@app.route('/view_reservation/<int:spot_id>')
def view_reservation_details(spot_id):
    reservation = Reservation.query.filter_by(spot_id=spot_id).first_or_404()
    return render_template('reservation_details.html', reservation=reservation)







