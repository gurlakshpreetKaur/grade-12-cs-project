import mysql.connector
from datetime import date
from contextlib import contextmanager
#library management system

BOOKS_STRUCTURE = { #structure of books table
    "isbn": str, # PRIMARY KEY char
    "book_name": str, # varchar
    "author_name": str, #varchar
    "genre": str, # varchar
    "year_of_publishing": int, # int
    "date_of_entry": str, #date
    }

#structure of members table
MEMBERS_STRUCTURE = {
    "id": str, #PRIMARY KEY
    "phone": str,
    "email": str,
    "address": str,
    "joining_date": str,
    }

ISSUES_STRUCTURE = {
    "id": str, # PRIMARY KEY
    "book_isbn": str,
    "member_id": str,
    "date_of_issue": str,
    "issue_duration": int, #in days
    "returned": int
    }

QUERY_OPERS = {
    1: ("EQUAL TO", "="),
    2: ("GREATER THAN", ">"),
    3: ("LESSER THAN", "<"),
    4: ("GREATER THAN OR EQUAL TO", ">="),
    5: ("LESSER THAN OR EQUAL TO", "<="),
    6: ("NOT EQUAL TO", "<>"),
    7: ("IN", "IN"),
    8: ("NOT IN", "NOT IN"),
    9: ("BETWEEN", "BETWEEN"),
    10: ("NOT BETWEEN", "NOT BETWEEN"),
    }
QUERY_OPERS_STR = {**QUERY_OPERS,
    (len(QUERY_OPERS)+1): ("PATTERN MATCHES (LIKE)", "LIKE"),
    (len(QUERY_OPERS)+2): ("DOES NOT PATTERN MATCH (NOT LIKE)", "NOT LIKE")
    }

CONFIG = { #configuration for sql connection
    "host":"localhost",
    "user":"root",
    "passwd":"root",
    "database":"library"
    }
#@contextmanager #this is a decorator. it turns the conn function into a context manager, so conn can be used with the 'with' statement. think: async functions in js using then function
def execute(statement, params=None):
    #'''Context manager for setting up an SQL connection and yielding the cursor object'''
    #already created a library database in SQL using CREATE DATABASE library
    conn = None
    try:
        conn = mysql.connector.connect(**CONFIG)

        if conn.is_connected():
            cursor = conn.cursor(dictionary=True) #formats the returned values as list of dictionary
            #yield cursor #this is the object that will be used in the 'with' statement
            cursor.execute(statement, params)
            if statement.startswith("SELECT"): #statement is select type
                return cursor.fetchall() #return the dataset
            else:
                conn.commit()
    except mysql.connector.Error as e:
        print(f"!!!SQL ERROR OCCURED: {e}!!!")
    finally:
        if conn is not None and conn.is_connected():
            conn.close() #safely closing the connection each time

def presentable(key, case="upper"):
    '''Takes a dictionary key and makes it presentable by replacing the _ with spaces and changing case'''
    if case=="lower":
        return " ".join(key.split("_")).lower()
    elif case=="title":
        return " ".join(key.split("_")).title()
    return " ".join(key.split("_")).upper()

def view_all_books():
    '''Prints the entire list of books in the library.'''
    data = execute("SELECT * FROM books")
    if len(data) == 0:
        print("NO BOOKS' DATA STORED YET")
        return
    for i in range(len(data)):
        print(data[i])
    
def view_books_with_query():
    '''Inputs a key and value, and uses that to query the database and shows specific books'''
    query = ""
    attributes = list(BOOKS_STRUCTURE.keys())

    while True:
        print("Attributes list:")
        for i in range(len(attributes)):
            print(f'-- {i+1}. {attributes[i]}')
        key_num = int(input("Enter the attribute number to query with: "))
        if key_num not in range(1, len(attributes) + 1):
            print("INVALID ATTRIBUTE NUMBER")
            continue
        key = attributes[key_num - 1]
        typecast = BOOKS_STRUCTURE.get(key) #tells us the type of this attribute
        is_str = typecast == str #allows us to make special arrangements to suit strings

        print()
 
        print("Opeators list:")
        opers_for_key = QUERY_OPERS_STR if is_str else QUERY_OPERS #includes LIKE and NOT LIKE operators that only work on strings
        for i in range(1, len(opers_for_key) + 1):
            print(f"-- {i} {opers_for_key.get(i)[0]}")
        comparision = int(input("Enter the operator number of your choice : "))
        if comparision not in opers_for_key:
            print("!!!INVALID OPERATOR, PLEASE ENTER A VALID OPERATOR!!!")
            continue
        oper = opers_for_key.get(comparision)[1]

        print()
       
        if oper in ["IN","NOT IN"]:
            values = []
            while True:
                check = input("Enter a value from value set: ")
                values.append(f'"{check}"' if is_str else check)
                if input("Add another value to the set? (Y for yes): ").lower()!="y":
                    break
            value="(" + ",".join(values) + ")" #convert to sql friendly form
        elif oper in ["BETWEEN", "NOT BETWEEN"]:
            start = input("Enter the start value: ")
            end = input("Enter the end value: ")
            start = f'"{start}"' if is_str else start
            end = f'"{end}"' if is_str else end
            value = f'{start} AND {end}'
        else:
            value = input("Enter the value to compare it with: ")
            value = f'"{value}"' if is_str else value #make it into a string with quotes added for querying purpose
        query += f"{key} {oper} {value}"
        if (input("Enter another contraint? (Y for yes): ").lower() != "y"):
            break
        else:
            query += " AND "
    print()
    
    statement = "SELECT * FROM books WHERE %s"
    data = execute(statement, (query,))
    print(data)
    for i in range(len(data)):
        print(data)
    
def view_book_with_isbn():
    '''Inputs an ISBN and uses it to show the book's data'''
    isbn = input("Enter the ISBN: ")
    statement = "SELECT * FROM books WHERE isbn=%s;"
    execute(statement, (isbn,))
    #print(statement)

def add_book():
    '''Inputs data related to the book and adds it to the database'''
    book_data = {
        "date_of_entry":  date.today().isoformat()
        }
    for key in BOOKS_STRUCTURE:
        if key in book_data:
            continue
        typecast = BOOKS_STRUCTURE.get(key)
        #is_str = typecast == str
        value = typecast(input("Enter the " + presentable(key) + ":")) #typecast ensures that data is in correct format
        #then we convert it to string in order to obtain the correct format for sql
        book_data[key] = value
    
    columns = "(" + ",".join(list(book_data.keys())) + ")"
    values_placeholder=", ".join(["%s"] * len(book_data))
    
    statement = f"INSERT INTO books {columns} VALUES ({values_placeholder});" 
    
    values = tuple(book_data.values())
    execute(statement, values)
    
    print(statement)
    
def remove_book_with_isbn():
    '''Inputs the ISBN of a book and deletes its data from the database'''
    isbn = input("Enter the ISBN: ")
    statement = f'DELETE FROM books WHERE isbn="{isbn}";'
    print(statement)
    
def update_book_data_with_isbn():
    '''Inputs the ISBN of a book and updates its data'''
    isbn = input("Enter the ISBN: ")
    data = {}
    attributes = list(BOOKS_STRUCTURE.keys())
    attributes.remove("isbn") #can't update primary key
    while True:
        print("ATTRIBUTES:")
        for i in range(len(attributes)):
            print(f"{i+1} {presentable(attributes[i])}")
            
        key_num = int(input("Enter the attribute number which you want to update: "))
        if key_num not in range(1, len(attributes)+1):
            print("!!!INVALID ATTRIBUTE NUMBER, PLEASE ENTER A VALID ATTRIBUTE NUMBER")
            continue
        key = attributes[key_num - 1]
        typecast = BOOKS_STRUCTURE[key]
        is_str = typecast == str
        
        value= str(typecast(input("Enter the value you want to update it to: ")))
        if is_str:
            data[key] = f'"{value}"' #add quotes if the field type is string
        else:
            data[key] = value

        if input("Update another field? (enter Y for yes): ").lower() != "y":
            break
    updates = []
    for key in data:
        updates.append(f"{key}={data[key]}")
    update_str = ",".join(updates)
    statement = f"UPDATE books SET {update_str} WHERE isbn='{isbn}'"
    print(statement)

def view_all_members():
    '''Displays the data of all members'''
    statement = "SELECT * FROM members;"
    print(statement)

def view_member_with_id():
    '''Inputs the ID of a member and displays their data'''
    member_id = input("Enter the member ID:")
    statement = f'SELECT * FROM members WHERE id="{member_id}";'
    print(statement)

def update_member_data_with_id():
    '''Inputs the ID of a member and updates its data'''
    id = input("Enter the ID: ")
    data = {}
    attributes = list(MEMBERS_STRUCTURE.keys())
    attributes.remove("id") #can't update primary key
    while True:
        print("ATTRIBUTES:")
        for i in range(len(attributes)):
            print(f"{i+1} {presentable(attributes[i])}")
            
        key_num = int(input("Enter the attribute number which you want to update: "))
        if key_num not in range(1, len(attributes)+1):
            print("!!!INVALID ATTRIBUTE NUMBER, PLEASE ENTER A VALID ATTRIBUTE NUMBER!!!")
            continue
        key = attributes[key_num - 1]
        typecast = MEMBERS_STRUCTURE[key]
        is_str = typecast == str
        
        value= str(typecast(input("Enter the value you want to update it to: ")))
        if is_str:
            data[key] = f'"{value}"' #add quotes if the field type is string
        else:
            data[key] = value

        if input("Update another field? (enter Y for yes): ").lower() != "y":
            break
    updates = []
    for key in data:
        updates.append(f"{key}={data[key]}")
    update_str = ",".join(updates)
    statement = f"UPDATE members SET {update_str} WHERE id='{id}'"
    print(statement)

def add_member():
    '''Inputs data related to the member and adds it to the database'''
    member_data = {
        "joining_date": f'"{date.today().isoformat()}"'
        }
    for key in MEMBERS_STRUCTURE:
        if key in member_data:
            continue
        typecast = MEMBERS_STRUCTURE.get(key)
        is_str = typecast == str
        value = str(typecast(input("Enter the " + presentable(key) + ":")))
        member_data[key] = value if not is_str else f'"{value}"'
    statement = "INSERT INTO members "
    columns = "(" + ",".join(list(member_data.keys())) + ")"
    values = "(" + ",".join(list(member_data.values())) + ")"
    statement = statement + columns + " VALUES " + values + ";"
    print(statement)

def remove_member_with_id():
    '''Inputs the ID of a member and deletes its data from the database'''
    id = input("Enter the ID: ")
    statement = f'DELETE FROM members WHERE id="{id}";'
    print(statement)

def view_members_with_query():
    '''Inputs a key and value, and uses that to query the database and shows specific members'''
    query = ""
    attributes = list(MEMBERS_STRUCTURE.keys())

    while True:
        print("Attributes list:")
        for i in range(len(attributes)):
            print(f'-- {i+1}. {attributes[i]}')
        key_num = int(input("Enter the attribute number to query with: "))
        if key_num not in range(1, len(attributes) + 1):
            print("!!!INVALID ATTRIBUTE NUMBER, PLEASE ENTER A VALID ATTRIBUTE NUMBER!!!")
            continue
        key = attributes[key_num - 1]
        typecast = MEMBERS_STRUCTURE.get(key) #tells us the type of this attribute
        is_str = typecast == str #allows us to make special arrangements to suit strings

        print()
 
        print("Opeators list:")
        opers_for_key = QUERY_OPERS_STR if is_str else QUERY_OPERS #includes LIKE and NOT LIKE operators that only work on strings
        for i in range(1, len(opers_for_key) + 1):
            print(f"-- {i} {opers_for_key.get(i)[0]}")
        comparision = int(input("Enter the operator number of your choice : "))
        if comparision not in opers_for_key:
            print("INVALID OPERATOR")
            continue
        oper = opers_for_key.get(comparision)[1]

        print()

        if oper in ["IN","NOT IN"]:
            values = []
            while True:
                check = input("Enter a value from value set: ")
                values.append(f'"{check}"' if is_str else check)
                if input("Add another value to the set? (Y for yes): ").lower()!="y":
                    break
            value="("+",".join(values)+")" #convert to sql friendly form
        elif oper in ["BETWEEN", "NOT BETWEEN"]:
            start = input("Enter the start value: ")
            end = input("Enter the end value: ")
            start = f'"{start}"' if is_str else start
            end = f'"{end}"' if is_str else end
            value = f'{start} AND {end}'
        else:
            value = input("Enter the value to compare it with: ")
            value = f'"{value}"' if is_str else value #make it into a string with quotes added for querying purpose
        query += f"{key} {oper} {value}"
        if (input("Enter another contraint? (Y for yes): ").lower() != "y"):
            break
        else:
            query += " AND "
    print()
    statement = "SELECT * FROM members WHERE " + query
    print(statement)

def issue_book():
    '''Inputs data related to the issue and adds it to the database'''
    issue_data = {
        "date_of_issue": f'"{date.today().isoformat()}"',
        "returned": 0, #False
        }
    for key in ISSUES_STRUCTURE:
        if key in issue_data:
            continue
        typecast = ISSUES_STRUCTURE.get(key)
        is_str = typecast == str
        value = str(typecast(input("Enter the " + presentable(key) + ":")))
        issue_data[key] = value if not is_str else f'"{value}"'

    #check if book with given isbn exists
    
    #check if user with given isbn exists
        
    statement = "INSERT INTO issues "
    columns = "(" + ",".join(list(issue_data.keys())) + ")"
    values = "(" + ",".join(list(issue_data.values())) + ")"
    statement = statement + columns + " VALUES " + values + ";"
    
    print(statement)

def return_book():
    '''Updates the issue so that it is no longer pending'''
    issue_id = input("Enter the issue id: ")
    statement = f'UPDATE issues SET returned=1 WHERE id="{issue_id}";'
    print(statement)

COMMANDS = {
    1: view_all_books,
    2: view_books_with_query,
    3: view_book_with_isbn,
    4: add_book,
    5: remove_book_with_isbn,
    6: update_book_data_with_isbn,
    7: view_all_members,
    8: view_member_with_id,
    9: update_member_data_with_id,
    10: issue_book,
    11: return_book,
    12: add_member,
    13: remove_member_with_id,
    14: view_members_with_query
    }

def menu():
    print("+-------------------------------------------------------------------------+")
    print("|                                                                         |")
    print("|-----------------------LIBRARY MANAGEMENT SYSTEM-------------------------|")
    print("|-------------*Through this programme you can manage a library*-----------|")
    print("|                        ****************************                     |")
    print("|                                ~~OPTIONS~~                              |")
    print("| ***1  => View all books                                                 |")
    print("| ***2  => View books with query                                          |")
    print("| ***3  => View book with ISBN                                            |")
    print("| ***4  => Add book                                                       |")
    print("| ***5  => Remove book with ISBN                                          |")
    print("| ***6  => Update book data with ISBN                                     |")
    print("| ***7  => View all members                                               |")
    print("| ***8  => View member with member ID                                     |")
    print("| ***9  => Update member data with member ID                              |")
    print("| ***10 => Issue a book                                                   |")
    print("| ***11 => Return a book                                                  |")
    print("| ***12 => Add a member                                                   |")
    print("| ***13 => Remove member with ID                                          |")
    print("| ***14 => View members with query                                        |")
    print("| ***15 => EXIT                                                           |")
    print("+-------------------------------------------------------------------------+")
    choice = int(input("Enter your choice: "))
    if choice in COMMANDS:
        action = COMMANDS.get(choice)
        action()
    elif choice==15:
        return 1
    else:
        print("Invalid choice. Please enter a number from the options given above")

def main():
    while True:
        br = menu()
        if br == 1:
            print("+-------------------------------------------------------------------------+")
            print("|                      *Programme execution over*                         |")
            print("|                       ~~Thank you for using~~                           |")
            print("+-------------------------------------------------------------------------+")
            break

main()
