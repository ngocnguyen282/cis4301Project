from flask import Flask, render_template, request, redirect, url_for
from validate_email import validate_email
import matplotlib.pyplot as plt
import getpass
import bcrypt
import oracledb

app = Flask(__name__)

# Function to establish database connection
def get_db_connection():
    un = 'nm.nguyen'
    cs = 'oracle.cise.ufl.edu/orcl'
    pw = '08N30XwYLBx4DUFWBuCUkzwH'
    connection = oracledb.connect(user=un, password=pw, dsn=cs)
    return connection

# Function to validate an email address
def is_valid_email(email):
    return validate_email(email)

# Function to check if a username or email exists in the database
def is_user_unique(identifier):
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT COUNT(*) FROM Users WHERE usersname = :1 OR usersEmail = :1"
                cursor.execute(sql, (identifier, identifier))
                count = cursor.fetchone()[0]
                return count == 0
    except oracledb.Error as error:
        print("An error occurred:", error)
        return False


# Function to check if user has at least 8 characters for password
def validate_password_length(password):
        return len(password) >= 8

# Function to validate form data
def validate_form_data(username, email, password):
    if not username or not email or not password:
        return False, "All fields are required."
    elif not is_valid_email(email):
        return False, "Invalid email address."
    elif not is_user_unique(username):
        return False, "Username already exists."
    elif not is_user_unique(email):
        return False, "Email already exists."
    # elif not validate_password_length(password):
    #     return False, "Password must be at least 8 characters long."
    return True, None

# Function to hash a password
def hash_password(password):
    # Hash the password using bcrypt's hashpw function
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')

# Function to authenticate user login
def authenticate_user(username, password):
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                # Retrieve the hashed password associated with the username from the database
                sql = "SELECT usersPassword FROM Users WHERE usersname = :1"
                cursor.execute(sql, (username,))
                hashed_password = cursor.fetchone()

                if hashed_password:
                    # Extract the hashed password from the result
                    hashed_password = hashed_password[0]

                    # Compare the hashed password with the input password
                    if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                        return True, None
                    else:
                        return False, "Password incorrect"
                else:
                    return False, "Username not found!"

    except oracledb.Error as error:
        print("An error occurred:", error)
        return False

# Route for rendering the HTML page and performing database insert
@app.route("/")
def index():
    return redirect(url_for('query1'))

@app.route("/signUp", methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        username = request.form['Username']
        email = request.form['Email']
        password = request.form['Password']

        # Validate form data
        is_valid, error_message = validate_form_data(username, email, password)
        if not is_valid:
            return render_template("signUp.html", error=error_message)

        try:
            # Hash the password
            password = hash_password(password)

            # Establish database connection
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    # SQL query to insert data into a table
                    sql = """INSERT INTO Users (usersname, usersEmail, usersPassword) VALUES (:1, :2, :3)"""

                    # Execute the SQL query
                    cursor.execute(sql, (username, email, password))
                    connection.commit()

            return render_template("logIn.html")

        except oracledb.Error as error:
            # Handle database connection or query errors
            return f"An error occurred: {error}"

    # Render the HTML template
    return render_template("signUp.html")

@app.route("/logIn", methods=['GET', 'POST'])
def logIn():
    if request.method == 'POST':
        username = request.form['Username']
        password = request.form['Password']

        # Authenticate user login
        authentication_result = authenticate_user(username, password)
        if authentication_result is not None:
            authenticated, error_message = authentication_result
            if authenticated:
                # Redirect to a different URL upon successful login
                return redirect(url_for('query1'))
            else:
                # Authentication failed, render login form with error message
                return render_template("logIn.html", error=error_message)
        else:
            # Handle the case where authentication_result is None
            error_message = "An unexpected error occurred during authentication."
            return render_template("logIn.html", error=error_message)

        # Render the HTML template for the login form
    return render_template("logIn.html")

# Route for rendering query1.html and generating data for the bar graph
@app.route("/query1", methods=['GET', 'POST'])
def query1():
    Y_value = request.form.get('Y')

    if Y_value is not None:
        sql = f"""SELECT playlists.pid, playlists.modified_at, playlists.name, playlists.num_followers, playlists.duration_ms
            FROM JORDANGREENE.playlists
            WHERE modified_at >= 1513728000 - (157680000) --number in parentheses is X years
            ORDER BY num_followers, duration_ms DESC
            FETCH FIRST {Y_value} ROWS ONLY --number here is top Y songs
        """

        # Execute the SQL query
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(sql)

        # Fetch the results
        data = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()
    else:
        # Handle the case where Y_value is None
        data = []

    # Render the query1.html template with the fetched data
    return render_template('query1.html', data=data)

# Route for rendering query2.html and generating data for the bar graph
@app.route("/query2", methods=['GET', 'POST'])
def query2():
    Y_value = request.form.get('Y')

    if Y_value is not None:
        sql = f"""SELECT playlists.pid, playlists.modified_at, playlists.name, playlists.num_followers, playlists.duration_ms
            FROM JORDANGREENE.playlists
            WHERE modified_at >= 1513728000 - (157680000) --number in parentheses is X years
            ORDER BY num_followers DESC
            FETCH FIRST {Y_value} ROWS ONLY --number here is top Y songs   
        """

        # Execute the SQL query
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(sql)

        # Fetch the results
        data = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()
    else:
        # Handle the case where Y_value is None
        data = []

    # Render the query1.html template with the fetched data
    return render_template("query2.html", data=data)

# Route for rendering query3.html and generating data for the bar graph
@app.route("/query3", methods=['GET', 'POST'])
def query3():
    Y_value = request.form.get('Y')

    if Y_value is not None:
        sql = f"""SELECT playlists.pid, playlists.modified_at, playlists.name, playlists.num_followers, playlists.duration_ms
            FROM JORDANGREENE.playlists
            WHERE modified_at >= 1513728000 - (157680000) --number in parentheses is X years
            ORDER BY num_followers DESC
            FETCH FIRST {Y_value} ROWS ONLY --number here is top Y songs   
        """

        # Execute the SQL query
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(sql)

        # Fetch the results
        data = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()
    else:
        # Handle the case where Y_value is None
        data = []

    # Render the query1.html template with the fetched data
    return render_template("query3.html", data=data)

# Route for rendering query4.html and generating data for the bar graph
@app.route("/query4", methods=['GET', 'POST'])
def query4():
    Y_value = request.form.get('Y')

    if Y_value is not None:
        sql = f"""SELECT playlists.pid, playlists.modified_at, playlists.name, playlists.num_followers, playlists.duration_ms
            FROM JORDANGREENE.playlists
            WHERE modified_at >= 1513728000 - (157680000) --number in parentheses is X years
            ORDER BY num_followers DESC
            FETCH FIRST {Y_value} ROWS ONLY --number here is top Y songs   
        """

        # Execute the SQL query
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(sql)

        # Fetch the results
        data = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()
    else:
        # Handle the case where Y_value is None
        data = []

    # Render the query1.html template with the fetched data
    return render_template("query4.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)
