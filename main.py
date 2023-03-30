import datetime
import uuid
import sqlite3


class LibrarySystem:
    def __init__(self, library_name):
        self.library_name = library_name
        self.conn = sqlite3.connect('library.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS books 
                          (book_id TEXT PRIMARY KEY, book_title TEXT, author TEXT, category TEXT,
                           quantity INTEGER, availability TEXT, lender_name TEXT DEFAULT NULL,
                            issue_date TEXT DEFAULT NULL)''')

        self.conn.commit()

    def add_book(self):
        book_title = input("Enter Book Title : ")
        author = input("Enter Author Name : ")
        category = input("Enter Book Category : ")
        quantity = input("Enter Book Quantity : ")
        if book_title == "" or author == "" or category == "" or quantity == "":
            print("Please enter valid input for book title, author, category and quantity!!!")
        else:
            book_id = str(uuid.uuid4())[:3]
            availability = "yes"
            self.c.execute("INSERT INTO books (book_id, book_title, author, category, quantity, availability) "
                           "VALUES (?, ?, ?, ?, ?, ?)",
                           (book_id, book_title, author, category, quantity, availability))
            self.conn.commit()
            print(f"The book '{book_title}' has been added successfully !!!")

    def display_books(self):
        print("-----------------------------------List Of Books------------------------------------"
              "---------------------------------------------")
        print("{:<10} {:<40} {:<30} {:<20} {:<10} {:<15}".format(
            "Book ID", "Title", "Author", "Category", "Quantity", "Availability"))
        print("---------------------------------------------------------------------------------------"
              "------------------------------------------")
        self.c.execute("SELECT * FROM books")
        rows = self.c.fetchall()
        for row in rows:
            print("{:<10} {:<40} {:<30} {:<20} {:<10} {:<15}".format(
                row[0], row[1], row[2], row[3], row[4], row[5]))

    def rent_books(self):
        rented_books = []
        while True:
            search_criteria = input("Enter book ID, title, author, or category to search for a book (q to quit): ")
            if search_criteria == 'q':
                break
            self.c.execute(
                "SELECT * FROM books WHERE book_title LIKE ? OR author LIKE ? OR category LIKE ? OR book_id = ?",
                (
                    '%' + search_criteria + '%', '%' + search_criteria + '%', '%' + search_criteria + '%',
                    search_criteria))
            rows = self.c.fetchall()
            if not rows:
                print(f"No books found for '{search_criteria}'")
            else:
                print("Found books:")
                print("Book ID", "\t", "Title", "\t\t\t", "Author", "\t\t", "Category", "\t\t", "Quantity", "\t",
                      "Availability")
                print("----------------------------------------------------------------------------")
                for row in rows:
                    print(row[0], "\t\t", row[1], "\t\t", row[2], "\t", row[3], "\t\t", row[4], "\t\t", row[5])
                book_id = input("\nEnter the book ID to rent (q to quit): ")
                if book_id == 'q':
                    break
                self.c.execute("SELECT * FROM books WHERE book_id = ?", (book_id,))
                row = self.c.fetchone()
                if not row:
                    print("Invalid book ID. Please enter a valid book ID.")
                elif row[5] == 'no':
                    print("This book is currently not available. Please choose another book or try again later.")
                elif row[4] == 0:
                    print("Sorry, all copies of this book have been rented out."
                          " Please choose another book or try again later.")
                else:
                    lender_name = input("Enter your name: ")
                    issue_date = datetime.date.today()
                    self.c.execute(
                        "UPDATE books SET lender_name = ?, issue_date = ?, quantity = quantity - 1 WHERE book_id = ?",
                        (lender_name, issue_date, book_id))
                    self.conn.commit()
                    rented_books.append(row[1])
                    print(f"\nCongratulations! You have rented the book '{row[1]}' successfully!!!\n")
                    if row[4] == 1:
                        self.c.execute("UPDATE books SET availability = 'no' WHERE book_id = ?", (book_id,))
                        self.conn.commit()
                    another_rental = input("Do you want to rent another book? (y/n) : ")
                    if another_rental.lower() == 'n':
                        self.print_receipt(rented_books)
                        break

    def display_rented_books(self):
        while True:
            self.c.execute("SELECT * FROM books WHERE availability = 'no'")
            rows = self.c.fetchall()
            if not rows:
                print("No books have been rented out.")
            else:
                print("Rented books:")
                print("{:<10} {:<40} {:<30} {:<20} {:<20} {:<15}".format(
                    "Book ID", "Title", "Author", "Category", "Lender Name", "Due Date"))
                print("-------------------------------------------------------------------------------"
                      "----------------")
                for row in rows:
                    lender_name = row[6]
                    due_date = row[7] + datetime.timedelta(days=30)
                    print("{:<10} {:<40} {:<30} {:<20} {:<20} {:<15}".format(
                        row[0], row[1], row[2], row[3], lender_name, due_date.strftime("%Y-%m-%d")))
            return_option = input("Press 'm' to return to the main menu or 'q' to exit, "
                                  "or any other key to return another book: ")
            if return_option.lower() == 'm':
                break
            elif return_option.lower() == 'q':
                exit()

    def remove_book(self):
        while True:
            book_id = input("Enter the book ID to remove (m to return to main menu): ")
            if book_id == 'm':
                return
            self.c.execute("SELECT * FROM books WHERE book_id = ?", (book_id,))
            row = self.c.fetchone()
            if not row:
                print("Invalid book ID. Please enter a valid book ID.")
            else:
                book_title = row[1]
                confirm = input(f"Are you sure you want to remove '{book_title}'? (y/n) ")
                if confirm.lower() == 'y':
                    self.c.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
                    self.conn.commit()
                    print(f"The book '{book_title}' has been removed successfully!")
                else:
                    continue
            another_removal = input("Do you want to remove another book? (y/n): ")
            if another_removal.lower() == 'n':
                break

    def search_books(self):
        while True:
            search_criteria = input("Enter a book title, author, or category to search for a book (q to quit): ")
            if search_criteria == 'q':
                break
            self.c.execute("SELECT * FROM books WHERE book_title LIKE ? OR author LIKE ? OR category LIKE ?",
                           ('%' + search_criteria + '%', '%' + search_criteria + '%', '%' + search_criteria + '%'))
            rows = self.c.fetchall()
            if not rows:
                print(f"No books found for '{search_criteria}'")
            else:
                print("Found books :")
                print(" Book ID", "\t", "Title", "\t\t\t", "Author", "\t\t", "Category", "\t\t", "Quantity", "\t",
                      "Availability")
                print("----------------------------------------------------------------------------")
                for row in rows:
                    book_id = row[0]
                    book_title = row[1]
                    author = row[2]
                    category = row[3]
                    quantity = row[4]
                    availability = row[5]
                    print(book_id, "\t\t", book_title, "\t\t", author, "\t", category, "\t\t", quantity, "\t\t",
                          availability)
                rent_option = input("\nDo you want to rent a book? (y/n): ")
                if rent_option.lower() == 'y':
                    book_id = input("\nEnter the book ID to rent: ")
                    self.c.execute("SELECT * FROM books WHERE book_id = ?", (book_id,))
                    row = self.c.fetchone()
                    if row and row[5] == 'yes':
                        lender_name = input("Please Enter your name: ")
                        issue_date = datetime.date.today()
                        self.c.execute("UPDATE books SET lender_name = ?, issue_date = ?, quantity = quantity - 1, "
                                       "availability = CASE WHEN quantity - 1 = 0 THEN 'no' ELSE 'yes' END "
                                       "WHERE book_id = ?", (lender_name, issue_date, book_id))
                        self.conn.commit()
                        print(f"\nCongratulations! You have rented the book '{row[1]}' successfully !!!\n")
                        return
                    else:
                        print("Invalid book ID or the book is not available for rent. Please enter a valid book ID.")
                else:
                    return

    def return_books(self):
        while True:
            book_id = input("Enter the book ID to return (m to return to main menu): ")
            if book_id == 'm':
                return
            self.c.execute("SELECT * FROM books WHERE book_id = ?", (book_id,))
            row = self.c.fetchone()
            if not row:
                print("Invalid book ID. Please enter a valid book ID.")
            elif row[5] == 'yes':
                print("This book has not been rented out yet. Please enter a book ID for a rented book.")
            else:
                book_title = row[1]
                lender_name = row[6]
                issue_date = row[7]
                return_date = datetime.date.today()
                days_rented = (return_date - issue_date).days
                print(f"\nBook ID: {book_id}\nTitle: {book_title}\nLender Name: {lender_name}\n"
                      f"Issue Date: {issue_date}\nReturn Date: {return_date}\nDays Rented: {days_rented}")
                confirm = input("Are you sure you want to return this book? (y/n) ")
                if confirm.lower() == 'y':
                    self.c.execute("UPDATE books SET lender_name = NULL, issue_date = NULL, quantity = quantity + 1, "
                                   "availability = 'yes' WHERE book_id = ?", (book_id,))
                    self.conn.commit()
                    print(f"\nThe book '{book_title}' has been returned successfully!")
                else:
                    continue
            another_return = input("Do you want to return another book? (y/n): ")
            if another_return.lower() == 'n':
                break

    def print_receipt(self, rented_books):
        print("Thank you for using the library system. Here is your receipt:")
        print("--------------------------------------------------------------------")
        print("Library Name:", self.library_name)
        print("Date:", datetime.date.today())
        print("Books rented:")
        for book in rented_books:
            print(book)
            print("--------------------------------------------------------------------")


if __name__ == "__main__":
    try:
        mylms = LibrarySystem("Python's Library")
        press_key_list = {"1": "Display Books", "2": "Rent Books", "3": "Donate Books", "4": "Return Books",
                          "5": "Search Books", "6": "Display Rented Books", "7": "Delete Books", "8": "Exit"}
        key_press = False
        while not (key_press == "8"):
            print(f"\n-------------Welcome TO {mylms.library_name}'s Library System---------------\n")
            for key, value in press_key_list.items():
                print("Press", key, "To", value)
            key_press = input("Press Key : ").lower()
            if key_press == "1":
                print("\nCurrent Selection : Display Books\n")
                mylms.display_books()

            elif key_press == "2":
                print("\nCurrent Selection : Rent Books\n")
                mylms.rent_books()

            elif key_press == "3":
                print("\nCurrent Selection : Donate Books\n")
                mylms.add_book()

            elif key_press == "4":
                print("\nCurrent Selection : Return Books\n")
                mylms.return_books()

            elif key_press == "5":
                print("\nCurrent Selection : Search Books\n")
                mylms.search_books()

            elif key_press == "6":
                print("\nCurrent Selection : Display Rented Books\n")
                mylms.display_rented_books()

            elif key_press == "7":
                print("\nCurrent Selection : Delete Books\n")
                mylms.remove_book()

            elif key_press == "8":
                continue

    except Exception as e:

        print("An error occurred:", e)

        # handle the exception here

    finally:

        # perform any necessary cleanup here

        print("Exiting Library System...")
