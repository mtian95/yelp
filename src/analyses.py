import numpy as np
import time

from Business import Business
import main


def analyze_national_correlation():
    t0 = time.time()
    b_array = main.load_businesses()
    t_post_loading_businesses = time.time()
    random_selected_businesses =main.get_k_random_businesses(1000, b_array)
    # takes ~5 seconds
    print "loading businesses: {} seconds".format(t_post_loading_businesses-t0)
    main.load_k_neighbors_for_businesses(40, random_selected_businesses, b_array)
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


if __name__ == "__main__":
    np.random.seed(12345)
    analyze_national_correlation()
