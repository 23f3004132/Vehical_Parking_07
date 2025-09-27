# 🚗 Vehical_Parking_07

## 📝 Project Overview

A modern web application for managing vehicle parking lots, spots, and reservations, supporting both **Admin** and **User** roles. It ensures easy parking space allocation, real-time spot tracking, and history summaries using Flask, Jinja2, SQLite, and Matplotlib.

---

## 🚦 Key Features

### **Admins:**
- Create, edit, and delete parking lots.
- Automatically generate parking spots as per lot capacity.
- View and manage all parking spots and their statuses.
- View a list of all users and their parking/reservation details.
- Monitor parking history and generate summaries.
- Search for users or parking spots to check status.
- Access comprehensive management tools for lots, spots, and users.

### **Users:**
- Register and log in to the platform.
- View available parking lots and spot availability.
- Automatically reserve the first available parking spot.
- Occupy or release a spot, with timestamps recorded for each action.
- Track and view their parking reservation history and costs.
- View summaries of their parking usage.

### **Parking System:**
- Real-time status updates for parking spots (available/occupied).
- Automatic calculation of parking cost based on duration and lot pricing.
- Reservation and release of spots with accurate time tracking.

### **Security & Access:**
- Role-based dashboards for admins and users.
- Predefined admin login for secure management.
- Route protection and session management.

---

## ✨ Optional Enhancements

- **Admin Search Functionality:**  
  Search for users or parking spots and check their status directly from the admin dashboard.

- **API Integration (Optional):**  
  Provide JSON-based APIs for parking lots, spots, and reservations using Flask.

- **Charts & Visualization:**  
  Use Matplotlib to generate charts and visual summaries for both users and admins (e.g., revenue, occupancy, booking history).

- **Frontend/Backend Validation:**  
  Implement form validation using HTML5, JavaScript, and backend validation in Flask routes.

- **Flask Session & Security:**  
  Use Flask session management for login/logout, and protect routes based on user roles.

---

## 🛠️ Technologies Used

- **Backend:** Python, Flask, Flask-SQLAlchemy  
- **Frontend:** HTML, CSS, Jinja2  
- **Database:** SQLite  
- **Visualization:** Matplotlib  
- **Session & Security:** Flask session management  
- **API (Optional):** Flask JSON endpoints  

---

## 🏁 Milestones

### **Milestone 1: Database Models and Schema Setup**
- Models: `User`, `ParkingLot`, `ParkingSpot`, `Reservation`  
- Foreign key relationships established  
- Database created programmatically

### **Milestone 2: Authentication and Role-Based Access**
- User registration/login  
- Predefined admin login  
- Role-specific dashboard rendering

### **Milestone 3: Admin Dashboard and Lot/Spot Management**
- Admin can create/edit/delete parking lots  
- Spots are auto-generated based on lot capacity  
- View lot/spot details and status  
- View user and reservation info

### **Milestone 4: User Dashboard and Reservation System**
- Users can view available parking lots  
- Automatic allocation of first available parking spot  
- Reserve and release spot with timestamp tracking  
- Parking summary and history page

### **Milestone 5: Reservation History and Summaries**
- Parking history stored and displayed for each user  
- Parking durations and timestamps recorded  
- Admin access to full reservation records

### **Milestone 6: Slot Time Calculation and Cost**
- Calculate cost based on duration and lot price  
- Cost details shown in summaries  

---

## 📁 Folder Structure

23f3004132
│   Project Report_ Vehicle Parking App 07.pdf
│   
└───Code
    │   .gitignore
    │   app.py
    │   README.md
    │   requirements.txt
    │   
    ├───controllers
    │       controller.py
    │       
    ├───instance
    │       parking.db
    │       
    ├───models
    │       model.py
    │       
    ├───static
    │   ├───images
    │   │       occupancy_bar.png
    │   │       revenue_pie.png
    │   │       user_active_chart.png
    │   │       user_completed_chart.png
    │   │       
    │   └───styles
    │           main.css
    │
    └───templates
            add_lot.html
            admin_base.html
            admin_dashboard.html
            book_spot.html
            edit_lot.html
            edit_profile.html
            login.html
            parking_history.html
            register.html
            release_spot.html
            reservation_details.html
            summary.html
            users.html
            user_base.html
            user_dashboard.html
            user_profile.html
            user_summary.html
            view_spot.html


## 🔐 Admin Credentials

- **Email:** `Satyanshi@gmail.com`  
- **Password:** `123`  

---

## ⚙️ How to Run the App

1. **unzip the project folder.**
2. Change the directory to code folder and open in vs code.

3. Create and activate virtual env : 
    python -m venv venv
    .\venv\Scripts\activate

2. Install dependencies :
    pip install -r requirements.txt

3. Run the application:
    python app.py

4. Open your browser and go to:
    http://127.0.0.1:5000/

5. Login as admin or register as user to explore functionalities.

---

## 🤖 AI Usage Declaration

- Percentage of AI-generated code: **30–40%**  
- AI was used for:  
- CSS styling and HTML layout suggestions  
- Debugging Flask route logic  
- Writing documentation and summaries  
- Creating matplotlib chart examples  

---

## 📽️ Demo Video Link

👉 https://drive.google.com/file/d/1p7z5pdpCIQ6zx2zOeT3hAAo1Y6dupSGF/view?usp=sharing
