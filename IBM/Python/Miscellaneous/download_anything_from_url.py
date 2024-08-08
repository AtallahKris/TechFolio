import requests
import datetime

# URL of the file to be downloaded
url = input("Enter the URL of the file: ")

# Extension of the file to be downloaded
print("Enter the extension of the file (exclude the .)")
extension = input("Note: The extension of the file is usually the last couple of letters after the last '.' in the URL: ")

# Send a GET request to the URL to download the file
response = requests.get(url)

# Define the local file path where the file will be saved
# Current time was added as a unique identifier so no files are overwritten
current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
file_path = f"downloaded_{current_time}.{extension}"

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # If successful, write the content to the specified local file path
    with open(file_path, "wb") as file:
        file.write(response.content)
    print("File downloaded successfully")
else:
    # If the request failed, print an error message
    print("Failed to download the file")
