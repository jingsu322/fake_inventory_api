from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fake_inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Updated model
class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(255))
    product_name = db.Column(db.String(255))
    factory_name = db.Column(db.String(255))
    seller_name = db.Column(db.String(255))
    url_key = db.Column(db.String(255))
    available_qty = db.Column(db.Float)
    product_url = db.Column(db.String(255))
    price_info = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "sku": self.sku,
            "name": self.name,
            "product_name": self.product_name,
            "factory_name": self.factory_name,
            "seller_name": self.seller_name,
            "url_key": self.url_key,
            "available_qty": self.available_qty,
            "product_url": self.product_url,
            "price_info": self.price_info
        }

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return jsonify({"message": "This is a fake inventory API"})

@app.route('/inventory/batch', methods=['POST'])
def batch_add_inventory():
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({"error": "Expected a list of inventory items"}), 400

    new_items = []
    for item in data:
        try:
            new_item = Inventory(
                sku=item.get("Sku"),
                name=item.get("Name"),
                product_name=item.get("Product Name"),
                factory_name=item.get("Factory Name"),
                seller_name=item.get("Seller Name"),
                url_key=item.get("Url Key"),
                available_qty=item.get("Available Qty"),
                product_url=item.get("Product URL"),
                price_info=item.get("Price Info")
            )
            new_items.append(new_item)
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    db.session.add_all(new_items)
    db.session.commit()
    return jsonify({"message": f"{len(new_items)} items added"}), 201

@app.route('/inventory', methods=['GET'])
def get_inventories():
    sku  = request.args.get('sku')
    name = request.args.get('product_name')

    query = Inventory.query
    if sku:
        query = query.filter_by(sku=sku)
    elif name:
        # Use ilike for case-insensitive, partial‐match searches:
        query = query.filter(Inventory.product_name.ilike(f"%{name}%"))

    items = query.all()
    return jsonify([item.to_dict() for item in items]), 200


# @app.route('/inventory/<int:inventory_id>', methods=['GET'])
# def get_inventory(inventory_id):
#     item = Inventory.query.get(inventory_id)
#     if item:
#         return jsonify(item.to_dict())
#     else:
#         return jsonify({"error": "Inventory not found"}), 404

# @app.route('/inventory', methods=['POST'])
# def add_inventory():
#     data = request.get_json()
#     if not data or not all(k in data for k in ("sku", "warehouse", "quantity", "price")):
#         return jsonify({"error": "Missing required fields"}), 400

#     new_item = Inventory(
#         sku=data["sku"],
#         warehouse=data["warehouse"],
#         quantity=data["quantity"],
#         price=data["price"]
#     )
#     db.session.add(new_item)
#     db.session.commit()
#     return jsonify(new_item.to_dict()), 201

# @app.route('/inventory/<int:inventory_id>', methods=['PUT'])
# def update_inventory(inventory_id):
#     data = request.get_json()
#     item = Inventory.query.get(inventory_id)
#     if item:
#         item.sku = data.get("sku", item.sku)
#         item.warehouse = data.get("warehouse", item.warehouse)
#         item.quantity = data.get("quantity", item.quantity)
#         item.price = data.get("price", item.price)
#         db.session.commit()
#         return jsonify(item.to_dict())
#     else:
#         return jsonify({"error": "Inventory not found"}), 404

# @app.route('/inventory/<int:inventory_id>', methods=['DELETE'])
# def delete_inventory(inventory_id):
#     item = Inventory.query.get(inventory_id)
#     if item:
#         db.session.delete(item)
#         db.session.commit()
#         return jsonify({"message": "Inventory deleted"})
#     else:
#         return jsonify({"error": "Inventory not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
