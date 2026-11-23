 # StockSync REST API Documentation

## 1. Introduction

The StockSync REST API is developed using Python and Flask to support the StockSync inventory management application.

The API allows users to retrieve, create and update product and inventory information stored in the MySQL database.

## 2. Technologies Used

- Python
- Flask
- MySQL
- MySQL Connector
- Python-dotenv

## 3. Database Structure

The API uses the existing StockSync database, which contains:

- Products
- Categories
- Stores
- Inventory
- Stock Movements

## 4. API Endpoints

| HTTP Method | Endpoint | Description |
|---|---|---|
| GET | /api/products | Retrieve all products |
| GET | /api/products/{product_id} | Retrieve one product |
| POST | /api/products | Create a product |
| PUT | /api/products/{product_id} | Update a complete product |
| PATCH | /api/products/{product_id} | Partially update a product |
| GET | /api/inventory | Retrieve inventory records |
| GET | /api/inventory/{inventory_id} | Retrieve one inventory record |
| POST | /api/inventory | Create an inventory record |
| PATCH | /api/inventory/{inventory_id} | Update inventory |
| POST | /api/stock-movements | Record stock movements |
| GET | /api/categories | Retrieve categories |
| GET | /api/stores | Retrieve stores |

## 5. Product API JSON Structure

### Create Product

HTTP Method: POST

Endpoint: /api/products

Request:

```json
{
  "product_name": "Bread 700g",
  "sku": "GRO008",
  "category_id": 1,
  "unit_price": 18.99,
  "description": "White bread"
}
```

Successful response: HTTP 201 Created.

```json
{
  "success": true,
  "message": "Product created successfully.",
  "product_id": 8
}
```

### Retrieve Products

HTTP Method: GET

Endpoint: /api/products

Example:

`/api/products?page=1&size=10`

The response contains product information and pagination details.

### Update Product

HTTP Method: PUT

Endpoint: /api/products/1

Request:

```json
{
  "product_name": "Rice 2kg Premium",
  "sku": "GRO001",
  "category_id": 1,
  "unit_price": 54.99,
  "description": "Premium rice"
}
```

Successful response: HTTP 200 OK.

## 6. Inventory API JSON Structure

### Create Inventory

HTTP Method: POST

Endpoint: /api/inventory

Request:

```json
{
  "store_id": 4,
  "product_id": 1,
  "quantity_on_hand": 100,
  "reorder_level": 20
}
```

### Update Inventory

HTTP Method: PATCH

Endpoint: /api/inventory/1

Request:

```json
{
  "quantity_on_hand": 150,
  "reorder_level": 25
}
```

## 7. Pagination and Filtering

The product and inventory list endpoints support pagination.

Available parameters:

- page: page number.
- size: number of records per page.
- category: filter products by category name.
- name: search products by name.
- store_id: filter inventory by store.
- product_id: filter inventory by product.

Example:

`/api/products?page=1&size=10&category=Groceries`

## 8. Validation

The API validates incoming JSON data.

Examples include:

- Required fields must be provided.
- Product prices cannot be negative.
- Product SKUs must be unique.
- Category IDs must be valid.
- Inventory quantities cannot be negative.
- Pagination values must be within the permitted range.

Invalid requests return HTTP 400 with an explanatory JSON response.

## 9. HTTP Status Codes

| Status Code | Meaning |
|---|---|
| 200 | Successful request |
| 201 | Resource created |
| 400 | Invalid request |
| 404 | Resource not found |
| 500 | Internal server error |

## 10. Error Handling and Logging

The application uses Flask error handlers to provide consistent JSON responses.

Python logging records application errors. Database write operations use transaction rollback when a failure occurs.

Detailed technical errors are not exposed to API users.

## 11. Blueprint Organisation

The application uses Flask Blueprints to organise its endpoints.

- products_bp: product operations.
- inventory_bp: inventory and stock movement operations.
- reference_bp: store and category operations.

## 12. Configuration

Database settings are stored in an environment file.

The application supports development, testing and production configurations.

## 13. Running the Application

Activate the Python virtual environment and install the dependencies.

Run:

```powershell
python -m pip install -r requirements.txt
python -m Backend.app
```

The API runs locally at:

http://127.0.0.1:5000