# Calculate factorial using loop only
from codecarbon import track_emissions
import time
import sys
import math
sys.set_int_max_str_digits(1000000000)

@track_emissions()

def factorial(n):
    if n < 0:
        return None

    t = time.time()
    result = math.factorial(n)
    print(time.time() - t, "seconds")

    return result

factorial(600000)  # This will take a long time and consume a lot of memory
# Example usage
# print(factorial(6000))
