import csv
from geopy.distance import geodesic

# Here we can define the latitude and longitude of our desired input. For this, we search in FR.txt file.
def find_local_info(input_name, coord_database="FR.txt", name_col=1, lat_col=4, lon_col=5, admin1_col=10, admin2_col=11):
    with open(coord_database, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            try:
                location_name = row[name_col]
                if location_name == input_name:
                    lat = float(row[lat_col])
                    lon = float(row[lon_col])
                    admin1_code = row[admin1_col]
                    admin2_code = row[admin2_col]
                    return lat, lon, admin1_code, admin2_code # We are going to use this information for the next functions...
            except (ValueError, IndexError):
                continue
    print(f"\nLocation '{input_name}' not found in {coord_database}.")
    return None, None, None, None

# Here, we can find the first administrative region matching the informations we achieved in the upper function, for this, we search in
# admin1CodesASCII.txt.
def find_admin1_name(admin1_code, country_code="FR", admin1_database="admin1CodesASCII.txt"):
    with open(admin1_database, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            try:
                code = row[0]
                if code == f"{country_code}.{admin1_code}":
                    return row[1]  # Returns the name of the first administrative region
            except IndexError:
                continue
    return None

# Here, we can find the second administrative region matching the informations we achieved in the first function, for this, we search in
# admin2Codes.txt.
def find_admin2_name(admin1_code, admin2_code, country_code="FR", admin2_database="admin2Codes.txt"):
    with open(admin2_database, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            try:
                code = row[0]
                if code == f"{country_code}.{admin1_code}.{admin2_code}":
                    return row[1]  # Returns the name of the first administrative region
            except IndexError:
                continue
    return None

# With the information about wich is the second administrative region, we can calculate the amount of population in this region.
# For this, we can use the file "cities500.txt", which contains the informations only of the CITIES.
def calculate_admin2_population(admin1_code, admin2_code, coord_database="cities500.txt", admin1_col=10, admin2_col=11, pop_col=14):
    total_population = 0

    with open(coord_database, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            try:
                # Here we can verify if is in the same line
                if row[admin1_col] == admin1_code and row[admin2_col] == admin2_code:
                    population = int(row[pop_col])
                    total_population += population
            except (ValueError, IndexError):
                continue

    return total_population

# Again, we're going to use the file "cities500.txt" to find the information about the closest 5 cities to our input.
def find_nearest_cities(input_lat, input_lon, coord_database="cities500.txt", name_col=1, lat_col=4, lon_col=5, num_cities=5):
    location_coords = (input_lat, input_lon)
    cities = []

    with open(coord_database, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            try:
                city_name = row[name_col]
                city_lat = float(row[lat_col])
                city_lon = float(row[lon_col])
                city_coords = (city_lat, city_lon)

                # We use the geopy library functions to find the distance between our input and the closest city
                distance = geodesic(location_coords, city_coords).km
                cities.append((city_name, distance))
            except (ValueError, IndexError):
                continue

    # Here its a ordering code of distance, from low to high distances.
    nearest_cities = sorted(cities, key=lambda x: x[1])[:num_cities]
    return nearest_cities

# Thats the function that we can find the closest airport and the distance to our input coord. In this example, are considered
# all kinds of airports, from small to big size. Heliports are desconsidered from the search.
def find_nearest_airport(input_lat, input_lon, airport_database="airports.csv", name_col=3, type_col=2, lat_col=4, lon_col=5):
    closest_airport = None
    min_distance = float("inf")
    location_coords = (input_lat, input_lon)

    with open(airport_database, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)  # skip the header
        for row in reader:
            try:
                airport_type = row[type_col]
                if airport_type == "heliport":
                    continue  # Ignores the heliports

                airport_name = row[name_col]
                airport_lat = float(row[lat_col])
                airport_lon = float(row[lon_col])
                airport_coords = (airport_lat, airport_lon)

                # calculate the distance to the input coord.
                distance = geodesic(location_coords, airport_coords).km
                if distance < min_distance:
                    min_distance = distance
                    closest_airport = (airport_name, distance)
            except (ValueError, IndexError):
                continue

    return closest_airport

# Here we ask the user the input name.
input_location = input("\nEnter the name of the location: ").strip()
latitude, longitude, admin1_code, admin2_code = find_local_info(input_location)

if latitude is not None and longitude is not None:
    print(f"\nCoordinates for {input_location}:\nLatitude = {latitude}\nLongitude = {longitude}\n")
    
    # Gets the first and second names of the administrative region
    admin1_name = find_admin1_name(admin1_code)
    admin2_name = find_admin2_name(admin1_code, admin2_code)
    
    # total population of the second administrative region
    total_population = calculate_admin2_population(admin1_code, admin2_code)
    
    # find the 5 closest cities
    nearest_cities = find_nearest_cities(latitude, longitude)
    
    # find the nearest airport
    nearest_airport = find_nearest_airport(latitude, longitude)
    
    # Show the results
    if nearest_airport:
        print(f"Nearest Airport: {nearest_airport[0]}, Distance: {nearest_airport[1]:.2f} km")
    else:
        print("\nNo nearby airports found.")

    print(f"\nFirst Administrative Division: {admin1_code} ({admin1_name if admin1_name else 'Unknown'})")
    print(f"Second Administrative Division: {admin2_code} ({admin2_name if admin2_name else 'Unknown'})")
    print(f"\nTotal Population in the Second Administrative Division ({admin2_name}): {total_population:,.2f}\n")
    
    print("The 5 closest cities are:")
    for city, distance in nearest_cities:
        print(f"{city}: {distance:.2f} km")
    print(f"\n")
    
else:
    print("\nCould not find coordinates or administrative division codes for the specified location.")