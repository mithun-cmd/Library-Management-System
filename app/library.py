from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "secretkey"

# ---------- MySQL connection ----------
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",        
        password="your_mysql_password",   # 🔑 Change this
        database="library_db"
    )
    print("Database connected successfully!")
except Exception as e:
    print("Database connection failed:", e)

cursor = db.cursor(dictionary=True)

# ---------- ROUTES ----------

@app.route("/")
def home():
    return render_template("index.html")


# ---------- Activity Log ----------
@app.route("/activity_log")
def activity_log():
    cursor.execute("SELECT * FROM activity_log ORDER BY log_time DESC")
    logs = cursor.fetchall()
    return render_template("index.html", history=logs, show_logs=True)


# ---------- Students ----------
@app.route("/students", methods=["GET", "POST"])
def students():
    if request.method == "POST":
        student_id = request.form["student_id"]
        student_name = request.form["student_name"]
        department = request.form.get("student_department", "")

        cursor.execute(
            "INSERT INTO students (student_id, student_name, department) VALUES (%s, %s, %s)",
            (student_id, student_name, department)
        )
        db.commit()
        flash("Student added successfully!")
        return redirect(url_for("students"))

    return render_template("students.html")


# ---------- View All Students ----------
@app.route("/all_students")
def all_students():
    cursor.execute("SELECT * FROM students ORDER BY student_id")
    students_list = cursor.fetchall()
    return render_template("students.html", all_students=students_list)


# ---------- Books ----------
@app.route("/books", methods=["GET", "POST"])
def books():
    if request.method == "POST":
        book_id = request.form["book_id"]
        book_title = request.form["book_title"]
        author = request.form.get("book_author", "")

        cursor.execute(
            "INSERT INTO books (book_id, book_title, author) VALUES (%s, %s, %s)",
            (book_id, book_title, author)
        )
        db.commit()
        flash("Book added successfully!")
        return redirect(url_for("books"))

    return render_template("books.html")


# ---------- View All Books ----------
@app.route("/all_books")
def all_books():
    cursor.execute("SELECT * FROM books ORDER BY book_id")
    books_list = cursor.fetchall()
    return render_template("books.html", all_books=books_list)


# ---------- Borrow/Return ----------
@app.route("/borrowreturn", methods=["GET", "POST"])
def borrowreturn():
    if request.method == "POST":
        # ---------- Borrow ----------
        if "borrow_student_id" in request.form:
            student_id = request.form["borrow_student_id"]
            book_id = request.form["borrow_book_id"]

            # Check if student exists
            cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
            student = cursor.fetchone()
            if not student:
                flash(f"Student ID {student_id} does not exist!", "error")
                return redirect(url_for("borrowreturn"))

            # Check if book exists
            cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
            book = cursor.fetchone()
            if not book:
                flash(f"Book ID {book_id} does not exist!", "error")
                return redirect(url_for("borrowreturn"))

            # Check if book is already borrowed (return_date IS NULL)
            cursor.execute(
                "SELECT * FROM borrow_logs WHERE book_id = %s AND return_date IS NULL",
                (book_id,)
            )
            existing_borrow = cursor.fetchone()

            if existing_borrow:
                flash(f"Book {book_id} is already borrowed and not yet returned!", "error")
            else:
                # Call stored procedure to borrow book
                cursor.callproc("borrow_book", [student_id, book_id])
                db.commit()
                flash(f"Book {book_id} borrowed successfully by Student {student_id}!", "success")

            return redirect(url_for("borrowreturn"))

        # ---------- Return ----------
        elif "return_borrow_id" in request.form:
            borrow_id = request.form["return_borrow_id"]

            # Check if borrow_id exists and book is not yet returned
            cursor.execute(
                "SELECT * FROM borrow_logs WHERE borrow_id = %s AND return_date IS NULL",
                (borrow_id,)
            )
            borrow_entry = cursor.fetchone()

            if borrow_entry:
                # Call stored procedure to return book
                cursor.callproc("return_book", [borrow_id])
                db.commit()
                flash(f"Borrow ID {borrow_id} returned successfully!", "success")
            else:
                flash(f"Invalid Borrow ID or book already returned!", "error")

            return redirect(url_for("borrowreturn"))

    return render_template("borrowreturn.html")



# ---------- History ----------
@app.route("/history", methods=["GET", "POST"])
def history():
    history_data = []
    if request.method == "POST":
        student_id = request.form["student_id"]
        cursor.callproc("get_student_history", [student_id])
        for result in cursor.stored_results():
            history_data = result.fetchall()
        if not history_data:
            flash(f"No borrow history found for Student {student_id}.")
    return render_template("history.html", history=history_data)




# ---------- Borrow Logs ----------
@app.route("/borrow_logs")
def borrow_logs():
    cursor.execute("SELECT * FROM borrow_logs ORDER BY borrow_id DESC")
    logs = cursor.fetchall()
    return render_template("history.html", history=logs, show_logs="borrow_logs")




if __name__ == "__main__":

    app.run(host='0.0.0.0',debug=True,port=5000)

