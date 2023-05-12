# OptiLima
1. please input the logindata for the database and the tunnnel in -[/static/py/passwords.py`

# Technologies
- Bootstrap 4
- Flask 2.02
- Python 3.9.7

# Project
## folder
- [/static](https://gitlab.com/je223xa/optilima/-/tree/main/static) holds all the file that are used and called
    - [/css](https://gitlab.com/je223xa/optilima/-/tree/main/static/css) holds the css code for the website
    - [/csv](https://gitlab.com/je223xa/optilima/-/tree/main/static/csv) is the output path for all the csv files that get generated
    - [/js](https://gitlab.com/je223xa/optilima/-/tree/main/static/js) the javascript code for buttons etc... later here will be the extaction of the json arrays
    - [/py](https://gitlab.com/je223xa/optilima/-/tree/main/static/py) the python scripts, that are needed to run the project
- [/templates](https://gitlab.com/je223xa/optilima/-/tree/main/templates) here are all the html pages and templates. I use jinja as well 

## python files
- [app.py](https://gitlab.com/je223xa/optilimaapp/-/blob/main/app.py) This is the main app with all the code that builds the different pages
- [fetch.py](https://gitlab.com/je223xa/optilima/-/tree/main/static/py/fetch.py) includes functions to fetch important data from either a csv file with the right structure or a satafram that is pushed to the function
- [passwords.py](https://gitlab.com/je223xa/optilima/-/tree/main/static/py/passwords.py) holds the passwords for the databases, tunnel. Is also used as a temporary store for data
- [sqlfetch.py](https://gitlab.com/je223xa/optilima/-/tree/main/static/py/sqlfetch.py) used to fetch data from the database through the tunnel. Holds the main function to get data
- [tunnelfunctions.py](https://gitlab.com/je223xa/optilima/-/tree/main/static/py/tunnelfunctions.py) this is used to connect to a tunnel and a database. Used as temporary storage for global variables from sqlfetch

# Run the project
```bash
python start.py
```
Go to [localhost](http://127.0.0.1:5000) to access the environment.
# pythontest
