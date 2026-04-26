# Retail Store Chain Management System

A robust, minimal Full-Stack application representing a retail store chain's point-of-sale and inventory management system.

## Tech Stack
- **Database**: SQLite (built-in relational database)
- **Backend**: Python 3 with Flask
- **Frontend**: HTML5, Vanilla JavaScript, Bootstrap 5

## Features
1. **Dynamic Dashboard:** Real-time metrics for Total Revenue, Total Stores, Product Catalog size, and Low Stock Alerts.
2. **Live Inventory Tracking:** Instantly pulls joined relational data mapping Products to specific Stores and showing current quantities.
3. **Point of Sale (POS):** Record new sale transactions. Upon recording, the application utilizes database connections to atomically log the sale and decrement stock quantities on the backend.
4. **Relational Setup:** The backend automatically spins up the `schema.sql` utilizing correct Primary/Foreign Key bindings ensuring DB integrity.

---

## Setup & Run Instructions

### Prerequisites
- Python 3.8+ installed
- Terminal / Command Prompt

### Step 1: Install Dependencies
Open your terminal to the project directory containing this README. Create a virtual environment (optional but recommended), then install the libraries:
```bash
pip install -r requirements.txt
```

### Step 2: Initialize Database and Start Server
Run the Flask backend application:
```bash
python app.py
```
*Note: The script is built so that if the `retail_chain.db` does not exist, it will automatically run the `schema.sql` file and populate it with seed data!*

### Step 3: Access the Application
Once the server is running, you'll see console output indicating `Running on http://127.0.0.1:5000`. 
Open your web browser and navigate to:
[http://127.0.0.1:5000](http://127.0.0.1:5000)

---
*Created as a DBMS Mini Project.*
# Retail-Chain-Management-System
