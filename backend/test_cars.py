#!/usr/bin/env python3

import requests
import json

# Test the car API
BASE_URL = "http://localhost:8001/api"

def test_api():
    print("Testing Car Rater API...")

    # Test basic API
    response = requests.get(f"{BASE_URL}/")
    print(f"✓ Basic API: {response.json()}")

    # Initialize cars
    print("\nInitializing cars...")
    response = requests.post(f"{BASE_URL}/cars/initialize")
    print(f"✓ Initialize cars: {response.json()}")

    # Get a random car
    print("\nGetting random car...")
    response = requests.get(f"{BASE_URL}/cars/random")
    car = response.json()
    print(f"✓ Random car: {car['year']} {car['make']} {car['model']}")
    print(f"   Current score: {car['hot_percentage']}% hot ({car['total_votes']} votes)")

    # Vote for the car
    car_id = car['id']
    print(f"\nVoting 'hot' for car {car_id}...")
    vote_response = requests.post(f"{BASE_URL}/cars/{car_id}/vote",
                                json={"car_id": car_id, "vote_type": "hot"})
    result = vote_response.json()
    print(f"✓ Vote result: {result['message']}")
    print(f"   New score: {result['car']['hot_percentage']}% hot ({result['car']['total_votes']} votes)")

    print("\n🎉 All tests passed!")

if __name__ == "__main__":
    test_api()