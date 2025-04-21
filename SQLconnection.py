# Imports
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pypyodbc as pyo
import dbConfig
import re

SERVER_NAME = dbConfig.dbConfig['Server']
DRIVER = dbConfig.dbConfig['Driver']


class SQLExplorer:
    def __init__(self, server):
        self.server = server
        self.connection = None
        self.cursor = None
        self.current_db = None
        self.current_table = None

    def connect_to_server(self):
        try:
            self.connection = pyo.connect(
                Driver=DRIVER,
                Server=self.server,
                Trusted_Connection='yes'
            )
            self.cursor = self.connection.cursor()
        except Exception as e:
            raise ConnectionError(f"Cannot connect to SQL Server: {e}")

    def get_databases(self):
        self.cursor.execute("SELECT name FROM sys.databases WHERE name NOT IN ('master', 'tempdb', 'model', 'msdb')")
        return [row[0] for row in self.cursor.fetchall()]

    def get_tables(self, db_name):
        self.cursor.execute(f"USE [{db_name}]")
        self.current_db = db_name
        self.cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        return [row[0] for row in self.cursor.fetchall()]

    def get_columns(self, table_name):
        self.cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?", [table_name])
        return [row[0] for row in self.cursor.fetchall()]

    def fetch_table_data(self, table_name):
        self.current_table = table_name
        query = f"SELECT * FROM [{table_name}]"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def run_query(self, query):
        self.cursor.execute(query)
        if query.strip().lower().startswith("select"):
            result = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]
            return result, columns
        else:
            self.connection.commit()
            return [], []

class ExplorerApp:
    def __init__(self, root, explorer: SQLExplorer):
        self.root = root
        self.explorer = explorer

        self.status_var = tk.StringVar()
        self.databases = []
        self.tables = []
        self.columns = []

        self._setup_gui()
        self._bind_events()

    def _setup_gui(self):
        self.root.title("🗂️ SQL Explorer")
        self.root.geometry("1000x750")
        self.root.configure(bg="#f0f4f7")

        control_frame = ttk.Frame(self.root)
        control_frame.grid(row=0, column=0, columnspan=8, padx=10, pady=5, sticky="w")

        ttk.Label(control_frame, text="Select Database:").grid(row=0, column=0, padx=5)
        self.db_box = ttk.Combobox(control_frame, width=30, state="readonly")
        self.db_box.grid(row=0, column=1, padx=5)

        ttk.Label(control_frame, text="Select Table:").grid(row=0, column=2, padx=5)
        self.table_box = ttk.Combobox(control_frame, width=30, state="readonly")
        self.table_box.grid(row=0, column=3, padx=5)

        ttk.Button(control_frame, text="🔄 Load Table", command=self.load_table_data).grid(row=0, column=4, padx=10)

        self.status_label = ttk.Label(self.root, textvariable=self.status_var, background="#f0f4f7",
                                      font=("Helvetica", 10, "italic"))
        self.status_label.grid(row=1, column=0, columnspan=8, padx=10, sticky="w")
        self.status_var.set("Select a database and table.")

        # Tree
        self.tree = ttk.Treeview(self.root, columns=[], show="headings", height=20)
        self.tree.grid(row=2, column=0, columnspan=7, padx=10, pady=10, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=2, column=7, sticky="ns")

        # DQL selection
        ttk.Label(self.root, text="🧠 Custom SQL Query:", background="#f0f4f7",
                  font=("Helvetica", 11, "bold")).grid(row=3, column=0, columnspan=8, padx=10, sticky="w")

        self.query_text = scrolledtext.ScrolledText(self.root, width=120, height=5, font=("Courier New", 10))
        self.query_text.grid(row=4, column=0, columnspan=8, padx=10, pady=5)

        ttk.Button(self.root, text="▶️ Run Query", command=self.run_custom_query).grid(row=5, column=0, padx=10, pady=5, sticky="w")

        ttk.Label(control_frame, text="Theme:").grid(row=0, column=5, padx=5)
        self.theme_box = ttk.Combobox(control_frame, width=15, state="readonly")
        self.theme_box.grid(row=0, column=6, padx=5)

        # ttk themes
        self.style = ttk.Style()
        available_themes = self.style.theme_names()
        self.theme_box['values'] = available_themes
        self.theme_box.set(self.style.theme_use())  # default theme

    def _bind_events(self):
        self.db_box.bind("<<ComboboxSelected>>", self.load_tables_for_db)
        self.theme_box.bind("<<ComboboxSelected>>", self.change_theme)
        self.query_text.bind("<KeyRelease>", self._highlight_syntax)

    def load_databases(self):
        try:
            self.explorer.connect_to_server()
            self.databases = self.explorer.get_databases()
            self.db_box['values'] = self.databases
            self.status_var.set(f"Found {len(self.databases)} databases.")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def load_tables_for_db(self, event=None):
        db_name = self.db_box.get()
        if not db_name:
            return
        try:
            self.tables = self.explorer.get_tables(db_name)
            self.table_box['values'] = self.tables
            self.status_var.set(f"Selected DB: {db_name} — {len(self.tables)} tables found.")
        except Exception as e:
            messagebox.showerror("Table Load Error", str(e))

    def load_table_data(self):
        table = self.table_box.get()
        if not table:
            messagebox.showwarning("No Table", "Please select a table first.")
            return
        try:
            self.columns = self.explorer.get_columns(table)
            records = self.explorer.fetch_table_data(table)
            self._populate_tree(records, self.columns)
            self.status_var.set(f"Viewing: {self.explorer.current_db}.{table} — {len(records)} rows")
        except Exception as e:
            messagebox.showerror("Data Load Error", str(e))

    def run_custom_query(self):
        query = self.query_text.get("1.0", tk.END).strip()
        if not query:
            return
        try:
            records, columns = self.explorer.run_query(query)
            if records and columns:
                self._populate_tree(records, columns)
                self.status_var.set(f"Query returned {len(records)} rows.")
            else:
                self.status_var.set("Query executed successfully.")
                messagebox.showinfo("Success", "Query executed.")
        except Exception as e:
            messagebox.showerror("SQL Error", str(e))
            self.status_var.set("Error running query.")

    def _populate_tree(self, records, columns):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.tree.config(columns=columns)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130)
        for row in records:
            self.tree.insert("", "end", values=row)
            
    def change_theme(self, event=None):
        selected_theme = self.theme_box.get()
        try:
            self.style.theme_use(selected_theme)
            self.status_var.set(f"Theme changed to: {selected_theme}")
        except Exception as e:
            messagebox.showerror("Theme Error", f"Could not apply theme: {e}")

    def _highlight_syntax(self, event=None):
        # Clear previous tags
        for tag in self.query_text.tag_names():
            self.query_text.tag_remove(tag, "1.0", tk.END)

        sql_keywords = r"\b(SELECT|FROM|WHERE|AND|OR|INSERT|INTO|VALUES|UPDATE|SET|DELETE|JOIN|ON|AS|CREATE|TABLE|DROP|ALTER|USE|INNER|LEFT|RIGHT|FULL|GROUP BY|ORDER BY|HAVING|DISTINCT|TOP|LIMIT|OFFSET|IS|NULL|NOT|IN|EXISTS)\b"
        strings = r"('[^']*'|\"[^\"]*\")"
        numbers = r"\b\d+(\.\d+)?\b"
        comments = r"--.*?$"

        content = self.query_text.get("1.0", tk.END)
        
        # Define tags
        self.query_text.tag_config("keyword", foreground="#569CD6", font=("Courier New", 10, "bold"))
        self.query_text.tag_config("string", foreground="#CE9178")
        self.query_text.tag_config("number", foreground="#B5CEA8")
        self.query_text.tag_config("comment", foreground="#6A9955", font=("Courier New", 10, "italic"))

        # Apply keyword tag
        for match in re.finditer(sql_keywords, content, re.IGNORECASE):
            start, end = match.span()
            self._apply_tag("keyword", start, end)

        # Apply string tag
        for match in re.finditer(strings, content):
            start, end = match.span()
            self._apply_tag("string", start, end)

        # Apply number tag
        for match in re.finditer(numbers, content):
            start, end = match.span()
            self._apply_tag("number", start, end)

        # Apply comment tag
        for match in re.finditer(comments, content, re.MULTILINE):
            start, end = match.span()
            self._apply_tag("comment", start, end)

    def _apply_tag(self, tag, start_idx, end_idx):
        start = f"1.0 + {start_idx} chars"
        end = f"1.0 + {end_idx} chars"
        self.query_text.tag_add(tag, start, end)
    


# --- MAIN ---
def main():
    root = tk.Tk()
    explorer = SQLExplorer(SERVER_NAME)
    app = ExplorerApp(root, explorer)
    app.load_databases()
    root.mainloop()


if __name__ == "__main__":
    main()
