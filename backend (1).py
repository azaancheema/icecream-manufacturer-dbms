import cx_Oracle


def connectToOracleSchoolDB():
    try:
        userName = "D2NADEEM"
        passWord = "02037805"  # Prompt for sensitive data in production
        dsn = cx_Oracle.makedsn("oracle.scs.ryerson.ca", 1521, sid="orcl")
        connection = cx_Oracle.connect(user=userName, password=passWord, dsn=dsn)
        print("Connected to Oracle School DB")
        return connection
    except cx_Oracle.DatabaseError as e:
        print(f"Failed to connect to Oracle Database: {e}")
        return None


def viewAllTables(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT table_name FROM user_tables")
        tables = cursor.fetchall()

        if not tables:
            print("No tables found.")
            return

        print("\nAvailable Tables:")
        for i, table in enumerate(tables, start=1):
            print(f"{i}. {table[0]}")

        cursor.close()
    except cx_Oracle.DatabaseError as e:
        print(f"Error retrieving tables: {e}")

def createTable(connection):
    try:
        def isValidIdentifier(name):
            # Check if the name starts with a letter and only contains alphanumeric characters or underscores
            return name.isidentifier() and not name[0].isdigit()

        cursor = connection.cursor()

        tableName = input("Enter the table name: ").strip().upper()
        if not isValidIdentifier(tableName):
            print("Error: Table name must start with a letter and contain only alphanumeric characters or underscores.")
            return

        primaryKey = input("Enter the primary key column name: ").strip().upper()
        if not isValidIdentifier(primaryKey):
            print("Error: Primary key name must start with a letter and contain only alphanumeric characters or underscores.")
            return

        numColumns = int(input("Total Columns (including primary key): "))
        if numColumns < 1:
            print("Error: The table must have at least one column.")
            return

        columns = [primaryKey]
        for i in range(1, numColumns):
            columnName = input(f"Enter the name for column {i + 1}: ").strip().upper()
            if not isValidIdentifier(columnName):
                print(f"Error: Column name '{columnName}' is invalid. It must start with a letter and contain only alphanumeric characters or underscores.")
                return
            columns.append(columnName)

        columnDefinitions = ", ".join(f"{col} VARCHAR2(50)" for col in columns)
        columnDefinitions += f", PRIMARY KEY ({primaryKey})"

        createStatement = f"CREATE TABLE {tableName} ({columnDefinitions})"
        cursor.execute(createStatement)
        print(f"Table {tableName} created successfully.")
        cursor.close()
    except cx_Oracle.DatabaseError as e:
        print(f"Error creating table: {e}")
    except ValueError:
        print("Error: Invalid input. Please enter a valid number for the total columns.")


def populateTables(connection):
    try:
        cursor = connection.cursor()

        cursor.execute("SELECT table_name FROM user_tables")
        tables = cursor.fetchall()

        if not tables:
            print("No tables available to populate.")
            return

        print("\nAvailable Tables:")
        for i, table in enumerate(tables, start=1):
            print(f"{i}. {table[0]}")

        tableChoice = int(input("Enter the number of the table to populate: "))
        if tableChoice < 1 or tableChoice > len(tables):
            print("Cancelled.")
            return

        tableName = tables[tableChoice - 1][0]

        cursor.execute(f"SELECT * FROM {tableName}")
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]

        print(f"\nColumns in {tableName}: {', '.join(columns)}")

        while True:
            values = [input(f"Enter value for {col} (or leave blank): ") for col in columns]
            placeholders = ", ".join(f":{i + 1}" for i in range(len(columns)))
            insertQuery = f"INSERT INTO {tableName} VALUES ({placeholders})"

            try:
                cursor.execute(insertQuery, values)
                print("Record inserted successfully. Don't forget to commit your changes.")
            except cx_Oracle.DatabaseError as e:
                print(f"Error inserting record: {e}")

            more = input("Do you want to insert another record? (yes/no): ").strip().lower()
            if more != "yes":
                break

        cursor.close()
    except cx_Oracle.DatabaseError as e:
        print(f"Error populating tables: {e}")


def dropTables(connection):
    try:
        cursor = connection.cursor()

        cursor.execute("SELECT table_name FROM user_tables")
        tables = cursor.fetchall()

        if not tables:
            print("No tables available to drop.")
            return

        print("\nAvailable Tables:")
        for i, table in enumerate(tables, start=1):
            print(f"{i}. {table[0]}")

        tableChoice = int(input("Enter the number of the table to drop: "))
        if tableChoice < 1 or tableChoice > len(tables):
            print("Cancelled.")
            return

        tableName = tables[tableChoice - 1][0]
        cursor.execute(f"DROP TABLE {tableName} CASCADE CONSTRAINTS PURGE")
        print(f"Table {tableName} dropped successfully.")
        cursor.close()
    except cx_Oracle.DatabaseError as e:
        print(f"Error dropping table: {e}")


def executeUserQuery(connection, query=None):
    try:
        cursor = connection.cursor()

        if not query:
            print("Enter your SQL query (end with an empty line):")
            lines = []
            while True:
                line = input()
                if not line.strip():
                    break
                lines.append(line)
            query = " ".join(lines)

        cursor.execute(query)

        if query.lower().startswith("select"):
            results = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            print("\nQuery Results:")
            print(" | ".join(columns))
            print("-" * len(" | ".join(columns)))
            for row in results:
                print(" | ".join(map(str, row)))
        else:
            print("Query executed successfully. Don't forget to commit your changes.")

        cursor.close()
    except cx_Oracle.DatabaseError as e:
        print(f"Error executing query: {e}")



def displayQueryResults(columns, results):
    """Display query results in the terminal."""
    if results:
        print("\nQuery Results:")
        print(" | ".join(columns))
        print("-" * len(" | ".join(columns)))
        for result in results:
            print(" | ".join(map(str, result)))
    else:
        print("No results available.")


def getMultiLineQuery():
    """Accept and construct a multi-line SQL query."""
    print("Enter your SQL query (type an empty line to finish):")
    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    return " ".join(lines)


def deleteRecord(connection):
    """Delete a record from a selected table."""
    try:
        cursor = connection.cursor()
        tableName = listAndSelectTable(cursor, "Enter the number of the table to delete from")
        if not tableName:
            return

        rows, columns = displayRecords(cursor, tableName)
        if not rows:
            return

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


def listAndSelectTable(cursor, prompt="Select a table"):
    """Helper function to list and select a table."""
    cursor.execute("SELECT table_name FROM user_tables")
    tables = cursor.fetchall()
    if not tables:
        print("No tables in the database.")
        return None

    print("\nTables in the database:")
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


def displayRecords(cursor, tableName):
    """Helper function to display records of a table."""
    try:
        cursor.execute(f"SELECT * FROM {tableName}")
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]

        if rows:
            print("\nRecords in table:", tableName)
            print(" | ".join(columns))
            print("-" * len(" | ".join(columns)))
            for idx, row in enumerate(rows, start=1):
                print(f"{idx}. " + " | ".join(map(str, row)))
        else:
            print(f"No records found in table {tableName}.")
        return rows, columns
    except cx_Oracle.DatabaseError as e:
        print(f"Error: {e}")
        return [], []


def updateRecord(connection):
    """Update a record in a selected table."""
    try:
        cursor = connection.cursor()
        tableName = listAndSelectTable(cursor, "Enter the number of the table to update records")
        if not tableName:
            return

        rows, columns = displayRecords(cursor, tableName)
        if not rows:
            return

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
        updatedValues.append(selectedRecord[0])  # Primary key value for WHERE clause
        cursor.execute(updateQuery, updatedValues)
        print(f"Record updated in {tableName}. Don't forget to commit!")
    except ValueError:
        print("Invalid input. Operation cancelled.")
    except cx_Oracle.DatabaseError as e:
        print(f"Error updating record: {e}")
    finally:
        try:
            cursor.close()
        except Exception as e:
            print(f"Error closing cursor: {e}")


def searchInRecords(connection):
    """Search for a term in all or a specific table."""
    try:
        cursor = connection.cursor()
        searchTerm = input("Enter a search term: ").strip()
        found = False

        tableName = listAndSelectTable(cursor, "Select a table to search or Cancel to search all tables")
        tables = [(tableName,)] if tableName else cursor.execute("SELECT table_name FROM user_tables").fetchall()

        for table in tables:
            tableName = table[0]
            try:
                cursor.execute(f"SELECT * FROM {tableName} WHERE ROWNUM = 1")
                columns = [col[0] for col in cursor.description]

                for column in columns:
                    query = f"SELECT * FROM {tableName} WHERE LOWER({column}) LIKE :searchTerm"
                    cursor.execute(query, {"searchTerm": f"%{searchTerm.lower()}%"})
                    results = cursor.fetchall()

                    for idx, row in enumerate(results, start=1):
                        print(f"Found in table: {tableName}, column: {column}, record number: {idx}")
                        print("Record:", " | ".join(map(str, row)))
                        print("-" * 100)
                        found = True
            except cx_Oracle.DatabaseError as e:
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
