

CREATE TABLE students (
	student_id INT PRIMARY KEY,
    student_name VARCHAR(50) NOT NULL,
    department VARCHAR(20)
);

CREATE TABLE books (
	book_id INT PRIMARY KEY,
    book_title VARCHAR(50) NOT NULL,
	author VARCHAR(50),
    available BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE borrow_logs (
	borrow_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id  INT,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    book_id INT,
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    borrow_date DATE NOT NULL,
    return_date DATE DEFAULT NULL
);

CREATE TABLE activity_log (
	log_id INT AUTO_INCREMENT PRIMARY KEY,
    activity TEXT,
    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
    

DELIMITER //
CREATE PROCEDURE borrow_book (p_student_id INT, p_book_id INT)
BEGIN
    DECLARE book_available BOOLEAN;

    SELECT available INTO book_available FROM books WHERE book_id = p_book_id;

    IF book_available THEN
        INSERT INTO borrow_logs (student_id, book_id, borrow_date)
        VALUES (p_student_id, p_book_id, CURRENT_DATE);

        INSERT INTO activity_log (activity)
        VALUES (CONCAT('Book ID ', p_book_id, ' borrowed by Student ID ', p_student_id));
		
        UPDATE books SET available = FALSE WHERE book_id = p_book_id;

    ELSE
        INSERT INTO activity_log (activity)
        VALUES (CONCAT('Failed attempt to borrow Book ID ', p_book_id, ' by Student ID ', p_student_id, ' - Not Available'));
    END IF;
END //
DELIMITER ;


DELIMITER //
CREATE PROCEDURE return_book (p_borrow_id INT)
BEGIN
    DECLARE already_returned BOOLEAN;

    SELECT return_date IS NOT NULL INTO already_returned
    FROM borrow_logs WHERE borrow_id = p_borrow_id;

    IF NOT already_returned THEN
        UPDATE borrow_logs
        SET return_date = CURRENT_DATE
        WHERE borrow_id = p_borrow_id;

        INSERT INTO activity_log (activity)
        VALUES (CONCAT('Book with Borrow ID ', p_borrow_id, ' returned'));

    ELSE
        INSERT INTO activity_log (activity)
        VALUES (CONCAT('Attempt to return already returned Borrow ID ', p_borrow_id));
    END IF;
END //
DELIMITER ;



DELIMITER //
CREATE PROCEDURE get_student_history (p_student_id INT)
BEGIN
	SELECT * FROM borrow_logs WHERE student_id=p_student_id;
END //
DELIMITER ;



DELIMITER //
CREATE TRIGGER after_borrowlog_insert
AFTER INSERT ON borrow_logs
FOR EACH ROW
BEGIN
	UPDATE books SET available=FALSE WHERE book_id=NEW.book_id;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER after_returndate_update
AFTER UPDATE ON borrow_logs
FOR EACH ROW
BEGIN
	IF NEW.return_date IS NOT NULL AND OLD.return_date IS NULL THEN
		UPDATE books SET available=TRUE WHERE book_id=NEW.book_id;
	END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER log_borrow_action
AFTER INSERT ON borrow_logs
FOR EACH ROW
BEGIN
  INSERT INTO activity_log (activity)
  VALUES (CONCAT('Book ID ', NEW.book_id, ' borrowed by Student ID ', NEW.student_id));
END //
DELIMITER ;




    