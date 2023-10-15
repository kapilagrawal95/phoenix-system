import requests
import re

def find_in_page(doc):
    # window.csrfToken = "DwSsXuVc-uECsSv6dW5ifI4025HacsODuhb8"
    decoded_data = doc.decode('utf-8')
    token_search = re.search('window.csrfToken = "([^"]+)"', decoded_data, re.IGNORECASE)
    assert token_search, "No csrf token found in response"
    return token_search.group(1)

# URL of the login page
session = requests.Session()  # Create a session to persist cookies

login_url = 'http://155.98.38.25:30910/login'
res = session.get(login_url)

csrf_token = find_in_page(res.content)
print(csrf_token)

data = {
"_csrf": csrf_token,
"email": "admin@example.com",
"password": "kapil123"
}

# Perform the POST request
# session = requests.Session()  # Create a session to persist cookies
response = session.post(login_url, data=data)

# Check the response for success
if response.status_code == 200:
    print("Login successful!")
    # print(response)
    response = session.get("http://155.98.38.25:30910/project/65149d5fbd5770068938c42e")
    print(response)

    
    # You can now continue to interact with the authenticated session if needed.
    # For example, make additional requests or scrape data.
else:
    print("Login failed. Status code:", response.status_code)

# Don't forget to close the session when done
session.close()

