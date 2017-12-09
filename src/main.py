import json
import numpy as np
import time
from scipy.stats.stats import pearsonr
import math

from Business import Business


def load_businesses(restaurant_only=True, path="../../dataset/business.json"):
    """
    :param restaurant_only: mark False if you want to load all businesses,
        true if you want to load only restaurants
    :param path: the path to wherever you've saved business.json
    :return: an array of the loaded businesses
    """

    line_count = 0
    business_array = []
    with open(path, "rb") as f:
        for line in f:
            business_data = json.loads(line)
            business = Business(business_data, line_count)
            if not restaurant_only or business.is_restaurant:
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

    Efficiency:
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


def analyze_rating_vs_neighbors(business_array):
    """
    requires business_array to be all restaurants or food establishments.
    nearest neighbors must have already been computed.

    Efficiency:
    This runs in O(n^2*c*k), where k is the number of neighbors and c is
    the number of categories.
    For n=1000 and k=40, this takes ~0 minutes

    :param business_array: an array of businesses
    :return: prints out various statistics
    """
    category_counts = {}
    category_ratings = {}
    for b in business_array:
        for category in b.categories:
            if category == "Restaurants" or category == "Food":
                continue
            count = count_category_occurence_in_businesses(category, b.nearest_neighbors)
            if category in category_counts:
                category_counts[category].append(count)
                category_ratings[category].append(b.rating)
            else:
                category_counts[category] = [count]
                category_ratings[category] = [b.rating]

    total_sum = 0
    count = 0
    for sums in category_counts.values():
        for inner_sum in sums:
            count += 1
            total_sum += inner_sum
    print "Average neighbor category overlap: {}".format(total_sum*1.0/count)

    high_similarity_category_counts = []
    high_similarity_category_ratings = []
    for category in category_counts:
        similar_nearby_sum = 0
        for inner_sum in category_counts[category]:
            similar_nearby_sum += inner_sum
        average_similar_neighbors = similar_nearby_sum*1.0 / len(category_counts[category])
        print "average neighbor overlap for category {}: {}".format(category, average_similar_neighbors)

        if average_similar_neighbors < 3.:
            high_similarity_category_counts.extend(category_counts[category])
            high_similarity_category_ratings.extend(category_ratings[category])

    for category in category_counts:
        correlation = pearsonr(category_counts[category], category_ratings[category])
        print "correlation coefficient for category {}: {}"\
            .format(category, correlation)

    master_category_counts = []
    master_category_ratings = []
    for category in category_counts:
        master_category_counts.extend(category_counts[category])
        master_category_ratings.extend(category_ratings[category])
    total_correlation = pearsonr(master_category_counts, master_category_ratings)
    print "category-independent correlation: {}".format(total_correlation)

    similar_neighbors_correlation = pearsonr(high_similarity_category_counts, high_similarity_category_ratings)
    print "high similarity correlation: {}".format(similar_neighbors_correlation)
    import ipdb; ipdb.set_trace()


def count_category_occurence_in_businesses(category, business_array):
    """
    Given a category, finds out how many businesses match that category
    :param category: the category so search for
    :param business_array: the businesses to search
    :return: the count of the amount of businesses that match the category
    in the array
    """
    category_count = 0
    for b in business_array:
        for c in b.categories:
            if c == category:
                category_count += 1
                break
    return category_count


if __name__ == "__main__":
