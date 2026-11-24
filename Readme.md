Project title
A Web-Based, Location-Aware Inventory Management System 
for Improving Online Order Fulfilment in Retail

Project Description
This project focuses on improving inventory visibility between Pick n Pay physical stores and the PnP asap online ordering platform.

The proposed web-based system helps users monitor stock availability across different stores, identify inventory discrepancies and improve online order fulfilment.

All group members' names and student numbers
Nomfundo Buthelezi u21766445 
Nyeleti Nwaila u23879824 
Rangoato Mankoe u22737139 
Lindelwa Ntuli u23612712-

Installation/setup instructions
Step Instruction	                                    Purpose
1	 Install Visual Studio Code (VS Code).	            To open and edit the project files.
2	 Install Python.                                    To run the Python calculations.    
3	 Download or clone the GitHub repository.	        To obtain the project files.
4	 Open the downloaded folder in VS Code.	            To access the project.
5	 Install any required Python libraries.	            To ensure the Python code works.
6	 Open index.html in a browser or with Live Server.	To view the inventory dashboard.
7	 Run the Python application or tests as instructed.	To check that the calculations work.

Project Files

index.html – Contains the dashboard structure.

style.css – Controls the dashboard appearance.

eoq.py – Contains Economic Order Quantity calculations.

test_calculations.py – Contains tests for the calculations.

# Stock Sync – Backend API

## 1. Project Overview

Stock Sync is a web-based, location-aware inventory management system designed to improve online order fulfilment in retail stores.

The backend was developed using Python and Flask. It provides REST API endpoints that allow the frontend to retrieve, create and update product and inventory information stored in MySQL.

## 2. Technologies Used

- Python
- Flask
- PyMySQL
- MySQL
- HTML
- CSS
- JavaScript
- python-dotenv

## 3. Backend Structure

- app.py: Creates and runs the Flask application.
- config.py: Contains development, testing and production configurations.
- Database/db.py: Handles MySQL database connections.
- Models/: Contains SQL queries and database operations.
- Routes/: Contains REST API endpoints.
- .env: Stores database connection settings.

## 4. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | / | API welcome message |
| GET | /api/health | Checks API status |
| GET | /api/products | Retrieves products |
| GET | /api/products/{product_id} | Retrieves one product |
| POST | /api/products | Creates a product |
| PUT | /api/products/{product_id} | Updates all product fields |
| PATCH | /api/products/{product_id} | Updates selected product fields |
| GET | /api/inventory | Retrieves inventory |
| GET | /api/inventory/{inventory_id} | Retrieves one inventory record |
| PATCH | /api/inventory/{inventory_id} | Updates inventory |
| POST | /api/stock-movements | Records stock movements |
| GET | /api/categories | Retrieves categories |
| GET | /api/stores | Retrieves stores |

## 5. Example Requests

### Create a product

POST /api/products

Request:

    {
      "product_name": "Wireless Barcode Scanner",
      "sku": "WBS001",
      "category_id": 1,
      "unit_price": 850.00,
      "description": "Wireless scanner for retail inventory"
    }

Successful response (201):

    {
      "message": "Product created successfully.",
      "product_id": 8
    }

### Retrieve products

GET /api/products?page=1&size=10

Successful response (200):

    {
      "data": [],
      "pagination": {
        "page": 1,
        "size": 10,
        "total": 0,
        "pages": 0
      }
    }

The data array contains the products returned by the database.

### Update a product

PATCH /api/products/1

Request:

    {
      "unit_price": 950.00
    }

### Record a stock movement

POST /api/stock-movements

Request:

    {
      "inventory_id": 1,
      "movement_type": "OUT",
      "quantity": 5,
      "notes": "Stock issued for an online order"
    }

Successful response (201):

    {
      "message": "Stock movement recorded successfully.",
      "movement_id": 1
    }

## 6. Pagination and Filtering

The product and inventory listing endpoints support pagination.

Example:

    GET /api/products?page=1&size=10

Product filtering:

    GET /api/products?category_id=1

Product name search:

    GET /api/products?name=scanner

Inventory filtering:

    GET /api/inventory?store_id=4

    GET /api/inventory?product_id=1

## 7. HTTP Status Codes

- 200: Request completed successfully.
- 201: Resource created successfully.
- 400: Invalid request or input.
- 404: Requested resource not found.
- 409: Duplicate product SKU.
- 500: Unexpected server or database error.

## 8. Validation and Error Handling

The API validates required fields, data types, numeric values and request formats.

Duplicate product SKUs are handled with a conflict response.

Database write operations use commit and rollback to maintain data consistency.

Python logging records application errors without exposing internal error details to API users.

## 9. Blueprints and Configuration

Flask Blueprints separate the API into product, inventory and reference-data routes.

The configuration file supports development, testing and production environments.

Database connection details are stored in environment variables rather than being written directly into the application code.

## 10. Stock Movement Logic

- IN increases the quantity available.
- OUT decreases the quantity available.
- ADJUSTMENT sets the quantity to a specified new stock level.

Stock movements update the inventory quantity and create a movement record in the same database transaction.

## 11. Running the Application

Install the required packages:

    python -m pip install -r requirements.txt

Activate the virtual environment on Windows:

    venv\Scripts\activate

Run the Flask application from the main project directory:

    python -m Backend.app

The API will be available at:

    http://127.0.0.1:5000/


## Installation, Database Setup and Running StockSync
## 1. Project Purpose

StockSync is a retail inventory management system designed to help manage products, stock levels and stock movements across multiple store locations. It uses a centralised database to maintain inventory information and provides API endpoints for retrieving and updating product and stock records.

## 2. Database Schema and ERD

StockSync uses a MySQL relational database named stocksync_db. The database consists of five main tables:

stores: Stores information about individual retail branches.

categories: Stores product categories.

products: Stores product details, including names, SKUs and prices.

inventory: Connects products to individual stores and records stock quantities and reorder levels.

stock_movements: Records stock movements, including stock received, stock issued and adjustments.

The tables are connected through primary keys and foreign keys to maintain relationships and data consistency.

The Entity Relationship Diagram (ERD) below illustrates the database structure and relationships between the five tables.



## 3. System Requirements

Before installing StockSync, ensure that the following software is available:

Python 3

MySQL Server

MySQL Workbench

Git

Visual Studio Code or another code editor

## 4. Clone the Repository

Open PowerShell or the VS Code terminal and execute:

git clone https://github.com/U23879824/BFB_321_GROUP_20.git

Navigate into the project directory:

cd BFB_321_GROUP_20

## 5. Create and Activate the Python Environment

Create a virtual environment:

python -m venv .venv

Activate it in Windows PowerShell:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

Once activated, (.venv) should appear at the beginning of the terminal prompt.

## 6. Install Project Dependencies

Install the required Python packages:

pip install -r requirements.txt

The requirements file includes Flask, MySQL Connector and python-dotenv.

## 7. Configure Environment Variables

Create a local environment file by copying the example:

Copy-Item .env.example .env

Open the .env file and configure the database connection settings:

FLASK_ENV=development
SECRET_KEY=your-local-secret-key
DB_HOST=localhost
DB_PORT=3306
DB_NAME=stocksync_db
DB_USER=root
DB_PASSWORD=your-mysql-password
TEST_DB_NAME=stocksync_test_db

Replace your-mysql-password with the password for your local MySQL account. If the account does not use a password, leave the value blank.

The .env file contains local configuration and should not be uploaded to GitHub.

## 8. Create and Populate the Database

Open MySQL Workbench and connect to your local MySQL Server.

Step 1: Create the main database

Open database/schema.sql from the project folder.

Open the SQL script in MySQL Workbench.

Execute the script to create stocksync_db and its five tables.

Step 2: Load sample data

Open database/seed.sql in MySQL Workbench.

Execute the script to insert the sample stores, categories, products, inventory records and stock movements.

Step 3: Create the test database (optional)

To create the separate test database, open and execute:

database/schema_test.sql

This creates stocksync_test_db with the required table structure.

After executing the scripts, check the SCHEMAS panel in MySQL Workbench to confirm that the databases and tables have been created.

## 9. Run the Application

Ensure that:

The virtual environment is activated.

MySQL Server is running.

The .env file contains the correct database connection settings.

The main database has been created and populated.

Start the Flask application using:

python app.py

When the application starts successfully, the local development server should be available at:

http://127.0.0.1:5000

The root endpoint can be accessed through a web browser to check the API welcome response.

## 10. Testing and Login Information

The project includes a calculation test file named test_calculations.py. It can be run using:

python -m unittest test_calculations.py

StockSync currently provides REST API functionality for product and inventory management. No sign-in credentials are specified because a user authentication and login system has not been established in the supplied implementation.

## 11. Troubleshooting

MySQL connection error: Confirm that MySQL Server is running and that the database credentials in .env are correct.

Module not found: Activate the virtual environment and run pip install -r requirements.txt.

Database not found: Execute database/schema.sql in MySQL Workbench.

Missing sample records: Execute database/seed.sql after creating the main database.

Application does not start: Check the terminal output for Python errors and confirm that the application files are up to date.

Following these instructions allows a new developer to configure the environment, create the database, load sample data and start the StockSync application.