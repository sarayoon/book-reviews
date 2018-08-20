import os
import psycopg2
import csv

try:
    conn = psycopg2.connect(os.environ['DATABASE_CREDENTIALS'])
except:
    print("I am unable to connect to the database")

cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS users;')
cur.execute('DROP TABLE IF EXISTS books;')
cur.execute('DROP TABLE IF EXISTS reviews;')

cur.execute('''
    CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL,
    hash VARCHAR NOT NULL
 );''')

cur.execute('''
    CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    isbn VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year VARCHAR(4) NOT NULL
);''')

cur.execute('''
    CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    books_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rating INTEGER NOT NULL,
    review TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL
);''')

with open('books.csv', 'r') as file:
    next(file)

    book_data = csv.reader(file, delimiter=',')
    for row in book_data:
        cur.execute("INSERT INTO books (isbn,title,author,year)"
                    "VALUES (%s,%s,%s,%s)",
                    row)
        print(row)

cur.execute("SELECT * FROM books;")
books_result = cur.fetchall()

print(books_result)

# Commit all our database operations so that they persist
conn.commit()

# Close the cursor
cur.close()

# Close the connection
conn.close()