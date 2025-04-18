import mysql from 'mysql2/promise';

// Debugging function
function debugEnvironment() {
    console.log("DB_HOST:", process.env.db_host);
    console.log("DB_PORT:", process.env.db_port);
    console.log("DB_NAME:", process.env.db_name);
    console.log("DB_USERNAME:", process.env.db_username);
    console.log("DB_PASSWORD exists:", !!process.env.db_password); // Avoid printing sensitive passwords
}

// Function to connect to the database and ensure the table exists
async function connectToDatabase() {
    debugEnvironment();

    // Connect to the database
    const connection = await mysql.createConnection({
        host: process.env.db_host,
        user: process.env.db_username,
        password: process.env.db_password,
        database: process.env.db_name,
        port: process.env.db_port,
    });

    console.log('Connected to RDS');

    // Create the `users` table if it does not exist
    const createTableQuery = `
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            age INT NOT NULL
        )
    `;
    await connection.execute(createTableQuery);
    console.log('Ensured "users" table exists');

    return connection;
}

// Lambda handler
export const handler = async (event) => {
    console.log("Event received:", JSON.stringify(event));

    try {
        const connection = await connectToDatabase();

        const httpMethod = event.httpMethod;
        const path = event.path;

        if (httpMethod === 'POST' && path === '/insert') {
            const body = JSON.parse(event.body);
            const { name, age } = body;

            const query = 'INSERT INTO users (name, age) VALUES (?, ?)';
            await connection.execute(query, [name, age]);

            return {
                statusCode: 200,
                body: JSON.stringify({ message: "Inserted successfully!" }),
            };
        } else if (httpMethod === 'GET' && path === '/retrieve') {
            const query = 'SELECT * FROM users';
            const [rows] = await connection.query(query);

            return {
                statusCode: 200,
                body: JSON.stringify(rows),
            };
        } else {
            return {
                statusCode: 404,
                body: JSON.stringify({ message: "Route not found" }),
            };
        }
    } catch (error) {
        console.error('Error:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({ message: 'Internal Server Error', error: error.message }),
        };
    }
};