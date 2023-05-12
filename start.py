import os
os.environ["FLASK_ENV"] = "development"
os.environ["FLASK_APP"] = "app"

# os.system("/usr/bin/firefox --new-window 127.0.0.1:5000")
os.system("cd optilima/; python3 -m flask run")
