import sys
import hashlib
import psycopg2
from psycopg2 import sql
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QComboBox, QSpinBox, QTextEdit, QDateEdit, QDialog, QFormLayout, QGridLayout
)
from PyQt5.QtCore import QDate, Qt
from datetime import date, timedelta

# ---------- DATABASE CONFIGURATION ----------
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'Limkokwing Smart Library System',
    'user': 'postgres',
    'password': 'julie22'
}


# ---------- HELPERS ----------
def get_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    return conn


def hash_password(plain: str) -> str:
    return hashlib.sha256(plain.encode('utf-8')).hexdigest()


def create_tables():
    # Creates all required tables

    queries = [
        # users table for authentication
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            role TEXT DEFAULT 'staff'
        );
        """,
        # authors (expanded)
        """
        CREATE TABLE IF NOT EXISTS author (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            bio TEXT,
            nationality TEXT,
            birth_year INTEGER
        );
        """,
        # members (expanded)
        """
        CREATE TABLE IF NOT EXISTS member (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            membership_type TEXT,
            join_date DATE
        );
        """,
        # bookclubs (expanded)
        """
        CREATE TABLE IF NOT EXISTS bookclub (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            meeting_day TEXT
        );
        """,
        # books (expanded)
        """
        CREATE TABLE IF NOT EXISTS book (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            author_id INTEGER REFERENCES author(id) ON DELETE SET NULL,
            isbn TEXT UNIQUE,
            publisher TEXT,
            published_year INTEGER,
            genre TEXT,
            copies_available INTEGER DEFAULT 1
        );
        """,
        # loans table
        """
        CREATE TABLE IF NOT EXISTS loan (
            id SERIAL PRIMARY KEY,
            book_id INTEGER REFERENCES book(id) ON DELETE CASCADE,
            member_id INTEGER REFERENCES member(id) ON DELETE CASCADE,
            loan_date DATE,
            due_date DATE,
            return_date DATE,
            status TEXT
        );
        """
    ]

    conn = get_connection()
    cur = conn.cursor()
    for q in queries:
        cur.execute(q)

    # create default admin user if not exists (username: admin, password: admin)
    admin_hash = hash_password("man")
    cur.execute(
        "INSERT INTO users (username, password_hash, full_name, role) VALUES (%s, %s, %s, %s) ON CONFLICT (username) DO NOTHING;",
        ('man', admin_hash, 'Administrator', 'admin'))

    cur.close()
    conn.close()


# ---------- GUI COMPONENTS ----------
class EntityTab(QWidget):
    # Base helper for entity tabs
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    def run_query(self, query, params=None, fetch=False):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, params or ())
        data = None
        if fetch:
            data = cur.fetchall()
        cur.close()
        conn.close()
        return data


# ---------- Author Tab ----------
class AuthorTab(EntityTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.build_ui()
        self.load_authors()

    def build_ui(self):
        form_layout = QHBoxLayout()
        left = QVBoxLayout()
        right = QVBoxLayout()

        self.name_input = QLineEdit()
        self.bio_input = QTextEdit()
        self.nationality_input = QLineEdit()
        self.birthyear_input = QSpinBox()
        self.birthyear_input.setRange(0, 2200)

        left.addWidget(QLabel('Name'))
        left.addWidget(self.name_input)
        left.addWidget(QLabel('Nationality'))
        left.addWidget(self.nationality_input)

        right.addWidget(QLabel('Bio'))
        right.addWidget(self.bio_input)
        right.addWidget(QLabel('Birth Year'))
        right.addWidget(self.birthyear_input)

        form_layout.addLayout(left)
        form_layout.addLayout(right)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton('Add Author')
        self.update_btn = QPushButton('Update Selected')
        self.delete_btn = QPushButton('Delete Selected')
        self.refresh_btn = QPushButton('Refresh')
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.refresh_btn)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(['ID', 'Name', 'Nationality', 'Birth Year', 'Bio'])
        self.table.setColumnHidden(0, True)

        self.layout.addLayout(form_layout)
        self.layout.addLayout(btn_layout)
        self.layout.addWidget(self.table)

        self.add_btn.clicked.connect(self.add_author)
        self.update_btn.clicked.connect(self.update_author)
        self.delete_btn.clicked.connect(self.delete_author)
        self.refresh_btn.clicked.connect(self.load_authors)
        self.table.cellClicked.connect(self.on_row_selected)

    def add_author(self):
        name = self.name_input.text().strip()
        bio = self.bio_input.toPlainText().strip()
        nationality = self.nationality_input.text().strip()
        birth_year = self.birthyear_input.value() or None
        if not name:
            QMessageBox.warning(self, 'Validation', 'Author name is required')
            return
        q = "INSERT INTO author (name, bio, nationality, birth_year) VALUES (%s, %s, %s, %s)"
        self.run_query(q, (name, bio, nationality, birth_year))
        self.load_authors()
        self.clear_form()

    def load_authors(self):
        q = "SELECT id, name, nationality, birth_year, bio FROM author ORDER BY id"
        rows = self.run_query(q, fetch=True) or []
        self.table.setRowCount(0)
        for r in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(r[0])))
            self.table.setItem(row, 1, QTableWidgetItem(r[1] or ''))
            self.table.setItem(row, 2, QTableWidgetItem(r[2] or ''))
            self.table.setItem(row, 3, QTableWidgetItem(str(r[3]) if r[3] else ''))
            self.table.setItem(row, 4, QTableWidgetItem(r[4] or ''))

    def on_row_selected(self, row, col):
        if not self.table.item(row, 0):
            return
        self.name_input.setText(self.table.item(row, 1).text())
        self.nationality_input.setText(self.table.item(row, 2).text())
        try:
            self.birthyear_input.setValue(int(self.table.item(row, 3).text()) if self.table.item(row, 3).text() else 0)
        except Exception:
            self.birthyear_input.setValue(0)
        self.bio_input.setPlainText(self.table.item(row, 4).text())

    def get_selected_id(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        row = rows[0].row()
        return int(self.table.item(row, 0).text())

    def update_author(self):
        sel_id = self.get_selected_id()
        if not sel_id:
            QMessageBox.warning(self, 'Selection', 'Select an author to update')
            return
        name = self.name_input.text().strip()
        bio = self.bio_input.toPlainText().strip()
        nationality = self.nationality_input.text().strip()
        birth_year = self.birthyear_input.value() or None
        if not name:
            QMessageBox.warning(self, 'Validation', 'Author name is required')
            return
        q = "UPDATE author SET name=%s, bio=%s, nationality=%s, birth_year=%s WHERE id=%s"
        self.run_query(q, (name, bio, nationality, birth_year, sel_id))
        self.load_authors()

    def delete_author(self):
        sel_id = self.get_selected_id()
        if not sel_id:
            QMessageBox.warning(self, 'Selection', 'Select an author to delete')
            return
        reply = QMessageBox.question(self, 'Confirm', 'Delete selected author?')
        if reply != QMessageBox.Yes:
            return
        q = "DELETE FROM author WHERE id=%s"
        self.run_query(q, (sel_id,))
        self.load_authors()

    def clear_form(self):
        self.name_input.clear()
        self.bio_input.clear()
        self.nationality_input.clear()
        self.birthyear_input.setValue(0)


# ---------- Book Tab ----------
class BookTab(EntityTab):
    def __init__(self, author_tab: AuthorTab, parent=None):
        super().__init__(parent)
        self.author_tab = author_tab
        self.build_ui()
        self.load_books()
        self.load_authors_into_combo()

    def build_ui(self):
        form_layout = QHBoxLayout()
        left_form = QVBoxLayout()
        right_form = QVBoxLayout()

        self.title_input = QLineEdit()
        self.isbn_input = QLineEdit()
        self.publisher_input = QLineEdit()
        self.pubyear_input = QSpinBox()
        self.pubyear_input.setRange(0, 9999)
        self.genre_input = QLineEdit()
        self.copies_input = QSpinBox()
        self.copies_input.setRange(0, 9999)
        self.author_combo = QComboBox()

        left_form.addWidget(QLabel('Title'))
        left_form.addWidget(self.title_input)
        left_form.addWidget(QLabel('ISBN'))
        left_form.addWidget(self.isbn_input)
        left_form.addWidget(QLabel('Publisher'))
        left_form.addWidget(self.publisher_input)

        right_form.addWidget(QLabel('Author'))
        right_form.addWidget(self.author_combo)
        right_form.addWidget(QLabel('Published Year'))
        right_form.addWidget(self.pubyear_input)
        right_form.addWidget(QLabel('Genre'))
        right_form.addWidget(self.genre_input)
        right_form.addWidget(QLabel('Copies Available'))
        right_form.addWidget(self.copies_input)

        form_layout.addLayout(left_form)
        form_layout.addLayout(right_form)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton('Add Book')
        self.update_btn = QPushButton('Update Selected')
        self.delete_btn = QPushButton('Delete Selected')
        self.refresh_btn = QPushButton('Refresh')
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.refresh_btn)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(['ID', 'Title', 'Author', 'ISBN', 'Publisher', 'Year', 'Genre', 'Copies'])
        self.table.setColumnHidden(0, True)

        self.layout.addLayout(form_layout)
        self.layout.addLayout(btn_layout)
        self.layout.addWidget(self.table)

        self.add_btn.clicked.connect(self.add_book)
        self.update_btn.clicked.connect(self.update_book)
        self.delete_btn.clicked.connect(self.delete_book)
        self.refresh_btn.clicked.connect(self.load_books)
        self.table.cellClicked.connect(self.on_row_selected)

    def run_query(self, query, params=None, fetch=False):
        return super().run_query(query, params, fetch)

    def load_authors_into_combo(self):
        q = "SELECT id, name FROM author ORDER BY name"
        rows = self.run_query(q, fetch=True) or []
        self.author_combo.clear()
        self.author_combo.addItem('--- None ---', None)
        for r in rows:
            self.author_combo.addItem(r[1], r[0])

    def add_book(self):
        title = self.title_input.text().strip()
        isbn = self.isbn_input.text().strip()
        publisher = self.publisher_input.text().strip()
        year = self.pubyear_input.value() or None
        genre = self.genre_input.text().strip()
        copies = self.copies_input.value() or 1
        author_id = self.author_combo.currentData()
        if not title:
            QMessageBox.warning(self, 'Validation', 'Book title is required')
            return
        q = "INSERT INTO book (title, author_id, isbn, publisher, published_year, genre, copies_available) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        try:
            self.run_query(q, (title, author_id, isbn, publisher, year, genre, copies))
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Could not add book: {e}')
        self.load_books()
        self.clear_form()

    def load_books(self):
        q = """
            SELECT b.id, b.title, a.name, b.isbn, b.publisher, b.published_year, b.genre, b.copies_available
            FROM book b LEFT JOIN author a ON b.author_id = a.id
            ORDER BY b.id
        """
        rows = self.run_query(q, fetch=True) or []
        self.table.setRowCount(0)
        for r in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col_index, val in enumerate(r):
                self.table.setItem(row, col_index, QTableWidgetItem(str(val) if val is not None else ''))

    def on_row_selected(self, row, col):
        if not self.table.item(row, 0):
            return
        self.title_input.setText(self.table.item(row, 1).text())
        self.isbn_input.setText(self.table.item(row, 3).text())
        self.publisher_input.setText(self.table.item(row, 4).text())
        try:
            self.pubyear_input.setValue(int(self.table.item(row, 5).text()) if self.table.item(row, 5).text() else 0)
        except Exception:
            self.pubyear_input.setValue(0)
        self.genre_input.setText(self.table.item(row, 6).text())
        try:
            self.copies_input.setValue(int(self.table.item(row, 7).text()) if self.table.item(row, 7).text() else 1)
        except Exception:
            self.copies_input.setValue(1)
        # select author in combo
        name = self.table.item(row, 2).text()
        idx = self.author_combo.findText(name)
        if idx >= 0:
            self.author_combo.setCurrentIndex(idx)
        else:
            self.author_combo.setCurrentIndex(0)

    def get_selected_id(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        row = rows[0].row()
        return int(self.table.item(row, 0).text())

    def update_book(self):
        sel_id = self.get_selected_id()
        if not sel_id:
            QMessageBox.warning(self, 'Selection', 'Select a book to update')
            return
        title = self.title_input.text().strip()
        isbn = self.isbn_input.text().strip()
        publisher = self.publisher_input.text().strip()
        year = self.pubyear_input.value() or None
        genre = self.genre_input.text().strip()
        copies = self.copies_input.value() or 1
        author_id = self.author_combo.currentData()
        if not title:
            QMessageBox.warning(self, 'Validation', 'Book title is required')
            return
        q = "UPDATE book SET title=%s, author_id=%s, isbn=%s, publisher=%s, published_year=%s, genre=%s, copies_available=%s WHERE id=%s"
        try:
            self.run_query(q, (title, author_id, isbn, publisher, year, genre, copies, sel_id))
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Could not update book: {e}')
        self.load_books()

    def delete_book(self):
        sel_id = self.get_selected_id()
        if not sel_id:
            QMessageBox.warning(self, 'Selection', 'Select a book to delete')
            return
        reply = QMessageBox.question(self, 'Confirm', 'Delete selected book?')
        if reply != QMessageBox.Yes:
            return
        q = "DELETE FROM book WHERE id=%s"
        self.run_query(q, (sel_id,))
        self.load_books()

    def clear_form(self):
        self.title_input.clear()
        self.isbn_input.clear()
        self.publisher_input.clear()
        self.pubyear_input.setValue(0)
        self.genre_input.clear()
        self.copies_input.setValue(1)
        self.author_combo.setCurrentIndex(0)


# ---------- Member Tab ----------
class MemberTab(EntityTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.build_ui()
        self.load_members()

    def build_ui(self):
        form_layout = QHBoxLayout()
        left = QVBoxLayout()
        right = QVBoxLayout()

        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.membership_type_input = QComboBox()
        self.membership_type_input.addItems(['Standard', 'Premium', 'Student', 'Senior'])
        self.join_date = QDateEdit()
        self.join_date.setCalendarPopup(True)
        self.join_date.setDate(QDate.currentDate())

        left.addWidget(QLabel('Name'))
        left.addWidget(self.name_input)
        left.addWidget(QLabel('Email'))
        left.addWidget(self.email_input)
        left.addWidget(QLabel('Phone'))
        left.addWidget(self.phone_input)

        right.addWidget(QLabel('Membership Type'))
        right.addWidget(self.membership_type_input)
        right.addWidget(QLabel('Join Date'))
        right.addWidget(self.join_date)

        form_layout.addLayout(left)
        form_layout.addLayout(right)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton('Add Member')
        self.update_btn = QPushButton('Update Selected')
        self.delete_btn = QPushButton('Delete Selected')
        self.refresh_btn = QPushButton('Refresh')
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.refresh_btn)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(['ID', 'Name', 'Email', 'Phone', 'Membership', 'Join Date'])
        self.table.setColumnHidden(0, True)

        self.layout.addLayout(form_layout)
        self.layout.addLayout(btn_layout)
        self.layout.addWidget(self.table)

        self.add_btn.clicked.connect(self.add_member)
        self.update_btn.clicked.connect(self.update_member)
        self.delete_btn.clicked.connect(self.delete_member)
        self.refresh_btn.clicked.connect(self.load_members)
        self.table.cellClicked.connect(self.on_row_selected)

    def add_member(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        membership_type = self.membership_type_input.currentText()
        join_date = self.join_date.date().toPyDate()
        if not name:
            QMessageBox.warning(self, 'Validation', 'Member name is required')
            return
        q = "INSERT INTO member (name, email, phone, membership_type, join_date) VALUES (%s, %s, %s, %s, %s)"
        try:
            self.run_query(q, (name, email, phone, membership_type, join_date))
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Could not add member: {e}')
        self.load_members()
        self.clear_form()

    def load_members(self):
        q = "SELECT id, name, email, phone, membership_type, join_date FROM member ORDER BY id"
        rows = self.run_query(q, fetch=True) or []
        self.table.setRowCount(0)
        for r in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for i, val in enumerate(r):
                self.table.setItem(row, i, QTableWidgetItem(str(val) if val is not None else ''))

    def on_row_selected(self, row, col):
        if not self.table.item(row, 0):
            return
        self.name_input.setText(self.table.item(row, 1).text())
        self.email_input.setText(self.table.item(row, 2).text())
        self.phone_input.setText(self.table.item(row, 3).text())
        idx = self.membership_type_input.findText(self.table.item(row, 4).text())
        if idx >= 0:
            self.membership_type_input.setCurrentIndex(idx)
        try:
            qdate = QDate.fromString(self.table.item(row, 5).text(), 'yyyy-MM-dd')
            if qdate.isValid():
                self.join_date.setDate(qdate)
        except Exception:
            pass

    def get_selected_id(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        row = rows[0].row()
        return int(self.table.item(row, 0).text())

    def update_member(self):
        sel_id = self.get_selected_id()
        if not sel_id:
            QMessageBox.warning(self, 'Selection', 'Select a member to update')
            return
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        membership_type = self.membership_type_input.currentText()
        join_date = self.join_date.date().toPyDate()
        if not name:
            QMessageBox.warning(self, 'Validation', 'Member name is required')
            return
        q = "UPDATE member SET name=%s, email=%s, phone=%s, membership_type=%s, join_date=%s WHERE id=%s"
        try:
            self.run_query(q, (name, email, phone, membership_type, join_date, sel_id))
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Could not update member: {e}')
        self.load_members()

    def delete_member(self):
        sel_id = self.get_selected_id()
        if not sel_id:
            QMessageBox.warning(self, 'Selection', 'Select a member to delete')
            return
        reply = QMessageBox.question(self, 'Confirm', 'Delete selected member?')
        if reply != QMessageBox.Yes:
            return
        q = "DELETE FROM member WHERE id=%s"
        self.run_query(q, (sel_id,))
        self.load_members()

    def clear_form(self):
        self.name_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
        self.membership_type_input.setCurrentIndex(0)
        self.join_date.setDate(QDate.currentDate())


# ---------- Bookclub Tab ----------
class BookclubTab(EntityTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.build_ui()
        self.load_bookclubs()

    def build_ui(self):
        form_layout = QHBoxLayout()
        left = QVBoxLayout()
        right = QVBoxLayout()

        self.name_input = QLineEdit()
        self.desc_input = QTextEdit()
        self.meeting_day_input = QLineEdit()

        left.addWidget(QLabel('Name'))
        left.addWidget(self.name_input)
        left.addWidget(QLabel('Meeting Day'))
        left.addWidget(self.meeting_day_input)

        right.addWidget(QLabel('Description'))
        right.addWidget(self.desc_input)

        form_layout.addLayout(left)
        form_layout.addLayout(right)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton('Add Bookclub')
        self.update_btn = QPushButton('Update Selected')
        self.delete_btn = QPushButton('Delete Selected')
        self.refresh_btn = QPushButton('Refresh')
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.refresh_btn)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(['ID', 'Name', 'Meeting Day', 'Description'])
        self.table.setColumnHidden(0, True)

        self.layout.addLayout(form_layout)
        self.layout.addLayout(btn_layout)
        self.layout.addWidget(self.table)

        self.add_btn.clicked.connect(self.add_bookclub)
        self.update_btn.clicked.connect(self.update_bookclub)
        self.delete_btn.clicked.connect(self.delete_bookclub)
        self.refresh_btn.clicked.connect(self.load_bookclubs)
        self.table.cellClicked.connect(self.on_row_selected)

    def add_bookclub(self):
        name = self.name_input.text().strip()
        desc = self.desc_input.toPlainText().strip()
        meeting_day = self.meeting_day_input.text().strip()
        if not name:
            QMessageBox.warning(self, 'Validation', 'Bookclub name is required')
            return
        q = "INSERT INTO bookclub (name, description, meeting_day) VALUES (%s, %s, %s)"
        self.run_query(q, (name, desc, meeting_day))
        self.load_bookclubs()
        self.clear_form()

    def load_bookclubs(self):
        q = "SELECT id, name, meeting_day, description FROM bookclub ORDER BY id"
        rows = self.run_query(q, fetch=True) or []
        self.table.setRowCount(0)
        for r in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for i, val in enumerate(r):
                self.table.setItem(row, i, QTableWidgetItem(str(val) if val is not None else ''))

    def on_row_selected(self, row, col):
        if not self.table.item(row, 0):
            return
        self.name_input.setText(self.table.item(row, 1).text())
        self.meeting_day_input.setText(self.table.item(row, 2).text())
        self.desc_input.setPlainText(self.table.item(row, 3).text())

    def get_selected_id(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        row = rows[0].row()
        return int(self.table.item(row, 0).text())

    def update_bookclub(self):
        sel_id = self.get_selected_id()
        if not sel_id:
            QMessageBox.warning(self, 'Selection', 'Select a bookclub to update')
            return
        name = self.name_input.text().strip()
        desc = self.desc_input.toPlainText().strip()
        meeting_day = self.meeting_day_input.text().strip()
        if not name:
            QMessageBox.warning(self, 'Validation', 'Bookclub name is required')
            return
        q = "UPDATE bookclub SET name=%s, description=%s, meeting_day=%s WHERE id=%s"
        self.run_query(q, (name, desc, meeting_day, sel_id))
        self.load_bookclubs()

    def delete_bookclub(self):
        sel_id = self.get_selected_id()
        if not sel_id:
            QMessageBox.warning(self, 'Selection', 'Select a bookclub to delete')
            return
        reply = QMessageBox.question(self, 'Confirm', 'Delete selected bookclub?')
        if reply != QMessageBox.Yes:
            return
        q = "DELETE FROM bookclub WHERE id=%s"
        self.run_query(q, (sel_id,))
        self.load_bookclubs()

    def clear_form(self):
        self.name_input.clear()
        self.desc_input.clear()
        self.meeting_day_input.clear()


# ---------- Loan Tab ----------
class LoanTab(EntityTab):
    def __init__(self, book_tab: BookTab, member_tab: MemberTab, parent=None):
        super().__init__(parent)
        self.book_tab = book_tab
        self.member_tab = member_tab
        self.build_ui()
        self.load_loans()
        self.load_books_members()

    def build_ui(self):
        form_layout = QHBoxLayout()
        left = QVBoxLayout()
        right = QVBoxLayout()

        self.book_combo = QComboBox()
        self.member_combo = QComboBox()
        self.loan_date = QDateEdit()
        self.loan_date.setCalendarPopup(True)
        self.loan_date.setDate(QDate.currentDate())
        self.due_days_spin = QSpinBox()
        self.due_days_spin.setRange(1, 365)
        self.due_days_spin.setValue(14)
        self.status_combo = QComboBox()
        self.status_combo.addItems(['On Loan', 'Returned', 'Overdue'])

        left.addWidget(QLabel('Book'))
        left.addWidget(self.book_combo)
        left.addWidget(QLabel('Member'))
        left.addWidget(self.member_combo)

        right.addWidget(QLabel('Loan Date'))
        right.addWidget(self.loan_date)
        right.addWidget(QLabel('Due in (days)'))
        right.addWidget(self.due_days_spin)
        right.addWidget(QLabel('Status'))
        right.addWidget(self.status_combo)

        form_layout.addLayout(left)
        form_layout.addLayout(right)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton('Add Loan')
        self.return_btn = QPushButton('Mark Returned')
        self.delete_btn = QPushButton('Delete Loan')
        self.refresh_btn = QPushButton('Refresh')
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.return_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.refresh_btn)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(['ID', 'Book', 'Member', 'Loan Date', 'Due Date', 'Return Date', 'Status'])
        self.table.setColumnHidden(0, True)

        self.layout.addLayout(form_layout)
        self.layout.addLayout(btn_layout)
        self.layout.addWidget(self.table)

        self.add_btn.clicked.connect(self.add_loan)
        self.return_btn.clicked.connect(self.mark_returned)
        self.delete_btn.clicked.connect(self.delete_loan)
        self.refresh_btn.clicked.connect(self.load_loans)
        self.table.cellClicked.connect(self.on_row_selected)

    def load_books_members(self):
        # populate book combo (only books with copies >= 1)
        books = self.run_query("SELECT id, title, copies_available FROM book ORDER BY title", fetch=True) or []
        self.book_combo.clear()
        self.book_combo.addItem('--- Select ---', None)
        for b in books:
            disp = f"{b[1]} (copies: {b[2]})"
            self.book_combo.addItem(disp, b[0])

        members = self.run_query("SELECT id, name FROM member ORDER BY name", fetch=True) or []
        self.member_combo.clear()
        self.member_combo.addItem('--- Select ---', None)
        for m in members:
            self.member_combo.addItem(m[1], m[0])

    def add_loan(self):
        book_id = self.book_combo.currentData()
        member_id = self.member_combo.currentData()
        loan_date = self.loan_date.date().toPyDate()
        due_date = loan_date + timedelta(days=self.due_days_spin.value())
        status = self.status_combo.currentText()

        if not book_id or not member_id:
            QMessageBox.warning(self, 'Validation', 'Select both book and member')
            return

        # check copies availability
        copies_row = self.run_query("SELECT copies_available FROM book WHERE id=%s", (book_id,), fetch=True)
        copies = copies_row[0][0] if copies_row and copies_row[0] else 0
        if copies < 1:
            QMessageBox.warning(self, 'Unavailable', 'No available copies for this book')
            return

        q = "INSERT INTO loan (book_id, member_id, loan_date, due_date, status) VALUES (%s, %s, %s, %s, %s)"
        try:
            self.run_query(q, (book_id, member_id, loan_date, due_date, status))
            # decrement copies available
            self.run_query("UPDATE book SET copies_available = copies_available - 1 WHERE id=%s", (book_id,))
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Could not create loan: {e}')
        self.load_loans()
        self.load_books_members()

    def load_loans(self):
        q = """
            SELECT l.id, b.title, m.name, l.loan_date, l.due_date, l.return_date, l.status
            FROM loan l
            LEFT JOIN book b ON l.book_id = b.id
            LEFT JOIN member m ON l.member_id = m.id
            ORDER BY l.id
        """
        rows = self.run_query(q, fetch=True) or []
        self.table.setRowCount(0)
        for r in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for i, val in enumerate(r):
                self.table.setItem(row, i, QTableWidgetItem(str(val) if val is not None else ''))

    def on_row_selected(self, row, col):
        if not self.table.item(row, 0):
            return
        # selecting a loan doesn't auto-fill combos here (keeps process simple)
        pass

    def get_selected_id(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        row = rows[0].row()
        return int(self.table.item(row, 0).text())

    def mark_returned(self):
        sel_id = self.get_selected_id()
        if not sel_id:
            QMessageBox.warning(self, 'Selection', 'Select a loan to mark returned')
            return
        return_date = date.today()
        try:
            # find book id for this loan
            b = self.run_query("SELECT book_id FROM loan WHERE id=%s", (sel_id,), fetch=True)
            book_id = b[0][0] if b else None
            self.run_query("UPDATE loan SET return_date=%s, status=%s WHERE id=%s", (return_date, 'Returned', sel_id))
            if book_id:
                self.run_query("UPDATE book SET copies_available = copies_available + 1 WHERE id=%s", (book_id,))
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Could not mark returned: {e}')
        self.load_loans()
        self.load_books_members()

    def delete_loan(self):
        sel_id = self.get_selected_id()
        if not sel_id:
            QMessageBox.warning(self, 'Selection', 'Select a loan to delete')
            return
        reply = QMessageBox.question(self, 'Confirm',
                                     'Delete selected loan? (this will not restore copies automatically)',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        q = "DELETE FROM loan WHERE id=%s"
        try:
            self.run_query(q, (sel_id,))
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Could not delete loan: {e}')
        self.load_loans()
        self.load_books_members()


class DashboardTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.build_ui()
        self.refresh_stats()

    def build_ui(self):
        # Background color for the whole dashboard
        self.setStyleSheet("background-color: #E8F1FF;")  # light blue

        main_layout = QVBoxLayout()

        title = QLabel("Limkokwing Smart Library Dashboard")
        title.setStyleSheet("""
            font-size: 22px; 
            font-weight: bold; 
            margin-bottom: 20px;
        """)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # ---------- GRID LAYOUT ----------
        grid = QGridLayout()
        grid.setSpacing(20)  # spacing between grid boxes

        # Create card widgets
        self.total_books = self.create_card()
        self.total_authors = self.create_card()
        self.total_members = self.create_card()
        self.active_loans = self.create_card()
        self.overdue_loans = self.create_card()
        self.out_of_stock = self.create_card()

        # Position cards in grid (2 rows × 3 columns)
        grid.addWidget(self.total_books, 0, 0)
        grid.addWidget(self.total_authors, 0, 1)
        grid.addWidget(self.total_members, 0, 2)

        grid.addWidget(self.active_loans, 1, 0)
        grid.addWidget(self.overdue_loans, 1, 1)
        grid.addWidget(self.out_of_stock, 1, 2)

        main_layout.addLayout(grid)

        refresh_btn = QPushButton("Refresh Dashboard")
        refresh_btn.clicked.connect(self.refresh_stats)
        refresh_btn.setStyleSheet("""
            font-size: 16px; 
            padding: 10px;
        """)
        main_layout.addWidget(refresh_btn, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

    # ---------- CARD CREATOR ----------
    def create_card(self):
        card = QWidget()
        card.setStyleSheet("""
            background: white;
            border: 2px solid #A9C1FF;     /* blue border */
            border-radius: 12px;
            padding: 20px;
        """)
        layout = QVBoxLayout()
        label = QLabel("Loading...")
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label)
        card.setLayout(layout)
        return card

    def refresh_stats(self):
        queries = {
            "books": "SELECT COUNT(*) FROM book;",
            "authors": "SELECT COUNT(*) FROM author;",
            "members": "SELECT COUNT(*) FROM member;",
            "active_loans": "SELECT COUNT(*) FROM loan WHERE status='On Loan';",
            "overdue_loans": "SELECT COUNT(*) FROM loan WHERE status='Overdue';",
            "out_of_stock": "SELECT COUNT(*) FROM book WHERE copies_available = 0;"
        }

        results = {}
        for key, query in queries.items():
            try:
                cur = self.db.cursor()
                cur.execute(query)
                results[key] = cur.fetchone()[0]
            except Exception as e:
                print("Dashboard Error:", e)
                results[key] = 0

        # Update the cards
        self.total_books.layout().itemAt(0).widget().setText(f"Total Books: {results['books']}")
        self.total_authors.layout().itemAt(0).widget().setText(f"Total Authors: {results['authors']}")
        self.total_members.layout().itemAt(0).widget().setText(f"Total Members: {results['members']}")
        self.active_loans.layout().itemAt(0).widget().setText(f"Active Loans: {results['active_loans']}")
        self.overdue_loans.layout().itemAt(0).widget().setText(f"Overdue Loans: {results['overdue_loans']}")
        self.out_of_stock.layout().itemAt(0).widget().setText(f"Books Out of Stock: {results['out_of_stock']}")


# ---------- Login Dialog ----------
class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login - Smart Library")
        self.setModal(True)
        self.resize(300, 120)
        layout = QVBoxLayout()
        form = QFormLayout()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        form.addRow("Username:", self.username_input)
        form.addRow("Password:", self.password_input)
        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        self.login_btn = QPushButton("Login")
        self.cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(self.login_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        self.login_btn.clicked.connect(self.attempt_login)
        self.cancel_btn.clicked.connect(self.reject)

        self.authenticated = False
        self.user = None

    def attempt_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            QMessageBox.warning(self, 'Validation', 'Enter username and password')
            return
        hashed = hash_password(password)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username, full_name, role FROM users WHERE username=%s AND password_hash=%s",
                    (username, hashed))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            self.authenticated = True
            self.user = {'id': row[0], 'username': row[1], 'full_name': row[2], 'role': row[3]}
            self.accept()
        else:
            QMessageBox.warning(self, 'Login Failed', 'Invalid credentials')


# ---------- Main Window ----------
class MainWindow(QMainWindow):
    def __init__(self, user_info=None):
        super().__init__()

        try:
            self.db = psycopg2.connect(
                host="localhost",
                database="Limkokwing Smart Library System",
                user="postgres",
                password="julie22"
            )
        except Exception as e:
            print("Database connection failed:", e)
            sys.exit(1)  # Exit if DB fails

        self.current_user = user_info
        self.setWindowTitle('Smart Library')
        self.resize(1000, 650)
        self.tabs = QTabWidget()

        # create table structure if needed
        create_tables()

        # instantiate tabs
        self.dashboard_tab = DashboardTab(self.db)
        self.author_tab = AuthorTab()
        self.book_tab = BookTab(self.author_tab)
        self.member_tab = MemberTab()
        self.bookclub_tab = BookclubTab()
        self.loan_tab = LoanTab(self.book_tab, self.member_tab)

        # add tabs
        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.addTab(self.book_tab, 'Books')
        self.tabs.addTab(self.author_tab, 'Authors')
        self.tabs.addTab(self.member_tab, 'Members')
        self.tabs.addTab(self.bookclub_tab, 'Bookclubs')
        self.tabs.addTab(self.loan_tab, 'Loans')

        central = QWidget()
        layout = QVBoxLayout()
        # small header showing logged in user
        header_layout = QHBoxLayout()
        user_label = QLabel(f"User: {self.current_user['username'] if self.current_user else 'Unknown'}")
        user_label.setAlignment(Qt.AlignLeft)
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout)
        header_layout.addWidget(user_label)
        header_layout.addStretch()
        header_layout.addWidget(logout_btn)
        layout.addLayout(header_layout)

        layout.addWidget(self.tabs)
        central.setLayout(layout)
        self.setCentralWidget(central)

        # when authors change, refresh author combo in books tab
        self.author_tab.refresh_btn.clicked.connect(self.book_tab.load_authors_into_combo)
        # when members or books change, refresh loan tab combos
        self.book_tab.refresh_btn.clicked.connect(self.loan_tab.load_books_members)
        self.member_tab.refresh_btn.clicked.connect(self.loan_tab.load_books_members)

    def logout(self):
        reply = QMessageBox.question(self, 'Logout', 'Are you sure you want to logout?',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()
            # show login dialog again
            main()


# ---------- Application Entrypoint ----------
def main():
    app = QApplication(sys.argv)

    # ensure tables exist before login (so admin user gets created)
    create_tables()

    login = LoginDialog()
    if login.exec_() == QDialog.Accepted and login.authenticated:
        w = MainWindow(user_info=login.user)
        w.show()
        sys.exit(app.exec_())
    else:
        # login canceled or failed -> exit
        sys.exit(0)


if __name__ == '__main__':
    main()