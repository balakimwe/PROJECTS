from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import flash
from pprint import pprint

DATABASE = 'egrocery_store'

class Product:
    
    def __init__(self, data):
        self.product_id = data['pproduct_id']
        self.name = data['name']
        self.quantity = data['quantity']
        self.price_per_unit = data['price']
        self.quantity = data['price_per_unit']
        self.first_name = data['first_name']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
    
    @classmethod
    def save(cls, data):
        query = "INSERT INTO egrocery_store (title, description, price, user_id) VALUES (%(title)s, %(description)s, %(price)s, %(user_id)s);"
        return connectToMySQL(DATABASE).query_db(query, data)

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM egrocery_storeJOIN users ON users.id = products.user_id;"
        results = connectToMySQL(DATABASE).query_db(query)
        pprint(results)
        products = []
        for product in results:
            products.append(cls(product))
        return products

    @classmethod
    def get_one(cls, data):
        query = "SELECT * FROM egrocery_store JOIN users ON users.id = products.user_id WHERE products.id = %(id)s;"
        result = connectToMySQL(DATABASE).query_db(query, data)
        pprint(result[0])
        return Product(result[0])
    
    @classmethod
    def update(cls, data):
        query = "UPDATE egrocery_store SET title = %(title)s, description = %(description)s, price = %(price)s WHERE products.id = %(id)s;"
        return connectToMySQL(DATABASE).query_db(query, data)
    
    @classmethod
    def delete(cls, data):
        query = "DELETE FROM egrocery_store WHERE id = %(id)s;"
        return connectToMySQL(DATABASE).query_db(query, data)
        
    

    @staticmethod
    def validate_product(product):
        is_valid = True
        if len(product['title']) < 2:
            flash("Name must be three chars")
            is_valid = False
        if len(product['description']) < 10:
            flash("Desc must be ten chars")
            is_valid = False
        if int(product['price']) <= 0:
            flash("Price must be at least greater than 0")
            is_valid = False  
        return is_valid
    