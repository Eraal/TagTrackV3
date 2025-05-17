from flask import Blueprint, request, jsonify
from models import db, Location

locations_bp = Blueprint('locations', __name__)

@locations_bp.route('/get_locations', methods=["GET"])
def get_locations():
    locations = Location.query.all()
    return jsonify([
        {
            'id': loc.id,
            'name': loc.name
        } for loc in locations
    ])

@locations_bp.route('/add_location', methods=['POST'])
def add_location():
    data = request.json
    name = data.get('name')
    
    if not name:
        return jsonify({"error": "Location name is required"}), 400
    
    # Check if location already exists
    existing_location = Location.query.filter_by(name=name).first()
    if existing_location:
        return jsonify({"error": "Location already exists"}), 400
    
    # Create new location
    new_location = Location(name=name)
    db.session.add(new_location)
    db.session.commit()
    
    return jsonify({"message": "Location added successfully"}), 201

@locations_bp.route('/update_location/<int:location_id>', methods=['PUT'])
def update_location(location_id):
    data = request.json
    location = Location.query.get_or_404(location_id)
    
    location.name = data.get('name')
    db.session.commit()
    
    return jsonify({"message": "Location updated successfully"}), 200

@locations_bp.route('/delete_location/<int:id>', methods=['DELETE'])
def delete_location(id):
    from models import Item
    
    location = Location.query.get_or_404(id)
    
    # Check if location is in use by any items
    has_items = db.session.query(Item.id).filter_by(location_id=location.id).first() is not None
    if has_items:
        return jsonify({"error": "Cannot delete location as it is in use by items"}), 400
    
    db.session.delete(location)
    db.session.commit()
    
    return jsonify({"message": "Location deleted successfully"}), 200
