import requests
from geopy.geocoders import Nominatim
import json
from math import radians, sin, cos, sqrt, atan2
from BM25 import BM25Ranker  
import time
from collections import defaultdict
import nltk
import ast
import tkinter as tk
from tkinter import scrolledtext
import re
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from difflib import get_close_matches


class RestaurantConcierge:
# 80km = 50 mile
    def __init__(self, distance = 82,ip_address='', filepath = 'yelp_dataset'):
        self.ip_address = ip_address
        self.filepath = filepath
        self.filepath_business = self.filepath + '/yelp_academic_dataset_business.json'
        self.filepath_review = self.filepath + '/yelp_academic_dataset_review.json'
        self.review_data = None
        self.review_data_inlocation = None
        self.business_withinLocation = None
        self.business_data = None
        self.ids_inLocation = []
        self.distance = distance


    # set up distance if need
    def set_distance(self, distance):
        self.distance = distance

    # get the address by the user ip address, return lat, long
    def get_address_by_ip(self):
        try:
            # If no IP address is provided, use the user's current IP address
            if not self.ip_address:
                self.ip_address = requests.get('https://api64.ipify.org?format=json').json().get('ip', '')

            # Make a request to ipinfo.io to get information about the specified IP address
            response = requests.get(f'https://ipinfo.io/{self.ip_address}')
            
            # Parse the JSON response
            data = response.json()

            # Extract location information
            loc_str = data.get('loc', 'Unknown')

            # Split the coordinates and return as a tuple (latitude, longitude)
            lat, long = loc_str.split(',')
            return float(lat), float(long)
        except Exception as e:
            return {'error': str(e)}
        
    # get city name by current ip
    def get_location_by_ip(self):
        try:
            # Make a request to ipinfo.io to get information about your IP address
            response = requests.get('https://ipinfo.io')
            
            # Parse the JSON response
            data = response.json()

            # Extract location information
            city = data.get('city', 'Unknown')
            region = data.get('region', 'Unknown')
            country = data.get('country', 'Unknown')
            location = f'{city}, {region}, {country}'

            return location
        except Exception as e:
            return f'Error: {str(e)}'
        
    # get lat and long by the address
    def get_lat_long_by_addr(self, address):
        try:
            geolocator = Nominatim(user_agent="my_geocoder")
            location = geolocator.geocode(address)

            if location:
                latitude = location.latitude
                longitude = location.longitude
                return latitude, longitude
            else:
                return None
        except Exception as e:
            print(f'"get_lat_long_by_addr" error out, There is error when getting loaction by address: {e}')
    
    # read the yelp json file return the data
    def read_yelp_data(self, file_path = ''):
        if file_path == '':
            file_path = self.filepath_business
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.business_data = [json.loads(line) for line in file]

            return self.business_data
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {str(e)}")
            return None

    # get lat long from data set for each business calculate the distanct for the address, passing distanct is the dist we want to filter, and user_location = [lat,long] that user located.
    def get_business_within_distance(self, data, user_location):
        try:
            businesses_within_distance = []
            c = 0
            for business in data:
                latitude = business.get('latitude')
                longitude = business.get('longitude')
                
                # Calculate distance between user location and business location
                business_distance = self.cal_distance(user_location, [latitude, longitude])
                
                # Check if the business is within the specified distance
                if business_distance <= self.distance:
                    c += 1
                    business_with_distance = business.copy()
                    business_with_distance['distance'] = business_distance
                    self.ids_inLocation.append(business_with_distance['business_id'])
                    businesses_within_distance.append(business_with_distance)
            
            print(f'Total count for match: {c}')

            ##########################
            ########

            business_expect_min =10
            business_exxpect_max = 20
            # Adjust self.distance based on the count
            if c <= business_expect_min and self.distance < 150:
                # If count is 0, increase self.distance by a certain amount
                self.distance += 0.1
                print(f'No businesses found within the current distance. Increasing distance to {self.distance}.')
                return self.get_business_within_distance(data, user_location)
            
            elif c > business_exxpect_max and self.distance < 150:
                # If count is more than business_exxpect_max, decrease self.distance by a certain amount
                self.distance -= 0.1
                print(f'More than {business_exxpect_max} businesses found within the current distance. Decreasing distance to {self.distance}.')
                return self.get_business_within_distance(data, user_location)
            
            elif c < 10 and self.distance >= 150:
                # the case if business do not have 10 within distance
                print(f'That is all business found within {self.distance} km')
                return businesses_within_distance
            elif c <= 0 and self.distance >= 150:
                print(f'No business found near by.')
                return
            else:
                # If count is within the desired range, update self.business_withinLocation and return the result
                self.business_withinLocation = businesses_within_distance
                return businesses_within_distance
        except Exception as e:
            print(f'get_business_within_distance error with msg: {e}')


    # calculate distance by 2 point( lat and long) so addr1 and addr2 should be passing as [lat, long], return distanct in Km
    def cal_distance(self, addr1, addr2):
        try:
            # Convert latitude and longitude from degrees to radians
            lat1, lon1 = radians(addr1[0]), radians(addr1[1])
            lat2, lon2 = radians(addr2[0]), radians(addr2[1])
            # Differences in coordinates
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            # Haversine formula
            a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))

            # Radius of the Earth in kilometers
            R = 6371.0

            # Calculate the distance
            distance = R * c

            return distance
        except Exception as e:
            print(f'cal_distance error out: {e}')

    # get review from review dataset, set it to self val
    def get_review_data(self):
        try:
            file_path = self.filepath_review
            #print(file_path)
            with open(file_path, 'r', encoding='utf-8') as file:
                self.review_data = [json.loads(line) for line in file]
                self.review_data_inlocation = [review for review in self.review_data if review.get('business_id') in self.ids_inLocation]
            print("Done fetching review datas")
            return self.review_data
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {str(e)}")
            return None
        
    def find_similar_words(self,keyword, text):

        similar_words = None
        # Get close matches
        if keyword:
            # Get all words from WordNet
            all_words = set(word for synset in wordnet.all_synsets() for word in synset.lemma_names())
            words = word_tokenize(text.lower())
            similar_words = get_close_matches(keyword.lower(), all_words)
            
            # Filter out words that are already in the text
            similar_words = [word for word in similar_words if word not in words]
        
        return similar_words

    ###TODO: return result base on the query input(taco should return business related to taco)
    # get rank function
    def get_rank(self, keyword, weight_bm25=0.7, weight_stars=0.5, weight_useful=0.33, weight_funny=0.05, weight_cool=0.05):
        try:
            # download package incase first time run
            nltk.download('wordnet')

            queries = ['Excellent', 'Outstanding', 'Superb', 'Exceptional', 'Amazing',
                            'Delicious', 'Fantastic', 'Wonderful', 'Terrific', 'Great',
                            'Impressive', 'Outstanding', 'Marvelous', 'Exceptional', 'Top-notch',
                            'High-quality', 'Delectable', 'Tasty', 'Yummy', 'Superlative'
                        ]
            if self.review_data is None:
                print("Review data is not loaded. Call 'get_review_data' first.")
                return

            # Extract review text and relevant features from the review data
            user_reviews_with_features = [
                {
                    'text': review.get('text', ''),
                    'business_id': review.get('business_id', ''),
                    'stars': review.get('stars', 0),
                    'useful': review.get('useful', 0),
                    'funny': review.get('funny', 0),
                    'cool': review.get('cool', 0)
                } for review in self.review_data_inlocation
            ]

            # Create a BM25Ranker instance using user reviews
            bm25_ranker = BM25Ranker([review['text'] for review in user_reviews_with_features])

            # Rank businesses based on the combined score for all queries
            combined_scores = defaultdict(lambda: {'bm25_score': 0.0, 'stars': 0, 'useful': 0, 'funny': 0, 'cool': 0})
            for query in queries:
                # Calculate BM25 scores for each query
                bm25_scores = bm25_ranker.rank_documents(query)

                # Combine scores for all queries
                for index, bm25_score in bm25_scores:
                    # Aggregate scores for each unique business_id
                    business_id = user_reviews_with_features[index]['business_id']
                    combined_scores[business_id]['bm25_score'] += bm25_score
                    combined_scores[business_id]['stars'] += user_reviews_with_features[index]['stars']
                    combined_scores[business_id]['useful'] += user_reviews_with_features[index]['useful']
                    combined_scores[business_id]['funny'] += user_reviews_with_features[index]['funny']
                    combined_scores[business_id]['cool'] += user_reviews_with_features[index]['cool']

            # Normalize scores (optional)
            max_bm25_score = max(score['bm25_score'] for score in combined_scores.values())
            for business_id in combined_scores:
                combined_scores[business_id]['bm25_score'] /= max_bm25_score

            # Calculate the relevance percentage for each result based on the keyword
            for business_id in combined_scores:
                review_text = next((review['text'] for review in user_reviews_with_features if review['business_id'] == business_id), '')  
                if keyword is None or len(keyword) <= 1:
                    combined_scores[business_id]['relevance_percentage'] = 0
                    combined_scores[business_id]['combined_score'] = (
                            weight_bm25 * combined_scores[business_id]['bm25_score'] +
                            weight_stars * combined_scores[business_id]['stars'] +
                            weight_useful * combined_scores[business_id]['useful'] +
                            weight_funny * combined_scores[business_id]['funny'] +
                            weight_cool * combined_scores[business_id]['cool'])
                    
                    
                else:
                    # Use regular expressions to find occurrences of the keyword and similar words
                    keyword_occurrences = len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', review_text.lower()))
                    
                    # Use NLTK to find similar words
                    similar_words_occurrences = len(self.find_similar_words(keyword, review_text))

                    total_words = len(word_tokenize(review_text))
                    relevance_percentage = ((keyword_occurrences + similar_words_occurrences) / total_words) * 100
                    combined_scores[business_id]['relevance_percentage'] = relevance_percentage
                    combined_scores[business_id]['combined_score'] = (
                            weight_bm25 * combined_scores[business_id]['bm25_score'] +
                            weight_stars * combined_scores[business_id]['stars'] +
                            weight_useful * combined_scores[business_id]['useful'] +
                            weight_funny * combined_scores[business_id]['funny'] +
                            weight_cool * combined_scores[business_id]['cool'])


            # Sort businesses based on the combined scores
            ranked_businesses = sorted(
                combined_scores.items(),
                key=lambda x: x[1]['combined_score'],
                reverse=True
            )
            keyword_percentage = defaultdict(lambda: 0.0)
            for index, review in enumerate(user_reviews_with_features):
                if keyword.lower() in review['text'].lower():
                    business_id = review['business_id']
                    keyword_percentage[business_id] += 1.0
            total_reviews_for_business = len([review for review in user_reviews_with_features if review['business_id'] == business_id])
            max_keyword_count = max(keyword_percentage.values())
            for business_id in keyword_percentage:
                keyword_percentage[business_id] /= max_keyword_count
                keyword_percentage[business_id] /= total_reviews_for_business
                keyword_percentage[business_id] *= 100  # Convert to percentage


            # Extract the relevant information for the result
            ranked_businesses_info = []
            for business_id, score in ranked_businesses:
                business_info = self.fetch_business_name(business_id)

                if business_info:
                    is_open_status = 'open' if business_info.get('is_open', 0) == 1 else 'closed'
                    combined_address = ' '.join(filter(None, [
                        business_info.get('address', ''),
                        business_info.get('city', ''),
                        business_info.get('state', ''),
                        business_info.get('postal_code', '')
                    ]))

                    # Construct the location string
                    latitude = business_info.get('latitude')
                    longitude = business_info.get('longitude')
                    location_str = (
                        f'latitude: {latitude}, longitude: {longitude}'
                        if latitude is not None and longitude is not None
                        else ''
                    )

                    # Extract the 'GoodForMeal' attribute from the 'attributes' dictionary
                    arrt_Ambience = None
                    type_arrt = None
                    all_attribute = business_info.get('attributes', {})
                    if all_attribute:
                        arrt_Ambience = all_attribute.get('Ambience', {})
                        type_arrt = all_attribute.get('GoodForMeal', {})

                    # Get the relevance percentage for the current business
                    if keyword is None or len(keyword) < 1:
                        relevance_percentage = 0
                    else:
                        relevance_percentage = keyword_percentage.get(business_id, 0.0)

                    # Check if 'combined_score' key is present in the score dictionary
                    combined_score = score.get('combined_score', 0.0)
                    combined_score = combined_score/1000

                    ranked_business = {
                        'name': business_info.get('name', ''),
                        'business_id': business_id,
                        'combined_score': combined_score,
                        'address': combined_address,
                        'location': location_str,
                        'is_open': is_open_status,
                        'categories': business_info.get('categories'),
                        'stars': business_info.get('stars'),
                        'hours': business_info.get('hours', {}),
                        'details': all_attribute,
                        'Ambience': arrt_Ambience,
                        'type': type_arrt,
                        'relevance_percentage': relevance_percentage,  # Add relevance percentage to the dictionary
                        # Add other business info fields as needed
                    }

                    ranked_businesses_info.append(ranked_business)
                
                else:
                    print(f"Skipping business with ID {business_id} because business_info is None.")
            return ranked_businesses_info
        except Exception as e:
            print(f'get_rank error out: {e}')



    # fetch the business name and address by business_id
    def fetch_business_name(self, business_id):
        try:
            if self.business_data is None:
                print(f'Ohhh, looks like business_data(yelp_academic_dataset_business) are not loaded yet.')
                return
            
            # Iterate through stored data to find the business with the specified business_id
            for business in self.business_data:
                if business.get('business_id') == business_id:
                    # Found the business, add all fields to the result
                    return business

        # If business_id is not found in the stored data
            print(f"No business found with business_id: {business_id}")
            return None
        
        except Exception as e:
            print(f'Error fetching business info by business_id: {e}')
            return None

    # main process for getting everything
    def run_main(self, keyword = "", addr=None):
        try:
            if addr is None:
                location = self.get_address_by_ip()
                if location is None:
                    print("Unable to determine current location. Exiting.")
                    return
                self.get_business_within_distance(self.business_data, location)
            else:
                location = self.get_lat_long_by_addr(addr)
                if location is None:
                    print(f"Unable to find location for address: {addr}. Exiting.")
                    return
                self.get_business_within_distance(self.business_data, location)
            
            start_time = time.time()
            self.get_review_data()
            end_time = time.time()
            ranked_businesses = self.get_rank(keyword)
            if ranked_businesses is None:
                print('Cannot find the result in your area')
                print('\n', 'Program Done')
            else:
                for res in ranked_businesses[:10]:
                    print(res)
                    print('\n')
            # Calculate the elapsed time
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            print('done')
            print(f"Time taken: {elapsed_time} seconds for main process")
            return ranked_businesses[:10]
        except Exception as e:
            print(f"An error occurred: {e}")




if __name__ == "__main__":
    print("Choose an option to get recommendations:")
    print("1. Using location from the current address")
    print("2. Inserting an address")
    print("0. Exit")

    try:
        option = int(input("Enter the number corresponding to your choice: "))
        concierge = RestaurantConcierge()
        business_data = concierge.read_yelp_data()
        if option == 1:
            concierge.run_main()
            
        elif option == 2:
            address_insert = input("Enter the address you want to search: ")
            concierge.run_main(address_insert)
            
        elif option == 0:
            print('program will exit...see yall')
            exit()
        else:
            print("Invalid option. Please enter 1, 2, or 0.")

    except ValueError:
        print("Invalid input. Please enter a valid number.")
    except Exception as e:
        print(f"Error: {e}")




