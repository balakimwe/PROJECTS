from flask_app.config.mysqlconnection import connectToMySQL
# TODO add email validation
import re	# the regex module
# create a regular expression object that we'll use later   
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

DATABASE = 'egrocery_store'

from flask_app import flash

class Customer:
    
    def __init__(self, data) -> None:
        self.customer_id = data['customer_id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        
    @classmethod
    def save(cls, data):
        query = "INSERT INTO customers (first_name, last_name, email, password) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s);"
        return connectToMySQL(DATABASE).query_db(query, data)
    
    # TODO Write a query method to verify the email entered in the login form
    @classmethod
    def get_by_email(cls, data):
        query = "SELECT * FROM customers WHERE email = %(email)s"
        result = connectToMySQL(DATABASE).query_db(query, data)
        print(result)
        if len(result) > 0:
            return Customer(result[0])
        else:
            return False
    
    @staticmethod
    def validate_customer(customer:dict) -> bool:
        is_valid = True
        # TODO Write a conditional statement for each validation
        if len(customer['first_name']) < 2:
            is_valid = False
            flash("first name must be at least 2 characters")
        if len(customer['last_name']) < 2:
            is_valid = False
            flash("first name must be at least 2 characters")
        if customer['password'] != customer['confirm-password']:
            is_valid = False
            flash("passwords do not match")
        if not EMAIL_REGEX.match(customer['email']): 
            flash("Invalid email address!")
            is_valid = False
        if len(customer['password']) < 8:
            is_valid = False
            flash("password must be at least 8 characters")

        return is_valid
    