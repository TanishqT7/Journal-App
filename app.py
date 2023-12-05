from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from datetime import datetime, timedelta

app = Flask(__name__)

# MySQL Configuration
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Tanishq@4321',
    database='journal_db'
)
cursor = db.cursor()

# Check if entries are initialized
cursor.execute(
    "SELECT COUNT(*) FROM configuration WHERE config_key='initialized'")
result = cursor.fetchone()
initialized = result[0] > 0 if result else False


@app.route('/')
def index():
    # Fetch journal entries from the database
    cursor.execute("SELECT * FROM journal_entries")
    entries = cursor.fetchall()

    # Convert the date column to strings
    entries = [(str(entry[0]), entry[1], entry[2], entry[3], entry[4], entry[5])
               for entry in entries]

    current_date = datetime.now().strftime('%Y-%m-%d')
# Check if entries are initialized dynamically
    cursor.execute(
        "SELECT COUNT(*) FROM configuration WHERE config_key='initialized'")
    result = cursor.fetchone()
    initialized = result[0] > 0 if result else False
    return render_template('index.html', entries=entries, initialized=initialized, current_date=current_date)


@app.route('/reset_initialized', methods=['POST'])
def reset_initialized():
    # Reset initialization status by deleting the entry from the configuration table
    cursor.execute("DELETE FROM configuration WHERE config_key='initialized'")
    db.commit()

    return redirect(url_for('index'))


@app.route('/initialize_entries', methods=['POST'])
def initialize_entries():
    # Retrieve start date from form
    start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')

    # Check if already initialized
    cursor.execute(
        "SELECT COUNT(*) FROM configuration WHERE config_key='initialized'")
    result = cursor.fetchone()
    initialized = result[0] > 0 if result else False

    if not initialized:
        # Create entry for the start date
        cursor.execute(
            "INSERT INTO journal_entries (day) VALUES (%s)", (start_date,))
        db.commit()

        # Update initialization status in the configuration table
        cursor.execute(
            "INSERT INTO configuration (config_key, value) VALUES (%s, %s)", ('initialized', 1))
        db.commit()

    # Recheck initialization status
    cursor.execute(
        "SELECT COUNT(*) FROM configuration WHERE config_key='initialized'")
    result = cursor.fetchone()
    initialized = result[0] > 0 if result else False

    return redirect(url_for('index', initialized=initialized))


@app.route('/add_entry', methods=['POST'])
def add_entry():
    # Retrieve form data
    work_done_1 = request.form['work_done_1']
    work_done_2 = request.form['work_done_2']
    work_done_3 = request.form['work_done_3']
    screen_time = request.form['screen_time']
    pushups = request.form['pushups']

    # Fetch the last entry to get the last date
    cursor.execute("SELECT day FROM journal_entries ORDER BY day DESC LIMIT 1")
    last_entry = cursor.fetchone()

    if last_entry:
        # Increment the last date by one day
        current_date = (last_entry[0] + timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        # If no previous entries, use the current date
        current_date = datetime.now().strftime('%Y-%m-%d')

    # Insert entry into the database
    cursor.execute("INSERT INTO journal_entries (day, work_done_1, work_done_2, work_done_3, screen_time, pushups) VALUES (%s, %s, %s, %s, %s, %s)",
                   (current_date, work_done_1, work_done_2, work_done_3, screen_time, pushups))
    db.commit()

    return redirect(url_for('index'))


@app.route('/table')
def table():
    # Fetch journal entries from the database
    cursor.execute("SELECT * FROM journal_entries")
    entries = cursor.fetchall()

    # Convert the date column to strings
    entries = [(str(entry[0]), entry[1], entry[2], entry[3], entry[4], entry[5])
               for entry in entries]

    return render_template('table.html', entries=entries)


@app.route('/edit_entry/<string:entry_date>', methods=['GET', 'POST'])
def edit_entry(entry_date):
    if request.method == 'POST':
        # Retrieve updated form data
        work_done_1 = request.form['work_done_1']
        work_done_2 = request.form['work_done_2']
        work_done_3 = request.form['work_done_3']
        screen_time = request.form['screen_time']
        pushups = request.form['pushups']

        # Update the entry in the database
        cursor.execute("UPDATE journal_entries SET work_done_1=%s, work_done_2=%s, work_done_3=%s, screen_time=%s, pushups=%s WHERE day=%s",
                       (work_done_1, work_done_2, work_done_3, screen_time, pushups, entry_date))
        db.commit()

        return redirect(url_for('table'))

    # Fetch the entry data for editing
    cursor.execute("SELECT * FROM journal_entries WHERE day=%s", (entry_date,))
    entry = cursor.fetchone()

    return render_template('edit_entry.html', entry_date=entry_date, entry=entry)


if __name__ == '__main__':
    app.run(debug=True)
