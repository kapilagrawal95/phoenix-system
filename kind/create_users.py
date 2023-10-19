import subprocess
import re
import requests
import time

def find_link_in_output(output):
    if "Done, without errors." not in output:
        raise Exception("some issue with creating new user")
    pattern = "http://localhost:8080//user/password/set\?passwordResetToken=.*"
    matches = re.findall(pattern, output)
    return matches[0].replace("localhost:8080//user/password", "localhost:8080/user/password")
def find_csrf_passwordReset_tokens(response):
    csrf_token = re.search('window.csrfToken = "([^"]+)"', response, re.IGNORECASE)
    assert csrf_token, "No csrf token found in response"
    passwordReset_token = re.search('name="passwordResetToken" value="([^"]+)"', response, re.IGNORECASE)
    return csrf_token.group(1), passwordReset_token.group(1)
def get_user_credentials(i):
    return ("user{}@netsail.uci.edu".format(str(i)), "iamuser{}".format(str(i)))

def create_overleaf_users(num_users, ns, port):
    for i in range(1, num_users+1):
        username, password = get_user_credentials(i)
        print("Trying to add new user with credentials username: {} and password: {}".format(username, password))
        pod_command = "kubectl get pods -n {} | grep '^web' | awk {}".format(ns, "'{print $1}'")
        # print(pod_command)
        output = subprocess.check_output(pod_command, shell=True)
        pod_name = output.decode("utf-8").strip()
        command = "kubectl exec -it "+pod_name+" -n {} -- grunt user:create-admin --email {}".format(ns, username)
        # print(command)
        output = subprocess.check_output(command, shell=True)
        output_str = output.decode("utf-8")
        print("Successfully, created new username...")
        url = find_link_in_output(output_str)
        ip_command = "hostname -I | awk '{print $1}'"
        output = subprocess.check_output(ip_command, shell=True)
        IP = output.decode("utf-8").strip()
        url = url.replace("localhost:8080", IP+":"+str(port))
        # print(url)
        resetToken = url.split("Token=")[-1].strip()
        session = requests.Session()  # Create a session to persist cookies
        response = session.get(url)
        # print(response.text)
        csrf, reset = find_csrf_passwordReset_tokens(str(response.content))
        data = {"_csrf":csrf,"password":password,"passwordResetToken":resetToken}
        post_url = "http://localhost:8080/user/password/set"
        post_url = post_url.replace("localhost:8080", IP+":"+str(port))
        response = session.post(post_url, data=data)
        if "200" not in str(response):
            raise Exception("some issue with setting {}'s password".format(username))
        else:
            print("Successfully, added password for {}...".format(username))
        session.close()

if __name__ == "__main__":
    create_overleaf_users(10, "overleaf0", 30911)