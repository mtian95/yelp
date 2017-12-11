import numpy as np
import time

from Business import Business
import main


def analyze_national_correlation():
    t0 = time.time()
    b_array = main.load_businesses()
    t_post_loading_businesses = time.time()
    random_selected_businesses = main.get_k_random_businesses(1000, b_array)
    # takes ~5 seconds
    print "loading businesses: {} seconds".format(t_post_loading_businesses-t0)
    main.load_k_neighbors_for_businesses(40, random_selected_businesses, b_array)
    main.display_average_distances_for_businesses(random_selected_businesses)
    t_post_loading_neighbors = time.time()
    # takes ~8 minutes
    print "loading distance matrix: {} seconds".format(t_post_loading_neighbors - t_post_loading_businesses)
    main.analyze_rating_vs_neighbors(random_selected_businesses)
    # average neighbor category overlap: ~4
    # correlation over all categories: ~.08 (with really low p val)
    # correlation over categories with an average of >3. neighbors: ~0 with high p
    # correlation over categories with an average of <3. neighbors: ~.08 with low p
    t_post_analysis = time.time()
    print "neighbor rating analysis: {} seconds".format(t_post_analysis - t_post_loading_neighbors)


def analyze_vegas_correlation():
    t0 = time.time()
    b_array = main.load_businesses()
    vegas_array = main.parse_businesses_for_vegas(b_array)
    t_post_loading_businesses = time.time()
    # random_selected_businesses = main.get_k_random_businesses(1000, vegas_array)
    # takes ~5 seconds
    print "loading businesses: {} seconds".format(t_post_loading_businesses-t0)
    main.load_k_neighbors_for_businesses(40, vegas_array, vegas_array)
    # main.load_nearby_neighbors_for_businesses(vegas_array, vegas_array)
    main.display_average_distances_for_businesses(vegas_array)
    t_post_loading_neighbors = time.time()
    # takes ~8 minutes
    print "loading distance matrix: {} seconds".format(t_post_loading_neighbors - t_post_loading_businesses)
    main.analyze_rating_vs_neighbors(vegas_array)
    # average neighbor category overlap: ~4
    # correlation over all categories: ~.08 (with really low p val)
    # correlation over categories with an average of >3. neighbors: ~0 with high p
    # correlation over categories with an average of <3. neighbors: ~.08 with low p
    t_post_analysis = time.time()
    print "neighbor rating analysis: {} seconds".format(t_post_analysis - t_post_loading_neighbors)
    """[(u'Fast Food', 6.872491145218418), (u'Mexican', 6.625690607734807), 
    (u'American (Traditional)', 6.2882273342354535), (u'Nightlife', 5.790575916230367), 
    (u'Bars', 5.518055555555556), (u'Chinese', 5.431707317073171), 
    (u'American (New)', 5.331531531531532), (u'Sandwiches', 4.913322632423756), 
    (u'Pizza', 4.778534923339012), (u'Burgers', 4.336633663366337), 
    (u'Japanese', 4.113846153846154), (u'Italian', 3.789189189189189), 
    (u'Breakfast & Brunch', 3.5025641025641026), (u'Asian Fusion', 3.3522267206477734), 
    (u'Seafood', 3.220779220779221), (u'Street Vendors', 3.0), 
    (u'Steakhouses', 2.9675925925925926), (u'Vietnamese', 2.9545454545454546), 
    (u'Sushi Bars', 2.938775510204082), (u'Food Trucks', 2.8780487804878048)]

"""


def analyze_vegas_correlation_with_top_restaurant_types():
    categories_of_study = [u'Fast Food', u'Mexican', u'American (Traditional)',
                           u'Chinese', u'American (New)', u'Sandwiches', u'Pizza',
                           u'Burgers', u'Japanese', u'Italian', u'Breakfast & Brunch',
                           u'Asian Fusion', u'Seafood', u'Steakhouses', u'Vietnamese',
                           u'Sushi Bars']

    b_array = main.load_businesses()
    vegas_array = main.parse_businesses_for_vegas(b_array)
    main.load_k_neighbors_for_businesses(40, vegas_array, vegas_array)
    main.analyze_rating_vs_neighbors(vegas_array, categories=categories_of_study)


def analyze_vegas_pricing():
    b_array = main.load_businesses()
    vegas_array = main.parse_businesses_for_vegas(b_array)
    main.load_k_neighbors_for_businesses(40, vegas_array, vegas_array)
    main.analyze_dollars_to_ratings(vegas_array)


if __name__ == "__main__":
    np.random.seed(12345)
    # analyze_vegas_correlation()
    analyze_vegas_pricing()

