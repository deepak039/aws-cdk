#!/bin/bash

# Update packages and install basic dependencies
sudo yum update -y
sudo yum install -y gcc-c++ make
sudo curl -sL https://rpm.nodesource.com/setup_16.x | sudo bash -
sudo yum install -y nodejs

# Create a directory for the application
mkdir -p /home/ec2-user/my-node-app
cd /home/ec2-user/my-node-app

# Create a basic Node.js application with DynamoDB integration
cat <<EOL > app.js
const http = require("http");
const url = require("url");
const AWS = require("aws-sdk");

// Set up AWS SDK (Assumes IAM role with DynamoDB permissions or ~/.aws/credentials are properly configured)
AWS.config.update({ region: "us-east-1" }); // Change region if required
const dynamodb = new AWS.DynamoDB.DocumentClient();

const port = 8080;

const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const path = parsedUrl.pathname;

  if (path === "/insert" && req.method === "POST") {
    // Insert route
    let body = "";
    req.on("data", chunk => {
      body += chunk;
    });
    req.on("end", () => {
      try {
        const data = JSON.parse(body);
        const params = {
          TableName: "TestTable" 
          Item: {
            id: data.id,             // Ensure the "id" attribute exists in the table schema
            name: data.name,         // Add attributes as per your table schema
          },
        };
        
        dynamodb.put(params, (err, result) => {
          if (err) {
            console.error("Error inserting item:", err);
            res.statusCode = 500;
            res.end(JSON.stringify({ message: "Failed to insert item" }));
          } else {
            res.statusCode = 200;
            res.end(JSON.stringify({ message: "Item inserted successfully", result }));
          }
        });
      } catch (error) {
        console.error("Error parsing request body:", error);
        res.statusCode = 400;
        res.end(JSON.stringify({ message: "Invalid request body" }));
      }
    });
  } else if (path === "/" && req.method === "GET") {
    // Health check route
    res.statusCode = 200;
    res.setHeader("Content-Type", "application/json");
    res.end(JSON.stringify({ message: "Application is healthy" }));
  } else {
    // Default route
    res.statusCode = 404;
    res.setHeader("Content-Type", "application/json");
    res.end(JSON.stringify({ message: "Route not found" }));
  }
});

server.listen(port, () => {
  console.log(\`Server running at http://localhost:\${port}/\`);
});
EOL

# Install project dependencies
npm init -y
npm install aws-sdk

# Start the application
nohup node app.js > output.log 2>&1 &