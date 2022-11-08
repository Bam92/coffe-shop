import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# https://dev-ft6rxlg4.us.auth0.com/u/login?state=hKFo2SBpeklSc1ktUloycWYtN2lObE5uTXlZRlcxaUszNEtDYqFur3VuaXZlcnNhbC1sb2dpbqN0aWTZIFQ0UC1pMXNQemJxcHhCdGxydm1kdzZrUTU1cE5LY3J4o2NpZNkgdEVDbkZLOTV2RFQxQUZvajN4RmJoZm5pRXZKRkg0Umg

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
@app.route("/drinks")
def get_drinks():
    drinks = Drink.query.all()
    formatted_drinks = [drink.short() for drink in drinks]

    return jsonify({ 'success' : True, 'drinks': formatted_drinks }), 200

@app.route("/drinks-detail")
def get_drinks_detail():
    drinks = Drink.query.all()
    formatted_drinks = [drink.long() for drink in drinks]

    return jsonify({ 'success' : True, 'drinks': formatted_drinks }), 200

@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def post_drinks():
    body = request.get_json()

    try:
        title = body['title']
        recipe = body['recipe']

        drink = Drink(title=title, recipe=recipe)
        drink.insert()
        
        return jsonify({ 'success' : True, 'drinks': [drink.long()] }), 201
    
    except Exception:
        abort(422)

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(drink_id, payload):
    body = request.get_json()

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if not drink:
        abort(404)

    try:

        drink.title = body['title']
        drink.recipe = body['recipe']

        drink.update()

        return jsonify({ 'success' : True, 'drinks': [drink.long()] }), 200

    except Exception:
        abort(422)

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(drink_id, payload):
    drink = Drink.query.filter(Drink.id == drink_id)

    if not drink:
        abort(404)

    try:

        drink.delete()

        return jsonify({ 'success': True, 'delete': drink.id })

    except Exception:
        abort(422)

# Error Handling

# Error Handler (401) Unauthorized
@app.errorhandler(AuthError)
def not_authenticated(auth_error):
    return jsonify({ 'success': False, 'message': auth_error.error }), 401

# Error Handler (404) Not Found
@app.errorhandler(404)
def not_found(error):
    return jsonify({ 'success': False, 'message': 'resource not found' }), 404


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({ 'success': False, 'message': 'unprocessable' }), 422

@app.errorhandler(500)
def server_error(error):
    return jsonify({ 'success': False, 'message': "this is a server error, don't worry everything is under controle" }), 500


