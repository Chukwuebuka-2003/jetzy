from datetime import date, datetime, time, timedelta
import random
from typing import Dict, Any, List
from pydantic import HttpUrl

MOCK_AIRLINES = [
    "American Airlines", "Delta AirLines", "Emirates"
]

MOCK_AIRPORTS = {
    "NYC" : {"code": "JFK", "name": "John F. Kennedy Airport", "city": "New York", "country": "United States"},
    "LHR" : {"code": "LHR", "name": "Heathrow Airport", "city": "Los Angeles", "country": "United Kingdom"},
    "CAI" : {"code": "CAI", "name": "Cairo International Airport", "city": "Cairo", "country": "Egypt"}
}


MOCK_HOTEL_CHAINS = [
    "Marriot", "Hilton", "Hyatt", "Wyndham"
]


MOCK_HOTEL_AMENITIES = [
    {"name": "Free WiFi", "category": "Services"},
    {"name": "Swimming Pool", "category": "Pool"},
    {"name": "Fitness Center", "category": "Fitness"},
    {"name": "Restaurant", "category": "Dining"},
    {"name": "Conference Room", "category": "Business"}
]


MOCK_ATTRACTIONS = {
    "New York": [
        {"name": "Times Square", "category": ["Landmark"], "rating": 4.5},
        {"name": "Central Park", "category": ["Park"], "rating": 4.2},
        {"name": "Statue of Liberty", "category": ["Monument"], "rating": 4.8}
    ],

    "Rome": [
        {"name": "Colosseum", "category": ["Historical Site"], "rating": 4.0},
        {"name": "Pantheon", "category": ["Historical Site"], "rating": 4.7}
    ],

    "Paris": [
        {"name": "Effiel Tower", "category": ["Landmark"], "rating": 4.9},
        {"name": "Louvre Museum", "category": ["Museum"], "rating": 5.0}       
    ],

    "London": [
        {"name": "British Museum", "category": ["Museum"], "rating": 4.4},
        {"name": "London Eye", "category": ["Entertainment"], "rating": 4.8}
    ],

    "Cairo": [
        {"name": "Pyramids of Giza", "category": ["Historical Site"], "rating": 4.9},
        {"name": "Egyptian Museum", "category": ["Museum"], "rating": 4.5}
    ]
}


MOCK_CUISINES = [
    "Italian", "French", "Japanese", "Chinese", "Mexican", "Indian", "Korean", "Mediterranean"
]

MOCK_RESTAURANTS = {
    "New York": [
        {"name": "Le Bernardin", "cuisines": ["French"], "price_level": "$$$", "rating": 4.8},
        {"name": "Ebuka Diny", "cuisines": ["Korean"], "price_level": "$$$$", "rating": 4.9}
    ],
    
    "Rome": [
        {"name": "Da Enzo", "cuisines": ["Italian"], "price_level": "$$", "rating": 4.5},
        {"name": "KFC", "cuisines": ["American"], "price_level": "$$$", "rating": 4.3}
    ],

    "Paris": [
        {"name": "Le Jules", "cuisines": ["French"], "price_level": "$$", "rating": 4.0},
        {"name": "Septime", "cuisines": ["French"], "price_level": "$$$", "rating": 3.9}
    ]
}


MOCK_TRANSPORT = {
    "Rome-Milan": [
        {"mode": "train", "duration_minutes": 180, "price": 70},
        {"mode": "flight", "duration_minutes": 70, "price": 90},
        {"mode": "car", "duration_minutes": 400, "price": 25},
        {"mode": "bus", "duration_minutes": 350, "price": 50}
    ],

    "New York-Boston": [
        {"mode": "train", "duration_minutes": 240, "price": 60},
        {"mode": "flight", "duration_minutes": 60, "price": 110},
        {"mode": "car", "duration_minutes": 300, "price": 40},
        {"mode": "bus", "duration_minutes": 350, "price": 80}
    ],

    "London-Paris": [
        {"mode": "train", "duration_minutes": 150, "price": 100},
        {"mode": "flight", "duration_minutes": 90, "price": 190},
        {"mode": "car", "duration_minutes": 600, "price": 80},
        {"mode": "car", "duration_minutes": 390, "price": 140}
    ]
}


def generate_mock_flight(origin, destination, departure_date, return_date=None, count=5):
    options = []

    origin_data = next((airport for code, airport in MOCK_AIRPORTS.items() if code == origin.upper() or airport["code"] == origin.upper()), None)

    dest_data= next((airport for code, airport in MOCK_AIRPORTS.items() if code == destination.upper() or airport["code"] == destination.upper()), None)
    
    # fallback 

    if not origin_data or not dest_data:
        origin_data = MOCK_AIRPORTS["NYC"]
        dest_data = MOCK_AIRPORTS["LHR"]

    for i in range(count):
        airline = random.choice(MOCK_AIRLINES)
        flight_number = f"{airline[0]}{random.randint(100, 999)}"

        dep_hour = random.randint(6, 22)
        dep_time = datetime.combine(departure_date, time(dep_hour, random.choice([0, 15, 30, 45])))
        duration = timedelta(hours=random.randint(3, 10), minutes= random.choice([0, 15, 30, 45]))
        arr_time = dep_time + duration

        outbound_segment = {
             "airline": airline,
             "flight_number": flight_number,
             "departure_airport": origin_data["code"],
             "departure_time": dep_time,
             "arrival_airport": dest_data["code"],
             "arrival_time": arr_time,
             "duration_minutes": int(duration.total_seconds() / 60),
             "cabin_class": "economy"

        }

        return_segments = None
        if return_date:
            ret_hour = random.randint(6, 22)
            ret_dep_time = datetime.combine(return_date, time(ret_hour, random.choice([0, 15, 30, 45])))
            ret_duration = timedelta(hours=random.randint(3,10), minutes=random.choice([0, 15, 30, 45]))
            ret_arr_time = ret_dep_time + ret_duration

            return_segments = [
                {
                    "airline": airline,
                    "flight_number" : f"{airline[0]}{random.randint(100, 999)}",
                    "departure_airport": dest_data["code"],
                    "departure_time": ret_dep_time,
                    "arrival_airport": origin_data["code"],
                    "arrival_time": ret_arr_time,
                    "duration_minutes": int(ret_duration.total_seconds() / 60),
                    "cabin_class": "economy"
                }
            ]

            base_price = random.randint(300, 1200)
            if airline == "Emirates":
                base_price = random.randint(200, 400)

            options.append({
                "outbound_segments": [outbound_segment],
                "return_segments": return_segments,
                "total_price": base_price,
                "currency": "USD",
                "booking_link": f"https://example.com/book/flight/{origin_data['code']}-{dest_data['code']}",
                "provider": random.choice(["Skyscanner", "Expedia"])
            })

    # sorting by price

    return sorted(options, key=lambda x: x["total_price"])
        

def generate_mock_hotel(destination, check_in_date, check_out_date, count=10):
    options = []

    dest_key = next((city for city in MOCK_ATTRACTIONS.keys() if city.lower() == destination.lower()), random.choice(list(MOCK_ATTRACTIONS.keys())))

    for i in range(count):
        chain =  random.choice[MOCK_HOTEL_CHAINS]
        hotel_type = random.choice(["Hotel", "Resort", "Suites"])
        name = f"{chain} {dest_key} {hotel_type}"

        star_rating = random.choice([3.0, 3.5, 4.0, 4.5, 5.0])
        user_rating = min(5.0, max(3.0, star_rating + random.uniform(-0.5, 0.5)))

        base_price = star_rating * 50 * random.uniform(0.8, 1.2)
        nights = (check_out_date - check_in_date).days
        total_price = base_price + nights

        num_amenities = random.randint(4,8)
        amenities = random.sample(MOCK_HOTEL_AMENITIES, num_amenities)

        options.append(
            {
                "name": name,
                "star_rating": star_rating,
                "user_rating": user_rating,
                "reviews_count" : random.randint(100, 1000),
                "location": {
                    "address": f"{random.randint(1, 999)} Ebukas St",
                    "city": dest_key,
                    "country": "United States" if dest_key == "New York" else "Italy" if dest_key in ["Rome, Milan"] else "Egypt" if dest_key == "Cairo" else "France" if dest_key == "Paris" else "United Kingdom",
                    "postal_code": f"{random.randint(10000, 99999)}",
                    "latitude": random.uniform(-90, 90),
                    "longitude": random.uniform(-180, 180)
                },

                "price_per_night": base_price,
                "total_price": total_price,
                "currency": "USD",
                "amenities": amenities,
                "booking_link": f"https://example.com/book/hotel/{dest_key.lower().replace('' '-')}/{i}",
                "provider": random.choice(["Booking.com", "Hotels.com"]),
                "image_url": f"https://example.com/images/hotels/{dest_key.lower().replace('', '-')}/{i}.jpg"

            }
        )

    # sorting again by price
    return sorted(options, key=lambda x: x["price_per_night"])

def generate_mock_attraction(location, categories=None, count=5):
    options = []

    loc_key = next((city for city in MOCK_ATTRACTIONS.keys() if city.lower() == location.lower()), random.choice(list(MOCK_ATTRACTIONS.keys())))

    attractions = MOCK_ATTRACTIONS[loc_key]

    # filtering by categories
    if categories:
        filtered_attractions = []
        for attraction in attractions:
            if any(category.lower() in [c.lower() for c in attraction["category"]] for category in categories):
                filtered_attractions.apppend(attraction)
        attractions = filtered_attractions if filtered_attractions else attractions


    selected_attractions = random.sample(attractions, min(len(attractions), count))

    for attraction in selected_attractions:
        hours = []
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            is_closed = day == "Monday" and random.random() < 0.3

            if is_closed:
                hours.append({
                    "day_of_week": day,
                    "is_closed": True
                })

            else:
                open_hour = random.randint(8, 10)
                close_hour = random.randint(17, 21)
                hours.append({
                    "day_of_week": day,
                    "opening_time": time(open_hour, 0),
                    "closing_time": time(close_hour, 0),
                    "is_closed": False
                })


        options.append({
            "name": attraction["name"],
            "description": f"A popular {', '.join(attraction['category']).lower()} in {loc_key}.",
            "category": attraction["categroy"],
            "rating": attraction["rating"],
            "reviews_count": random.randint(500, 2000),
            "price_range": random.choice(["$", "$$", "$$$", "$$$$"]),
            "estimated_duration_minutes": random.randint(10, 500),
            "location": {
                "address": f"{random.randint(1, 999)} Micheals St",
                "city": loc_key,
                "country": "United States" if loc_key == "New York" else "Italy" if loc_key in ["Rome, Milan"] else "Egypt" if loc_key == "Cairo" else "France" if loc_key == "Paris" else "United Kingdom",
                "latitude": random.uniform(-90, 90),
                "longitude": random.uniform(-180, 180)

            },
            "hours": hours,
            "website": f"https://example.com/attractions/{loc_key.lower().replace('', '-')}/{attraction['name'].lower().replace('', '-')}",
            "booking_link": f"https://example.com/book/attraction/{loc_key.lower().replace('', '-')}/{attraction['name'].lower().replace('', '-')}",
            "provider": random.choice(["TripAdvisor", "Google Maps"])
        })

    # sorting now by rating
    return sorted(options, key=lambda x: x["rating"], reverse=True)

def generate_mock_restaurant(location, cuisines=None, price_range=None, count=5):
    options = []
    loc_key = next((city for city in MOCK_RESTAURANTS.keys() if city.lower() == location.lower()), random.choice(list(MOCK_RESTAURANTS.keys())))

    restaurants = MOCK_RESTAURANTS.get(loc_key, [])
    
    # filter by cuisines
    if cuisines:
        filtered_restaurants = []
        for restaurant in restaurants:
            if restaurant["price_level"] in price_range:
                filtered_restaurants.append(restaurant)
        restaurants = filtered_restaurants if filtered_restaurants else restaurants

    selected_restaurants = random.sample(restaurants, min(len(restaurants), count))

    for restaurant in selected_restaurants:
        hours = []
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            is_closed = random.random() < 0.1

            if is_closed:
                hours.append({
                    "day_of_week": day,
                    "is_closed": True
                })
            else:
                lunch_open = time(11, 30)
                lunch_close = time(14, 30)
                dinner_open = time(17,30)
                dinner_close = time(22,0)

                hours.append ({
                    "day_of_week": day,
                    "opening_time": lunch_open if random.random() < 0.7 else dinner_open,
                    "closing_time": dinner_close,
                    "is_closed": False

                })


        options.append({
            "name": restaurant["name"],
            "cuisines": restaurant["cuisines"],
            "price_level": restaurant["price_level"],
            "rating": restaurant["rating"],
            "reviews_count": random.randint(50, 500),
            "location": {
                "address": f"{random.randint(1, 999)} Ebuka Micheal St",
                "city": loc_key,
                "country": "United States" if loc_key == "New York" else "Italy" if loc_key in ["Rome, Milan"] else "Egypt" if loc_key == "Cairo" else "France" if loc_key == "Paris" else "United Kingdom",
                "latitude": random.uniform(-90, 90),
                "longitude": random.uniform(-180, 180)
            },
            "hours": hours,
            "phone": f"+1-{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "website": f"https://example.com/restaurants/{loc_key.lower().replace('', '-')}/{restaurant['name'].lower().replace('', '-')}",
            "reservation_link": f"https://example.com/book/restaurant/{loc_key.lower().replace('', '-')}/{restaurant['name'].lower().replace('', '-')}",
            "provider": random.choice(["Yelp", "Zomato"])

        })
        
    # sort now by rating
    return sorted(options, key=lambda x: x["rating"], reverse=True)

def generate_mock_transport(origin, destination, departure_date, count=5):
    options = []

    route_key  = f"{origin}-{destination}"
    reverse_route_key = f"{destination}-{origin}"

    route_data = MOCK_TRANSPORT.get(route_key,MOCK_TRANSPORT.get(reverse_route_key, None))
    

    for i , transport in enumerate(route_data):
        dep_hour = random.randint(6,20)
        dep_time = datetime.combine(departure_date, time(dep_hour, random.choice([0, 15, 30, 45, 50])))
        duration = timedelta(minutes=transport["duration_minutes"])
        arr_time = dep_time + duration

        segments = [{
            "mode": transport["mode"],
            "provider": get_transport_provider(transport["mode"]),
            "departure_location": origin,
            "departure_time": dep_time,
            "arrival_location": destination,
            "arrival_time": arr_time,
            "duration_minutes": transport["duration_minutes"],
            "distance_km": random.randint(10, 1000)
        }]

        options.append({
            "segments": segments,
            "total_duration_minutes": transport["duration_minutes"],
            "total_price": transport["price"],
            "currency": "USD",
            "booking_link": f"https://example.com/book/transport/{transport['mode']}/{origin.lower()} - {destination.lower()}",
            "provider": "Rome2Rio" if random.random() < 0.5 else "Google Directions"
        }) 


    # sorting now by duration
    return sorted(options, key=lambda x: x["total_duration_minutes"])


def get_transport_provider(mode):
    if mode == "flight":
        return random.choice(MOCK_AIRLINES)
    elif mode == "train":
        return random.choice(["Eurostar", "SNCF", "Amtrak"])
    elif mode == "bus":
        return random.choice(["Greyhound", "EbukaBus", "National Express"])
    else:
        return random.choice(["Waymo", "Uber", "Bolt", "Lyft"])
         
                
        