import subprocess
import re
import requests
import time

def find_link_in_output(output):
    # check is done without errors
    if "Done, without errors." not in output:
        raise Exception("some issue with creating new user")
    pattern = "http://localhost:8080//user/password/set\?passwordResetToken=.*"

    # Use re.findall to extract all matching substrings
    matches = re.findall(pattern, output)
    # print(len(matches))
    # print(matches[0])
    return matches[0].replace("localhost:8080//user/password", "localhost:8080/user/password")


def find_csrf_passwordReset_tokens(response):
    # window.csrfToken = "DwSsXuVc-uECsSv6dW5ifI4025HacsODuhb8"
    # decoded_data = response.decode('utf-8')
    csrf_token = re.search('window.csrfToken = "([^"]+)"', response, re.IGNORECASE)
    assert csrf_token, "No csrf token found in response"
    passwordReset_token = re.search('name="passwordResetToken" value="([^"]+)"', response, re.IGNORECASE)
    return csrf_token.group(1), passwordReset_token.group(1)

def get_user_credentials(i):
    return ("user{}@netsail.uci.edu".format(str(i)), "iamuser{}".format(str(i)))

for i in range(1, 11):
    username, password = get_user_credentials(i)

    print("Trying to add new user with credentials username: {} and password: {}".format(username, password))
    # If running docker container uncomment this and comment kubernetes
    command = "docker exec -it sharelatex-dockerized_web_1 grunt user:create-admin --email {}".format(username)
    output = subprocess.check_output(command, shell=True, text=True)

    # if running kubernetes then first get the pod
    #pod_command = "kubectl get pods | grep '^web' | awk '{print $1}'"
    #output = subprocess.check_output(pod_command, shell=True)
    #pod_name = output.decode("utf-8").strip()
    #command = "kubectl exec -it "+pod_name+" -- grunt user:create-admin --email {}".format(username)
    #output = subprocess.check_output(command, shell=True)

    #output_str = output.decode("utf-8")

    # # Run the command and capture the output
    # # Print or store the output
    print("Successfully, created new username...")
    print("Now adding password..")

    url = find_link_in_output(output)


    # if running kubernetes replace localhost:8080 with the IP and 30910
    #ip_command = "hostname -I | awk '{print $1}'"
    #output = subprocess.check_output(ip_command, shell=True)
    #IP = output.decode("utf-8").strip()
    #url = url.replace("localhost:8080", IP+":30910")
    #print(url)
    #resetToken = url.split("Token=")[-1].strip()
    #print(resetToken)
    #Else do nothing and go below

    print(url)

    session = requests.Session()  # Create a session to persist cookies
    response = session.get(url)
    #print(str(response.content))
    csrf, reset = find_csrf_passwordReset_tokens(str(response.content))

    data = {"_csrf":csrf,"password":password,"passwordResetToken":reset}
    post_url = "http://localhost:8080/user/password/set"
    print(data)
    # if running on kubernetes, then replace localhost:8080
    #post_url = post_url.replace("localhost:8080", IP+":30910")
    # if running docker then comment above

    print(post_url)
    response = session.post(post_url, data=data)
    print(response)

    if "200" not in str(response):
        raise Exception("some issue with setting {}'s password".format(username))
    else:
        print("Successfully, added password for {}...".format(username))

    session.close()
    #time.sleep(5)
