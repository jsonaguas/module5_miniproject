from library_main import connect_database
from mysql.connector import Error


class Book:
    def __init__(self, title, publication_date, isbn, author_id=None, available=1):
        self.title = title
        self.isbn = isbn
        self.publication_date = publication_date    
        self.available = available
        self.author_id = author_id

    def is_available(self):
        return self.available
    
    def add_book_to_database(self, cursor):
        query = 'INSERT INTO books (title, author_id, publication_date, isbn, availability) VALUES (%s, %s, %s, %s, %s)'
        cursor.execute(query, (self.title, self.author_id, self.publication_date, self.isbn, self.available))
        
def add_book(cursor):
    title = input("Enter the title of the book: ")
    author = input("Enter the author of the book: ")
    query = 'SELECT id FROM authors WHERE name = %s'
    cursor.execute(query, (author,))
    query_result = cursor.fetchone()
    if query_result:
        author_id = query_result[0]
    else:
        return None
    publication_date = input("Enter the publication date of the book: ")
    isbn = input("Enter the ISBN of the book: ")
    new_book = Book(title, publication_date, isbn, author_id)
    new_book.add_book_to_database(cursor)

    
def check_out(isbn, cursor, library_id):
    isbn = isbn.strip()
    print(f"Checking out ISBN: {isbn}")
    # Combine the availability check and book ID retrieval into one query
    query = 'SELECT id, availability FROM books WHERE isbn = %s'
    cursor.execute(query, (isbn,))
    book = cursor.fetchone()
    
    if not book:
        print("Book not found.")
        return
    
    book_id, availability = book
    
    if availability == 0:
        print("Book is already checked out.")
        return
    
    if availability == 1:
    # Retrieve the user ID
        query = 'SELECT id FROM users WHERE library_id = %s'
        cursor.execute(query, (library_id,))
        user = cursor.fetchone()
        
        if user:
            user_id = user[0]
            # Insert into borrowed_books
            borrow_date = input("Enter the date you borrowed the book: ")
            return_date = input("Enter the date you will return the book: ")
            query = 'INSERT INTO borrowed_books (user_id, book_id,borrow_date, return_date) VALUES (%s, %s, %s, %s)'
            cursor.execute(query, (user_id, book_id,borrow_date, return_date))
            return book_id
    
        else:
            print("User not found.")
            return None
    else:
        print("Book is already checked out.")
    

def update_book_availablity(cursor, isbn):
    query = 'UPDATE books SET availability = 0 WHERE isbn = %s'
    cursor.execute(query, (isbn,))

    

def return_book(isbn,cursor):
    query = 'SELECT id FROM books WHERE isbn = %s'
    cursor.execute(query, (isbn,))
    book = cursor.fetchone()
    if book:
        query = 'UPDATE books SET availability = 1 WHERE isbn = %s'
        cursor.execute(query, (isbn,))
        print(f"Book with ISBN {isbn} has been returned.")
        query = 'DELETE FROM borrowed_books WHERE book_id = %s'
        cursor.execute(query, (book[0],))





class User:
    def __init__(self, name, library_id):
        self.name = name
        self.library_id = library_id
        self.loaned_books = []

    def loan_book(self, book):
        self.loaned_books.append(book)
        print(f"{book.title} has been loaned to {self.name}.")
    

    def add_user_to_database(self, cursor):
        query = 'INSERT INTO users (name, library_id) VALUES (%s, %s)'
        cursor.execute(query, (self.name, self.library_id))

def add_user(users, cursor):
    name = input("Enter the name of the user: ")
    library_id = input("Enter the ID of the user: ")
    new_user = User(name, library_id)
    users[library_id] = new_user
    new_user.add_user_to_database(cursor)




class Author:
    def __init__(self, name, biography=None):
        self.name = name
        self.biography = biography
    def add_author_to_database(self, cursor):
        query = 'INSERT INTO authors (name, biography) VALUES (%s, %s)'
        cursor.execute(query, (self.name, self.biography))
def add_author(authors,cursor):
    name = input("Enter the name of the author: ")
    biography = input("Enter the biography of the author: ")
    new_author = Author(name, biography)
    authors[name] = new_author
    new_author.add_author_to_database(cursor)
def display_author(writer, authors):
    for author in authors.values():
        if author.name == writer:
            print(f"Name: {author.name}")
            print(f"Biography: {author.biography}")




def main():
    conn = connect_database()
    if conn is not None:
        try:
            cursor = conn.cursor()
            library = {}
            users = {}
            authors = {}
            while True:

                print("Welcome to the Library Management System!")
                print(
                '''Main Menu
                1. Book Operations
                2. User Operations
                3. Author Operations
                4. Quit
                ''')
                choice = input("Please enter your choice: ")
                if choice == '1':
                    print('''Book Operations
                        1. Add a new book
                        2. Borrow a book
                        3. Return a book
                        4. Search for a book
                        5. Display all books''')
                    book_choice = input("Please enter your choice: ")
                    if book_choice == '1':
                        add_book(cursor)
                        conn.commit()
                    elif book_choice == '2':
                        isbn = input("Enter the ISBN of the book you'd like to borrow: ")
                        try:
                            library_id = input("Enter your user ID: ")
                        except KeyError:
                            print("User does not exist. Please add the user first.")
                            continue
                        check_out(isbn, cursor, library_id)
                        conn.commit()
                        update_book_availablity(cursor, isbn)
                        conn.commit()
                    elif book_choice == '3':
                        isbn = input("Enter the ISBN of the book you'd like to return: ")
                        return_book(isbn,cursor)
                        conn.commit()
                    elif book_choice == '4':
                        search_book = input("Enter the title of the book you'd like to search for: ")
                        query = 'SELECT * FROM books WHERE title = %s'
                        cursor.execute(query, (search_book,))
                        book = cursor.fetchone()
                        if book:
                            print(f"Title: {book[1]}")
                            print(f"Author ID: {book[2]}")
                            print(f"Publication Date: {book[3]}")
                            print(f"ISBN: {book[4]}")
                            print(f"Availability: {book[5]}")
                    elif book_choice == '5':
                        query = 'SELECT * FROM books'
                        cursor.execute(query)
                        books = cursor.fetchall()
                        for book in books:
                            print(f"Title: {book[1]}")
                            print(f"Author ID: {book[2]}")
                            print(f"Publication Date: {book[4]}")
                            print(f"ISBN: {book[3]}")
                            print(f"Availability: {book[5]}")
                elif choice == '2':
                    print('''User Operations
                            1. Add a new user
                            2. View user details
                            3. Display all users''')
                    user_choice = input("Please enter your choice: ")
                    if user_choice == '1':
                        add_user(users, cursor)
                        conn.commit()
                    elif user_choice == '2':
                        user_id = input("Enter the ID of the user you'd like to view: ")
                        query = 'SELECT * FROM users WHERE library_id = %s'
                        cursor.execute(query, (user_id,))
                        user = cursor.fetchone()
                        if user:
                            print(f"Name: {user[1]}")
                            print(f"ID: {user[2]}")
                        else:
                            print("User not found.")
                    elif user_choice == '3':
                        query = 'SELECT * FROM users'
                        cursor.execute(query)
                        users = cursor.fetchall()
                        for user in users:
                            print(f"Name: {user[1]}")
                            print(f"ID: {user[2]}")
                    else:
                        print("Invalid choice. Please try again.")
                        continue
                elif choice == '3':
                        print('''Author Operations
                            1. Add a new author
                            2. View author details
                            3. Display all authors''')
                        author_choice = input("Please enter your choice: ")
                        if author_choice == '1':
                            add_author(authors,cursor)
                            conn.commit()
                        elif author_choice == '2':
                            writer = input("Enter the name of the author you'd like to view: ")
                            query = 'SELECT * FROM authors WHERE name = %s'
                            cursor.execute(query, (writer,))
                            author = cursor.fetchone()
                            if author:
                                display_author(writer, authors)
                            else:
                                print("Author not found.")
                        elif author_choice == '3':
                            query = 'SELECT * FROM authors'
                            cursor.execute(query) 
                            authors = cursor.fetchall()
                            for author in authors:
                                print(f"Name: {author[1]}")
                                print(f"Biography: {author[2]}")
                        else:
                            print("Invalid choice. Please try again.")
                            continue
                elif choice == '4':
                        break
                else:
                        print("Invalid choice. Please try again.")
                        continue
        except Error as e:
            print(f"Error: {e}")
        finally:
            if conn and conn.is_connected():
                conn.close()
                cursor.close()
                print('Disconnected from MySQL database')
if __name__ == '__main__':
            main()


