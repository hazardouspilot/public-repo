from Database_Class import BWDB
from datetime import datetime

GLOBALS = {}
MY_HOST = "localhost"
MY_USER = "root"
MY_PASS = "ClimbingShoes"
DATABASE = "climbing_mysql"

def connect():
    db = BWDB(
        dbms="mysql", host=MY_HOST, user=MY_USER, password=MY_PASS, database=DATABASE
    )

    GLOBALS["db"] = db
    return db

def do_menu():
    while True:
        menu = (
            "A) Add Attempt",
            "R) Add Route",
            "V) View Attempts",
            "Q) Quit",
        )
        print()
        for s in menu:
            print(s)
        response = input("Select an action or Q to quit > ").upper()
        if len(response) != 1:
            print("\nInput too long or empty")
            continue
        elif response in "ARVQ":
            break
        else:
            print("\nInvalid response")
            continue
    return response


def jump(response):
    if response == "A":
        add_attempt()
    elif response == "R":
        add_route()
    elif response == "V":
        view_attempts()
    else:
        print("jump: invalid argument")
    return


def input_privacy_pref():
    db = GLOBALS["db"]
    print("Valid privacy preferences include: ")
    query = "SELECT PrivacyPref FROM privacyprefs"
    options = db.sql_query(query)
    options_list = list(options)
    for pref in options_list:
        print(pref[0])
    user_input = "x"
    while user_input not in [pref[0] for pref in options_list]:
        user_input = input("Enter privacy preference: ")
    return user_input


def input_CID():
    db = GLOBALS["db"]
    search_again = "Y"
    while search_again.upper() == "Y":
        name = input("Enter your last name: ")
        query = f"SELECT CID, FirstName, LastName, Alias FROM climbers WHERE LastName = '{name}'"
        rows = db.sql_query(query)
        x = 0
        for row in rows:
            x += 1
            print(row)
        in_list = "x"
        if x == 0:
            in_list = "N"
            print("That last name does not appear in our list of users")
        # if in the list, enter CID, if not, search again or enter new details
        while in_list.upper() not in "YN":
            in_list = input("Are you in the above list [Y/N] ? ")
        if in_list.upper() == "Y":
            CID = input("Enter the number beside your name: ")  # error proof this later
            search_again = "N"
            return CID
        else:
            search_again = "x"
            while search_again.upper() not in "YN":
                search_again = input(
                    "Would you like to search for your name again? [Y/N]"
                )
    if in_list.upper() == "N":
        firstName = input("Enter your first name: ")
        lastName = input("Enter your last name: ")
        alias = input("Enter your alias: ")
        privacyPref = input_privacy_pref()
        access = "Regular"
        email = input("Enter your email address: ")
        fb = input("Enter your Facebook url or leave blank: ")
        ig = input("Enter your Instagram url or leave blank: ")
        yt = input("Enter your YouTube url or leave blank: ")
        x = input("Enter your Twitter url or leave blank: ")
        CID = list(db.sql_query("SELECT max(CID) FROM climbers"))[0][0] + 1

        query3 = """INSERT INTO climbers (CID, FirstName, LastName, Alias, 
                                    PrivacyPref, Access, Email, FB, Insta, YT, X) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        data = (
            CID,
            firstName,
            lastName,
            alias,
            privacyPref,
            access,
            email,
            fb,
            ig,
            yt,
            x,
        )
        count = db.sql_do(query3, data)
        print(f"{count} row/s added to the climbers table")
        return CID


def input_company():
    db = GLOBALS["db"]
    print("Valid company names include: ")
    query = "SELECT CompanyName FROM companys"
    options = db.sql_query(query)
    options_list = list(options)
    for company in options_list:
        print(company[0])
    user_input = "x"
    while user_input not in [company[0] for company in options_list]:
        user_input = input("Enter company: ")
    return user_input


def input_gym(company):
    db = GLOBALS["db"]
    print("Valid gym names include: ")
    query = f"SELECT Suburb FROM gyms WHERE CompanyName = '{company}'"
    options = db.sql_query(query)
    options_list = list(options)
    for suburb in options_list:
        print(suburb[0])
    user_input = "x"
    while user_input not in [suburb[0] for suburb in options_list]:
        user_input = input("Enter gym: ")
    return user_input


def input_type():
    db = GLOBALS["db"]
    print("Valid types include: ")
    query = "SELECT * FROM type_table"
    options = db.sql_query(query)
    options_list = list(options)
    for type in options_list:
        print(type[0])

    user_input = "x"
    while user_input not in [type[0] for type in options_list]:
        user_input = input("Enter type: ")
    return user_input


def input_location(company, gym, climb_type):
    db = GLOBALS["db"]
    print("Valid locations include: ")
    if climb_type == "Boulder":
        query = f"SELECT Location FROM locations WHERE CompanyName = '{company}' AND Suburb = '{gym}' AND Location REGEXP '^[a-zA-Z]+$'"
    elif climb_type == "Sport":
        query = f"SELECT Location FROM locations WHERE CompanyName = '{company}' AND Suburb = '{gym}' AND Location REGEXP '^[0-9]+$'"
    options = db.sql_query(query)
    options_list = list(options)
    for location in options_list:
        print(location[0])
    user_input = "x"
    while user_input not in [location[0] for location in options_list]:
        user_input = input("Enter location: ")
    return user_input


def input_grade(gradeSystem):
    db = GLOBALS["db"]
    print("Valid grades include: ")
    query = f"SELECT Grade FROM grades WHERE GradingSystem = '{gradeSystem}'"
    options = db.sql_query(query)
    options_list = list(options)
    for grade in options_list:
        print(grade[0])

    user_input = "x"
    while user_input not in [grade[0] for grade in options_list]:
        user_input = input("Enter grade: ")
    return user_input


def input_mode():
    db = GLOBALS["db"]
    print("Valid modes include: ")
    query = "SELECT Mode_column FROM modes"
    options = db.sql_query(query)
    options_list = list(options)
    for mode in options_list:
        print(mode[0])

    user_input = "x"
    while user_input not in [mode[0] for mode in options_list]:
        user_input = input("Enter mode: ")
    return user_input


def get_grade_system(company, climb_type):
    db = GLOBALS["db"]
    query = f"SELECT * FROM companys WHERE CompanyName = '{company}'"
    db.table = "companys"
    gradeSystem = None
    if climb_type == "Boulder":
        gradeSystem = list(db.sql_query(query))[0][1]
    elif climb_type == "Sport":
        gradeSystem = list(db.sql_query(query))[0][2]
    print(f"The grading system for this problem is {gradeSystem}")
    return gradeSystem


def input_route_details():
    company = input_company()
    gym = input_gym(company)
    climb_type = input_type()
    location = input_location(company, gym, climb_type)
    gradeSystem = get_grade_system(company, climb_type)
    grade = input_grade(gradeSystem)
    colour = input("Enter colour of holds: ")
    return company, gym, climb_type, location, gradeSystem, grade, colour


def input_attempt_no(route_ID):
    db = GLOBALS["db"]
    # check highest attempt number for this climber and this route and get a higher number from user
    query = f"SELECT max(AttemptNo) FROM attempts WHERE CID = '{db.climber_ID}' AND RID = '{route_ID}' GROUP BY CID"
    try:
        max_attempts = db.sql_query_value(query)
    except:
        max_attempts = 0
    attempt_no = 0
    while str(attempt_no).isnumeric() == False or int(attempt_no) <= max_attempts:
        attempt_no = input(
            f"You have made {max_attempts} attempts at this problem, enter the number of this attempt: "
        )
    return attempt_no


def input_result():
    db = GLOBALS["db"]
    print("Valid results include: ")
    query = "SELECT Result FROM results"
    options = db.sql_query(query)
    options_list = list(options)
    for result in options_list:
        print(result[0])

    user_input = "x"
    while user_input not in [result[0] for result in options_list]:
        user_input = input("Enter mode: ")
    return user_input


def add_route(
    company=None,
    gym=None,
    climb_type=None,
    location=None,
    gradeSystem=None,
    grade=None,
    colour=None,
):
    print("Add Route")
    db = GLOBALS["db"]
    if company is None:
        (
            company,
            gym,
            climb_type,
            location,
            gradeSystem,
            grade,
            colour,
        ) = input_route_details()
    new_ID = list(db.sql_query("SELECT max(RID) FROM routes"))[0][0] + 1
    query3 = """INSERT INTO routes (RID, CompanyName, Suburb, Location, 
                                    GradingSystem, Grade, Type_column, Colour, Existing) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    data = (new_ID, company, gym, location, gradeSystem, grade, climb_type, colour, 1)
    count = db.sql_do(query3, data)
    print(f"{count} row/s added to the routes table")


def add_attempt():
    print("Add Attempt")
    db = GLOBALS["db"]
    (
        company,
        gym,
        climb_type,
        location,
        gradeSystem,
        grade,
        colour,
    ) = input_route_details()
    # check if this is an existing route, if not, create it
    db.table = "routes"
    query = f"SELECT * FROM routes WHERE CompanyName = '{company}' AND Suburb = '{gym}' AND Location = '{location}' AND Grade = '{grade}' AND Colour = '{colour}' AND Existing = 1"
    row = db.sql_query_row(query)
    if row:
        route_ID = row[0]
    else:
        add_route(company, gym, climb_type, location, gradeSystem, grade, colour)
        route_ID = list(db.sql_query("SELECT max(RID) FROM routes"))[0][0]
    # ask if existing routes at this location are still there
    route_rows_same_location = db.find_rows("Location", location)
    for row_id in route_rows_same_location:
        if row_id != route_ID:
            print(row)
            existing = "x"
            while existing.upper() not in "YN":
                existing = input(
                    "Is the above problem still present at this location? [y/n]"
                )
            if existing.upper() == "N":
                db.update_row(row[0], {"Existing": 0})
    # if sport route get mode
    mode = None
    if climb_type == "Sport":
        mode = input_mode()
    attempt_no = input_attempt_no(route_ID)
    current_date = datetime.now()
    date = current_date.strftime("%Y-%m-%d")
    result = input_result()
    rating = -1
    while str(rating).isnumeric() == False or int(rating) > 5 or int(rating) < 0:
        rating = input(
            "Enter your rating for this route from 1 to 5, or enter 0 to omit a rating: "
        )
    notes = input("Enter any notes about your attempt or leave blank: ")
    query3 = """INSERT INTO attempts (CID, RID, Mode_column, AttemptNo, Date_column, 
                                    Result, Rating, Notes) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
    data = (db.climber_ID, route_ID, mode, attempt_no, date, result, rating, notes)
    count = db.sql_do(query3, data)
    print(f"{count} row/s added to the attempts table")


def view_attempts():
    print("View Attempts")
    db = GLOBALS["db"]
    query = """
            SELECT a.Date_column, r.Grade, a.Mode_column, r.Location, a.Result, a.AttemptNo, r.CompanyName, r.Suburb
            FROM attempts a JOIN routes r ON r.RID = a.RID
            ORDER BY r.Grade DESC
            """
    rows = db.sql_query(query)
    for row in rows:
        print(row)


def main():
    connect()
    db = GLOBALS["db"]
    db.climber_ID = input_CID()
    while True:
        response = do_menu()
        if response == "Q":
            print("Quitting.")
            exit(0)
        else:
            print()  # blank line
            jump(response)


if __name__ == "__main__":
    main()

# import sys
# print(sys.executable)
