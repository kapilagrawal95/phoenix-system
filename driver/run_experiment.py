# This file assumes the following:
# OVERLEAF_INSTANCES ARE ALL UP AND RUNNING
# OVERLEAF IS EXPOSED ON <IP>:30911, 30913, 309135 and so on..
# USERS ARE CREATED.. If you're spawning 100 users then make sure 100 users are created.
import subprocess

if __name__ == "__main__":
    BASE_PORT = 30911
    # INPUTS
    overleaf_instances = 1
    runtime = "30s"
    LOG_DIR = "logs/"
    logfile = LOG_DIR+"mylogs.log"
    host = "http://155.98.38.116"
    users = 2
    # We will spawn the locust file using subprocess
    for i in overleaf_instances:
        port = BASE_PORT + 30911 + i*2
        cmd = f"locust -f locust/overleaf_v2.py --host {host}:{port} --headless --user {users} --run-time {runtime} --loglevel INFO --logfile {logfile}"
        output = subprocess.check_output(cmd, shell=True, text=True)