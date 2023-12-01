import random

def generate_random_fee() -> float:
    fee_range_start = 2.5
    fee_range_end = 0.25

    # Generate a random fee within the specified range
    fee = random.uniform(fee_range_end, fee_range_start)

    # Round the fee to two decimal places
    fee = round(fee, 2)

    return fee