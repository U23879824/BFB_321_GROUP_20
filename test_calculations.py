from eoq import *

def test_calculate_atp():
    assert calculate_atp(20, 5) == 15

def test_inventory_discrepancy():
    assert inventory_discrepancy(100, 95) == 5

def test_inventory_accuracy():
    assert inventory_accuracy(94, 100) == 94.0

def test_calculate_eoq():
    assert calculate_eoq(1200, 150, 8) == 212.13

def test_safety_stock():
    assert safety_stock(30, 20, 4) == 40

def test_reorder_point():
    assert reorder_point(20, 3, 40) == 100

def test_substitution_rate():
    assert substitution_rate(12, 100) == 12.0

def test_cancellation_rate():
    assert cancellation_rate(6, 100) == 6.0


# ==========================================
# UNIT TESTS
# ==========================================

print("\n===== UNIT TEST RESULTS =====")

print(
    "ATP Test:",
    calculate_atp(20, 5) == 15
)

print(
    "Inventory Discrepancy Test:",
    inventory_discrepancy(100, 95) == 5
)

print(
    "Inventory Accuracy Test:",
    inventory_accuracy(94, 100) == 94.0
)

print(
    "EOQ Test:",
    calculate_eoq(1200, 150, 8) == 212.13
)

print(
    "Safety Stock Test:",
    safety_stock(30, 20, 4) == 40
)

print(
    "Reorder Point Test:",
    reorder_point(20, 3, 40) == 100
)

print(
    "Substitution Rate Test:",
    substitution_rate(12, 100) == 12.0
)

print(
    "Cancellation Rate Test:",
    cancellation_rate(6, 100) == 6.0
)

print(
    "Fulfilment Success Rate Test:",
    fulfil_success_rate(82, 100) == 82.0
)

print(
    "Fulfilment Cost Test:",
    fulfilment_cost(25, 2, 10) == 45
)