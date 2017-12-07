from math import radians, cos, sin, asin, sqrt
import numpy as np


class Business:
    """
        If an attribute of a business is ever needed from the clump
        of json attributes, by convention pull it out into its own
        attribute.
    """
    def __init__(self, json_obj, integer_id):
        """

        :param json_obj: the json object that describes a restaurant
        :param integer_id: the unique integer-based id so that we can
        use ids as indices and simplify referential data structures.
        """
        self.integer_id = integer_id
        self.json_attrs = json_obj
        self.latitude = json_obj['latitude']
        self.longitude = json_obj['longitude']
        self.categories = json_obj["categories"]

        # looking at the below link, this looks sufficient. Excludes businesses
        # that only serve alcohol (bars, clubs).
        # https://www.yelp.com/developers/documentation/v3/all_category_list
        self.is_restaurant = "Restaurants" in self.categories
        self.is_food = "Food" in self.categories
        self.rating = json_obj["stars"]
        if "RestaurantsPriceRange2" in json_obj["attributes"]:
            self.price_range = json_obj["attributes"]["RestaurantsPriceRange2"]
        else:
            self.price_range = 0
        self.nearest_neighbors = None
        self.nearest_neighbor = None

    def distance_to(self, other_business):
        """
        :param other_business another Business object to compare distance to
        :return: the distance between the two businesses using the vincenty distance
        """
        return haversine(self.latitude, self.longitude, other_business.latitude, other_business.longitude)

    def find_k_nearest_neighbors(self, k, other_businesses):
        """
        used in large-dataset situations where a complete distance matrix is
        infeasible. Attempts were made to optimize this step.
        :param k: the number of nearest neighbors to find
        :param other_businesses: a list of other businesses to
        search through
        :return: the k nearest neighbors to self
        """
        nearest_neighbors = [None] * k
        nearest_neighbors_dist = np.full(k, np.inf)
        for o in other_businesses:
            dist_between = self.distance_to(o)
            for index, neighbor_dist in enumerate(nearest_neighbors_dist):
                if neighbor_dist > dist_between:
                    nearest_neighbors[index] = o
                    nearest_neighbors_dist[index] = dist_between
                    break
        return nearest_neighbors

    def set_nearest_neighbors(self, nearest_neighbors):
        """
        used in large-dataset situations where a complete distance matrix is
        infeasible.
        :param nearest_neighbors: the neighbors to save
        """
        self.nearest_neighbors = nearest_neighbors

    def find_neighbors_in_radius(self, radius, other_businesses):
        """
        :param radius: in kilometers
        :param other_businesses: the other businesses to find the nearby neighbors in
        """
        neighbors = []
        for o in other_businesses:
            dist_between = self.distance_to(o)
            if dist_between < radius:
                neighbors.append(o)
        return neighbors

# grabbed from
# https://stackoverflow.com/questions/15736995/how-can-i-quickly-estimate-the-distance-between-two-latitude-longitude-points
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers is 6371
    km = 6371 * c
    return km
