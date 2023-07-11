from app import app
import pytest
from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
from bson import ObjectId
from flask_socketio import SocketIO
from unittest.mock import Mock

# MongoDB connection
client = MongoClient('mongodb+srv://vishalpadaswan3:vishal@cluster0.907cq.mongodb.net/ZoMaTo?retryWrites=true&w=majority')
db = client['zomatoAIdata']

@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    yield client

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

# Mock the MongoDB collection 'menu'
mock_menu = [
    {
        '_id': '1',
        'dish_name': 'Dish 1',
        'price': 9.99,
        'availability': True
    },
    {
        '_id': '2',
        'dish_name': 'Dish 2',
        'price': 14.99,
        'availability': False
    }
]

mock_db = Mock()
mock_db.menu.find.return_value = mock_menu
app.config['db'] = mock_db

# Route for serving the index.html page
def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'<!DOCTYPE html>\n<html>\n<head>\n    <title>Chatbot</title>\n    <link rel="stylesheet" type="text/css" href="{{ url_for(' in response.data

# Route for displaying the feedback form
def test_feedback(client):
    response = client.get('/feedback')
    assert response.status_code == 200
    assert b'<!DOCTYPE html>\n<html>\n<head>\n    <title>Feedback Form</title>\n</head>\n<body>\n    <h1>Feedback Form</h1>\n\n    <form action="/feedback" method="POST">' in response.data

# Route for displaying the menu
def test_show_menu(client):
    response = client.get('/show_menu')
    assert response.status_code == 200
    assert b'<h1>Menu</h1>' in response.data

# Route for adding a new dish
def test_add_dish(client):
    response = client.post('/add_dish', data={
        'dish_name': 'New Dish',
        'price': 9.99,
        'availability': 'on'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'New Dish' in response.data

# Route for removing a dish
def test_confirm_remove(client):
    response = client.get('/confirm_remove/1')
    assert response.status_code == 200
    assert b'<h2>Confirm Removal</h2>' in response.data

# Route for updating the availability of a dish
def test_update_availability(client):
    response = client.post('/update_availability/1', data={
        'availability': 'on'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'<h1>Menu</h1>' in response.data

# Route for displaying the menu with the update availability option
def test_update_avail(client):
    response = client.get('/updateAvail')
    assert response.status_code == 200
    assert b'<h1>Menu</h1>' in response.data

# Route for creating a new order
def test_new_order(client):
    response = client.post('/new_order', data={
        'customer_name': 'John Doe',
        'dish_ids': '1,2'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'<h1>Orders</h1>' in response.data

# Route for viewing the orders
def test_show_orders(client):
    response = client.get('/show_orders')
    assert response.status_code == 200
    assert b'<h1>Orders</h1>' in response.data

# Route for exiting the application
def test_exit_app(client):
    response = client.get('/exit_app')
    assert response.status_code == 200
    assert response.data == b'Exiting the application...'

# WebSocket event handler for updating availability
def test_handle_update_availability(client):
    # Simulate a WebSocket event
    with app.test_client() as socket_client:
        socketio.connect()
        socketio.emit('update_availability', {'dish_id': '1'})
        socketio.on_event('availability_update', lambda data: assert data['dish_id'] == '1' and data['availability'] == False)

# Run the tests
if __name__ == '__main__':
    pytest.main()
