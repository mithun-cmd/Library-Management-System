from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "secretkey"

# =========================================================
# MYSQL CONNECTION
# =========================================================

db = None
cursor = None

try:

    db = mysql.connector.connect(
        host="localhost",                       ## YOUR HOST HERE IF DIFFERENT
        user="root",                            ## YOUR USERNAME HERE IF DIFFERENT
        password="rootmysql",                   ## YOUR PASSWORD HERE
        database="LibraryManagementSystem"      ## YOUR DATABASE NAME HERE
    )

    cursor = db.cursor(dictionary=True)

    print("Database connected successfully!")

except Exception as e:

    print("Database connection failed:", e)


# =========================================================
# DATABASE CHECK
# =========================================================

def check_db():

    if db is None or cursor is None:

        return False

    return True

# =========================================================
# DASHBOARD HOME
# =========================================================

@app.route("/")
def home():

    if not check_db():

        return render_template(
            "dashboard.html",
            total_students=0,
            total_books=0,
            borrowed_books=0,
            available_books=0,
            recent_logs=[],
            db_error=True
        )

    # Total Students
    cursor.execute(
        "SELECT COUNT(*) AS total FROM students"
    )

    total_students = cursor.fetchone()["total"]

    # Total Books
    cursor.execute(
        "SELECT COUNT(*) AS total FROM books"
    )

    total_books = cursor.fetchone()["total"]

    # Borrowed Books
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM borrow_logs
        WHERE return_date IS NULL
    """)

    borrowed_books = cursor.fetchone()["total"]

    # Available Books
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM books
        WHERE available = TRUE
    """)

    available_books = cursor.fetchone()["total"]

    # Recent Logs
    cursor.execute("""
        SELECT *
        FROM activity_log
        ORDER BY log_time DESC
        LIMIT 5
    """)

    recent_logs = cursor.fetchall()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_books=total_books,
        borrowed_books=borrowed_books,
        available_books=available_books,
        recent_logs=recent_logs
    )

# =========================================================
# ACTIVITY LOGS
# =========================================================

@app.route("/activity_log")
def activity_log():

    cursor.execute("""
        SELECT *
        FROM activity_log
        ORDER BY log_time DESC
    """)

    logs = cursor.fetchall()

    return render_template(
        "history.html",
        history=logs,
        show_logs="activity_logs"
    )

# =========================================================
# STUDENTS
# =========================================================

@app.route("/students", methods=["GET", "POST"])
def students():

    if request.method == "POST":

        student_id = request.form["student_id"]
        student_name = request.form["student_name"]
        department = request.form.get("student_department", "")

        try:
            cursor.execute("""
                INSERT INTO students (student_id, student_name, department)
                VALUES (%s, %s, %s)
            """, (student_id, student_name, department))

            db.commit()

            flash("Student added successfully!", "success")

        except Exception as e:
            flash(f"Error: {e}", "error")

        return redirect(url_for("students"))

    return render_template("students.html")

# =========================================================
# VIEW ALL STUDENTS
# =========================================================

@app.route("/all_students")
def all_students():

    cursor.execute("""
        SELECT *
        FROM students
        ORDER BY student_id
    """)

    students_list = cursor.fetchall()

    return render_template(
        "students.html",
        all_students=students_list
    )

# =========================================================
# BOOKS
# =========================================================

@app.route("/books", methods=["GET", "POST"])
def books():

    if request.method == "POST":

        book_id = request.form["book_id"]
        book_title = request.form["book_title"]
        author = request.form.get("book_author", "")

        try:

            cursor.execute("""
                INSERT INTO books (book_id, book_title, author)
                VALUES (%s, %s, %s)
            """, (book_id, book_title, author))

            db.commit()

            flash("Book added successfully!", "success")

        except Exception as e:
            flash(f"Error: {e}", "error")

        return redirect(url_for("books"))

    return render_template("books.html")

# =========================================================
# VIEW ALL BOOKS
# =========================================================

@app.route("/all_books")
def all_books():

    cursor.execute("""
        SELECT *
        FROM books
        ORDER BY book_id
    """)

    books_list = cursor.fetchall()

    return render_template(
        "books.html",
        all_books=books_list
    )

# =========================================================
# BORROW / RETURN
# =========================================================

@app.route("/borrowreturn", methods=["GET", "POST"])
def borrowreturn():

    if request.method == "POST":

        # -------------------------------------------------
        # BORROW BOOK
        # -------------------------------------------------

        if "borrow_student_id" in request.form:

            student_id = request.form["borrow_student_id"]
            book_id = request.form["borrow_book_id"]

            # Check student
            cursor.execute("""
                SELECT *
                FROM students
                WHERE student_id = %s
            """, (student_id,))

            student = cursor.fetchone()

            if not student:
                flash("Student does not exist!", "error")
                return redirect(url_for("borrowreturn"))

            # Check book
            cursor.execute("""
                SELECT *
                FROM books
                WHERE book_id = %s
            """, (book_id,))

            book = cursor.fetchone()

            if not book:
                flash("Book does not exist!", "error")
                return redirect(url_for("borrowreturn"))

            # Check availability
            cursor.execute("""
                SELECT *
                FROM borrow_logs
                WHERE book_id = %s
                AND return_date IS NULL
            """, (book_id,))

            existing_borrow = cursor.fetchone()

            if existing_borrow:
                flash("Book already borrowed!", "error")

            else:
                cursor.callproc("borrow_book", [student_id, book_id])
                db.commit()

                flash("Book borrowed successfully!", "success")

            return redirect(url_for("borrowreturn"))

        # -------------------------------------------------
        # RETURN BOOK
        # -------------------------------------------------

        elif "return_borrow_id" in request.form:

            borrow_id = request.form["return_borrow_id"]

            cursor.execute("""
                SELECT *
                FROM borrow_logs
                WHERE borrow_id = %s
                AND return_date IS NULL
            """, (borrow_id,))

            borrow_entry = cursor.fetchone()

            if borrow_entry:

                cursor.callproc("return_book", [borrow_id])

                db.commit()

                flash("Book returned successfully!", "success")

            else:
                flash("Invalid borrow ID!", "error")

            return redirect(url_for("borrowreturn"))

    return render_template("borrowreturn.html")

# =========================================================
# HISTORY
# =========================================================

@app.route("/history", methods=["GET", "POST"])
def history():

    history_data = []

    if request.method == "POST":

        student_id = request.form["student_id"]

        cursor.callproc("get_student_history", [student_id])

        for result in cursor.stored_results():
            history_data = result.fetchall()

        if not history_data:
            flash("No borrow history found!", "error")

    return render_template(
        "history.html",
        history=history_data
    )

# =========================================================
# BORROW LOGS
# =========================================================

@app.route("/borrow_logs")
def borrow_logs():

    cursor.execute("""
        SELECT *
        FROM borrow_logs
        ORDER BY borrow_id DESC
    """)

    logs = cursor.fetchall()

    return render_template(
        "history.html",
        history=logs,
        show_logs="borrow_logs"
    )

# =========================================================
# RUN APP
# =========================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )