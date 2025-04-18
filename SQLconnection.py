# db_viewer.py
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pypyodbc as pyo
from dbConfig import *


class DatabaseHandler:
    def __init__(self, config):
        try:
            self.connection = pyo.connect(**config)
            self.cursor = self.connection.cursor()
            self.table = config['Table']
            print(f"[INFO] Connected to database: {self.table}")
        except Exception as e:
            messagebox.showerror("Database Connection Error", str(e))
            raise

    def get_columns(self):
        query = f"""
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = N'{self.table}'
        """
        self.cursor.execute(query)
        return [col[0] for col in self.cursor.fetchall()]

    def fetch_all(self):
        try:
            query = f"SELECT * FROM {self.table}"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Query Error", str(e))
            return []


class App:
    def __init__(self, root, db_handler):
        self.root = root
        self.db = db_handler
        self.columns = self.db.get_columns()

        self.root.title("📊 Database Viewer")
        self.root.geometry("950x700")
        self.root.configure(bg="#f0f4f7")
        self.root.resizable(False, False)

        self.status_var = tk.StringVar()
        self._setup_styles()
        self._build_layout()
        self._bind_shortcuts()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=('Helvetica', 11, 'bold'), background="#2c3e50", foreground="white")
        style.configure("Treeview", font=('Helvetica', 10), rowheight=24, background="white", fieldbackground="white")

    def _build_layout(self):
        # Title
        ttk.Label(self.root, text="📁 Database Table Viewer", font=("Helvetica", 16, "bold"),
                  background="#f0f4f7", foreground="#2c3e50").grid(row=0, column=0, columnspan=8, pady=10)

        # Treeview
        self.tree = ttk.Treeview(self.root, columns=self.columns, show="headings", height=14)
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor="center")
        self.tree.grid(row=1, column=0, columnspan=7, padx=10, pady=10, sticky="nsew")

        scroll = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.grid(row=1, column=7, sticky="ns")

        # View All Button
        ttk.Button(self.root, text="🔍 View All Records", command=self.view_records).grid(row=2, column=0, padx=10, pady=5, sticky="w")

        # SQL Editor Label
        ttk.Label(self.root, text="🧠 Custom SQL Query:", background="#f0f4f7", font=("Helvetica", 11, "bold")).grid(row=3, column=0, columnspan=8, padx=10, sticky="w")

        # SQL Editor
        self.query_text = scrolledtext.ScrolledText(self.root, width=115, height=5, font=("Courier New", 10))
        self.query_text.grid(row=4, column=0, columnspan=8, padx=10, pady=5)

        # Execute Button
        ttk.Button(self.root, text="▶️ Run Query", command=self.run_custom_query).grid(row=5, column=0, padx=10, pady=5, sticky="w")

        # Status Bar
        ttk.Label(self.root, textvariable=self.status_var, background="#f0f4f7", anchor="w",
                  font=("Helvetica", 9)).grid(row=6, column=0, columnspan=8, sticky="we", padx=10, pady=5)
        self.status_var.set("Ready. Press Ctrl+R to refresh.")

    def _bind_shortcuts(self):
        self.root.bind("<Control-r>", lambda event: self.view_records())

    def view_records(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        records = self.db.fetch_all()
        self._populate_tree(records, self.columns)
        self.status_var.set(f"Loaded {len(records)} records from {self.db.table}.")

    def run_custom_query(self):
        query = self.query_text.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning("Empty Query", "Please enter a SQL query.")
            return

        try:
            self.db.cursor.execute(query)
            if query.lower().startswith("select"):
                records = self.db.cursor.fetchall()
                columns = [desc[0] for desc in self.db.cursor.description]
                self._populate_tree(records, columns)
                self.status_var.set(f"Query executed successfully. {len(records)} rows returned.")
            else:
                self.db.connection.commit()
                self.status_var.set("Query executed successfully.")
                messagebox.showinfo("Success", "Query executed successfully.")
        except Exception as e:
            messagebox.showerror("Query Error", str(e))
            self.status_var.set("Error executing query.")

    def _populate_tree(self, records, columns):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree.config(columns=columns)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor="center")
        for row in records:
            self.tree.insert("", "end", values=row)


def main():
    root = tk.Tk()
    try:
        db_handler = DatabaseHandler(dbConfig)
        app = App(root, db_handler)
        root.mainloop()
    except Exception as e:
        print(f"Application failed to start: {e}")

if __name__ == "__main__":
    main()
