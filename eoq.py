from math import sqrt, radians, sin, cos, asin
# Inventory functions to keep track of demand, stock levels, and discrepancies

def calculate_atp(on_hand, reserved):
    """
    Calculation of Available-to-Promise (ATP) inventory:

    Formula:
    ATP = Stock on_hand - Reserved Stock

    Inputs:
    on_hand: Total physical inventory available.
    reserved: Inventory allocated to existing customer orders.

    Assumptions:
    Inventory records are accurate.
    Reserved stock cannot be allocated to another order.

    Returns:
    Inventory available for new customer orders.
    """
    atp = on_hand - reserved
    return atp


def inventory_discrepancy(system_stock, physical_stock):
    """
    Calculate the difference between recorded and physical inventory.

    Formula:
    Discrepancy = System Stock - Physical Stock

    Inputs:
    system_stock: Quantity recorded in the system.
    physical_stock: Quantity physically counted in store.

    Assumptions:
    Physical stock count is accurate.

    Returns:
    Inventory discrepancy in units.
    """
    discrepancy = system_stock - physical_stock
    return discrepancy


def inventory_accuracy(correct_records, total_records):
    """
    Calculate inventory record accuracy.

    Formula:
    Inventory Accuracy (%) = (Correct Records / Total Records) * 100

    Inputs:
    correct_records: Number of accurate inventory records.
    total_records: Total inventory records assessed.

    Assumptions:
    Inventory audit results are reliable.

    Returns:
    Inventory accuracy percentage.
    """ 
    accuracy = (correct_records/total_records) * 100
    return round(accuracy, 2)



# EOQ calclulations to determine optimal order quantities and safety stock levels and if there is enough stock in specific store locations

def calculate_eoq(demand, ordering_cost, holding_cost):
    """
    Calculate Economic Order Quantity (EOQ).

    Formula:
    EOQ = sqrt((2DS) / H)

    Inputs:
    demand: Annual demand (units).
    ordering_cost: Cost of placing one order.
    holding_cost: Annual holding cost per unit.

    Assumptions:
    Demand is constant.
    Lead time is constant.
    Replenishment is instantaneous.
    No stock-outs occur.

    Returns:
    Optimal order quantity in units.
    """
    eoq = round(sqrt((2 * demand * ordering_cost) / holding_cost),2)
    return eoq


def safety_stock(max_daily_demand, average_daily_demand, lead_time):
    """
    Calculate safety stock.

    Formula:
    Safety Stock = (Maximum Daily Demand - Average Daily Demand) * Lead Time

    Inputs:
    max_daily_demand: Highest daily demand observed.
    average_daily_demand: Average daily demand.
    lead_time: Supplier lead time in days.

    Assumptions:
    Demand variability is the primary source of uncertainty.

    Returns:
    Required safety stock in units.
    """
    safety_stock = (max_daily_demand - average_daily_demand) * lead_time
    return safety_stock


def reorder_point(average_daily_demand, lead_time, safety_stock):
    """
    Calculate the reorder point (ROP).

    Formula:
    ROP =(Average Daily Demand * Lead Time) + Safety Stock

    Inputs:
    average_daily_demand: Average units sold per day.
    lead_time: Supplier lead time in days.
    safety_stock: Safety stock quantity.

    Assumptions:
    Demand is stable during lead time.
    Safety stock is maintained.

    Returns:
    Inventory level at which a replenishment order should be placed.
    """
    Rop = (average_daily_demand * lead_time) + safety_stock
    return Rop

# KPI calculations to measure performance and efficiency of the inventory management system

def substitution_rate(substitutions, total_orders):
    """Calculate the rate of order substitutions.

    Formula:
        Substitution Rate (%) =
        (Substituted Orders / Total Orders) * 100

    Inputs:
        substitutions: Number of orders requiring substitutions.
        total_orders: Total customer orders.

    Returns:
        Percentage of orders requiring substitutions.
    """
    sub_rate = (substitutions / total_orders) * 100
    return round(sub_rate,2)

def cancellation_rate(cancellations, total_orders):
    """Calculate the rate at which orders are cancelled.

    Formula:
        Cancellation Rate (%) =
        (Cancelled Orders / Total Orders) * 100

    Inputs:
        cancellations: Number of cancelled orders.
        total_orders: Total customer orders.

    Returns:
        Percentage of cancelled orders.
    """
    cancel_rate = (cancellations / total_orders) * 100
    return round(cancel_rate,2)

def fulfil_success_rate(fulfilled, total_orders):
    """Calculate fulfilment success rate.
    
    Formula:
        Fulfilment Success Rate (%) =
        (Fulfilled Orders / Total Orders) * 100

    Inputs:
        fulfilled: Number of successfully fulfilled orders.
        total_orders: Total customer orders.

    Returns:
        Percentage of successfully fulfilled orders.
    """
    success_rate = (fulfilled / total_orders) * 100
    return round(success_rate,2)


# Distance calculation to measure the distance between store and customer 

def calc_distance(lati1, longi1, lati2, longi2):
    """Calculate the distance between a customer and a store

    using the Haversine Formula-calculates the great-circle distance 
    (the shortest "as-the-crow-flies" path along the surface) between two points on 
    a sphere using their latitude and longitude coordinates.

    Inputs:
        lati1: Store latitude.
        longi1: Store longitude.
        lati2: Customer latitude.
        longi2: Customer longitude.

    Assumptions:
        - The Earth is approximated as a sphere.
        - Earth's average radius is 6371 km.
    
    Returns:
        Distance between the store and customer in kilometres.
    """

    earth_rad = 6371 # Average radius of Earth used to calculate distance between 2 geographical locations in km.

    lati1, longi1, lati2, longi2 = map(radians, [lati1, longi1, lati2, longi2]) # Convert latitude and longitude values from degrees to radians.

    dlati = lati2 - lati1  # Calculate difference between 2 locations in terms of latitude.
    dlongi = longi2 - longi1  # Calculate difference between 2 locations in terms of longitude.

    a = (sin(dlati / 2) ** 2 + cos(lati1) * cos(lati2) * sin(dlongi / 2) ** 2) # Determine the angular distance between customer and store locations

    c = 2 * asin(sqrt(a)) # Calculate the central angle between 2 points
    a_conv = earth_rad* c
    return round(a_conv,2)

# Cost calculation to calculate the cost of the distance between a store and a customer.

def fulfilment_cost(fixed_cost, cost_per_km, distance):
    """Calculate total fulfilment cost.

    Formula:
        Fulfilment Cost =
        Fixed Cost +
        (Cost per Kilometre * Distance)

    Inputs:
        fixed_cost: Base delivery cost.
        cost_per_km: Cost charged per kilometre travelled.
        distance: Distance between store and customer.

    Assumptions:
        - Transport cost increases proportionally with distance.

    Returns:
        Estimated fulfilment cost.
    """
    fulfil_cost = round(fixed_cost+ (cost_per_km * distance),2)
    return fulfil_cost
        

# How each store is selected.

def select_best_store(stores, order_quantity, customer_lati, customer_longi):
    """Select the most cost-effective store for order fulfilment.

    Selection Criteria:
        - Store must have sufficient ATP inventory.
        -A fulfilment cost is calculated for each eligible store.
        -The store with the lowest fulfilment cost is selected.

    Inputs:
        stores: List of store inventory records.
        order_quantity: Customer order quantity.
        customer_lati: Customer latitude.
        customer_longi: Customer longitude.

    Returns:
        Dictionary containing the selected store and
        fulfilment information, or None if no store
        can fulfil the order.
    """

    potential_stores = []

    for store in stores:

        atp = calculate_atp(store["on_hand"],store["reserved"])

        if atp >= order_quantity:

            distance = calc_distance(store["lati"],store["longi"],customer_lati,customer_longi)

            cost = fulfilment_cost(fixed_cost=25,cost_per_km=2,distance=distance)

            potential_stores.append({"name": store["name"],"atp": atp,"distance": distance,"cost": cost})

    if not potential_stores:
        return None

    return min(potential_stores,key=lambda x: x["cost"])



# Sample data from HTML dashboard

stores = [{"name": "Hatfield","on_hand": 30,"reserved": 10,"lati": -25.7479,"longi": 28.2293},
          {"name": "Hillcrest Boulevard","on_hand": 21,"reserved": 6,"lati": -25.7540,"longi": 28.2310},
          {"name": "Menlyn Maine","on_hand": 25,"reserved": 5,"lati": -25.7850,"longi": 28.2750},
          {"name": "Equestria","on_hand": 35,"reserved": 12,"lati": -25.7560,"longi": 28.2300},
          {"name": "The Grove","on_hand": 10,"reserved": 4,"lati": -25.7600,"longi": 28.2200}]

# KPI we aim to achieve with this website 

accuracy = inventory_accuracy(correct_records=95,total_records=100)

sub_rate = substitution_rate(substitutions=10,total_orders=100)

cancel_rate = cancellation_rate(cancellations=5,total_orders=100)

success_rate = fulfil_success_rate(fulfilled=85, total_orders=100)


# EOQ calculations

eoq = calculate_eoq(demand=1000, ordering_cost=150, holding_cost=7)

ss = safety_stock(max_daily_demand=30, average_daily_demand=20, lead_time=4)

rop = reorder_point(average_daily_demand=20, lead_time=3, safety_stock=ss)



# Fulfilment example

best_store = select_best_store(stores=stores, order_quantity=10, customer_lati=-25.7500, customer_longi=28.2300)


