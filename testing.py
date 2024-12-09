import oracledb

# Database connection details
hostname = 'prophet.njit.edu'
port = 1521
sid = 'course'
username = 'kk749'
password = 'Kiri@23122001'

# Construct the DSN (Data Source Name)
dsn = oracledb.makedsn(hostname, port, sid)
connection = oracledb.connect(user=username, password=password, dsn=dsn)
cursor = connection.cursor()
cursor.execute("SELECT * FROM Branch")

# Fetch and print all rows
rows = cursor.fetchall()
print(f"Rows fetched: {len(rows)}")
print("ff")
for row in rows:
    print("ff")
    print(row)
cursor.close()
connection.close()