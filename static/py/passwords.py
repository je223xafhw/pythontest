ssh_host = ''
ssh_username = ''
ssh_password = ''
database_username = ''
database_password = ''
logindata = [ssh_host, ssh_username, ssh_password,
             database_username, database_password]
csv_file_path = './static/csv/test.csv'
timestamp_start = 1616214158294
timestamp_end = 1616214158294
sql_columns = ['camera', 'server', 'videoFilename', 'frameId', 'objectCount',
               'objectBoxes', 'timestamp_server', 'timestamp']
connection = None
msg = None
