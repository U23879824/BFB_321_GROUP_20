from math import sqrt, radians, sin, cos, asin

# ==================================================
# INVENTORY FUNCTIONS
# ==================================================

def calculate_atp(on_hand, reserved):
    return on_hand - reserved


def inventory_discrepancy(system_stock, physical_stock):
    return system_stock - physical_stock


def inventory_accuracy(correct_records, total_records):
    return round((correct_records / total_records) * 100, 2)


# ==================================================
# EOQ FUNCTIONS
# ==================================================

def calculate_eoq(demand, ordering_cost, holding_cost):

    return round(
        sqrt(
            (2 * demand * ordering_cost)
            / holding_cost
        ),
        2
    )


def safety_stock(
        max_daily_demand,
        average_daily_demand,
        lead_time):

    return (
        max_daily_demand
        - average_daily_demand
    ) * lead_time


def reorder_point(
        average_daily_demand,
        lead_time,
        safety_stock_units):

    return (
        average_daily_demand
        * lead_time
    ) + safety_stock_units


# ==================================================
# KPI FUNCTIONS
# ==================================================

def substitution_rate(
        substitutions,
        total_orders):

    return round(
        (substitutions / total_orders) * 100,
        2
    )


def cancellation_rate(
        cancellations,
        total_orders):

    return round(
        (cancellations / total_orders) * 100,
        2
    )


def fulfilment_success_rate(
        fulfilled,
        total_orders):

    return round(
        (fulfilled / total_orders) * 100,
        2
    )


# ==================================================
# DISTANCE CALCULATION
# ==================================================

def calc_distance(
        lat1,
        lon1,
        lat2,
        lon2):

    earth_radius = 6371

    lat1, lon1, lat2, lon2 = map(
        radians,
        [lat1, lon1, lat2, lon2]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * asin(sqrt(a))

    return round(
        earth_radius * c,
        2
    )


# ==================================================
# COST FUNCTION
# ==================================================

def fulfilment_cost(
        fixed_cost,
        cost_per_km,
        distance):

    return round(
        fixed_cost
        + (cost_per_km * distance),
        2
    )


# ==================================================
# STORE SELECTION
# ==================================================

def select_best_store(
        stores,
        order_quantity,
        customer_lat,
        customer_lon):

    candidate_stores = []

    for store in stores:

        atp = calculate_atp(
            store["on_hand"],
            store["reserved"]
        )

        if atp >= order_quantity:

            distance = calc_distance(
                store["lat"],
                store["lon"],
                customer_lat,
                customer_lon
            )

            cost = fulfilment_cost(
                fixed_cost=25,
                cost_per_km=2,
                distance=distance
            )

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


# ==================================================
# SAMPLE DATA FROM HTML DASHBOARD
# ==================================================

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


# ==================================================
# KPI CALCULATIONS
# ==================================================

accuracy = inventory_accuracy(
    correct_records=94,
    total_records=100
)

sub_rate = substitution_rate(
    substitutions=12,
    total_orders=100
)

cancel_rate = cancellation_rate(
    cancellations=6,
    total_orders=100
)

success_rate = fulfilment_success_rate(
    fulfilled=82,
    total_orders=100
)


# ==================================================
# EOQ CALCULATIONS
# ==================================================

eoq = calculate_eoq(
    demand=1200,
    ordering_cost=150,
    holding_cost=8
)

ss = safety_stock(
    max_daily_demand=30,
    average_daily_demand=20,
    lead_time=4
)

rop = reorder_point(
    average_daily_demand=20,
    lead_time=3,
    safety_stock_units=ss
)


# ==================================================
# FULFILMENT EXAMPLE
# ==================================================

best_store = select_best_store(
    stores=stores,
    order_quantity=10,
    customer_lat=-25.7500,
    customer_lon=28.2300
)


# ==================================================
