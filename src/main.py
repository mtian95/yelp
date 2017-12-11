import json
import numpy as np
import time
from scipy.stats.stats import pearsonr
import scipy
import math
import matplotlib.pyplot as plt

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


def load_nearby_neighbors_for_businesses(source_array, target_array):
    for business in source_array:
        nearest_neighbors = business.find_neighbors_in_radius(.4, target_array)
        business.set_nearest_neighbors(nearest_neighbors)


def get_k_random_businesses(k, business_array):
    rand_array = np.random.rand(k)
    rand_businesses = []
    for i in range(0, k):
        rand_business_index = int(round(rand_array[i]*len(business_array)))
        rand_businesses.append(business_array[rand_business_index])
    return rand_businesses


def analyze_rating_vs_neighbors(business_array, categories=None):
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
            if category == "Restaurants" or category == "Food" or (categories and category not in categories):
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
    category_with_averages = {}
    for category in category_counts:
        similar_nearby_sum = 0
        for inner_sum in category_counts[category]:
            similar_nearby_sum += inner_sum
        average_similar_neighbors = similar_nearby_sum*1.0 / len(category_counts[category])
        category_with_averages[category] = average_similar_neighbors
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
    display_average_category_overlap(category_with_averages)
    display_mean_with_error(master_category_counts, master_category_ratings)


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


def parse_businesses_for_vegas(b_array):
    return_array = []
    for b in b_array:
        if b.city == "Las Vegas" or b.city == "las vegas":
            return_array.append(b)
    return return_array


def analyze_dollars_to_ratings(b_array):
    dollars = []
    ratings = []
    for b in b_array:
        if b.price_range:
            dollars.append(b.price_range)
            ratings.append(b.rating)
    display_dollars_to_ratings(dollars, ratings)

# display stuff


def display_average_distances_for_businesses(b_array):
    averages = []
    for business in b_array:
        nn_sum = 0
        for neighbor in business.nearest_neighbors:
            nn_sum += business.distance_to(neighbor)
        averages.append(nn_sum/len(business.nearest_neighbors))

    plt.hist(averages)
    plt.title("Distribution of Average Distance of 40 Nearest Neighbors")
    plt.xlabel("Average distance (km)")
    plt.ylabel("Number of Restaurants (1000 total)")
    plt.show()


def display_average_category_overlap(categories_to_average_similar_neighbors, n=20):
    plt.hist(categories_to_average_similar_neighbors.values())
    plt.title("Distribution of Average Nearby Similar Neighbors")
    plt.xlabel("Average Nearby Similar Neighbors")
    plt.ylabel("Number of Categories")
    plt.show()

    # also figure out the top n categories
    categories_with_counts = [(category, categories_to_average_similar_neighbors[category]) for category in categories_to_average_similar_neighbors]
    sorted_categories_with_counts = sorted(categories_with_counts, key=lambda x: x[1], reverse=True)
    print sorted_categories_with_counts[0:n]
    return sorted_categories_with_counts[0:n]


def display_mean_with_error(list_o_similarity_counts, list_o_ratings):
    count_to_ratings = {}
    for count, rating in zip(list_o_similarity_counts, list_o_ratings):
        if count in count_to_ratings:
            count_to_ratings[count].append(rating)
        else:
            count_to_ratings[count] = [rating]

    counts = []
    average_ratings = []
    ses = []
    for count in sorted(count_to_ratings.keys()):
        arr = np.array(count_to_ratings[count])
        counts.append(count)
        average_ratings.append(np.mean(arr))
        ses.append(scipy.stats.sem(arr))

    plt.plot(counts, average_ratings)

    plt.title("Average Stars per Amount of Similar Nearby Restaurants")
    plt.xlabel("Amount of Similar Nearby Restaurants")
    plt.ylabel("Average Stars")
    plt.fill_between(counts, np.array(average_ratings)-np.array(ses),
                     np.array(average_ratings)+np.array(ses), alpha=.5)

    plt.show()


def display_dollars_to_ratings(list_o_dollars, list_o_ratings):
    buckets = [(1, 1.5), (1.5, 2), (2, 2.5), (2.5, 3), (3, 3.5), (3.5, 4)]

    bucket_sums = {}
    for dollar, rating in zip(list_o_dollars, list_o_ratings):
        for low, high in buckets:
            if high >= dollar >= low:
                if low in bucket_sums:
                    bucket_sums[low].append(rating)
                else:
                    bucket_sums[low] = [rating]
    x_labels = [1.25, 1.75, 2.25, 2.75, 3.25, 3.75]
    means = []
    ses = []
    for bucket in bucket_sums:
        arr = np.array(bucket_sums[bucket])
        means.append(np.mean(arr))
        ses.append(scipy.stats.sem(arr))

    plt.plot(x_labels, means)

    plt.title("Average Stars per Average Neighbor Dollar Rating")
    plt.xlabel("Average Neighbor Dollar Rating")
    plt.ylabel("Average Stars")
    plt.fill_between(x_labels, np.array(means)-np.array(ses),
                     np.array(means)+np.array(ses), alpha=.5)

    plt.show()



