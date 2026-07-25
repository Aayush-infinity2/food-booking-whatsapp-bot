USE food_booking_bot;

CREATE TABLE IF NOT EXISTS students (
    registration_number VARCHAR(30) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (

    id INT AUTO_INCREMENT PRIMARY KEY,

    customer_phone VARCHAR(20) NOT NULL,

    area VARCHAR(100) NOT NULL,

    restaurant VARCHAR(100) NOT NULL,

    category VARCHAR(100) NOT NULL,

    item VARCHAR(150) NOT NULL,

    variant VARCHAR(100),

    quantity INT NOT NULL,

    total DECIMAL(10,2) NOT NULL,

    pickup_slot VARCHAR(50) NOT NULL,

    booking_reference VARCHAR(36) NULL,

    status ENUM(
        'Pending',
        'Preparing',
        'Ready',
        'Completed',
        'Cancelled'
    ) DEFAULT 'Pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_phone_created ON orders (customer_phone, created_at);
CREATE INDEX idx_orders_status_created ON orders (status, created_at);
CREATE INDEX idx_orders_booking_reference ON orders (booking_reference);
