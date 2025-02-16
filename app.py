# DON'T USE PYTHON 3.13!!! USE PYTHON 3.12!!!
# Developed by Alex Desatoff
from flask import Flask, request, jsonify
from models.user import User, Diet
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
import bcrypt

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:admin123@127.0.0.1:3306/flask-crud'

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)
#View Login
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Login
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username and password:
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
            login_user(user)
            print(current_user.is_authenticated)
            return jsonify({"message": "Authentication Completed Successfully!"})

    return jsonify({"message": "Invalid or Missing Credentials!"}), 400

# Logout
@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout Sucessfully!"})

# Create New User
@app.route('/register', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username and password:
        hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
        user = User(username=username, password=hashed_password, role='user')
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User Registered Sucessfully!"})

    return jsonify({"message": "Invalid Data!"}), 400

# Update User
@app.route('/user_update/<int:id_user>', methods=["PUT"])
@login_required
def update_user(id_user):
    data = request.json
    user = User.query.get(id_user)

    if id_user != current_user.id and current_user.role == 'user':
        return jsonify({'message': "Operation Not Permitted!"}), 403

    if user and data.get("password"):
        user.password = data.get("password")
        db.session.commit()

        return jsonify({"message": f"User {id_user} Updated Sucessfully!"})
    
    return jsonify({"message": "User Not Found!"}), 404

# Delete User
@app.route('/user_delete/<int:id_user>', methods=["DELETE"])
@login_required
def delete_user(id_user):
    user = User.query.get(id_user)

    if current_user.role != 'admin':
        return jsonify({"message": "Operation Not Permitted!"}), 403
    
    if id_user == current_user.id:
        return jsonify({"message": "Action Not Allowed (Logged User)!"}), 403

    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"User {id_user} Deleted Successfully!"})

    return jsonify({"message": "User Not Found!"}), 404

# Create new diet
@app.route('/diets_create', methods=['POST'])
@login_required
def create_diet():
    data = request.get__json()

    new_diet = Diet(
        name=data['name'],
        description=data['description'],
        date=data['date'],
        ondiet=data['ondiet'],
        user_id=current_user.id # Associating the diet with the logged user
    )
    db.session.add(new_diet)
    db.session.commit()
    return jsonify({"message": "Successfully Registered Diet!"}), 201

# Show all diets
@app.route('/diets_list', methods=['GET'])
@login_required
def show_diets():
    diet = Diet.query.filter_by(user_id=current_user.id).all()
    diet_list = [{'id': r.id, "name": r.name, "description": r.description, "date": r.date, "ondiet": r.ondiet}for r in diet]
    return jsonify(diet_list)

# Show a Specific Diet
@app.route('/diets_specific/<int:id>', methods=['GET'])
@login_required
def view_diet(id):
    diet = Diet.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    diet_data = {
        "id": diet.id,
        "name": diet.name,
        "description": diet.description,
        "date": diet.date,
        "ondiet": diet.ondiet
    }
    return jsonify(diet_data)

# Update a Diet
@app.route('/diets_update/<int:id>', methods=['PUT'])
@login_required
def update_diet(id):
    diet = Diet.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    data = request.get_json()

    diet.name = data['name']
    diet.description = data['description']
    diet.date = data['date']
    diet.ondiet = data['ondiet']

    db.session.commit()
    return jsonify({'message': "Successfully Edited Diet!"})

# Delete a Diet
@app.route('/diets_delete/<int:id>', methods=['DELETE'])
@login_required
def delete_diet(id):
    diet = Diet.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(diet)
    db.session.commit()
    return jsonify({"message": "Diet successfully excluded!"})

# User loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Running app
if __name__ == '__main__':
    app.run(debug=True)
