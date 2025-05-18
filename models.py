from extensions import db 

# Admin Table
class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    full_name = db.Column(db.String(100), nullable=True)
    position = db.Column(db.String(100), nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=True)



# Categories Table
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255)) 
    status = db.Column(db.String(20), default="Active")  
    items = db.relationship('Item', back_populates="category", lazy=True)



# Locations Table
class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    items = db.relationship('Item', back_populates="location", lazy=True)



# Items Table
class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id', ondelete='CASCADE'), nullable=False)
    date_reported = db.Column(db.Date, nullable=False)
    image_file = db.Column(db.String(255))
    rfid_tag = db.Column(db.String(255))
    status = db.Column(db.String(50), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    unique_code = db.Column(db.String(20), unique=True, nullable=True)
    registration_date = db.Column(db.DateTime, nullable=True)


    category = db.relationship('Category', back_populates="items")
    location = db.relationship('Location', back_populates="items")
    owner = db.relationship('User', back_populates="items")

    @property
    def item_name(self):
        """Extract the item name from the description (format: 'Item Name: Description')"""
        item_parts = self.description.split(':', 1)
        if len(item_parts) > 1:
            return item_parts[0].strip()
        return "Unnamed Item"

 


# Users Table
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    contact_number = db.Column(db.String(15), nullable=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    account_status = db.Column(db.String(20), default="Active")

    items = db.relationship('Item', back_populates="owner")
  


# Claims Table
class Claim(db.Model):
    __tablename__ = 'claims'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    claim_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), nullable=False)

    item = db.relationship('Item', backref=db.backref('claim', uselist=False))