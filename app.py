import sqlite3
from flask import Flask, jsonify, g, render_template, request, redirect, url_for

DATABASE = 'database.db'
app = Flask(__name__, static_folder='static')

#==================================================================================================
#CREATE TABLE

def create_table(table_name):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                profile_image BLOB,
                email TEXT NOT NULL,
                password TEXT NOT NULL,
                user_id_tag TEXT NOT NULL,
                age INTEGER NOT NULL
            )
        ''')
        conn.commit()
        print(f"{table_name} table created successfully")
    except Exception as e:
        print(f"Error creating table {table_name}: {str(e)}")
    finally:
        conn.close()
        
#==================================================================================================
#INSERT DATA

def insert_data(table, name, profile_image, email, password, user_id_tag, age):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        if isinstance(profile_image, str) and profile_image.endswith(('.jpg', '.png', '.jpeg')):
            with open(profile_image, 'rb') as file:
                blob_data = file.read()
        else:
            blob_data = profile_image
            
        cursor.execute(f'''
            INSERT INTO {table} (name, profile_image, email, password, user_id_tag, age) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, blob_data, email, password, user_id_tag, age))
        conn.commit()
        print(f"{table} user {user_id_tag} created successfully")
        return True  # Added return value for success
    except Exception as e:
        print(f"Error inserting data: {str(e)}")
        return False
    finally:
        conn.close()
        
#==================================================================================================
#READ DATA

def read_data(table):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM {table}')
        data = cursor.fetchall()
        for info in data:
            print(f"ID: {info[0]}, Name: {info[1]}, Email: {info[3]}, UserID: {info[5]}, Age: {info[6]}")
        print("All data:", data)
        return data
    except Exception as e:
        print(f"Error getting data: {str(e)}")
    finally:
        conn.close()
    
#==================================================================================================
#DELETE USER BY ID        

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user_by_id(user_id):
    try:
        cur = get_db().cursor()
        cur.execute('DELETE FROM users WHERE id = ?', (user_id,))
        get_db().commit()
        if cur.rowcount > 0:
            return jsonify({"message": f"User with ID {user_id} deleted"}), 200
        return jsonify({"message": f"No user found with ID {user_id}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#==================================================================================================
#CREATE NEW USER

@app.route('/add_user', methods=['POST'])  # Removed trailing slash for consistency
def add_user():
    try:
        name = request.form['name']
        email = request.form['email']
        user_id_tag = request.form['user_id_tag']
        age = int(request.form['age'])
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            return jsonify({"error": "Passwords do not match"}), 400
        
        profile_image = None  # No file upload in this form
        
        if insert_data('users', name, profile_image, email, password, user_id_tag, age):
            return redirect(url_for('view_users'))
        return jsonify({"error": "Failed to add user"}), 500
            
    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#==================================================================================================
#FLASK ROUTES

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        
@app.route('/data')
def data():
    try:
        cur = get_db().cursor()
        cur.execute('SELECT * FROM users')
        users = [dict(row) for row in cur.fetchall()]
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/')
def view_users():
    try:
        cur = get_db().cursor()
        cur.execute('SELECT * FROM users')
        users = cur.fetchall()
        return render_template('index.html', users=users)
    except Exception as e:
        return f"Error: {str(e)}", 500
    
#==================================================================================================

if __name__ == '__main__':
    create_table('users')
    read_data('users')
    app.run(debug=True)