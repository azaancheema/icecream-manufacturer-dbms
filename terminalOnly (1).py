import cx_Oracle

#search/delete

def connectToOracleSchoolDB():
    try:
        
        userName = "D2NADEEM"  
        passWord = "02037805"  #should probably prompt for this
        
        
        
        dsn = cx_Oracle.makedsn("oracle.scs.ryerson.ca", 1521, sid="orcl")
        connection = cx_Oracle.connect(user=userName, password=passWord, dsn=dsn)
        
        print("Connected to Oracle School DB")
        
        return connection

    except cx_Oracle.DatabaseError as e:
        
        print("Failed to connect to Oracle:", e)
        
        return None

def viewAllTables(connection):
    try:
        cursor = connection.cursor()
        tableName = listAndSelectTable(cursor, "Enter the number of the table to view records")
        if tableName:
            _, _ = displayRecords(cursor, tableName)
        cursor.close()
    except cx_Oracle.DatabaseError as e:
        print("Error retrieving tables or records:", e)



def dropTables(connection):
    try:
        cursor = connection.cursor()

        # first list all available tables
        cursor.execute("SELECT table_name FROM user_tables")
        tables = cursor.fetchall()

        if not tables:
            print("No tables available to drop.")
            return

        # Display the list of tables
        print("\nAvailable Tables:")
        for i, table in enumerate(tables, start=1):
            print(f"{i}. {table[0]}")

        print(f"{len(tables) + 1}. Cancel")
        choice = int(input("Enter the number of the table to drop: "))

        if choice < 1 or choice > len(tables):
            print("Cancelled.")
            return

        tableName = tables[choice - 1][0]

        # Step 2: Drop the table
        cursor.execute(f"DROP TABLE {tableName} CASCADE CONSTRAINTS PURGE")
        print(f"Table {tableName} dropped successfully.")

        cursor.close()

    except cx_Oracle.DatabaseError as e:
        print(f"Error dropping table: {e}")


def createTable(connection):
    try:
        
        
        cursor = connection.cursor()


        tableName = input("Enter the table name: ").strip().upper()  # Convert table name to uppercase
        primaryKey = input("Enter the primary key column name: ").strip().upper()  #strip of whitespaces
        numColumns = int(input("Total Columns?? (including primary key)? "))


       
        columns = [primaryKey]  # Include the primary key as the first column
        for i in range(1, numColumns):
            columnName = input(f"Enter the name for column {i + 1}: ").strip().upper()
            columns.append(columnName)

        # building the statements....because of fstring we have to make it seperate 

        columnDefinitions = ", ".join(f"{col} VARCHAR2(50)" for col in columns)
        columnDefinitions += f", PRIMARY KEY ({primaryKey})"
        
        createStatement = f"CREATE TABLE {tableName} ({columnDefinitions})"
        cursor.execute(createStatement)
        print(f"Table {tableName} created successfully.")



        cursor.close()

    except cx_Oracle.DatabaseError as e:
        print(f"Error creating table: {e}")



def populateTables(connection):
    try:
        
        cursor = connection.cursor()

        #list all available tables
        cursor.execute("SELECT table_name FROM user_tables")
        tables = cursor.fetchall()

        if not tables:
            print("No tables available to populate.")
            return

        #display all
        print("\nAvailable Tables:")
        for i, table in enumerate(tables, start=1):
            print(f"{i}. {table[0]}")

        print(f"{len(tables) + 1}. Cancel")
        choice = int(input("Enter the number of the table to populate: "))

        if choice < 1 or choice > len(tables):
            print("Cancelled.")
            return

        tableName = tables[choice - 1][0]

        #show records
        print(f"\nSelected Table: {tableName}")
        cursor.execute(f"SELECT * FROM {tableName}")
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]

        print("\Current Records:")
        if rows:
            print(" | ".join(columns))
            print("-" * 50)
            for row in rows:
                print(" | ".join(str(item) for item in row))
        else:
            print("The table is empty.")


        # Step 3: Insert new records dynamically... u have to get the column names first, and then prompt the user for value
        print("\nEnter values for the columns (blank to skip):")
        
        while True:
            values = []
            for column in columns:
                value = input(f"Enter value for {column}: ").strip()
                values.append(value if value else None)


            #insert INTO statement
            placeholders = ", ".join([f":{i + 1}" for i in range(len(columns))])
            insertQuery = f"INSERT INTO {tableName} VALUES ({placeholders})"

            try:
                cursor.execute(insertQuery, values)
                print(f" Inserted row into {tableName} \n(Dont forget to commit your changes!).")
                
            except cx_Oracle.DatabaseError as e:
                print(f"Error inserting row: {e}")

            #are you done???
            more = input("Do you want to add another record? (yes/no): ").strip().lower()
            if more != "yes":
                break

        cursor.close()

    except cx_Oracle.DatabaseError as e:
        print(f"Error populating tables: {e}")



def executeUserQuery(connection, query):
    try:
        cursor = connection.cursor()
        print(f"Executing query: {query}")
        cursor.execute(query)

        #Fetch the results and column headers for SELECT queries
        if query.strip().lower().startswith("select"):
            results = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
        
        else:
            results = []
            columns = []
            print("Query executed (dont forget commit).")

        cursor.close()
        return columns, results


    except cx_Oracle.DatabaseError as e:
        print("Error executing query:", e)
        return [], []



def displayQueryResults(columns, results):
    
    if results:
        
        print("\n")
        print(" | ".join(columns))
        print("_" * (len(columns) * 15))

        for result in results:
            print(" | ".join(str(item) for item in result))

    else:
        print("Mo results available.")



#because we were using input line earlier and they only accept single lined inputs...
def getMultiLineQuery():
    
    print("Enter your SQL query (type an empty line to finish):")
    
    lines = [] #will hold all the lines
    
    while True:
        line = input()
        
        if line.strip() == "":  #enter an empty line to finish ^^
            break
        
        lines.append(line)
   
    return " ".join(lines)  #turns all we typed into a SQL query


def deleteRecord(connection):
    try:
        cursor = connection.cursor()
        tableName = listAndSelectTable(cursor, "Enter the number of the table to delete from")
        if not tableName:
            return

        rows, columns = displayRecords(cursor, tableName)
        if not rows:
            return

        try:
            recordChoice = int(input(f"\nEnter the number of the record to delete (1-{len(rows)}) or 0 to cancel: "))
            if recordChoice < 1 or recordChoice > len(rows):
                print("Cancelled.")
                return

            recordToDelete = rows[recordChoice - 1]
            primaryKeyColumn = columns[0]
            primaryKeyValue = recordToDelete[0]

            query = f"DELETE FROM {tableName} WHERE {primaryKeyColumn} = :1"
            cursor.execute(query, [primaryKeyValue])
            print(f"Record deleted from {tableName}. Don't forget to commit!")
        except ValueError:
            print("Invalid input. Operation cancelled.")

    except cx_Oracle.DatabaseError as e:
        print(f"Error deleting record: {e}")
    finally:
        try:
            cursor.close()
        except Exception as e:
            print(f"Error closing cursor: {e}")



#helper function
def listAndSelectTable(cursor, prompt="Select a table"):
    
    cursor.execute("SELECT table_name FROM user_tables")
    
    tables = cursor.fetchall()
    
    if not tables:
        print("No tables in the database.")
        return None

    print("\Tables in the database:")
    
    for i, table in enumerate(tables, start=1):
        
        print(f"{i}. {table[0]}")
        
    print(f"{len(tables) + 1}. Cancel")

    try:
        
        choice = int(input(f"{prompt}: "))
        
        if choice < 1 or choice > len(tables):
            
            print("Cancelled.")
            
            return None
        return tables[choice - 1][0]
    
    except ValueError:
        
        print("Invalid input. Operation cancelled.")
        return None






#helper function, thank me later :)
def displayRecords(cursor, tableName):
    
    try:
        
        cursor.execute(f"SELECT * FROM {tableName}")
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]


        if rows:
            print("\nRecords in table:", tableName)
            print(" | ".join(columns))
            print("-" * (len(columns) * 15))
            for idx, row in enumerate(rows, start=1):
                print(f"{idx}. " + " | ".join(str(item) for item in row))
        else:
            print(f"No records found in table {tableName}.")
        return rows, columns

    except cx_Oracle.DatabaseError as e:
        print(f"Error \n{e}")
        return [], []



def updateRecord(connection):
    try:
        cursor = connection.cursor()
        tableName = listAndSelectTable(cursor, "Enter the number of the table to update records")
        if not tableName:
            return

        rows, columns = displayRecords(cursor, tableName)
        if not rows:
            return

        try:
            recordChoice = int(input(f"\nEnter the number of the record to update (1-{len(rows)}) or 0 to cancel: "))
            if recordChoice < 1 or recordChoice > len(rows):
                print("Cancelled.")
                return

            selectedRecord = rows[recordChoice - 1]
            updatedValues = []
            setClauses = []
            print("\nEnter new values for the fields (leave blank to keep current value):")
            
            for i, column in enumerate(columns):
                currentValue = selectedRecord[i]
                newValue = input(f"{column} (current: {currentValue}): ").strip()
                if newValue:
                    updatedValues.append(newValue)
                    setClauses.append(f"{column} = :{len(updatedValues)}")

            if not setClauses:
                print("No changes made.")
                return

            updateQuery = f"UPDATE {tableName} SET {', '.join(setClauses)} WHERE {columns[0]} = :{len(updatedValues) + 1}"
            updatedValues.append(selectedRecord[0])  #primary key value for WHERE clause
            cursor.execute(updateQuery, updatedValues)
            print(f"Record updated in {tableName}. Don't forget to commit!")
        except ValueError:
            print("Invalid input. Operation cancelled.")

    except cx_Oracle.DatabaseError as e:
        print(f"Error updating record: {e}")
    finally:
        try:
            cursor.close()
        except:
            pass




def searchInRecords(connection):
    try:
        cursor = connection.cursor()

        # Prompt user for search term
        searchTerm = input("Enter a search term: ").strip()
        found = False

        # Use modular function to list and select tables if needed
        tableName = listAndSelectTable(cursor, "Select a table to search or Cancel to search all tables")

        #List the tables
        if tableName:
            tables = [(tableName,)]  # Search only the selected table
        else:
            cursor.execute("SELECT table_name FROM user_tables")
            tables = cursor.fetchall()

        # Iterate through all tables and search
        for table in tables:
            tableName = table[0]

            try:
                # col names
                cursor.execute(f"SELECT * FROM {tableName} WHERE ROWNUM = 1")
                columns = [col[0] for col in cursor.description]

                # searching through each of the columns
                for column in columns:
                    
                    query = f"SELECT * FROM {tableName} WHERE LOWER({column}) LIKE :searchTerm"
                    cursor.execute(query, {"searchTerm": f"%{searchTerm.lower()}%"})
                    results = cursor.fetchall()

                    for idx, row in enumerate(results, start=1):
                        print(f"Found in table: {tableName}\ncolumn: {column}\nrecord number: {idx}")
                        print("Record:", " | ".join(str(item) for item in row))
                        print("-" * 100)
                        found = True

            except cx_Oracle.DatabaseError as e:
                #if cant find the data/column
                print(f"Error searching in table {tableName}: {e}")

        if not found:
            print(f"No results found for term '{searchTerm}'.")

    except cx_Oracle.DatabaseError as e:
        print(f"Error searching records: {e}")

    finally:
        try:
            cursor.close()
        except Exception as e:
            print(f"Error closing cursor: {e}")





# Updated main menu
if __name__ == "__main__":

    connection = connectToOracleSchoolDB()

    if connection:

        while True:

            print("\nMenu:")
            print("1. View All Tables")
            print("2. Create Table")
            print("3. Populate Tables")
            print("4. Update/Modify a Record")
            print("5. Remove a Record")
            print("6. Search in Records")
            print("7. Execute a Query")
            print("8. Commit Changes")
            print("9. Drop Tables")
            print("10. Exit")

            choice = input("Enter your choice: ")

            if choice == "1":
                viewAllTables(connection)

            elif choice == "2":
                createTable(connection)

            elif choice == "3":
                populateTables(connection)

            elif choice == "4":
                updateRecord(connection)

            elif choice == "5":
                deleteRecord(connection)

            elif choice == "6":
                searchInRecords(connection)

            elif choice == "7":
                query = getMultiLineQuery()
                columns, results = executeUserQuery(connection, query)
                if columns and results:
                    displayQueryResults(columns, results)

            elif choice == "8":
                try:
                    connection.commit()
                    print("Changes committed successfully.")
                except cx_Oracle.DatabaseError as e:
                    print("Error committing changes:", e)

            elif choice == "9":
                dropTables(connection)

            elif choice == "10":
                print("Exiting the program.")
                break

            else:
                print("Invalid choice. Please try again.")

        connection.close()
        print("Connection closed.")

    else:
        print("Connection failed.")



# Updated main menu
if __name__ == "__main__":

    connection = connectToOracleSchoolDB()

    if connection:

        while True:

            print("\nMenu:")
            print("1. View All Tables")
            print("2. Create Table")
            print("3. Populate Tables")
            print("4. Update/Modify a Record")
            print("5. Remove a Record")
            print("6. Search in Records")
            print("7. Execute a Query")
            print("8. Commit Changes")
            print("9. Drop Tables")
            print("10. Exit")

            choice = input("Enter your choice: ")

            if choice == "1":
                viewAllTables(connection)

            elif choice == "2":
                createTable(connection)

            elif choice == "3":
                populateTables(connection)

            elif choice == "4":
                updateRecord(connection)

            elif choice == "5":
                deleteRecord(connection)

            elif choice == "6":
                searchInRecords(connection)

            elif choice == "7":
                query = getMultiLineQuery()
                columns, results = executeUserQuery(connection, query)
                if columns and results:
                    displayQueryResults(columns, results)

            elif choice == "8":
                try:
                    connection.commit()
                    print("Changes committed successfully.")
                except cx_Oracle.DatabaseError as e:
                    print("Error committing changes:", e)

            elif choice == "9":
                dropTables(connection)

            elif choice == "10":
                print("Exiting the program.")
                break

            else:
                print("Invalid choice. Please try again.")

        connection.close()
        print("Connection closed.")

    else:
        print("Connection failed.")
