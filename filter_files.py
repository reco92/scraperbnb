import pandas as pd
import glob


file_columns = [
        'pdpUrlType', 'propertyType', 'location', 'personCapacity', 'reviewCount', 'starRating', 'listingId', 'listingLat', 'listingLng',
        'homeTier', 'roomType', 'pictureCount', 'accuracyRating', 'checkinRating', 'cleanlinessRating',
        'communicationRating', 'locationRating', 'valueRating', 'guestSatisfactionOverall', 'visibleReviewCount', 'namenities',
        'price', 'total_amenities', 'amenities'
    ]

columns_to_fill = ['accuracyRating', 'checkinRating', 'cleanlinessRating', 'communicationRating', 'locationRating', 'valueRating', 'guestSatisfactionOverall', 'visibleReviewCount']

locations_map = { 'Cercado De Arequipa': 'Arequipa', 'Cayma District': 'Cayma', 'Arequipa Metropolitana': 'Arequipa', 'José Luis Bustamante District': 'José Luis Bustamante y Rivero', 'José Luis Bustamante': 'José Luis Bustamante y Rivero', 'Urb Señor de la Caña': 'Cayma'}

# Create an empty DataFrame to store the data
combined_data = pd.DataFrame(columns=file_columns)

# List all CSV files in the directory
csv_files = glob.glob("*.csv")  # Adjust the pattern to match your file names

print(csv_files)

# Iterate through each CSV file and append its data to the combined DataFrame
for csv_file in csv_files:
    df = pd.read_csv(csv_file, sep=';', usecols=file_columns)
    # combined_data = combined_data.append(df)
    combined_data = pd.concat([combined_data, df])

# Filter duplicates based on the 7th column (listingId)
filtered_data = combined_data.drop_duplicates(subset=["listingId"])


filtered_data[columns_to_fill] = filtered_data[columns_to_fill].fillna(0)
filtered_data['price'] = filtered_data['price'].str.replace('S/', '')
filtered_data['location'] = filtered_data['location'].replace(locations_map)

# Save the filtered data to a new CSV file
filtered_data.to_csv('filtered_data.csv', index=False)
