# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, mock_open,Mock
from restaurant_concierge import RestaurantConcierge
import BM25

class TestRestaurantConcierge(unittest.TestCase):
    def setUp(self):
        # Initialize the RestaurantConcierge instance with test data or mock data
        self.concierge = RestaurantConcierge(distance=10, filepath='test_data')

    def test_get_address_by_ip(self):
        # Mock the response from the IP address API
        with patch('restaurant_concierge.requests.get') as mock_get:
            mock_get.return_value.json.return_value = {'ip': '127.0.0.1', 'loc': '40.7128,-74.0060'}
            result = self.concierge.get_address_by_ip()
            self.assertEqual(result, (40.7128, -74.0060))

    def test_get_location_by_ip(self):
        # Mock the response from the IP address API
        with patch('restaurant_concierge.requests.get') as mock_get:
            mock_get.return_value.json.return_value = {'city': 'New York', 'region': 'NY', 'country': 'US'}
            result = self.concierge.get_location_by_ip()
            self.assertEqual(result, 'New York, NY, US')

    def test_get_lat_long_by_addr(self):
        # Mock the response from the geocoding API
        with patch('restaurant_concierge.Nominatim') as mock_geolocator:
            mock_location = mock_geolocator.return_value.geocode.return_value
            mock_location.latitude = 40.7128
            mock_location.longitude = -74.0060

            result = self.concierge.get_lat_long_by_addr('New York')
            self.assertEqual(result, (40.7128, -74.0060))

    def test_cal_distance(self):
        # Test the distance calculation method
        result = self.concierge.cal_distance((40.7128, -74.0060), (34.0522, -118.2437))
        self.assertAlmostEqual(result, 3935.7, delta=0.1)

    @patch('builtins.open', new_callable=mock_open, read_data='{"business_id": "123", "name": "Test Business"}\n{"business_id": "456", "name": "Another Business"}')
    def test_read_yelp_data(self, mock_file_open):
        file_path = 'test_business.json'

        # Call the method with the mocked file
        result = self.concierge.read_yelp_data(file_path)

        # Assertions
        self.assertEqual(result, [{'business_id': '123', 'name': 'Test Business'}, {'business_id': '456', 'name': 'Another Business'}])
        mock_file_open.assert_called_once_with(file_path, 'r', encoding='utf-8')

    @patch.object(RestaurantConcierge, 'cal_distance', side_effect=[5.0, 12.0, 8.0])  # Mock cal_distance with predefined distances
    def test_get_business_within_distance(self, mock_cal_distance):
        user_location = [40.0, -75.0]  # Example user location
        business_data = [
            {'business_id': '1', 'latitude': 40.1, 'longitude': -74.9},
            {'business_id': '2', 'latitude': 40.2, 'longitude': -74.8},
            {'business_id': '3', 'latitude': 40.3, 'longitude': -75.1}
        ]

        # Call the method with the mocked data
        result = self.concierge.get_business_within_distance(business_data, user_location)
        # Assertions
        self.assertEqual(result, None)
        
        mock_cal_distance.assert_called_with(user_location, [40.1, -74.9])  # Check if cal_distance was called with the correct parameters

    @patch('restaurant_concierge.sin') 
    @patch('restaurant_concierge.cos')
    @patch('restaurant_concierge.atan2')  
    @patch('restaurant_concierge.sqrt')  
    def test_cal_distance(self, mock_sqrt, mock_atan2, mock_cos, mock_sin):
        # Set up mock return values for the trigonometric functions
        mock_sin.side_effect = lambda x: x
        mock_cos.side_effect = lambda x: x
        mock_atan2.side_effect = lambda x, y: x
        mock_sqrt.side_effect = lambda x: x

        # Test case 1: Same coordinates should result in 0 distance
        addr1 = [40.7128, -74.0060]
        addr2 = [34.0522, -118.2437]
        result1 = self.concierge.cal_distance(addr1, addr2)
        self.assertAlmostEqual(result1, 845.0, delta = 0.5)



if __name__ == '__main__':
    unittest.main()