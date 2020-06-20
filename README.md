My project is a catalogue page, based off the web track distribution code for Finance.
I made this project to improve my understanding of using databases and the Flask framework to make dynamic pages. 
I used the following technologies: Python, SQLite3, Flask.

The first step was creating an appropriate database that could store all of the necessary data. I made 5 tables - "user_master", "product_master", "order_header", "order_detail" and "basket".

1. "user_master" -> This has the headers - "user_id" (Primary Key that identifies each user), "email" (Used for logging in), "user_name" (Identification), "mobile" (stores their number), "date_created" and "time_created" (timestamps), and password.

Passwords are hashed using the generate_password_hash function.

2. "product_master" -> "product_code" (Primary Key), "product_description" (name of product), "price" (cost of product), "stock" (how many are in stock), "image" (was not used in this project).

I used a addProduct.sql script to add products when I needed them.

3. "basket" -> "order_no" (number of order), "product_code" (composite key along with time_created), "product_description", "price", "order_qty", "user_id", "date_created" and "time_created".

This table stores the items in the basket of each user. The data is saved if not checked out, and once you complete the checkout process, all of the data is copied into the "order_detail" table and a header is created in the "order_header" table. The basket is then cleared.

4. "order_header" -> "order_no" (Primary Key), "order_date" (DATE), "addr_1" and "addr_2" (Address lines), "user_id", "date_created" and "time_created".

5. "order_detail" -> identical to basket table. Initially there was no basket, but it caused many problems so I created "basket". This stores permanent data of each purchase.

I made a tableCreate.sql script to create the tables.


In order to make the project, I needed the base from Finance, such as login, logout and register. I then moved on to make functions like order, checkout, change (password) and remove (items).

It uses the Flask microframework to dynamically create the websites, and gets data from the database using the CS50 Python SQL library.

A "templates" folder was created, with a base "layout.html" and multiple .html files that render the website.

I switched the usd function to a euro function, and removed the apology function to flash error messages instead.

It has minimum and maximum values for adding to cart and removing from cart, based on the available stock of the item and the quantity added to cart respectively.

It also updates the database based on how much stock is leftover. 

The site always checks to ensure passwords match, that all fields are filled, and that no accounts have the same email.
Before checking out, it asks you to enter your email and password to verify once again, before completing the order. 

