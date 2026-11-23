
# StockSync REST API

## 1. Project Description

StockSync is a Flask-based REST API developed to support the StockSync inventory management system.

The API communicates with the MySQL database developed in Part B1.

It provides functionality for managing products, inventory records and stock movements.

## 2. Technologies Used

- Python 3.14
- Flask 3.1.3
- MySQL
- mysql-connector-python
- python-dotenv

## 3. Application Structure

Backend/
- Routes/
  - products.py
  - inventory.py
- Models/
- Database/
- app.py
- config.py
- db.py
- .env
- requirements.txt
- README.md

## 4. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /api/products | Retrieve products |
| GET | /api/products/{id} | Retrieve one product |
| POST | /api/products | Create a product |
| PUT | /api/products/{id} | Update a product |
| GET | /api/inventory | Retrieve inventory |
| GET | /api/inventory/{id} | Retrieve one inventory record |
| PATCH | /api/inventory/{id} | Update inventory |
| POST | /api/stock-movements | Record a stock movement |

## 5. Pagination and Filtering

The products endpoint supports pagination and filtering.

Example:

GET /api/products?page=1&size=10&category=Groceries

The inventory endpoint supports filtering by store and product.

Example:

GET /api/inventory?page=1&size=10&store_id=4

## 6. Request and Response Examples

### Create Product

POST /api/products

Request:

{
  "product_name": "Bread 700g",
  "sku": "GRO008",
  "category_id": 1,
  "unit_price": 18.99,
  "description": "White bread"
}

Successful response:

{
  "success": true,
  "message": "Product created successfully.",
  "product_id": 8
}

Status code: 201 Created

### Update Product

PUT /api/products/1

Request:

{
  "product_name": "Rice 2kg Premium",
  "unit_price": 54.99
}

Successful response:

{
  "success": true,
  "message": "Product updated successfully.",
  "product_id": 1
}

Status code: 200 OK

### Record Stock Movement

POST /api/stock-movements

Request:

{
  "inventory_id": 1,
  "movement_type": "IN",
  "quantity": 20,
  "notes": "New stock received"
}

Successful response:

{
  "success": true,
  "message": "Stock movement recorded successfully.",
  "movement_id": 1,
  "previous_quantity": 130,
  "new_quantity": 150
}

Status code: 201 Created

## 7. HTTP Status Codes

- 200: Request successful.
- 201: Resource created successfully.
- 400: Invalid request or validation error.
- 404: Resource not found.
- 500: Internal server error.

## 8. Error Handling and Logging

The application uses centralised Flask error handlers.

Errors are returned as JSON responses.

The Python logging module records application failures in stocksync.log.

Database transactions are rolled back when a database write fails.

## 9. Configuration

Database credentials are stored in the .env file.

The config.py file provides development, testing and production configurations.

The .env file must not be uploaded to GitHub.

## 10. Running the Application

Activate the virtual environment.

Install dependencies:

pip install -r requirements.txt

Run the application:

python app.py

The API runs locally at:

http://127.0.0.1:5000
