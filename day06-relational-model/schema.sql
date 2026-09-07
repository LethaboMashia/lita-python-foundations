-- client_id uniquely identifies each client, name is the name of the client, phone is the client's phone number, and email is the client's email address. The primary key constraint ensures that each client has a unique identifier.
CREATE TABLE clients (
    client_id INTEGER PRIMARY KEY, 
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT
);

-- booking_id uniquely identifies each booking, date is the date of the booking, service is the type of service booked, and client_id is a foreign key that references the client who made the booking. The foreign key constraint ensures that each booking is associated with a valid client in the clients table.
CREATE TABLE bookings (
    booking_id INTEGER PRIMARY KEY, 
    date TEXT,
    service TEXT,
    client_id INTEGER,
    -- the foreign key links each booking to its corresponding client in the clients table and it lives in bookings because it is the child table in this relationship. The clients table is the parent table.
    FOREIGN KEY (client_id) REFERENCES clients(client_id) 
);