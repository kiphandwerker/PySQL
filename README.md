# SQL Database Viewer (Tkinter + PyODBC)

A simple yet powerful GUI application that lets you explore and query Microsoft SQL Server databases using Python, Tkinter, and PyODBC.

# Table of Contents
- [Features](#-features)
- [Getting Started](#-getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
- [Usage](#-usage)
- [To do](#-to-do--future-features)

## 🔧 Features

- 🔌 Connect to a SQL Server instance using Windows Authentication
- 📂 Browse and select any available **database**
- 🗃️ Browse and select **tables** within a selected database
- 👁️ View all table contents in a responsive Treeview
- 🧠 Run **custom SQL queries** and view results dynamically
    - SQL syntax highlighting in the query editor
- 📝 Clean, user-friendly interface built with Tkinter
    - Change themes based on default ttk options

---

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- Access to a Microsoft SQL Server instance
- Windows Authentication enabled (or modify for SQL Auth)

### Installation
<ol>
<li> Clone the repo:

```bash
   git clone https://github.com/your-username/sql-viewer.git
```

<li> Install dependencies:

```bash
pip install pypyodbc
```

<li> Edit the dbConfig.py:

```python
dbConfig = {
    'Driver': 'SQL Server',
    'Server': 'Your-server-name'
    }
```

</ol>

# 🧪 Usage

<ol>

<li>Launch the app

```python
py SQLconnection.py
```

<li>Choose a database from the dropdown

<li>Choose a table to view its contents

<li>Optionally, type a custom SQL query into the query editor and hit Run Query

</ol>

The Treeview will display the results of your selected table or SQL query.

## ✅ To Do / Future Features

- Add support for SQL Server Authentication (username/password)

- Export query results to CSV or Excel

- Dark mode theme toggle
