# this is the basis for the webapp, this holds the references to the files and the different functions
# first, iclude the needed packages
#fmt: off
import sys
import os
from flask import *
from datetime import *
sys.path.append('./static/py/')
import passwords
from fetch import *
import sqlfetch
#fmt: on
# this is the file fetch, that includes the function fetchData.
# if i wanna import any more files and functions, I do that here
# =====================================================================================
# this is needed to run the flask environment locally on my maschine
# WINDOWS
# cd .\WebApp\; $env:FLASK_ENV = "development"; $env:FLASK_APP = "app"; python3 -m flask run
# MAC/LINUX
# export FLASK_AP="app"; export FLASK_ENV="development" ;python3 -m flask run
# =====================================================================================
# ssh -L 8080:localhost:8080 optilima@optilima.wolution.com -p 2211
app = Flask(__name__)
# SELECT `camera`,`objectCount`,`timestamp` FROM `detections` WHERE `timestamp_server`>=1616164156828 AND `timestamp_server`<=1616174158294

# the index for the webserver, this is where i test the connection
# if i really want to, i could hash the inputed passwords and put these in the cookies
# i have no idea how other websites do it though

# ====================================================================
# +++++++++++++++++++++++++INDEX++++++++++++++++++++++++++++++++++++
# ====================================================================


@app.route('/', methods=["GET", "POST"])
def index():
    page_title = 'Homepage'
    # if theres a post request to the page
    if request.method == 'POST':
        # if the disconnect button is pressed
        # get all the values from the input fields
        logindata = [request.form.get('ssh_host'),
                     request.form.get('ssh_username'),
                     request.form.get('ssh_password'),
                     request.form.get('database_username'),
                     request.form.get('database_password')]
        # a test to connect to the database trough the tunnel
        # getting the log message as return

        log = sqlfetch.establishConnection(logindata, True)
        # if an exception accurs, we return the page and show an error message
        if log == 2:
            return cookies()
        # # if the post is successfull and it all goes through
        # the success message is displayed
        return render_template("index.html",
                               page_title=page_title,
                               ssh_host=logindata[0],
                               ssh_username=logindata[1],
                               ssh_password=logindata[2],
                               database_username=logindata[3],
                               database_password=logindata[4],
                               log=log)
    # if theres no post request, we just show that theres no connection
    return render_template("index.html",
                           page_title=page_title,
                           ssh_host='',
                           ssh_username='',
                           ssh_password='',
                           database_username='',
                           database_password='',
                           log=1)

# ====================================================================
# +++++++++++++++++++++++++CAM_OVV++++++++++++++++++++++++++++++++++++
# ====================================================================
# the template that lets the user choose from all the different cameras
# on here, also the number of animals on one field should be displayed


@app.route('/cam_ovv', methods=["GET", "POST"])
def cam_ovv():
    page_title = 'Kamera Übersicht'
    count = []
    diffsec = 0
    sql_columns = passwords.sql_columns
    # inital values for the Forms, these have to be edited, when cookies are set
    start_date_form = '2021-05-01 05:00:52.000'
    end_date_form = '2021-05-01 06:00:52.000'
    # the value out of the cookies, could be none
    start_date_cookie = request.cookies.get('begin')
    end_date_cookie = request.cookies.get('end')
    diffsec = request.cookies.get('diffsec')
    csv_file_path = request.cookies.get('csv_file_path')
    # i need to get the cookies first, if there not set, than we cant display the cams
    # this is just an error value
    if start_date_cookie is None or end_date_cookie is None or csv_file_path is None or diffsec is None:
        return render_template("cam_ovv.html", page_title=page_title,
                               start_date_form=start_date_form,
                               end_date_form=end_date_form,
                               sql_columns=sql_columns,
                               log=1,
                               date_limits=[],
                               )
    else:  # if the cookies have been set, i have to fetch the data from the csv file and output that on the template
        # first i need to check what the limits of the inputed file are. that way i make sure that
        # the times that the user chooses are in bounds of the file
        date_limits = []
        date_limits_cookies = []
        # if theres already a file at the set path from the passwords file, then we can import it immediately
        if os.path.exists(csv_file_path):
            # then we get the date limits from the dataset
            try:
                # try to get the datat out of the csv file
                date_limits = maxDate(csv_file_path, [], True)
            except:
                # if that fails, show a message that it did,
                # most likely something is wrong with the file
                return render_template("cam_ovv.html", page_title=page_title,
                                       sql_columns=sql_columns,
                                       log=4,
                                       start_date_form=start_date_form,
                                       end_date_form=end_date_form,
                                       )
            # now i cut off the miliseconds from the time, i want it always to shift down, otherwise it would give out faulty errors
            # for that i have to convert both timevalues (one from the csv-dataframe and one from the cookies)
            # to datetime and then i can compare them using maths logic
            date_limits = [datetime.strptime(date_limits[0], '%Y-%m-%d %H:%M:%S.%f'),
                           datetime.strptime(date_limits[1], '%Y-%m-%d %H:%M:%S.%f')]
            date_limits_cookies = [datetime.strptime(start_date_cookie, '%Y-%m-%d %H:%M:%S.%f'),
                                   datetime.strptime(end_date_cookie, '%Y-%m-%d %H:%M:%S.%f')]
            # if the inputed dates are out of bounds of the inputed csv file...
            if date_limits_cookies[0] < date_limits[0] or date_limits_cookies[1] > date_limits[1] or date_limits_cookies[0] > date_limits_cookies[1]:
                # then the function will return the template, without reading out the data from the file
                # it will also set the input fields to the max and min date of the csv file,
                # just as they were computed before
                return render_template("cam_ovv.html", page_title=page_title,
                                       date_limits=date_limits,
                                       sql_columns=sql_columns,
                                       start_date_form=date_limits[0],
                                       end_date_form=date_limits[1],
                                       date_limits_cookies=[],
                                       log=3,
                                       )
            # after getting the limits and the checks, we can get the data from the frame,
            count = fetch.getAverageOverTimeByCamera(csv_file_path,
                                                     start_date_cookie,
                                                     end_date_cookie, 12, [], True)

            # here i replace the form values with the cookies, that way they change dynamically
            start_date_form = start_date_cookie
            end_date_form = end_date_cookie
            # ==========================================================
            # EVERYTHING FINE AND CHECKED
            # ==========================================================
            return render_template("cam_ovv.html", page_title=page_title,
                                   start_date_cookie=start_date_cookie,
                                   start_date_form=start_date_form,
                                   end_date_cookie=end_date_cookie,
                                   end_date_form=end_date_form,
                                   diffsec=diffsec,
                                   count=count,
                                   date_limits=date_limits,
                                   date_limits_cookies=date_limits_cookies,
                                   size=fetch.size(csv_file_path),
                                   sql_columns=sql_columns,
                                   log=0,)
        # if there is NO file and therefore no data to implement, we just show the message that theres no data avaiable
        # and we also check the checkbox that a query has to be made
        else:
            return render_template("cam_ovv.html", page_title=page_title,
                                   start_date_form=start_date_form,
                                   end_date_form=end_date_form,
                                   date_limits=date_limits,
                                   filePath=csv_file_path,
                                   sql_columns=sql_columns,
                                   log=1,
                                   )


# ====================================================================
# +++++++++++++++++++++++++IND_CAMS++++++++++++++++++++++++++++++++++++
# ====================================================================
# template for all the individual cams, i want to have one page that renders all of them, just based on the
# imported data and variables

@ app.route('/ind_cams', methods=["GET", "POST"])
def ind_cams():
    log = 0
    diffsec = 0
    # index is the value that gets posted from the cam_ovv template
    # chosen_index is the value that get posted from a dropdown menu on this template
    index = request.form.get('camButton')
    chosen_index = request.form.get('chosenCamID')
    # this is to ensure that the cams get set accordingly
    # going on the page the first time (while using the cam_ovv template) will result in
    # index being set and chosen_index being None
    # to make sure that the website functions right, the values get copied
    if (chosen_index is None) and (index is not None):
        chosen_index = index
    # when the dropdownmenu is being used and the button is pressed, chosen_index will have the value from the menu
    # and index will be None
    elif (chosen_index is not None) and (index is None):
        index = chosen_index
    # if both are None, someone cheated or I got something wrong. In this case, we go to cam 0 to display an error
    else:
        index = 1
        chosen_index = 1
        log = 1
    # read the cookies, set by the browser.
    start_date_cookie = request.cookies.get('begin')
    end_date_cookie = request.cookies.get('end')
    diffsec = request.cookies.get('diffsec')
    # diffsec = 0

    # error message if the cookies arent set
    if start_date_cookie is None or end_date_cookie is None or diffsec is None:
        log = 1
    # set strings for the page_title of the page and the name of the classes
    page_title = "Cam" + str(index)
    # this is to set a class for the position of the animals. I set up a file with 700x700 classes, that have all the possible positions inplemented
    # but im pretty sure i have to implement the movement of the animals with javascript
    style = 'cam' + str(index)
    return render_template("ind_cams.html", page_title=page_title,
                           index=index,
                           style=style,
                           diffsec=diffsec,
                           begin_date=start_date_cookie,
                           end_date=end_date_cookie,
                           log=log)

# ====================================================================
# +++++++++++++++++++++++++COOKIES++++++++++++++++++++++++++++++++++++
# ====================================================================

# i cant send the set data back to the same page to write it in the cookies,
# thats what this page is for. Its just making sure the data is valid and then sets the cookies accordingly
# im immediately forwarding the page to the cam_ovv template
# here i also make the query to the database and write the CSV file, if all checks are done


@app.route('/cookies', methods=["POST"])
def cookies():
    page_title = 'SetAppata'
    logindata = [passwords.ssh_host, passwords.ssh_username,
                 passwords.ssh_password, passwords.database_username, passwords.database_password]
    chunk_size = 10000
    chosen_columns_array = ''  # empty string to start concatenating
    # if the page gets a post, but its not about setting the filepath or fetch things
    # but just to update the dates, what do i do?
    try:
        # i try to fetch the filename from the input field, this works everytime the input field can be seen
        csv_file_path = './static/csv/' + \
            request.form['csvFileName'] + '.csv'
    except:
        # if theres no form (so no file has been chosen), i try to find if theres a cookie avaiable
        # because if there is, the file is already there and i can use it
        if request.cookies.get('csv_file_path'):
            csv_file_path = request.cookies.get('csv_file_path')
        else:
            # if there is no input field, so no file has been selected AND no cookie, then we get this
            # but for that, one would have to actually delete the cookies on purpose
            # because normally this case would never happen, i cant change the cookie without
            # submitting a new file
            return render_template('cookies.html',
                                   page_title=page_title, e="Ich bin eine Biene")
    # if there is NO file avaible to the user, i have to fetch and generate it
    # but for that, we also have to check if the user wants to generate a file, because when theres
    # no file and we dont wanna download one, why would we do that?
    # so this is how the function starts
    if os.path.exists(csv_file_path) == False and request.form.get('gen') == 'on':
        # if the stuff above doesnt work, i have to make a query to the database and set the
        # csv file
        # i start with setting the timestamps to get the boundaries for the database
        try:
            # first, he tries to import the time with milliseconds
            timestamp_start = int(datetime.timestamp(
                datetime.strptime(request.form['TimeStartIn'], '%Y-%m-%d %H:%M:%S.%f')) * 1000)
            # print('TIME:' + str(timestamp_start))
            timestamp_end = int(datetime.timestamp(
                datetime.strptime(request.form['TimeEndIn'], '%Y-%m-%d %H:%M:%S.%f')) * 1000)
            # print('TIME:' + str(timestamp_end))
        except:
            # when that doesnt work
            try:
                # he tries it without the milliseconds
                timestamp_start = int(datetime.timestamp(
                    datetime.strptime(request.form['TimeStartIn'], '%Y-%m-%d %H:%M:%S')) * 1000)
                timestamp_end = int(datetime.timestamp(
                    datetime.strptime(request.form['TimeEndIn'], '%Y-%m-%d %H:%M:%S')) * 1000)
            except:
                # and when that also failes, the dates are wrongly submitted and theres an error message displayed
                return render_template('cookies.html',
                                       page_title=page_title, e="Falsche Query")
        # now i try to fetch all the chosen Boxes from the Modal
        # this is done by looping through the names of the fields and checking if there on
        for active_column in passwords.sql_columns:
            # if they are i just put the string together with all the fields
            if request.form.get('SQL_' + active_column) == 'on':
                chosen_columns_array = chosen_columns_array + '`' + active_column + '`,'
        # and in the end i delete the last colon, cause thats always too much
        chosen_columns_array = chosen_columns_array[:-1]
        # the timestamps are not really necessary here, but when theyre 0 or
        # the user doesnt choose any columns, an error is displayed
        if timestamp_start == 0 or timestamp_end == 0 or chosen_columns_array == '':
            return render_template('cookies.html',
                                   page_title=page_title, e="Falsche Query")
        # now i want to implement a function, that sees when the query is over an hour long, then i wanna make
        # loads of small queries and add them to the csv file, lets see if that works
        # 60k timestampunits are roughly an hour of data

        chunk_timestamps_array = sqlfetch.Timechunks(
            timestamp_start, timestamp_end, chunk_size)
        # print(chunk_timestamps_array)
        try:

            sqlfetch.main(chunk_timestamps_array, chosen_columns_array,
                          logindata, csv_file_path)
        except Exception as e:
            return render_template('cookies.html',
                                   page_title=page_title, e=e)
        # At this point, the query is done and the csv file is generated
        # so i can just return to the main page
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        return render_template('cookies.html',
                               page_title=page_title, e="CSV Datei generiert. Zurück zur Übersicht..")
        # if the timestamps are not too big, i can just fetch the data as a whole

    # if theres a file, i can just start and use the dates and stuff
    # because the inputfields have to be there
    # just to make sure (if the file is broken or whatever, i display an error message when this goes wrong)
    try:
        date_from_form_start = request.form['begin_date']
        date_from_form_end = request.form['end_date']

    except Exception as e:
        return render_template('cookies.html',
                               page_title=page_title, e=e)
        try:
            date_from_form_start = request.form['TimeStartIn']
            date_from_form_end = request.form['TimeEndIn']
        except:
            if request.form.get('gen') != ['on']:
                resp = make_response(render_template('cookies.html',
                                                     page_title=page_title))
                resp.set_cookie('csv_file_path', str(csv_file_path))
                return resp
            return render_template('cookies.html',
                                   page_title=page_title, e=e)
    # if there is already a file in place, then i can just check for the dates and work
    # with the dataset that is already there
    # so, i have to set the cookies to the start and end_date that have been selected
    try:
        datetime_begin = datetime.strptime(date_from_form_start,
                                           '%Y-%m-%d %H:%M:%S.%f')
        datetime_end = datetime.strptime(date_from_form_end,
                                         '%Y-%m-%d %H:%M:%S.%f')
    # if we get a ValueError exeption, meaning the dates cant be converted,
    # it takes us back to the mainPage and outputs a warning
    except ValueError:
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        return render_template('cam_ovv.html',
                               log=2,
                               page_title='Kameras',
                               sdte=date_from_form_start,
                               edte=date_from_form_end,
                               count=[])

    # now i wanna split the dates into each, date and time to keep calculating with it, if i want to
    # now array = [yyyy-mm-dd, HH:MM-ss]
    datetime_arrar_start = [datetime.strftime(datetime_begin, '%Y-%m-%d'),
                            datetime.strftime(datetime_begin, '%H:%M:%S')]
    datetime_array_end = [datetime.strftime(datetime_end, '%Y-%m-%d'),
                          datetime.strftime(datetime_end, '%H:%M:%S')]
    # further splitting the time into each frame, now array = [y,m,d]
    day_array_start = datetime_arrar_start[0].split("-")
    day_array_end = datetime_array_end[0].split("-")
    # further splitting the time into each frame, now array = [h,m,s]
    time_array_start = datetime_arrar_start[1].split(":")
    time_array_end = datetime_array_end[1].split(":")
    for i in range(0, 3):
        day_array_start[i] = int(day_array_start[i])
        day_array_end[i] = int(day_array_end[i])
        time_array_start[i] = int(time_array_start[i])
        time_array_end[i] = int(time_array_end[i])

    # timeelements = [startmin, startsec, endmin, endsec]
    # difference in seconds, taking also the minutes in account
    # aight so this works, the problem is that sometimes i want hours, and sometimes i want seconds
    # so i havent decided how i do that yet, but thats a problem for future-jonny
    diffsec = (abs(day_array_end[2] - day_array_start[2]) * 60 * 60 * 24)
    diffsec = diffsec + abs(time_array_end[0] - time_array_start[0]) * 3600
    diffsec = diffsec + abs(time_array_end[1] - time_array_start[1]) * 60
    diffsec = diffsec + abs(time_array_end[2] - time_array_start[2])
    # make a response with the cookies page
    # just to calculate the array that i get from the string function
    # this will be really handy, since all the positions are in one
    # sizeofitems = [len(items), len(items[1])]
    # optimal would be if we had checkboxes for all the different columns avaiable
    resp = make_response(render_template('cookies.html',
                                         page_title=page_title))
    resp.set_cookie('begin', str(date_from_form_start))
    resp.set_cookie('end', str(date_from_form_end))
    resp.set_cookie('diffsec', str(diffsec))
    resp.set_cookie('csv_file_path', str(csv_file_path))
    # with the return of the response, the cookies have been set
    return resp


@ app.route('/video', methods=["GET", "POST"])
def video():
    page_title = 'Video'
    return render_template("video.html", log=0, page_title=page_title)
