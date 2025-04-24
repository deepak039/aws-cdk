#!/bin/bash

# Exit script if there are any errors
set -e

echo "==========================================="
echo "⚙️  Starting Deployment Script for EC2..."
echo "==========================================="

# ---------------------------------------
# Step 1: Update and Install Dependencies
# ---------------------------------------
echo "🔄 Updating system and installing dependencies..."
sudo apt update -y
sudo apt upgrade -y

# Install Node.js (v18)
echo "🔄 Installing Node.js (v18)..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo bash -
sudo apt install -y nodejs

# Install MySQL Client
echo "🔄 Installing MySQL client..."
sudo apt install -y mysql-client

# Install PM2 (process manager for Node.js applications)
echo "🔄 Installing PM2 (for process management)..."
sudo npm install -g pm2

# ------------------------------------------
# Step 2: Validate Environment Variables
# ------------------------------------------
echo "🔍 Validating environment variables from /etc/environment..."

if [ ! -f /etc/environment ]; then
    echo "Error: User Data environment variables are not set!"
    exit 1
fi

# Export variables into the current shell session (this is optional, depends on your app)
export $(cat /etc/environment | xargs)

echo "Environment variables loaded:"
cat /etc/environment

# --------------------------------------
# Step 3: Copy Application Code to EC2
# --------------------------------------
echo "📂 Setting up application code..."
APP_DIR="/home/ubuntu/app"
sudo mkdir -p $APP_DIR

# Replace this with the actual Node.js code (index.mjs)
cat > $APP_DIR/index.mjs <<'EOL'
import mysql from 'mysql2/promise';
import express from 'express';

const app = express();
app.use(express.json());

// Debugging function
function debugEnvironment() {
    console.log("DB_HOST:", process.env.DB_HOST);
    console.log("DB_PORT:", process.env.DB_PORT);
    console.log("DB_NAME:", process.env.DB_NAME);
    console.log("DB_USERNAME:", process.env.DB_USERNAME);
    console.log("DB_PASSWORD exists:", !!process.env.DB_PASSWORD);
}

// Function to connect to the database
async function connectToDatabase() {
    debugEnvironment();

    const connection = await mysql.createConnection({
        host: process.env.DB_HOST,
        user: process.env.DB_USERNAME,
        password: process.env.DB_PASSWORD,
        database: process.env.DB_NAME,
        port: process.env.DB_PORT,
    });

    console.log('Connected to RDS');

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

app.post('/insert', async (req, res) => {
    try {
        const connection = await connectToDatabase();
        const { name, age } = req.body;

        const query = 'INSERT INTO users (name, age) VALUES (?, ?)';
        await connection.execute(query, [name, age]);

        res.status(200).json({ message: "Inserted successfully!" });
    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({ message: 'Internal Server Error', error: error.message });
    }
});

app.get('/retrieve', async (req, res) => {
    try {
        const connection = await connectToDatabase();
        const query = 'SELECT * FROM users';
        const [rows] = await connection.query(query);

        res.status(200).json(rows);
    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({ message: 'Internal Server Error', error: error.message });
    }
});

app.all('*', (req, res) => {
    res.status(404).json({ message: "Route not found" });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
EOL

echo "✔️ Application code copied to $APP_DIR/index.mjs"

# ------------------------------------------
# Step 4: Install Node.js Project Dependencies
# ------------------------------------------
cd $APP_DIR
echo "{}" > package.json # Initialize package.json (if missing)
echo "📦 Installing required Node.js dependencies..."
npm install mysql2 express

# ------------------------------------------
# Step 5: Start the Application using PM2
# ------------------------------------------
echo "🚀 Starting application using PM2..."
pm2 start $APP_DIR/index.mjs --name ec2-rds-app --env production

# Save process state to restart EC2 instance
pm2 startup
pm2 save

echo "==========================================="
echo "🎉 Deployment complete! Your app is live!"
echo "==========================================="
echo "Access it at: http://<YOUR-EC2-PUBLIC-IP>:3000"