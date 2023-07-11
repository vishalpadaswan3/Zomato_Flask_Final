from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
from bson import ObjectId
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

# MongoDB connection
client = MongoClient('mongodb+srv://vishalpadaswan3:vishal@cluster0.907cq.mongodb.net/ZoMaTo?retryWrites=true&w=majority')
db = client['zomatoAIdata']

# Model class for menu item
class MenuItem:
    def __init__(self, id, dish_name, price, availability):
        self.id = id
        self.dish_name = dish_name
        self.price = price
        self.availability = availability

    def to_dict(self):
        return {
            'dish_name': self.dish_name,
            'id': self.id,
            'price': self.price,
            'availability': self.availability
        }

# Route for serving the index.html page
@app.route('/')
def index():
    return render_template('index.html')




# Define a dictionary of predefined responses based on user queries
predefined_responses = {
    'hours_of_operation': 'Our hours of operation are Monday to Friday, 9 AM to 6 PM.',
    'order_status': 'To check the status of your order, please provide your order number.',
    'popular_dish': 'Our most popular dish is the Special Burger. It comes with a juicy patty and special sauce.',
    'greeting': 'Hello! How can I help you today?, Please enter your query in the text box below.',
    'goodbye': 'Thank you for visiting us. Have a great day!',
    'thanks': 'You are welcome!',
    'order_number': 'Your order number is 123456.',
    'order_status': 'Your order is out for delivery.',
    'order_status': 'Your order has been delivered. Thank you for choosing us!',
    "onlyvp": "My Name is Vishal Padaswan"
    # Add more predefined responses for other queries
}

# Route for handling chatbot requests
@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    user_message = data['message']

    # Process user message and generate a response
    response = process_user_message(user_message)

    return jsonify({'response': response})

# Function to process user message and generate a response
def process_user_message(message):
    # Convert the user message to lowercase for easier comparison
    message = message.lower()

    if 'hours' in message:
        return predefined_responses['hours_of_operation']
    elif 'order' in message and 'status' in message:
        return predefined_responses['order_status']
    elif 'popular' in message and 'dish' in message:
        return predefined_responses['popular_dish']
    elif 'hello' in message or 'hi' in message:
        return predefined_responses['greeting']
    elif 'bye' in message or 'goodbye' in message:
        return predefined_responses['goodbye']
    elif 'thank' in message:
        return predefined_responses['thanks']
    elif 'order' in message and 'number' in message:
        return predefined_responses['order_number']
    elif 'order' in message and 'status' in message:
        return predefined_responses['order_status']
    elif 'order' in message and 'delivered' in message:
        return predefined_responses['order_delivered']
    elif 'name' in message:
        return predefined_responses['onlyvp']
    else:
        return 'Sorry, I did not understand your question.'
    

# Route for displaying the feedback form
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        # Get the form data
        customer_name = request.form['customer_name']
        feedback = request.form['feedback']
        rating = int(request.form['rating'])

        # Store the feedback in the database
        db.feedback.insert_one({
            'customer_name': customer_name,
            'feedback': feedback,
            'rating': rating,
        })

        alert_message = 'Feedback submitted successfully!'
        return redirect(url_for('index'))
    else:
        return render_template('feedback_form.html')



# Route for displaying the menu
@app.route('/show_menu')
def show_menu():
    items = db.menu.find()
    menu = [MenuItem(str(item['_id']), item['dish_name'], item['price'], item['availability']) for item in items]
    return render_template('menu.html', menu=menu)

# Route for adding a new dish
@app.route('/add_dish', methods=['GET', 'POST'])
def add_dish():
    if request.method == 'POST':
        # Get the form data
        dish_name = request.form['dish_name']
        price = float(request.form['price'])
        availability = request.form.get('availability') == 'on'

        # Create a new MenuItem object
        new_dish = MenuItem(None, dish_name, price, availability)

        # Insert the new dish into the database
        db.menu.insert_one(new_dish.to_dict())

        return redirect(url_for('show_menu'))

    return render_template('add_dish.html')

# Route for removing a dish
@app.route('/confirm_remove/<dish_id>', methods=['GET', 'POST'])
def confirm_remove(dish_id):
    if request.method == 'POST':
        # Convert the dish_id to ObjectId
        dish_id = ObjectId(dish_id)

        # Remove the dish from the menu based on dish_id
        db.menu.delete_one({'_id': dish_id})

        return redirect(url_for('show_menu'))
    else:
        return render_template('confirm_remove.html', dish_id=dish_id)

# Route for updating the availability of a dish
@app.route('/update_availability/<dish_id>', methods=['POST'])
def update_availability(dish_id):
    # Convert the dish_id to ObjectId
    dish_id = ObjectId(dish_id)

    # Find the dish with the given ID
    dish = db.menu.find_one({'_id': dish_id})

    if dish:
        # Update the availability of the dish
        new_availability = request.form.get('availability') == 'on'
        db.menu.update_one({'_id': dish_id}, {'$set': {'availability': new_availability}})

    return redirect(url_for('show_menu'))

# Route for displaying the menu with the update availability option
@app.route('/updateAvail')
def update_avail():
    items = db.menu.find()
    menu = [MenuItem(str(item['_id']), item['dish_name'], item['price'], item['availability']) for item in items]
    return render_template('updateAvail.html', menu=menu)

# WebSocket event handler for updating availability
@socketio.on('update_availability')
def handle_update_availability(data):
    dish_id = ObjectId(data['dish_id'])
    dish = db.menu.find_one({'_id': dish_id})

    if dish:
        new_availability = not dish['availability']
        db.menu.update_one({'_id': dish_id}, {'$set': {'availability': new_availability}})
        # Emit availability update event to all clients
        socketio.emit('availability_update', {'dish_id': str(dish_id), 'availability': new_availability})


# Route for creating a new order
@app.route('/new_order', methods=['GET', 'POST'])
def new_order():
    if request.method == 'POST':
        # Get the form data
        customer_name = request.form['customer_name']
        dish_ids_str = request.form['dish_ids']
        dish_ids = [dish_id.strip() for dish_id in dish_ids_str.split(',')]

        # Convert dish IDs to ObjectIds
        dish_ids = [ObjectId(dish_id) for dish_id in dish_ids if dish_id.isdigit()]

        # Find the dishes based on the IDs
        ordered_dishes = db.menu.find({'_id': {'$in': dish_ids}})
        ordered_dishes = [MenuItem(item['_id'], item['dish_name'], item['price'], item['availability']) for item in ordered_dishes]

        # Check if all dishes are available
        all_available = all(dish.availability for dish in ordered_dishes)

        if all_available:
            # Assign a unique order ID
            order_id = db.orders.count_documents({}) + 1

            # Create a new order
            new_order = {
                'id': order_id,
                'customer_name': customer_name,

                'dishes': [dish.to_dict() for dish in ordered_dishes],
                'status': 'received'
            }

            # Add the new order to the orders collection
            db.orders.insert_one(new_order)

            return redirect(url_for('show_orders'))

    items = db.menu.find()
    menu = [MenuItem(item['_id'], item['dish_name'], item['price'], item['availability']) for item in items]

    return render_template('new_order.html', menu=menu)

# Route for viewing the orders
@app.route('/show_orders')
def show_orders():
    orders = db.orders.find()
    return render_template('orders.html', orders=orders)



# Route for exiting the application
@app.route('/exit_app')
def exit_app():
    # You can perform any necessary cleanup operations here
    return 'Exiting the application...'

if __name__ == '__main__':
    socketio.run(app)
