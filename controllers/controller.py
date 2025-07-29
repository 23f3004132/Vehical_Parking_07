from flask import request,render_template,redirect,url_for, session, flash
from flask import current_app as app
from models.model import *
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from datetime import datetime
from collections import defaultdict

@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email, password=password).first()

        if user:
            session['user_id'] = user.id
            session['role'] = user.role
            session['full_name'] = user.full_name

            if user.role == 'admin':
                flash('Login successful! Welcome, Admin.')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Login successful! Welcome, User.')
                return redirect(url_for('user_dashboard'))
            
        else:
            flash('Invalid email or password. Please try again.')
            return render_template('login.html')
        
    return render_template('login.html')

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
            flash('Email already registered. Please log in or use a different email.')
            return render_template('register.html')
        
        new_user = User(full_name=full_name, email=email, password=password, role=role, address=address, pin_code=pin_code)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():

    session.clear()

    flash('You have been logged out successfully.')
    return redirect(url_for('login'))

#========================================================================= Admin Dashboard ====================================================================

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
        lot_name = request.form['lot_name']
        address = request.form['address']
        pin_code = request.form['pin_code']
        price_per_unit = float(request.form['price_per_unit'])
        total_spots = int(request.form['total_spots'])
        
        new_lot = ParkingLot(
            lot_name=lot_name,
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
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    lot = ParkingLot.query.get_or_404(lot_id)

    if request.method == 'POST':
        lot.lot_name = request.form['lot_name']
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

@app.route('/delete_lot/<int:lot_id>', methods=['GET'])
def delete_lot(lot_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    lot = ParkingLot.query.get_or_404(lot_id)

    if lot.occupied_spot > 0:
        flash('Cannot delete lot with occupied lot.')
        return redirect(url_for('admin_dashboard'))
    db.session.delete(lot)
    db.session.commit()
    flash('Parking lot deleted successfully!')
    return redirect(url_for('admin_dashboard'))

@app.route('/view_spot/<int:spot_id>', methods=['GET', 'POST'])
def view_spot(spot_id):

    spot = ParkingSpot.query.get_or_404(spot_id)
    lot = ParkingLot.query.get(spot.lot_id)

    if request.method == 'POST':
        if spot.status == 'A':
            lot.total_spots -= 1
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

@app.route('/parking_history')
def parking_history():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    reservations = Reservation.query.all()
    return render_template('parking_history.html', reservations=reservations)

@app.route('/users')
def users_page():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    all_users = User.query.filter_by(role='user').all()
    return render_template('users.html', users=all_users)


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
        lot_names.append(lot.lot_name)
        occupied = sum(1 for spot in lot.spots if spot.status == 'O')
        available = sum(1 for spot in lot.spots if spot.status == 'A')
        revenue = occupied * lot.price_per_unit
        revenues.append(revenue)
        occupied_counts.append(occupied)
        available_counts.append(available)

    total_revenue = sum(revenues)
    threshold_ratio = 0.05
    grouped_labels = []
    grouped_values = []
    others_value = 0

    for name, value in zip(lot_names, revenues):
        if total_revenue > 0 and value / total_revenue < threshold_ratio:
            others_value += value
        else:
            grouped_labels.append(name)
            grouped_values.append(value)

    if others_value > 0:
        grouped_labels.append("Others")
        grouped_values.append(others_value)

    if all(rev == 0 for rev in grouped_values):
        grouped_values = [1 for _ in grouped_values]

    plt.figure(figsize=(5, 5))
    plt.pie(grouped_values, labels=grouped_labels, autopct='%1.1f%%', startangle=140)
    plt.title("Revenue from each parking lot")
    pie_path = 'static/images/revenue_pie.png'
    plt.savefig(pie_path)
    plt.close()

    plt.figure(figsize=(5, 5))
    x = range(len(lot_names))
    plt.bar(x, occupied_counts, color='red', label='Occupied')
    plt.bar(x, available_counts, bottom=occupied_counts, color='green', label='Available')
    plt.xticks(x, lot_names, rotation=30)
    plt.ylabel("Number of Spots")
    plt.title("Available vs Occupied Spots per Lot")
    plt.legend()
    bar_path = 'static/images/occupancy_bar.png'
    plt.savefig(bar_path)
    plt.close()

    return render_template("summary.html", pie_chart=pie_path, bar_chart=bar_path)

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])

    if request.method == 'GET':
        return render_template('edit_profile.html', user=user)
    
    if request.method == 'POST':
        user.full_name = request.form['full_name']
        user.email = request.form['email']
        user.address = request.form['address']
        user.pin_code = request.form['pin_code']
        user.password = request.form['password']

        db.session.commit()
        flash('Profile updated successfully!', 'success')
    


#========================================================================= User Dashboard ====================================================================

@app.route('/user_dashboard', methods=['GET', 'POST'])
def user_dashboard():
    if 'user_id' not in session and session.get('role') != 'user':
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')

    lots = ParkingLot.query.all()
    reservations = Reservation.query.filter_by(user_id=user_id).all()

    return render_template("user_dashboard.html", reservations=reservations, lots=lots)


@app.route('/book/<int:lot_id>', methods=['GET', 'POST'])
def book_spot(lot_id):
    if 'user_id' not in session or session.get('role') != 'user':
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    lot = ParkingLot.query.get_or_404(lot_id)
    available_spot = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').first()


    if request.method == 'GET':
        if not available_spot:
            flash('No available spots in this lot.')
            return redirect(url_for('user_dashboard'))
        
        return render_template('book_spot.html', lot=lot, spot=available_spot,user_id=user_id)

    if request.method == 'POST':
        vehicle_no = request.form.get('vehicle_no')

        if not vehicle_no:
            flash('Vehicle number is required.')
            return redirect(url_for('show_book_form', lot_id=lot_id))

        lot.occupied_spot += 1
        db.session.commit()

        reservation = Reservation(
            user_id=user_id,
            spot_id=available_spot.id,
            vehicle_number=vehicle_no,
            parking_time=datetime.now()
        )

        available_spot.status = 'O'
        db.session.add(reservation)
        db.session.commit()

        flash('Spot successfully booked.')
        return redirect(url_for('user_dashboard'))


@app.route('/release_spot/<int:reservation_id>', methods=['GET', 'POST'])
def release_spot(reservation_id):
    if 'user_id' not in session or session.get('role') != 'user':
        return redirect(url_for('login'))
    
    reservation = Reservation.query.get_or_404(reservation_id)
    lot  = ParkingLot.query.get(reservation.parking_spot.lot_id)
    leaving_time = datetime.now()
    parked_duration = (leaving_time - reservation.parking_time).total_seconds() / 3600

    if request.method == 'GET':
        total_cost = parked_duration * lot.price_per_unit
        return render_template(
            "release_spot.html",
            reservation=reservation,
            leaving_time=leaving_time.strftime('%Y-%m-%d %H:%M:%S'),
            total_cost= round(total_cost, 2)
        )

    if request.method == 'POST':
        reservation.leaving_time = datetime.now()
    
        parked_duration = (reservation.leaving_time - reservation.parking_time).total_seconds() / 3600  # in hours 
        total_cost = parked_duration * reservation.parking_spot.parking_lot.price_per_unit
        
        reservation.total_price = round(total_cost, 2)

        db.session.commit()
        
        spot = ParkingSpot.query.get(reservation.spot_id)
        spot.status = 'A'

        lot = ParkingLot.query.get(spot.lot_id)
        lot.occupied_spot -= 1

        db.session.commit()

        flash(f"Spot released successfully. Total cost: ₹{total_cost:.2f}", 'success')
        return redirect(url_for('user_dashboard'))

@app.route('/user_summary')
def user_summary():
    if 'user_id' not in session or session.get('role') != 'user':
        return redirect(url_for('login'))

    user_id = session['user_id']
    reservations = Reservation.query.filter_by(user_id=user_id).all()

    if not reservations:
        return render_template("user_summary.html", active_chart=None, completed_chart=None, reservations=[])

    active_counts = defaultdict(int)
    completed_counts = defaultdict(int)

    for res in reservations:
        lot = res.parking_spot.parking_lot
        if lot:
            if res.leaving_time:
                completed_counts[lot.lot_name] += 1
            else:
                active_counts[lot.lot_name] += 1

    def group_low_counts(data):
        total = sum(data.values())
        threshold = 0.05
        grouped = defaultdict(int)
        for lot, count in data.items():
            if total > 0 and count / total < threshold:
                grouped["Others"] += count
            else:
                grouped[lot] += count
        return grouped

    grouped_active = group_low_counts(active_counts)
    grouped_completed = group_low_counts(completed_counts)
    print("Grouped Active:", grouped_active)
    print("Grouped Completed:", grouped_completed)

    if grouped_active:
        plt.figure(figsize=(6,4))
        plt.bar(grouped_active.keys(), grouped_active.values(), color='skyblue', width=0.6)
        plt.xlabel('Parking Lots')
        plt.ylabel('Active Bookings')
        plt.title('Active Reservations per Lot')
        plt.xticks(rotation=45)
        plt.tight_layout()
        active_path = "static/images/user_active_chart.png"
        plt.savefig(active_path)
        plt.close()
    else:
        active_path = None

    if grouped_completed:
        plt.figure(figsize=(6, 4))
        lot_names = list(grouped_completed.keys())
        counts = list(grouped_completed.values())

        bar_width = 0.4 if len(lot_names) == 1 else 0.6  

        plt.bar(lot_names, counts, color='violet', width=bar_width)
        plt.xlabel('Parking Lots')
        plt.ylabel('Completed Bookings')
        plt.title('Released Reservations per Lot')
        plt.xticks(rotation=45)
        plt.tight_layout()
        completed_path = "static/images/user_completed_chart.png"
        plt.savefig(completed_path)
        plt.close()
    else:
        completed_path = None

    return render_template("user_summary.html",
                           active_chart='user_active_chart.png' if active_path else None,
                           completed_chart='user_completed_chart.png' if completed_path else None,
                           reservations=reservations)

@app.route('/user_profile', methods=['GET', 'POST'])
def user_profile():
    if 'user_id' not in session or session.get('role') != 'user':
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if request.method == 'GET':
        return render_template('user_profile.html', user=user)

    if request.method == 'POST':
        user.password = request.form['password']
        user.full_name = request.form['full_name']
        user.pin_code = request.form['pin_code']
        user.address = request.form['address']

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user_dashboard'))
