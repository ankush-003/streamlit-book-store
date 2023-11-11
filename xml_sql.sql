-- Create the database for the Online Bookstore
CREATE DATABASE OnlineBookstore;

-- Use the created database
USE OnlineBookstore;

-- Create a table for storing information about books
CREATE TABLE Books (
    BookID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(255) NOT NULL,
    Author VARCHAR(255) NOT NULL,
    Price DECIMAL(10, 2) NOT NULL,
    Quantity INT NOT NULL
);

-- Create a table for storing user information
CREATE TABLE Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(50) NOT NULL,
    Password VARCHAR(255) NOT NULL
);

-- Create a table to store user cart information
CREATE TABLE Carts (
    CartID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT NOT NULL,
    BookID INT NOT NULL,
    Quantity INT NOT NULL
);

-- Add foreign keys to establish relationships between tables
ALTER TABLE Carts
ADD FOREIGN KEY (UserID)
REFERENCES Users(UserID);

ALTER TABLE Carts
ADD FOREIGN KEY (BookID)
REFERENCES Books(BookID);