from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# Sample data for menu and orders
menu = [
    {'id': 1, 'name': 'Pasta', 'price': 10.99, 'availability': True},
    {'id': 2, 'name': 'Pizza', 'price': 12.99, 'availability': True},
    {'id': 3, 'name': 'Burger', 'price': 8.99, 'availability': False},
]

orders = []

# Route for serving the index.html page
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

# Route for displaying the menu
@app.route('/menu')
def show_menu():
    return render_template('menu.html', menu=menu)

# Route for adding a new dish
@app.route('/add_dish', methods=['GET', 'POST'])
def add_dish():
    if request.method == 'POST':
        # Get the form data
        dish_name = request.form['dish_name']
        price = float(request.form['price'])
        availability = request.form.get('availability') == 'on'
        
        # Create a new dish
        new_dish = {
            'id': len(menu) + 1,
            'name': dish_name,
            'price': price,
            'availability': availability
        }
        
        # Add the new dish to the menu
        menu.append(new_dish)
        
        return redirect('/menu')
    
    return render_template('add_dish.html')

# Route for removing a dish
@app.route('/remove_dish/<int:dish_id>')
def remove_dish(dish_id):
    # Find the dish with the given ID
    dish = next((d for d in menu if d['id'] == dish_id), None)
    
    if dish:
        # Remove the dish from the menu
        menu.remove(dish)
    
    return redirect('/menu')

# Route for updating the availability of a dish
@app.route('/update_availability/<int:dish_id>', methods=['POST'])
def update_availability(dish_id):
    # Find the dish with the given ID
    dish = next((d for d in menu if d['id'] == dish_id), None)
    
    if dish:
        # Update the availability of the dish
        dish['availability'] = request.form.get('availability') == 'on'
    
    return redirect('/menu')

# Route for taking a new order
@app.route('/new_order', methods=['GET', 'POST'])
def new_order():
    if request.method == 'POST':
        # Get the form data
        customer_name = request.form['customer_name']
        dish_ids_str = request.form['dish_ids']
        dish_ids = [int(dish_id) for dish_id in dish_ids_str.split(',')]

        # Find the dishes based on the IDs
        ordered_dishes = [d for d in menu if d['id'] in dish_ids]

        # Check if all dishes are available
        all_available = all(dish['availability'] for dish in ordered_dishes)

        if all_available:
            # Assign a unique order ID
            order_id = len(orders) + 1

            # Create a new order
            new_order = {
                'id': order_id,
                'customer_name': customer_name,
                'dishes': ordered_dishes,
                'status': 'received'
            }

            # Add the new order to the orders list
            orders.append(new_order)

            print(f"Redirecting to /orders with order ID: {order_id}")
            return redirect('/orders')

    return render_template('new_order.html', menu=menu)


# Route for updating the status of an order
@app.route('/update_status/<int:order_id>', methods=['POST'])
def update_status(order_id):
    # Find the order with the given ID
    order = next((o for o in orders if o['id'] == order_id), None)
    
    if order:
        new_status = request.form['status']
        
        # Update the status of the order
        order['status'] = new_status
    
    return redirect('/orders')

@app.route('/remove_dish/<int:dish_id>', methods=['GET', 'POST'])
def confirm_remove(dish_id):
    if request.method == 'POST':
        # Remove the dish from the menu based on dish_id
        for dish in menu:
            if dish['id'] == dish_id:
                menu.remove(dish)
                break
        return redirect(url_for('show_menu'))
    else:
        return render_template('confirm_remove.html', dish_id=dish_id)



# Route for viewing the orders
@app.route('/orders')
def show_orders():
    return render_template('orders.html', orders=orders)

# Route for exiting the application
@app.route('/exit')
def exit_app():
    # You can perform any necessary cleanup operations here
    return 'Exiting the application...'

if __name__ == '__main__':
    app.run()
