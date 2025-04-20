#!/bin/bash

# Update system packages and install Node.js
yum update -y
curl -sL https://rpm.nodesource.com/setup_16.x | bash -
yum install nodejs -y

# Go to the home directory of ec2-user
cd /home/ec2-user || exit

# Initialize a Node.js project
sudo -u ec2-user mkdir node_app
cd node_app || exit
sudo -u ec2-user npm init -y

# Install necessary packages
sudo -u ec2-user npm install aws-sdk

# Write Node.js application code
sudo -u ec2-user bash -c 'cat > app.js << "EOF"
const http = require("http");
const AWS = require("aws-sdk");

// Configure AWS SDK (DynamoDB is assumed to run in the same AWS environment)
AWS.config.update({ region: "us-east-1" }); // Replace "us-east-1" with your actual region
const dynamoDb = new AWS.DynamoDB.DocumentClient();

// Define the HTTP server and routes
const server = http.createServer(async (req, res) => {
  if (req.method === "POST" && req.url === "/data") {
    let body = "";
    req.on("data", chunk => {
      body += chunk.toString();
    });
    req.on("end", async () => {
      // Parse the incoming JSON data
      const item = JSON.parse(body);

      // Define DynamoDB PUT parameters
      const params = {
        TableName: "YourTableName", // Replace with your DynamoDB table name
        Item: item
      };

      try {
        await dynamoDb.put(params).promise();
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ message: "Item written successfully." }));
      } catch (error) {
        res.writeHead(500, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ message: "Failed to write item.", error }));
      }
    });
  } else if (req.method === "GET" && req.url.startsWith("/data")) {
    const id = req.url.split("/")[2]; // Assume ID is passed as the last segment of the URL

    // Define DynamoDB GET parameters
    const params = {
      TableName: "YourTableName", // Replace with your DynamoDB table name
      Key: { id } // Key should match your table's schema }'
    try {
      const data = await dynamoDb.get(params).promise();
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify(data.Item || { message: "Item not found." }));
    } catch (error) {
      res.writeHead(500, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ message: "Failed to retrieve item.", error }));
    }
  } else {
    res.writeHead(404, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ message: "Route not found." }));
  }
});

// Start the server
server.listen(3000, () => console.log("Server is running on port 3000"));
EOF'

# Make sure the app.js file is owned by ec2-user
chown ec2-user:ec2-user app.js

# Install and configure PM2 to manage the Node.js application as a service
npm install -g pm2
su - ec2-user -c "pm2 start app.js --name 'node-dynamodb-app'"
su - ec2-user -c "pm2 startup"
su - ec2-user -c "pm2 save"

# Inform the user of the application status
echo "Node.js application has been set up and is managed by PM2."