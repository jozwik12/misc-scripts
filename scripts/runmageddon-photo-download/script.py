import os
import requests

# Define the range of hrefs
start_index_1 = 4877
end_index_1 = 5943

start_index_2 = 3660
end_index_2 = 3760

# Create a folder to store the images
folder_path = './images'
os.makedirs(folder_path, exist_ok=True)

# Loop through the range of hrefs for the first set
for i in range(start_index_1, end_index_1 + 1):
    url = f'https://cdn.runmageddon.pl/2023-08/5u9a{i}.jpg?download=1'
    filename = f'image_{i}.jpg'
    filepath = os.path.join(folder_path, filename)
    
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Save the image to the folder
        with open(filepath, 'wb') as file:
            file.write(response.content)
        print(f'Saved {filename}')
    else:
        print(f'Failed to download {filename}')

# Loop through the range of hrefs for the second set
for i in range(start_index_2, end_index_2 + 1):
    url = f'https://cdn.runmageddon.pl/2023-08/img_{i}.jpg?download=1'
    filename = f'img_{i}.jpg'
    filepath = os.path.join(folder_path, filename)
    
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Save the image to the folder
        with open(filepath, 'wb') as file:
            file.write(response.content)
        print(f'Saved {filename}')
    else:
        print(f'Failed to download {filename}')

print('Download complete!')
