-- Insert 10 users
INSERT INTO users (username, password_hash, full_name, role) VALUES
('admin1', 'hash1', 'Alice Johnson', 'admin'),
('staff1', 'hash2', 'Bob Smith', 'staff'),
('staff2', 'hash3', 'Carol Davis', 'staff'),
('manager1', 'hash4', 'David Wilson', 'manager'),
('librarian1', 'hash5', 'Emma Brown', 'librarian'),
('staff3', 'hash6', 'Frank Miller', 'staff'),
('admin2', 'hash7', 'Grace Lee', 'admin'),
('staff4', 'hash8', 'Henry Taylor', 'staff'),
('librarian2', 'hash9', 'Irene Clark', 'librarian'),
('staff5', 'hash10', 'Jack White', 'staff');


-- Insert 10 authors
INSERT INTO author (name, bio, nationality, birth_year) VALUES
('George Orwell', 'English novelist and essayist', 'British', 1903),
('Jane Austen', 'English novelist known for social commentary', 'British', 1775),
('J.K. Rowling', 'Author of Harry Potter series', 'British', 1965),
('Stephen King', 'Master of horror fiction', 'American', 1947),
('Haruki Murakami', 'Japanese writer of surreal fiction', 'Japanese', 1949),
('Agatha Christie', 'Queen of crime fiction', 'British', 1890),
('Ernest Hemingway', 'American novelist and journalist', 'American', 1899),
('Toni Morrison', 'Nobel Prize-winning American novelist', 'American', 1931),
('Gabriel Garcia Marquez', 'Colombian magical realism writer', 'Colombian', 1927),
('Chimamanda Ngozi Adichie', 'Contemporary Nigerian writer', 'Nigerian', 1977);

-- Insert 10 members
INSERT INTO member (name, email, phone, membership_type, join_date) VALUES
('Michael Scott', 'michael@example.com', '555-0101', 'premium', '2023-01-15'),
('Pam Beesly', 'pam@example.com', '555-0102', 'standard', '2023-02-20'),
('Jim Halpert', 'jim@example.com', '555-0103', 'premium', '2023-03-10'),
('Dwight Schrute', 'dwight@example.com', '555-0104', 'standard', '2023-01-25'),
('Angela Martin', 'angela@example.com', '555-0105', 'premium', '2023-04-05'),
('Kevin Malone', 'kevin@example.com', '555-0106', 'basic', '2023-05-12'),
('Stanley Hudson', 'stanley@example.com', '555-0107', 'standard', '2023-06-18'),
('Phyllis Vance', 'phyllis@example.com', '555-0108', 'premium', '2023-03-22'),
('Oscar Martinez', 'oscar@example.com', '555-0109', 'standard', '2023-07-30'),
('Meredith Palmer', 'meredith@example.com', '555-0110', 'basic', '2023-08-14');

-- Insert 10 book clubs
INSERT INTO bookclub (name, description, meeting_day) VALUES
('Mystery Lovers', 'Discusses mystery and thriller novels', 'Monday'),
('Science Fiction Club', 'Focus on sci-fi and fantasy books', 'Tuesday'),
('Classic Literature', 'Reading classic novels', 'Wednesday'),
('Contemporary Fiction', 'Modern fiction discussions', 'Thursday'),
('Non-fiction Readers', 'Explores non-fiction works', 'Friday'),
('Poetry Circle', 'Shares and discusses poetry', 'Saturday'),
('Historical Fiction', 'Historical novel enthusiasts', 'Sunday'),
('Young Adult Book Club', 'YA literature discussions', 'Monday'),
('Business Books', 'Professional development reading', 'Tuesday'),
('Cookbook Club', 'Shares recipes and cooking tips', 'Wednesday');

-- Insert 10 books (author_id references author table)
INSERT INTO book (title, author_id, isbn, publisher, published_year, genre, copies_available) VALUES
('1984', 1, '9780451524935', 'Signet Classic', 1949, 'Dystopian', 5),
('Pride and Prejudice', 2, '9780141439518', 'Penguin Classics', 1813, 'Romance', 3),
('Harry Potter and the Philosopher''s Stone', 3, '9780747532743', 'Bloomsbury', 1997, 'Fantasy', 7),
('The Shining', 4, '9780307743657', 'Doubleday', 1977, 'Horror', 4),
('Norwegian Wood', 5, '9780375704024', 'Vintage', 1987, 'Literary Fiction', 2),
('Murder on the Orient Express', 6, '9780062693662', 'William Morrow', 1934, 'Mystery', 6),
('The Old Man and the Sea', 7, '9780684801223', 'Scribner', 1952, 'Literary Fiction', 3),
('Beloved', 8, '9781400033416', 'Knopf', 1987, 'Historical Fiction', 2),
('One Hundred Years of Solitude', 9, '9780060883287', 'Harper & Row', 1967, 'Magical Realism', 4),
('Americanah', 10, '9780307271082', 'Knopf', 2013, 'Contemporary Fiction', 5);

-- Insert 10 loans
INSERT INTO loan (book_id, member_id, loan_date, due_date, return_date, status) VALUES
(1, 1, '2024-01-10', '2024-01-24', '2024-01-23', 'returned'),
(2, 2, '2024-01-12', '2024-01-26', NULL, 'overdue'),
(3, 3, '2024-01-15', '2024-01-29', '2024-01-28', 'returned'),
(4, 4, '2024-01-18', '2024-02-01', NULL, 'active'),
(5, 5, '2024-01-20', '2024-02-03', '2024-02-02', 'returned'),
(6, 6, '2024-01-22', '2024-02-05', NULL, 'active'),
(7, 7, '2024-01-25', '2024-02-08', NULL, 'active'),
(8, 8, '2024-01-28', '2024-02-11', '2024-02-10', 'returned'),
(9, 9, '2024-01-30', '2024-02-13', NULL, 'active'),
(10, 10, '2024-02-01', '2024-02-15', NULL, 'active');