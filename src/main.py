import json
import numpy as np
import time

from Business import Business


def load_businesses(restaurant_only=True, path="../../dataset/business.json"):
    """
    :param restaurant_only: mark False if you want to load all businesses,
        true if you want to load only food & drink establishments
    :param path: the path to wherever you've saved business.json
    :return: an array of the loaded businesses
    """

    line_count = 0
    business_array = []
    with open(path, "rb") as f:
        for line in f:
            business_data = json.loads(line)
            business = Business(business_data, line_count)
            if restaurant_only and business.is_restaurant:
                business_array.append(business)
                line_count += 1
    return business_array


def load_business_distance_matrix(business_array):
    """
    Note: Can't be used on the whole data set, requires too much RAM :(
    (~12GB for all restaurants). Use Business.get_nearest_neighbors instead
    :param business_array: the array of businesses to make a distance
        matrix from
    :return: the distance matrix
    """
    len_b_array = len(business_array)
    distance_matrix = np.zeros((len_b_array, len_b_array))
    for i in range(0, len_b_array):
        for j in range(i, len_b_array):
            distance_matrix[i, j] = business_array[i].distance_to(business_array[j])
            distance_matrix[j, i] = distance_matrix[i, j]
    return distance_matrix


def load_k_neighbors_for_businesses(k, source_array, target_array):
    """
    sets k nearest neighbors for all businesses in the given array.
    Takes ~15 hours when k=100 (~4 when k=1) and len of source_array = target_array = 65000.
    Because of this I advise selecting a subset for the source_array.
    Takes ~8 minutes when k=40, source_array = 1000, target_array = 65000.
    :param k: the amount of nearest neighbors to compute
    :param source_array: the businesses to find neighbors for
    :param target_array: the businesses to use when finding neighbors
    """
    for business in source_array:
        nearest_neighbors = business.find_k_nearest_neighbors(k, target_array)
        business.set_nearest_neighbors(nearest_neighbors)


def get_k_random_businesses(k, business_array):
    rand_array = np.random.rand(k)
    rand_businesses = []
    for i in range(0, k):
        rand_business_index = int(round(rand_array[i]*len(business_array)))
        rand_businesses.append(business_array[rand_business_index])
    return rand_businesses


if __name__ == "__main__":
    t0 = time.time()
    b_array = load_businesses()
    t_post_loading_businesses = time.time()
    # takes ~5 seconds
    random_selected_businesses = get_k_random_businesses(1000, b_array)
    print "loading businesses: {} seconds".format(t_post_loading_businesses-t0)
    load_k_neighbors_for_businesses(40, random_selected_businesses, b_array)
    t_post_loading_neighbors = time.time()
    # takes ~8 minutes
    print "loading distance matrix: {} seconds".format(t_post_loading_businesses-t_post_loading_neighbors)
    import ipdb; ipdb.set_trace()
