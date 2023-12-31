
from io import BytesIO
from flask import Flask, make_response, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:rudramanu%4000@localhost/travelplanner'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Destination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.String(255))
    location = db.Column(db.String(255))

    itineraries = db.relationship('Itinerary', backref='destination', lazy=True)

class Hotel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    location = db.Column(db.String(255))
    price_per_night = db.Column(db.Float)
    amenities = db.Column(db.String(255))
    rooms = db.relationship('Room', backref='hotel', lazy=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    amount = db.Column(db.Float)
    category = db.Column(db.String(255))
    date = db.Column(db.Date)

class Itinerary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    activities = db.relationship('Activity', backref='itinerary', lazy=True)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    size = db.Column(db.String(255))
    sleeps = db.Column(db.Integer)
    bed_type = db.Column(db.String(255))
    price = db.Column(db.Float)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    date = db.Column(db.Date)

    itinerary_id = db.Column(db.Integer, db.ForeignKey('itinerary.id'), nullable=False)

app.app_context().push()
db.create_all()

# Create a route for adding a destination
@app.route('/destination', methods=['POST'])
def add_destination():
    data = request.get_json()

    new_destination = Destination(name=data['name'], description=data.get('description'), location=data.get('location'))

    db.session.add(new_destination)
    db.session.commit()

    return jsonify({"message": "Destination added successfully!"}), 201

@app.route('/destinations', methods=['GET'])
def get_destinations():
    destinations = Destination.query.all()

    result = []
    for destination in destinations:
        result.append({
            'id': destination.id,
            'name': destination.name,
            'description': destination.description,
            'location': destination.location
        })

    return jsonify({"destinations": result}), 200

@app.route('/destination/<int:destination_id>', methods=['GET'])
def get_destination(destination_id):
    destination = Destination.query.get_or_404(destination_id)

    result = {
        'id': destination.id,
        'name': destination.name,
        'description': destination.description,
        'location': destination.location
    }

    return jsonify({"destination": result}), 200

@app.route('/destination/<int:destination_id>/update', methods=['PUT'])
def update_destination(destination_id):
    destination = Destination.query.get_or_404(destination_id)
    data = request.get_json()

    destination.name = data.get('name', destination.name)
    destination.description = data.get('description', destination.description)
    destination.location = data.get('location', destination.location)

    db.session.commit()

    return jsonify({"message": "Destination updated successfully!"}), 200

@app.route('/destination/<int:destination_id>/delete', methods=['DELETE'])
def delete_destination(destination_id):
    destination = Destination.query.get_or_404(destination_id)

    db.session.delete(destination)
    db.session.commit()

    return jsonify({"message": "Destination deleted successfully!"}), 200

@app.route('/itinerary/<int:itinerary_id>/activity', methods=['POST'])
def add_activity_to_itinerary(itinerary_id):
    data = request.get_json()

    itinerary = Itinerary.query.get_or_404(itinerary_id)

    new_activity = Activity(name=data['name'], description=data.get('description'), date=data.get('date'))
    new_activity.itinerary = itinerary

    db.session.add(new_activity)
    db.session.commit()

    return jsonify({"message": "Activity added to the itinerary successfully!"}), 201

@app.route('/itinerary/<int:itinerary_id>/activities', methods=['GET'])
def get_activities_in_itinerary(itinerary_id):
    itinerary = Itinerary.query.get_or_404(itinerary_id)

    activities = Activity.query.filter_by(itinerary=itinerary).all()

    result = []
    for activity in activities:
        result.append({
            'id': activity.id,
            'name': activity.name,
            'description': activity.description,
            'date': activity.date
        })

    return jsonify({"activities": result}), 200

@app.route('/itinerary/<int:itinerary_id>/activity/<int:activity_id>', methods=['PUT'])
def update_activity_in_itinerary(itinerary_id, activity_id):
    itinerary = Itinerary.query.get_or_404(itinerary_id)
    activity = Activity.query.get_or_404(activity_id)

    data = request.get_json()

    activity.name = data.get('name', activity.name)
    activity.description = data.get('description', activity.description)
    activity.date = data.get('date', activity.date)

    db.session.commit()

    return jsonify({"message": "Activity in the itinerary updated successfully!"}), 200

@app.route('/itinerary/<int:itinerary_id>/activity/<int:activity_id>', methods=['DELETE'])
def delete_activity_from_itinerary(itinerary_id, activity_id):
    itinerary = Itinerary.query.get_or_404(itinerary_id)
    activity = Activity.query.get_or_404(activity_id)

    db.session.delete(activity)
    db.session.commit()

    return jsonify({"message": "Activity deleted from the itinerary successfully!"}), 200

@app.route('/expense', methods=['POST'])
def add_expense():
    data = request.get_json()

    new_expense = Expense(name=data['name'], amount=data['amount'], category=data['category'], date=data['date'])

    db.session.add(new_expense)
    db.session.commit()

    return jsonify({"message": "Expense added successfully!"}), 201

@app.route('/expenses', methods=['GET'])
def get_all_expenses():
    expenses = Expense.query.all()

    result = []
    for expense in expenses:
        result.append({
            'id': expense.id,
            'name': expense.name,
            'amount': expense.amount,
            'category': expense.category,
            'date': expense.date
        })

    return jsonify({"expenses": result}), 200

@app.route('/expense/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    data = request.get_json()

    expense.name = data.get('name', expense.name)
    expense.amount = data.get('amount', expense.amount)
    expense.category = data.get('category', expense.category)
    expense.date = data.get('date', expense.date)

    db.session.commit()

    return jsonify({"message": "Expense updated successfully!"}), 200

@app.route('/expense/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)

    db.session.delete(expense)
    db.session.commit()

    return jsonify({"message": "Expense deleted successfully!"}), 200

@app.route('/hotel/<int:hotel_id>/room', methods=['POST'])
def add_room_to_hotel(hotel_id):
    data = request.get_json()

    hotel = Hotel.query.get_or_404(hotel_id)

    new_room = Room(name=data['name'], size=data.get('size'), sleeps=data.get('sleeps'),
                    bed_type=data.get('bed_type'), price=data.get('price'))
    new_room.hotel = hotel

    db.session.add(new_room)
    db.session.commit()

    return jsonify({"message": "Room added to the hotel successfully!"}), 201

@app.route('/hotel/<int:hotel_id>/rooms', methods=['GET'])
def get_rooms_in_hotel(hotel_id):
    hotel = Hotel.query.get_or_404(hotel_id)

    rooms = Room.query.filter_by(hotel=hotel).all()

    result = []
    for room in rooms:
        result.append({
            'id': room.id,
            'name': room.name,
            'size': room.size,
            'sleeps': room.sleeps,
            'bed_type': room.bed_type,
            'price': room.price
        })

    return jsonify({"rooms": result}), 200

@app.route('/hotel/<int:hotel_id>/room/<int:room_id>', methods=['PUT'])
def update_room_in_hotel(hotel_id, room_id):
    hotel = Hotel.query.get_or_404(hotel_id)
    room = Room.query.get_or_404(room_id)

    data = request.get_json()

    room.name = data.get('name', room.name)
    room.size = data.get('size', room.size)
    room.sleeps = data.get('sleeps', room.sleeps)
    room.bed_type = data.get('bed_type', room.bed_type)
    room.price = data.get('price', room.price)

    db.session.commit()

    return jsonify({"message": "Room in the hotel updated successfully!"}), 200

@app.route('/hotel/<int:hotel_id>/room/<int:room_id>', methods=['DELETE'])
def delete_room_from_hotel(hotel_id, room_id):
    hotel = Hotel.query.get_or_404(hotel_id)
    room = Room.query.get_or_404(room_id)

    db.session.delete(room)
    db.session.commit()

    return jsonify({"message": "Room deleted from the hotel successfully!"}), 200

@app.route('/destination/<int:destination_id>/hotel', methods=['POST'])
def add_hotel_to_destination(destination_id):
    data = request.get_json()

    destination = Destination.query.get_or_404(destination_id)

    new_hotel = Hotel(name=data['name'], location=data.get('location'))
    new_hotel.destination = destination

    db.session.add(new_hotel)
    db.session.commit()

    return jsonify({"message": "Hotel added to the destination successfully!"}), 201

@app.route('/destination/<int:destination_id>/hotels', methods=['GET'])
def get_hotels_in_destination(destination_id):
    destination = Destination.query.get_or_404(destination_id)

    hotels = Hotel.query.filter_by(destination=destination).all()

    result = []
    for hotel in hotels:
        result.append({
            'id': hotel.id,
            'name': hotel.name,
            'location': hotel.location
        })

    return jsonify({"hotels": result}), 200

@app.route('/destination/<int:destination_id>/hotel/<int:hotel_id>', methods=['PUT'])
def update_hotel_in_destination(destination_id, hotel_id):
    destination = Destination.query.get_or_404(destination_id)
    hotel = Hotel.query.get_or_404(hotel_id)

    data = request.get_json()

    hotel.name = data.get('name', hotel.name)
    hotel.location = data.get('location', hotel.location)

    db.session.commit()

    return jsonify({"message": "Hotel in the destination updated successfully!"}), 200

@app.route('/destination/<int:destination_id>/hotel/<int:hotel_id>', methods=['DELETE'])
def delete_hotel_from_destination(destination_id, hotel_id):
    destination = Destination.query.get_or_404(destination_id)
    hotel = Hotel.query.get_or_404(hotel_id)

    db.session.delete(hotel)
    db.session.commit()

    return jsonify({"message": "Hotel deleted from the destination successfully!"}), 200

@app.route('/destination/<int:destination_id>/itinerary', methods=['POST'])
def add_itinerary_to_destination(destination_id):
    data = request.get_json()

    destination = Destination.query.get_or_404(destination_id)

    new_itinerary = Itinerary()
    new_itinerary.destination = destination

    db.session.add(new_itinerary)
    db.session.commit()

    return jsonify({"message": "Itinerary added to the destination successfully!"}), 201

@app.route('/destination/<int:destination_id>/itineraries', methods=['GET'])
def get_itineraries_in_destination(destination_id):
    destination = Destination.query.get_or_404(destination_id)

    itineraries = Itinerary.query.filter_by(destination=destination).all()

    result = []
    for itinerary in itineraries:
        result.append({
            'id': itinerary.id,
            'destination_id': itinerary.destination_id
        })

    return jsonify({"itineraries": result}), 200

@app.route('/destination/<int:destination_id>/itinerary/<int:itinerary_id>', methods=['PUT'])
def update_itinerary_in_destination(destination_id, itinerary_id):
    destination = Destination.query.get_or_404(destination_id)
    itinerary = Itinerary.query.get_or_404(itinerary_id)
    db.session.commit()
    return jsonify({"message": "Itinerary in the destination updated successfully!"}), 200

@app.route('/destination/<int:destination_id>/itinerary/<int:itinerary_id>', methods=['DELETE'])
def delete_itinerary_from_destination(destination_id, itinerary_id):
    destination = Destination.query.get_or_404(destination_id)
    itinerary = Itinerary.query.get_or_404(itinerary_id)

    db.session.delete(itinerary)
    db.session.commit()

    return jsonify({"message": "Itinerary deleted from the destination successfully!"}), 200

if __name__ == '__main__':
    app.run(debug=True)
