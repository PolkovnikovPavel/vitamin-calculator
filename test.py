from requests import get, post, put, delete
from data import db_session
from data.products import Products


db_session.global_init("db/vitamin_calculator.sqlite")
session = db_session.create_session()
all_products = session.query(Products).all()

for product in all_products:
    print(float(str(product.vitamin).replace(',', '.')))

