# -*- coding: utf-8 -*-
from tkinter import Tk, Button, Label, Scrollbar, Listbox,StringVar, Entry, W,E,N,S,END
from tkinter import ttk
from tkinter import messagebox
from dbConfig import *
import pypyodbc as pyo


con = pyo.connect(**dbConfig)
cursor = con.cursor()
tbl = dbConfig['Table']


class SQLconnection:
    def __init__(self):
        self.con = pyo.connect(**dbConfig)
        self.cursor = con.cursor()
        print(f"You have connected to the database >> {con}")
        
    def view(self):
        sql = 'SELECT * FROM '+ tbl
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        return rows
        
def view_records():
    for row in tree.get_children():
        tree.delete(row)
    for row in dbcon.view():
        tree.insert('', 'end', values=row)


dbcon = SQLconnection()
        
col_qry = "SELECT COLUMN_NAME from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME = N'"+(tbl)+"'"
cursor.execute(col_qry)
columns = cursor.fetchall()

extracted_variables = []
for item in columns:
    extracted_variables.append(item[0])
    
root = Tk()
root.title("Database Viewer")
root.configure(background="light blue")
root.geometry("850x500")
root.resizable(width=False, height=False)


# Treeview Widget
tree = ttk.Treeview(root, columns=extracted_variables, show="headings", height=16)
tree.grid(row=3, column=0, columnspan=7, sticky=W+E, pady=25, padx=5)

# Define Columns and Headers
for header in extracted_variables:
    tree.heading(header, text=header)
    tree.column(header, width=150)


# Scrollbar for Treeview
scroll_bar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
scroll_bar.grid(row=3, column=7, sticky=W+E+N+S)
tree.configure(yscrollcommand=scroll_bar.set)

#tree.bind('<<TreeviewSelect>>', get_selected_row)
view_btn = Button(root, text="View all records", bg="green", fg="white", font="helvetica 10 bold", command=view_records)
view_btn.grid(row=15, column=1)

root.mainloop()    