from z3 import *
import numpy as np
import heapq

# All extra variables needed.

def all_variables(m, n, li, sj, D):

  # Let's define the minimum of places travelled by all couriers
  # First possiblity : all couriers take at least one item. Then it will remain n-m items.
  # So the max ammount of places travelled by a courier will be n-m (taking all the remaining items) + 1 (taking his/her first item like other couriers) + 1 (the depot)
  # Second possibility : the couriers do not have enough space to take all the remaining items (n-m). Then it will have max_item_per_courier + 1 (the depot)

  sj_sorted = sorted(sj)
  max_li = max(li)
  max_item_per_courier_option_2 = 0
  i = 0
  while max_li >= 0 and i != (len(sj_sorted)) :
    max_li = max_li - sj_sorted[i]
    if max_li < 0:
      max_li = max_li + sj_sorted[i]
      break
    else:
      i = i + 1
      max_item_per_courier_option_2 = max_item_per_courier_option_2 + 1

  max_places_travelled_opt_2 = max_item_per_courier_option_2 + 1
  # Then we take the minimum of the two posssibilities

  max_places_travelled = min(max_places_travelled_opt_2, n - m + 2)

  D_1 = np.array(D)
  # First possibility : the sum of the maximum of each row of the distance's matrix D
  max_distance_per_courier_opt_1 = sum(np.max(row) for row in D_1)

  # Second possibility : the courier can move only max_places_travelled,
  # then we can just take the max_places_travelled + 1 first max distances of the list since we have max_places_travelled places there are max_places_travelled + 1 distances
  max_distance_per_courier_opt_2 = sum(heapq.nlargest(max_places_travelled + 1, D_1.flatten()))
  max_distance_per_courier = min(max_distance_per_courier_opt_1, max_distance_per_courier_opt_2)

  # The routes can be asymetrics, so since the depot is n + 1 in D (python list start from 0 so it is n), we look the minimum of these :
  min_distance_per_courier = min([D[n][i] + D[i][n] for i in range(n)])

  # all_incrementation_variables
  COURIERS = range(m)
  ITEMS = range(n)
  LOCATIONS = range(n+1)
  MAX_PLACES_TRAVELLED = range(max_places_travelled+1)
  MAX_ROAD_TRAVELLED = range(max_places_travelled)


  dict_all_variables = {"m" : m, "n" : n, "li" : li, "sj" : sj, "D" : D,
                   "COURIERS" : COURIERS, "ITEMS" : ITEMS, "LOCATIONS" : LOCATIONS, "MAX_PLACES_TRAVELLED" : MAX_PLACES_TRAVELLED, "MAX_ROAD_TRAVELLED" : MAX_ROAD_TRAVELLED,
                   "max_places_travelled" : max_places_travelled,
                   "max_distance_per_courier" : max_distance_per_courier, "min_distance_per_courier" : min_distance_per_courier
                   }

  return dict_all_variables
