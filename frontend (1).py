import tkinter as tk
from tkinter import ttk, messagebox
from backend import (
    connectToOracleSchoolDB,
    viewAllTables,
    createTable,
    populateTables,
    updateRecord,
    deleteRecord,
    searchInRecords,
    dropTables,
    executeUserQuery,
)

# Establish database connection
connection = connectToOracleSchoolDB()
if not connection:  # Check if connection is successful
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error", "Failed to connect to Oracle Database.")
    exit()

# Callbacks for operations
def onViewTables():
    viewAllTables(connection)

def onCreateTable():
    createTable(connection)

def onPopulateTables():
    populateTables(connection)

def onUpdateRecord():
    updateRecord(connection)

def onDeleteRecord():
    deleteRecord(connection)

def onSearchRecords():
    searchInRecords(connection)

def onDropTables():
    dropTables(connection)

def onExecuteQuery():
    executeUserQuery(connection, "")

def onCommitChanges():
    try:
        connection.commit()
        print("Changes committed successfully.")
    except Exception as e:
        print(f"Failed to commit changes: {e}")

# Create GUI
root = tk.Tk()
root.title("Oracle Database Management")
root.geometry("200x600")

# Main Frame
mainFrame = ttk.Frame(root, width=200, height=600)
mainFrame.pack(side=tk.LEFT, fill=tk.Y)
mainFrame.pack_propagate(False)

# Buttons for Operations
buttonWidth = 20
ttk.Button(mainFrame, text="View Tables", command=onViewTables, width=buttonWidth).pack(pady=10)
ttk.Button(mainFrame, text="Create Table", command=onCreateTable, width=buttonWidth).pack(pady=10)
ttk.Button(mainFrame, text="Populate Tables", command=onPopulateTables, width=buttonWidth).pack(pady=10)
ttk.Button(mainFrame, text="Update Record", command=onUpdateRecord, width=buttonWidth).pack(pady=10)
ttk.Button(mainFrame, text="Delete Record", command=onDeleteRecord, width=buttonWidth).pack(pady=10)
ttk.Button(mainFrame, text="Search Records", command=onSearchRecords, width=buttonWidth).pack(pady=10)
ttk.Button(mainFrame, text="Drop Tables", command=onDropTables, width=buttonWidth).pack(pady=10)
ttk.Button(mainFrame, text="Execute Query", command=onExecuteQuery, width=buttonWidth).pack(pady=10)
ttk.Button(mainFrame, text="Commit Changes", command=onCommitChanges, width=buttonWidth).pack(pady=10)
ttk.Button(mainFrame, text="Exit", command=root.destroy, width=buttonWidth).pack(pady=10)

# Run GUI
root.mainloop()
