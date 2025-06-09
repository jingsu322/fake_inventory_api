from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fake_inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Inventory model
class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(20), nullable=False)
    warehouse = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "sku": self.sku,
            "warehouse": self.warehouse,
            "quantity": self.quantity,
            "price": self.price
        }

# Create tables if not exist
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return jsonify({"message": "This is a fake inventory API"})

# @app.route('/inventory', methods=['GET'])
# def get_inventories():
#     inventories = Inventory.query.all()
#     return jsonify([item.to_dict() for item in inventories])

@app.route('/inventory', methods=['GET'])
def get_inventories():
    sku = request.args.get('sku')
    if sku:
        inventories = Inventory.query.filter_by(sku=sku).all()
    else:
        inventories = Inventory.query.all()
    return jsonify([item.to_dict() for item in inventories])


@app.route('/inventory/<int:inventory_id>', methods=['GET'])
def get_inventory(inventory_id):
    item = Inventory.query.get(inventory_id)
    if item:
        return jsonify(item.to_dict())
    else:
        return jsonify({"error": "Inventory not found"}), 404

@app.route('/inventory', methods=['POST'])
def add_inventory():
    data = request.get_json()
    if not data or not all(k in data for k in ("sku", "warehouse", "quantity", "price")):
        return jsonify({"error": "Missing required fields"}), 400

    new_item = Inventory(
        sku=data["sku"],
        warehouse=data["warehouse"],
        quantity=data["quantity"],
        price=data["price"]
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify(new_item.to_dict()), 201

@app.route('/inventory/<int:inventory_id>', methods=['PUT'])
def update_inventory(inventory_id):
    data = request.get_json()
    item = Inventory.query.get(inventory_id)
    if item:
        item.sku = data.get("sku", item.sku)
        item.warehouse = data.get("warehouse", item.warehouse)
        item.quantity = data.get("quantity", item.quantity)
        item.price = data.get("price", item.price)
        db.session.commit()
        return jsonify(item.to_dict())
    else:
        return jsonify({"error": "Inventory not found"}), 404

@app.route('/inventory/<int:inventory_id>', methods=['DELETE'])
def delete_inventory(inventory_id):
    item = Inventory.query.get(inventory_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Inventory deleted"})
    else:
        return jsonify({"error": "Inventory not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
