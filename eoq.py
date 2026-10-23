from math import sqrt, radians, sin, cos, asin
# Inventory functions to keep track of demand, stock levels, and discrepancies

def calculate_atp(on_hand, reserved):
    atp = on_hand - reserved
    return atp


def inventory_discrepancy(system_stock, physical_stock):
    discrepancy = system_stock - physical_stock
    return discrepancy


def inventory_accuracy(correct_records, total_records):
    accuracy = (correct_records/total_records) * 100
    return round(accuracy, 2)



# EOQ calclulations to determine optimal order quantities and safety stock levels and if there is enough stock in specific store locations

def calculate_eoq(demand, ordering_cost, holding_cost):
    eoq = round(sqrt((2 * demand * ordering_cost) / holding_cost),2)
    return eoq

def safety_stock(max_daily_demand,average_daily_demand,lead_time):
    safety_stock = (max_daily_demand - average_daily_demand) * lead_time
    return safety_stock


def reorder_point(average_daily_demand,lead_time,safety_stock):
    Rop = (average_daily_demand * lead_time) + safety_stock
    return Rop


# KPI calculations to measure performance and efficiency of the inventory management system

def substitution_rate(substitutions,total_orders):
    sub_rate = (substitutions / total_orders) * 100
    return round(sub_rate,2)


def cancellation_rate(cancellations,total_orders):
    cancel_rate = (cancellations / total_orders) * 100
    return round(cancel_rate,2)


def fulfil_success_rate(fulfilled,total_orders):
    success_rate = (fulfilled / total_orders) * 100
    return round(success_rate,2)

# Distance calculation to measure the distance between store and customer 

def calc_distance(lati1,longi1,lati2,longi2):

    earth_rad = 6371 #Average radius of Earth used to calculate distance between 2 geographical locations in km.

    lati1, longi1, lati2, longi2 = map(radians, [lati1, longi1, lati2, longi2]) #Convert latitude and longitude values from degrees to radians.

    dlati = lati2 - lati1  #Calculate difference between 2 locations in terms of latitude.
    dlongi = longi2 - longi1  #Calculate difference between 2 locations in terms of longitude.

    a = (sin(dlati / 2) ** 2 + cos(lati1) * cos(lati2) * sin(dlongi / 2) ** 2) #Determine the angular distance between customer and store locations

    c = 2 * asin(sqrt(a)) #Calculate the central angle between 2 points
    a_conv = earth_rad* c
    return round(a_conv,2)

# Cost calculation to calculate the cost of the distance between a store and a customer

def fulfilment_cost(fixed_cost,cost_per_km,distance):
    fulfil_cost = round(fixed_cost+ (cost_per_km * distance),2)
    return fulfil_cost
        

# how each store is selected


def select_best_store(stores, order_quantity, customer_lati, customer_longi):

    potential_stores = []

    for store in stores:

        atp = calculate_atp(store["on_hand"], store["reserved"])

        if atp >= order_quantity:

            distance = calc_distance(store["lat"], store["lon"], customer_lati, customer_longi)

            cost = fulfilment_cost(fixed_cost=25, cost_per_km=2,distance=distance)

            candidate_stores.append({

                "name": store["name"],
                "atp": atp,
                "distance": distance,
                "cost": cost

            })

    if not candidate_stores:
        return None

    return min(
        candidate_stores,
        key=lambda x: x["cost"]
    )



# sample data from HTML dashboard

stores = [

    {
        "name": "Hatfield",
        "on_hand": 20,
        "reserved": 5,
        "lat": -25.7479,
        "lon": 28.2293
    },

    {
        "name": "Hillcrest Boulevard",
        "on_hand": 25,
        "reserved": 8,
        "lat": -25.7540,
        "lon": 28.2310
    },

    {
        "name": "Menlyn Maine",
        "on_hand": 18,
        "reserved": 3,
        "lat": -25.7850,
        "lon": 28.2750
    }

]

# KPI calculations

accuracy = inventory_accuracy(correct_records=94,total_records=100)

sub_rate = substitution_rate(substitutions=12,total_orders=100)

cancel_rate = cancellation_rate(cancellations=6,total_orders=100)

success_rate = fulfil_success_rate(fulfilled=82,total_orders=100)


# EOQ calculations


eoq = calculate_eoq(demand=1200,ordering_cost=150,holding_cost=8)

ss = safety_stock(max_daily_demand=30,average_daily_demand=20,lead_time=4)

rop = reorder_point(average_daily_demand=20, lead_time=3, safety_stock=ss)



# Fulfilment example


best_store = select_best_store(stores=stores, order_quantity=10, customer_lati=-25.7500, customer_longi=28.2300)


