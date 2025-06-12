from flask import Flask, render_template, request, jsonify, url_for, redirect, session, flash, Blueprint, g
from functools import wraps
from datetime import datetime, timedelta
from models import Item, Category, Location
import os
from flask import send_from_directory
from werkzeug.utils import secure_filename
from models import db, Item, Claim, Category, Location, User, Admin
from collections import defaultdict
from locations import locations_bp
import qrcode
import secrets
import base64
from io import BytesIO
import hashlib
from config import Config


# Initialize the Flask app
app = Flask(__name__)
app.config.from_object(Config)


# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'  # Folder to store uploaded images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed file extensions

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# QR Code Utility Functions
def generate_unique_code():
    """Generate a unique code for item registration"""
    return secrets.token_urlsafe(8)  # 8-character unique code

def generate_qr_code(unique_code, base_url):
    """Generate a QR code for the given unique code"""
    qr_url = f"{base_url}/scan/{unique_code}"
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to BytesIO
    buffered = BytesIO()
    img.save(buffered)
    
    # Create base64 string for embedding in HTML
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}", qr_url


db.init_app(app)

from models import *

# Register blueprints
app.register_blueprint(locations_bp)

with app.app_context():
    db.create_all()  

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


########################################### ADMIN PAGE ####################################

# Initial admin credentials (will be migrated to the database)
ADMIN_CREDENTIALS = {"admin": "123"}

# ------------------ ADMIN LOGIN ROUTE ------------------
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if admin exists in database
        admin = Admin.query.filter_by(username=username).first()
        
        # For debugging
        print(f"Login attempt: {username}")
        print(f"Admin found in DB: {admin is not None}")
        if admin:
            print(f"Password comparison: {admin.password} vs input: {password}")
        
        # If admin exists in database, use that for authentication
        if admin and admin.password.strip() == password.strip():  # Compare with whitespace trimmed
            session['admin_logged_in'] = True
            session['admin_username'] = admin.username
            session['admin_id'] = admin.id
            
            # Update last login time
            admin.last_login = datetime.now()
            db.session.commit()
            
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))        # If not in database, use legacy credentials (temporary for migration)
        elif username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username].strip() == password.strip():
            session['admin_logged_in'] = True
            session['admin_username'] = username
            
            # Create admin in database if doesn't exist yet
            new_admin = Admin(
                username=username,
                password=password,  # In production, this should be hashed
                created_at=datetime.now(),
                last_login=datetime.now()
            )
            db.session.add(new_admin)
            db.session.commit()
            session['admin_id'] = new_admin.id
            
            flash("Login successful! New admin account created.", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials! Please check your username and password.", "danger")

    return render_template('admin/admin_login.html')

    return render_template('admin/admin_login.html')

# ------------------ ADMIN LOGOUT ROUTE ------------------
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash("Logged out successfully!", "info")
    return redirect(url_for('admin_login'))

# ------------------ ADMIN AUTH DECORATOR ------------------
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash("Please log in to access the dashboard!", "warning")
            return redirect(url_for('admin_login'))
        
        # Add admin info to g for access in templates
        if session.get('admin_username'):
            admin = Admin.query.filter_by(username=session['admin_username']).first()
            if not admin:
                # If admin no longer exists in DB, log them out
                session.pop('admin_logged_in', None)
                session.pop('admin_username', None)
                session.pop('admin_id', None)
                flash("Admin account not found. Please log in again.", "warning")
                return redirect(url_for('admin_login'))
            
            g.admin = admin
        
        return f(*args, **kwargs)
    return decorated_function

# ------------------ ADMIN PROFILE ROUTES ------------------
@app.route('/admin/profile')
@admin_required
def admin_profile():
    admin = Admin.query.filter_by(username=session['admin_username']).first_or_404()
    return render_template('admin/admin_profile.html', admin=admin)

@app.route('/admin/profile/edit', methods=['GET', 'POST'])
@admin_required
def edit_admin_profile():
    admin = Admin.query.filter_by(username=session['admin_username']).first_or_404()
    
    if request.method == 'POST':
        admin.email = request.form.get('email')
        admin.full_name = request.form.get('full_name')
        admin.position = request.form.get('position')
        
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('admin_profile'))
    
    return render_template('admin/edit_profile.html', admin=admin)

@app.route('/admin/profile/change-password', methods=['GET', 'POST'])
@admin_required
def change_admin_password():
    admin = Admin.query.filter_by(username=session['admin_username']).first_or_404()
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if admin.password.strip() != current_password.strip():
            flash("Current password is incorrect!", "danger")
            return redirect(url_for('change_admin_password'))
        
        if new_password != confirm_password:
            flash("New passwords do not match!", "danger")
            return redirect(url_for('change_admin_password'))
        
        admin.password = new_password
        db.session.commit()
        
        flash("Password changed successfully!", "success")
        return redirect(url_for('admin_profile'))
    
    return render_template('admin/change_password.html', admin=admin)
############################################################## DASHBOARD ###################################################################

@app.route('/')
@admin_required
def dashboard():
    total_items_active = Item.query.filter_by(status='Unclaimed').count()
    # Count items that are truly lost - include both 'Lost' and 'Unclaimed' statuses
    total_items_lost = Item.query.filter(
        (Item.status == 'Lost') | 
        (Item.status == 'Unclaimed')
    ).count()
    total_tagged_items = Item.query.filter(Item.rfid_tag.isnot(None)).filter(Item.rfid_tag != "").count()  
    total_items_found = Item.query.filter_by(status='Claimed').count()
    lost_items_by_category = (
        db.session.query(Category.name, db.func.count(Item.id))
        .join(Item, Category.id == Item.category_id)
        .filter((Item.status == 'Lost') | (Item.status == 'Unclaimed'))  # Include both Lost and Unclaimed status
        .group_by(Category.name)
        .all()
    )
    
    lost_items_by_category_dict = {category: count for category, count in lost_items_by_category}
    
    latest_tagged_items = (
        Item.query.filter(Item.rfid_tag.isnot(None))
        .filter(Item.rfid_tag != "")
        .filter(Item.status.in_(["Unclaimed", "Lost"]))  # Only include lost/unclaimed items
        .order_by(Item.date_reported.desc())  # Assuming date_reported is used for latest items
        .limit(5)
        .all()
    )
 
    print("Fetched latest tagged lost items:", latest_tagged_items)

    return render_template(
        'dashboard.html',
        total_items_active=total_items_active,
        total_tagged_items=total_tagged_items,
        total_items_lost=total_items_lost,
        total_items_found=total_items_found,
        lost_items_by_category=lost_items_by_category_dict,
        latest_tagged_items=latest_tagged_items
    )

@app.route('/lost-items-by-location')
def lost_items_by_location():
    results = (
        db.session.query(Location.name, db.func.count(Item.id))
        .join(Item, Location.id == Item.location_id)
        .filter((Item.status == 'Lost') | (Item.status == 'Unclaimed'))  # Count both lost and unclaimed items
        .group_by(Location.name)
        .all()
    )

    data = [{"location": loc, "count": count} for loc, count in results]
    return jsonify(data)


############################################## UPDATE ITEM ON LIST ENTRY ##########################################

@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    try:
        item = Item.query.get(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404

        print(f"Current item status: {item.status}")

        if "category_id" in request.form and request.form["category_id"].isdigit():
            item.category_id = int(request.form["category_id"])

        if "location_id" in request.form and request.form["location_id"].isdigit():
            item.location_id = int(request.form["location_id"])

        if "description" in request.form:
            item.description = request.form["description"].strip()

        if "date_reported" in request.form:
            try:
                item.date_reported = datetime.strptime(request.form["date_reported"], "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

        if "status" in request.form:
            new_status = request.form["status"].strip()
            
            if item.status != "Claimed" and new_status == "Claimed":
                print("Status changed to Claimed. Creating a new claim record...") 
                item.status = "Claimed"

                claim_entry = Claim(item_id=item.id, claim_date=datetime.utcnow(), status="Claimed")
                db.session.add(claim_entry)
            else:
                item.status = new_status
                
        if "rfid_tag" in request.form:
            item.rfid_tag = request.form["rfid_tag"].strip()
            # If item is set to not tagged, clear the unique_code
            if item.rfid_tag == "None" and "unique_code" not in request.form:
                item.unique_code = None

        if "unique_code" in request.form:
            unique_code = request.form["unique_code"].strip()
            if unique_code:
                item.unique_code = unique_code
            else:
                item.unique_code = None

        if "image" in request.files:
            image = request.files["image"]
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                item.image_file = filename 

        db.session.commit()
        return jsonify({"message": "Item updated successfully!"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error updating item: {str(e)}")  
        return jsonify({"error": str(e)}), 500
    

@app.route('/api/claimed-items', methods=['GET'])
def get_claimed_items():
    """Fetch all claimed items with their claim date."""
    claimed_items = (
        db.session.query(
            Item.id, Item.description, Item.status, Item.date_reported.label("date_reported"),
            Claim.claim_date.label("date_claimed"), Category.name.label("category"),
            Item.rfid_tag
        )
        .join(Claim, Claim.item_id == Item.id)
        .join(Category, Item.category_id == Category.id)
        .filter(Item.status == "Claimed") 
        .all()
    )

    result = []
    for item in claimed_items:
        result.append({
            "id": item.id,
            "category": item.category,
            "description": item.description,
            "date_reported": item.date_reported.strftime("%Y-%m-%d"),
            "date_claimed": item.date_claimed.strftime("%Y-%m-%d") if item.date_claimed else "Not Available",
            "rfid_tag": item.rfid_tag,
            "status": item.status
        })

    return jsonify(result)



################################# CATEGORIES ####################################################

@app.route('/categories')
@admin_required
def categories():
    categories = Category.query.all()
    print('Go to Categories')
    return render_template('categories.html', categories=categories)

@app.route('/locations')
@admin_required
def locations():
    locations = Location.query.all()
    return render_template('locations.html', locations=locations)

@app.route('/add_category', methods=['POST'])
def add_category():
    data = request.json
    new_category = Category(name=data['name'], description=data['description'])
    db.session.add(new_category)
    db.session.commit()
    return jsonify({"message": "Category added successfully!"}), 201



@app.route('/get_locations', methods=["GET"])
def get_locations():
    locations = Location.query.all()
    return jsonify([
        {
            'id': loc.id,
            'name': loc.name
        } for loc in locations
    ])

@app.route('/update_location/<int:location_id>', methods=['PUT'])
def update_location(location_id):
    try:
        location = Location.query.get(location_id)
        if not location:
            return jsonify({"error": "Location not found"}), 404

        data = request.json
        location.name = data.get("name", location.name)

        db.session.commit()
        return jsonify({"message": "Location updated successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/delete_location/<int:id>', methods=['DELETE'])
def delete_location(id):
    location = Location.query.get(id)
    if not location:
        return jsonify({"error": "Location not found"}), 404
        
    # Check if location is in use by any items
    has_items = db.session.query(Item.id).filter_by(location_id=location.id).first() is not None
    if has_items:
        return jsonify({"error": "Cannot delete location as it is in use by items"}), 400
        
    db.session.delete(location)
    db.session.commit()
    
    return jsonify({"message": "Location deleted successfully"}), 200

@app.route("/get_categories", methods=["GET"])
def get_categories():
    categories = Category.query.all()
    categories_data = []

    for category in categories:
        has_items = db.session.query(Item.id).filter_by(category_id=category.id).first() is not None
        status = "Active" if has_items else "Inactive"

        categories_data.append({
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "status": status, 
        })

    return jsonify(categories_data)


@app.route('/update_category/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    try:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({"error": "Category not found"}), 404

        data = request.json
        category.name = data.get("name", category.name)
        category.description = data.get("description", category.description)
        category.status = data.get("status", category.status)

        db.session.commit()
        return jsonify({"message": "Category updated successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@app.route('/delete_category/<int:id>', methods=['DELETE'])
def delete_category(id):
    category = Category.query.get(id)
    if not category:
        return jsonify({"error": "Category not found"}), 404

    db.session.delete(category)
    db.session.commit()
    
    return jsonify({"message": "Category deleted successfully"}), 200


######################################## ITEMS/ LIST ENTRY ITEMS ####################################################

@app.route('/items/listEntryItem')
def list_entry_item_page():
    categories = Category.query.all()
    locations = Location.query.all() 
    return render_template('items/listEntryItem.html', categories=categories, locations=locations)

@app.route("/api/items", methods=["GET"])
def get_items():
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()
    location_id = request.args.get("location", "").strip()
    date_sort = request.args.get("date", "").strip()  # Sorting order

    query = Item.query

    # Search by description (case-insensitive)
    if search:
        query = query.filter(Item.description.ilike(f"%{search}%"))

    # Filter by status (Claimed / Unclaimed)
    if status:
        query = query.filter(Item.status == status)

    # Filter by location_id (ensure conversion to integer)
    if location_id.isdigit():
        query = query.filter(Item.location_id == int(location_id))

    # Sort by date (Newest / Oldest)
    if date_sort.lower() == "newest":
        query = query.order_by(Item.date_reported.desc())
    elif date_sort.lower() == "oldest":
        query = query.order_by(Item.date_reported.asc())

    items = query.all()
    
    return jsonify([
        {
            "id": item.id,
            "category": item.category.name if item.category else "Unknown",
            "description": item.description,
            "location": item.location.name if item.location else "Unknown",
            "location_id": item.location_id,
            "date_reported": item.date_reported.strftime("%B %d, %Y"),
            "status": item.status,
            "rfid_tag": item.rfid_tag,
            "unique_code": item.unique_code,
            "image_file": item.image_file if item.image_file else "default.jpg"
        }
        for item in items
    ])


@app.route("/api/items/<int:item_id>", methods=["GET"])
def get_item_by_id(item_id):
    item = Item.query.get(item_id)

    if not item:
        return jsonify({"error": "Item not found"}), 404
        
    return jsonify({
        "id": item.id,
        "category_id": item.category_id,
        "description": item.description,
        "location": item.location.name if item.location else "Unknown",
        "location_id": item.location_id,
        "date_reported": item.date_reported.strftime("%Y-%m-%d"),
        "status": item.status,
        "rfid_tag": item.rfid_tag,
        "unique_code": item.unique_code,
        "image_file": item.image_file if item.image_file else "default.jpg"
    })

@app.route("/api/items", methods=["POST"])
def list_entry_item_api():
    try:
        # Get form data
        category_id = request.form.get("category_id")
        location_id = request.form.get("location_id")
        description = request.form.get("description")
        date_reported = request.form.get("date_reported")
        status = request.form.get("status")
        rfid_tag = request.form.get("rfid_tag")
        image = request.files.get("image")

        print(f"Received Data: {request.form}")

        # Validate required fields
        if not category_id or not location_id:
            return jsonify({"error": "Category and location are required!"}), 400

        # Convert IDs to integers
        category_id = int(category_id)
        location_id = int(location_id)

        # Validate category and location IDs
        if not Category.query.get(category_id):
            return jsonify({"error": "Invalid category ID"}), 400

        if not Location.query.get(location_id):
            return jsonify({"error": "Invalid location ID"}), 400

        # Parse date
        try:
            date_reported = datetime.strptime(date_reported, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

        # Handle image upload
        image_file = None
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            image_file = filename

        # Create new item
        new_item = Item(
            category_id=category_id,
            description=description,
            location_id=location_id,
            date_reported=date_reported,
            image_file=image_file,
            status=status,
            rfid_tag=rfid_tag
        )

        db.session.add(new_item)
        db.session.commit()

        return jsonify({"message": "Item added successfully!"}), 201

    except ValueError:
        return jsonify({"error": "Invalid ID format. Ensure category_id and location_id are integers."}), 400
    except Exception as e:
        db.session.rollback()
        print("Error:", str(e)) 
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/locations', methods=["GET"])
def get_active_locations():
    """Fetch all locations"""
    locations = Location.query.all()
    return jsonify([{"id": loc.id, "name": loc.name} for loc in locations])


@app.route('/api/categories', methods=["GET"])
def get_active_categories():
    """Fetch all active categories"""
    categories = Category.query.all()  # Get all categories instead of filtering by status
    print("Fetched categories:", categories)  # Debugging: Print fetched categories
    return jsonify([{"id": cat.id, "name": cat.name} for cat in categories])


#################### LIST TAG ITEMS ####################################################

@app.route('/api/tagged-items', methods=['GET'])
def get_tagged_items():
    # Get all items related to the tagging system
    # Include both student submissions and officially tagged items
    items = Item.query.filter(
        # Include items with Registered status (student submissions)
        (Item.status == "Registered") |
        # Include items with Approved status
        (Item.status == "Approved") |
        # Include items with Completed status
        (Item.status == "Completed") |
        # Include items with RFID tags (even if they have other statuses)
        ((Item.rfid_tag.isnot(None)) & (Item.rfid_tag != "None") & (Item.rfid_tag != ""))
    ).all()

    items_list = [
        {
            "id": item.id,
            "category": item.category.name,
            "description": item.description,
            "location": item.location.name,
            "date_reported": item.date_reported.strftime("%Y-%m-%d"),
            "status": item.status,
            "image_file": item.image_file,
            "rfid_tag": item.rfid_tag if item.rfid_tag else "",
            "unique_code": item.unique_code if item.unique_code else "",
            "owner_name": item.owner.name if item.owner else "N/A",
            "owner_email": item.owner.email if item.owner else "N/A",
            "owner_student_id": item.owner.student_id if item.owner else "N/A",
            "owner_contact": item.owner.contact_number if item.owner else "N/A",
            "category_id": item.category_id,
            "location_id": item.location_id,
            "owner_id": item.owner_id
        }
        for item in items
    ]
    return jsonify(items_list)



@app.route('/listtagitems')
def listtagitems():
    return render_template('/items/listTagItem.html')


@app.route('/register-item', methods=['GET', 'POST'])
def register_item():
    if request.method == 'POST':
        # Get form data
        owner_name = request.form.get('owner_name')
        student_id = request.form.get('student_id')
        email = request.form.get('email')
        contact = request.form.get('contact')
        category_id = request.form.get('category_id')
        location_id = request.form.get('location_id')
        description = request.form.get('description')
        
        # Create or find user
        user = User.query.filter_by(student_id=student_id).first()
        if not user:
            user = User(
                name=owner_name,
                email=email,
                student_id=student_id,
                contact_number=contact
            )
            db.session.add(user)
            db.session.flush()  # Get the user ID before committing
        
        # Generate unique code
        unique_code = generate_unique_code()
        
        # Create new item with "Registered" status
        new_item = Item(
            category_id=category_id,
            description=description,
            location_id=location_id,
            date_reported=datetime.now(),
            status="Registered",
            rfid_tag="QR-Tagged",
            owner_id=user.id,
            registration_date=datetime.now(),
            unique_code=unique_code
        )
        
        # Handle image upload if provided
        image = request.files.get('image')
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            new_item.image_file = filename
        
        db.session.add(new_item)
        db.session.commit()
        
        # Generate QR code for the item
        base_url = request.host_url.rstrip('/')
        qr_code, qr_url = generate_qr_code(unique_code, base_url)
        
        return render_template(
            'items/registration_complete.html', 
            item=new_item,
            owner=user,
            qr_code=qr_code,
            qr_url=qr_url
        )
    
    # GET request - show registration form
    categories = Category.query.all()
    locations = Location.query.all()
    return render_template('items/registerItem.html', categories=categories, locations=locations)


@app.route('/scan/<unique_code>')
def scan_item(unique_code):
    """Handle QR code scans"""
    item = Item.query.filter_by(unique_code=unique_code).first()
    
    if not item:
        return render_template('items/item_not_found.html')
    
    # Get owner information
    owner = User.query.get(item.owner_id) if item.owner_id else None
    
    return render_template('items/scanned_item.html', item=item, owner=owner)


@app.route('/api/item/<int:item_id>')
def get_item_details(item_id):
    item = Item.query.get_or_404(item_id)
    
    # Find the latest claim (if any)
    claim = Claim.query.filter_by(item_id=item.id).first()
    owner = User.query.get(claim.user_id) if claim else None

    return jsonify({
        "id": item.id,
        "category": item.category.name,
        "description": item.description,
        "location": item.location.name,
        "date_reported": item.date_reported.strftime('%Y-%m-%d'),
        "status": item.status,
        "image_file": item.image_file,
        "owner_name": owner.name if owner else "Unclaimed",
        "owner_email": owner.email if owner else "N/A"
    })



# Create a blueprint for tagged items functionality
tagged_items_bp = Blueprint('tagged_items', __name__)

# Render the tagged items page
@tagged_items_bp.route('/tagged-items')
def tagged_items_page():
    return render_template('tagged_items.html')

# API routes for frontend AJAX calls
@tagged_items_bp.route('/api/tagged-items', methods=['GET'])
def get_tagged_items():
    # Query items with RFID tags
    items_query = db.session.query(
        Item.id,
        Item.description,
        Item.date_reported,
        Item.image_file,
        Item.rfid_tag,
        Item.status,
        Item.category_id,
        Item.location_id,
        Item.owner_id,
        Category.name.label('category'),
        Location.name.label('location'),
        User.name.label('owner_name'),
        User.email.label('owner_email'),
        User.student_id.label('owner_student_id'),
        User.contact_number.label('owner_contact')
    ).join(
        Category, Item.category_id == Category.id
    ).join(
        Location, Item.location_id == Location.id
    ).outerjoin(
        User, Item.owner_id == User.id
    ).filter(
        Item.rfid_tag.isnot(None),
        Item.rfid_tag != ''
    ).all()
    
    # Convert to list of dictionaries
    items = []
    for item in items_query:
        item_dict = {
            'id': item.id,
            'description': item.description,
            'date_reported': item.date_reported.strftime('%Y-%m-%d'),
            'image_file': item.image_file,
            'rfid_tag': item.rfid_tag,
            'status': item.status,
            'category_id': item.category_id,
            'location_id': item.location_id,
            'owner_id': item.owner_id,
            'category': item.category,
            'location': item.location,
            'owner_name': item.owner_name,
            'owner_email': item.owner_email,
            'owner_student_id': item.owner_student_id,
            'owner_contact': item.owner_contact
        }
        items.append(item_dict)
    
    return jsonify(items)







#################### TOTAL LOST ITEM ####################################################


@app.route('/items/totalLostItem')
def total_lost_items():    
    status_filter = request.args.get("status", "")
    category_filter = request.args.get("category", "")
    tag_filter = request.args.get("tag", "")
    
    query = (
        db.session.query(
            Item.id, Item.description, Item.status, Item.date_reported.label("date_reported"),
            Claim.claim_date.label("date_claimed"), Category.name.label("category"),
            Item.rfid_tag        )
        .outerjoin(Claim, Claim.item_id == Item.id)  
        .join(Category, Item.category_id == Category.id) 
    )
    
    # Only show items with status "Lost" or "Unclaimed"
    if status_filter:
        query = query.filter(Item.status == status_filter)
    else:
        query = query.filter(Item.status.in_(["Lost", "Unclaimed"]))

    if category_filter:
        query = query.filter(Category.name == category_filter)
        
    if tag_filter == "Tagged":
        query = query.filter((Item.rfid_tag.isnot(None)) | (Item.unique_code.isnot(None)))
    elif tag_filter == "Not Tagged":
        query = query.filter((Item.rfid_tag.is_(None)) & (Item.unique_code.is_(None)))

    lost_items = query.all()

    categories = Category.query.with_entities(Category.name).distinct().all()
    categories = [cat.name for cat in categories]

    return render_template(
        "items/totalLostItem.html",
        lost_items=lost_items,
        total_lost_items_count=len(lost_items),
        categories=categories
    )

####### TOTAL LOST ITEMMM ####################################################

@app.route('/items/totalFoundItem')
def total_found_items():
  
    category_filter = request.args.get("category", "")
    tag_filter = request.args.get("tag", "")

    query = (
        db.session.query(
            Item.id, Item.description, Item.status, Item.date_reported.label("date_found"),
            Claim.claim_date.label("date_claimed"), Category.name.label("category"),
            Item.rfid_tag
        )
        .outerjoin(Claim, Claim.item_id == Item.id)
        .join(Category, Item.category_id == Category.id) 
        .filter(Item.status == "Claimed")  
    )

    if category_filter:
        query = query.filter(Category.name == category_filter)

    if tag_filter == "Tagged":
        query = query.filter(Item.rfid_tag.isnot(None))
    elif tag_filter == "Not Tagged":
        query = query.filter(Item.rfid_tag.is_(None)) 

    found_items = query.all()

    categories = Category.query.with_entities(Category.name).distinct().all()
    categories = [cat.name for cat in categories]

    return render_template(
        "items/totalFoundItem.html",
        found_items=found_items,
        total_found_items_count=len(found_items),
        categories=categories
    )

############################################################ USER ################################################

@app.route('/api/stats')
def get_stats():
    """API endpoint to provide real-time statistics for the landing page"""
    try:
        # Total items found (claimed)
        total_items_found = Item.query.filter_by(status='Claimed').count()
        
        # Total items in the system (all statuses)
        total_items = Item.query.count()
        
        # Calculate return rate (claimed items / total items)
        return_rate = int((total_items_found / total_items * 100) if total_items > 0 else 0)
        
        # Count total users
        active_users = User.query.count()
        
        # Calculate average return time
        # Get all claims that have claim_date
        claims = Claim.query.filter(Claim.claim_date.isnot(None)).all()
        
        avg_return_hours = 24  # Default value
        if claims:
            total_hours = 0
            count = 0
            
            for claim in claims:
                # Get the corresponding item
                item = Item.query.get(claim.item_id)
                if item and item.date_reported:
                    # Calculate the difference in hours
                    diff = claim.claim_date - item.date_reported
                    total_hours += diff.total_seconds() / 3600  # Convert to hours
                    count += 1
            
            if count > 0:
                avg_return_hours = int(total_hours / count)
        
        return jsonify({
            'return_rate': return_rate,
            'items_returned': total_items_found,
            'active_users': active_users,
            'avg_return_time': avg_return_hours
        })
    except Exception as e:
        print(f"Error calculating stats: {str(e)}")
        return jsonify({
            'return_rate': 95,
            'items_returned': 0,
            'active_users': 0,
            'avg_return_time': 24
        })

@app.route('/users/landingpage')
def landingpage():
    return render_template('users/landingpage.html')

@app.route('/report-lost')
def report_lost():
    """Route for reporting lost items, providing guidance on the lost item reporting process"""
    return render_template('users/report_lost.html')

@app.route('/report-found')
def report_found():
    """Route for reporting found items, providing guidance on where to submit found items"""
    return render_template('users/report_found.html')

@app.route('/users/lostandfounditem')
def lostandfound():
    # Get filter parameters
    category_id = request.args.get('category', type=int)
    location_id = request.args.get('location', type=int)
    status = request.args.get('status')
    date_filter = request.args.get('date')
    search = request.args.get('search')
    has_rfid = request.args.get('has_rfid')
    
    # Base query
    query = Item.query
    
    # Only show lost/unclaimed items and claimed items, not registered items
    # that aren't lost or claimed
    query = query.filter(
        (Item.status == 'Unclaimed') | 
        (Item.status == 'Lost') |
        (Item.status == 'Claimed')
    )
    
    # Apply filters
    if category_id:
        query = query.filter(Item.category_id == category_id)
    
    if location_id:
        query = query.filter(Item.location_id == location_id)
    
    if status:
        query = query.filter(Item.status == status)
    
    if search:
        query = query.filter(Item.description.ilike(f'%{search}%'))
    
    # Filter by RFID tag presence
    if has_rfid == 'yes':
        query = query.filter(Item.rfid_tag.isnot(None))
        query = query.filter(Item.rfid_tag != '')
    
    # Date filter
    today = datetime.now().date()
    if date_filter == 'today':
        query = query.filter(Item.date_reported == today)
    elif date_filter == 'week':
        # Calculate the date 7 days ago
        week_ago = today - timedelta(days=7)
        query = query.filter(Item.date_reported >= week_ago)
    elif date_filter == 'month':
        # Calculate the date 30 days ago
        month_ago = today - timedelta(days=30)
        query = query.filter(Item.date_reported >= month_ago)
    
    # Execute query to get the filtered items
    items = query.order_by(Item.date_reported.desc()).all()
    
    # Print debug information
    print(f"Query returned {len(items)} items")
    
    # Get all categories and locations for filters
    categories = Category.query.filter_by(status="Active").all()
    locations = Location.query.all()
    
    return render_template(
        'users/lostandfounditem.html', 
        items=items,
        categories=categories,
        locations=locations
    )

############################################################ USER AUTHENTICATION ################################################

# Hash a password
def hash_password(password):
    # A simple hashing function, in production use a better one like bcrypt
    return hashlib.sha256(password.encode()).hexdigest()

# User registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        student_id = request.form.get('student_id')
        contact_number = request.form.get('contact_number')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate form data
        if not name or not email or not student_id or not password:
            flash("All fields are required", "error")
            return render_template('users/register.html', error="All fields are required.")
        
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template('users/register.html', error="Passwords do not match.")
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.email == email) | (User.student_id == student_id)
        ).first()
        
        if existing_user:
            flash("Email or Student ID already registered", "error")
            return render_template('users/register.html', error="Email or Student ID already registered.")
        
        # Create new user
        new_user = User(
            name=name,
            email=email,
            student_id=student_id,
            contact_number=contact_number,
            password=hash_password(password),
            created_at=datetime.now(),
            account_status='Active'
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
    
    return render_template('users/register.html')

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == 'on'
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if user and user.password == hash_password(password):
            if user.account_status != 'Active':
                flash("Your account is inactive. Please contact support.", "error")
                return render_template('users/login.html', error="Your account is inactive. Please contact support.")
            
            # Set session variables
            session['user_logged_in'] = True
            session['user_id'] = user.id
            session['user_name'] = user.name
            
            # Update last login time
            user.last_login = datetime.now()
            db.session.commit()
            
            # Set session expiration if remember_me is checked
            if remember_me:
                session.permanent = True
                app.permanent_session_lifetime = timedelta(days=30)
            
            flash("Login successful!", "success")
            return redirect(url_for('user_dashboard'))
        else:
            flash("Invalid email or password.", "error")
            return render_template('users/login.html', error="Invalid email or password.")
    
    return render_template('users/login.html')

# User logout
@app.route('/logout')
def logout():
    session.pop('user_logged_in', None)
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash("Logged out successfully!", "info")
    return redirect(url_for('landingpage'))

# User authentication decorator
def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_logged_in'):
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        
        # Add user info to g for access in templates
        if session.get('user_id'):
            user = User.query.get(session['user_id'])
            if not user:
                # If user no longer exists in DB, log them out
                session.pop('user_logged_in', None)
                session.pop('user_id', None)
                session.pop('user_name', None)
                flash("User account not found. Please log in again.", "warning")
                return redirect(url_for('login'))
            
            g.user = user
        
        return f(*args, **kwargs)
    return decorated_function

# User dashboard
@app.route('/user/dashboard')
@user_required
def user_dashboard():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    # Get filter parameter
    status_filter = request.args.get('filter', '')
    
    # Base query for items owned by this user
    query = Item.query.filter_by(owner_id=user_id)
    
    # Apply status filter if specified
    if status_filter == 'pending':
        query = query.filter_by(status='Registered')
    elif status_filter == 'approved':
        query = query.filter_by(status='Approved')
    elif status_filter == 'completed':
        query = query.filter_by(status='Completed')
    
    # Get items
    items = query.order_by(Item.registration_date.desc()).all()
    
    # Count items by status
    pending_count = Item.query.filter_by(owner_id=user_id, status='Registered').count()
    approved_count = Item.query.filter_by(owner_id=user_id, status='Approved').count()
    completed_count = Item.query.filter_by(owner_id=user_id, status='Completed').count()
    
    # Check if user has approved items
    has_approved_items = approved_count > 0
    
    return render_template(
        'users/user_dashboard.html',
        user=user,
        items=items,
        pending_count=pending_count,
        approved_count=approved_count,
        completed_count=completed_count,
        current_filter=status_filter,
        has_approved_items=has_approved_items
    )

@app.route('/user/item/<int:item_id>')
@user_required
def view_registered_item(item_id):
    # Get the item and verify ownership
    item = Item.query.get_or_404(item_id)
    
    if item.owner_id != session.get('user_id'):
        flash("You don't have permission to view this item.", "error")
        return redirect(url_for('user_dashboard'))
    
    # Generate QR code if item has a unique code
    qr_code = None
    if item.unique_code:
        base_url = request.host_url.rstrip('/')
        qr_code, _ = generate_qr_code(item.unique_code, base_url)
    
    return render_template(
        'users/view_registered_item.html',
        item=item,
        qr_code=qr_code
    )

# Edit registered item
@app.route('/user/item/<int:item_id>/edit', methods=['GET', 'POST'])
@user_required
def edit_registered_item(item_id):
    # Get the item and verify ownership
    item = Item.query.get_or_404(item_id)
    
    if item.owner_id != session.get('user_id'):
        flash("You don't have permission to edit this item.", "error")
        return redirect(url_for('user_dashboard'))
    
    # Only allow editing of items in 'Registered' status
    if item.status != 'Registered':
        flash("This item can no longer be edited as it has already been processed.", "error")
        return redirect(url_for('view_registered_item', item_id=item.id))
    
    # Extract item name and description for the form
    item_parts = item.description.split(':', 1)
    if len(item_parts) > 1:
        item_name = item_parts[0].strip()
        description = item_parts[1].strip()
    else:
        item_name = "Unnamed Item"
        description = item.description
    
    if request.method == 'POST':
        # Get form data
        new_category_id = request.form.get('category_id')
        new_description = request.form.get('description')
        new_item_name = request.form.get('item_name')
        
        # Validate form data
        if not new_category_id or not new_description or not new_item_name:
            flash("All fields are required", "error")
            categories = Category.query.all()
            return render_template(
                'users/edit_registered_item.html', 
                item=item,
                item_name=new_item_name,
                description=new_description,
                categories=categories,
                error="All fields are required"
            )
        
        # Update item
        item.category_id = new_category_id
        item.description = f"{new_item_name}: {new_description}"
        
        # Handle image upload if provided
        image = request.files.get('image')
        if image and image.filename and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            item.image_file = filename
        
        db.session.commit()
        
        flash("Item updated successfully!", "success")
        return redirect(url_for('view_registered_item', item_id=item.id))
    
    # GET request - show edit form
    categories = Category.query.all()
    return render_template(
        'users/edit_registered_item.html',
        item=item,
        item_name=item_name,
        description=description,
        categories=categories
    )

# User register item (requires login)
@app.route('/user/register-item', methods=['GET', 'POST'])
@user_required
def user_register_item():
    if request.method == 'POST':
        # Get form data
        item_name = request.form.get('item_name')
        description = request.form.get('description')
        category_id = request.form.get('category_id')
        
        # Get current user information from session
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        # Validate form data
        if not item_name or not description or not category_id:
            flash("All fields are required", "error")
            categories = Category.query.all()
            locations = Location.query.all()  # Get locations for the form
            return render_template('users/register_item.html', categories=categories, locations=locations)
        
        # Generate unique code
        unique_code = generate_unique_code()
        
        # Create new item with "Registered" status (pending approval)
        new_item = Item(
            category_id=category_id,
            # Combine item name and description
            description=f"{item_name}: {description}",
            # Use a default location or let admin assign it later
            location_id=1,  # Default location ID, adjust as needed
            date_reported=datetime.now(),
            status="Registered",  # Start with registered status (pending approval)
            rfid_tag=None,  # Will be assigned when approved
            owner_id=user.id,
            registration_date=datetime.now(),
            unique_code=unique_code
        )
        
        # Handle image upload if provided
        image = request.files.get('image')
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            new_item.image_file = filename
        
        db.session.add(new_item)
        db.session.commit()
        
        flash("Item registered successfully! It is now pending approval.", "success")
        return redirect(url_for('user_dashboard'))
    
    # GET request - show registration form
    categories = Category.query.all()
    locations = Location.query.all()
    return render_template('users/register_item.html', categories=categories, locations=locations)

@app.route('/api/tagged-items/<int:item_id>', methods=['PUT'])
def update_tagged_item(item_id):
    try:
        item = Item.query.get(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404

        # Handle form data
        form_data = request.form

        # Extract data from form
        if "category_id" in form_data:
            item.category_id = int(form_data["category_id"])
        
        if "location_id" in form_data:
            item.location_id = int(form_data["location_id"])
            
        if "description" in form_data:
            item.description = form_data["description"].strip()
            
        if "date_reported" in form_data:
            try:
                item.date_reported = datetime.strptime(form_data["date_reported"], "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        if "status" in form_data:
            new_status = form_data["status"].strip()
            old_status = item.status
            
            # Handle status transitions
            if old_status == "Registered" and new_status == "Approved":
                # When approving a student item registration
                item.status = "Approved"
                # Send notification to student could be added here
                
            elif old_status == "Approved" and new_status == "Completed":
                # When marking an approved item as completed (tag issued)
                item.status = "Completed"
                # Send notification to student could be added here
                
            elif old_status == "Registered" and new_status == "Rejected":
                # When rejecting a student item registration
                item.status = "Rejected"
                # Send notification to student could be added here
                
            else:
                # Any other status change
                item.status = new_status
        
        if "rfid_tag" in form_data:
            item.rfid_tag = form_data["rfid_tag"].strip()
        
        if "owner_id" in form_data and form_data["owner_id"]:
            item.owner_id = int(form_data["owner_id"])
        
        # Handle file upload if provided
        if "image" in request.files:
            image = request.files["image"]
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                item.image_file = filename
        
        db.session.commit()
        return jsonify({"message": "Item updated successfully", "status": item.status}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating tagged item: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/item-status/<int:item_id>', methods=['PUT'])
@admin_required
def update_item_status(item_id):
    """API endpoint for admins to approve or complete student item registrations"""
    try:
        # Get the item
        item = Item.query.get_or_404(item_id)
        
        # Get the new status from the request body
        data = request.json
        new_status = data.get('status')
        
        # Validate the status transition
        valid_statuses = ['Registered', 'Approved', 'Completed']
        if new_status not in valid_statuses:
            return jsonify({"error": "Invalid status. Must be one of: Registered, Approved, Completed"}), 400
        
        # Enforce status workflow (Registered -> Approved -> Completed)
        if item.status == 'Registered' and new_status not in ['Approved', 'Registered']:
            return jsonify({"error": "Items must be approved before being marked as completed"}), 400
        elif item.status == 'Approved' and new_status == 'Registered':
            return jsonify({"error": "Cannot revert approved items to registered status"}), 400
        
        # Update the item status
        item.status = new_status
        
        # Add any additional processing
        if new_status == 'Approved':
            # If we're approving an item, we might add processing here (like setting approval date)
            # For example, you could add an approval_date field to the Item model
            pass
        elif new_status == 'Completed':
            # If marking as completed, make sure it has a QR code or tag
            if not item.unique_code and not item.rfid_tag:
                # Generate a unique code if one doesn't exist
                item.unique_code = generate_unique_code()
            
            # You might also record the completion date
            pass
        
        # Save the changes
        db.session.commit()
        
        return jsonify({
            "message": f"Item status updated to {new_status}",
            "item_id": item.id,
            "status": item.status
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating item status: {str(e)}")
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)