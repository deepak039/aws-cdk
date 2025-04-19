#!/bin/bash
# Update packages and install basic dependencies
sudo yum update -y
sudo yum install -y gcc-c++ make
sudo curl -sL https://rpm.nodesource.com/setup_16.x | sudo bash -
sudo yum install -y nodejs
# Create a directory for the application
mkdir -p /home/ec2-user/my-node-app
cd /home/ec2-user/my-node-app
# Create a basic Node.js application with a check route
cat <<EOL > app.js
const http = require("http");
const AWS = require("aws-sdk");

// Set up AWS SDK (Assumes IAM role or ~/.aws/credentials are properly configured)
AWS.config.update({ region: "us-east-1" }); // Change region if required
const dynamodb = new AWS.DynamoDB();

const TABLE_NAME = "TestTable"; // Define the table name

const port = 8080;
const server = http.createServer((req, res) => {
  // Define routing logic

  if (req.url === "/check" && req.method === "GET") {
    res.statusCode = 200;
    res.setHeader("Content-Type", "application/json");
    res.end(JSON.stringify({ status: "up", message: "Server is running!" }));
  } else if (req.url === "/get-item" && req.method === "GET") {
    // Simple GET request to DynamoDB
    const params = {
      TableName: TABLE_NAME,
      Key: {
        pk: { S: '1' }, // Replace '1' with the actual partition key value
        sk: { S: '1' }, // Replace '1' with the actual sort key value
      },
    };

    dynamodb.getItem(params, (err, data) => {
      if (err) {
        console.error("Error retrieving item:", err);
        res.statusCode = 500;
        res.setHeader("Content-Type", "application/json");
        res.end(JSON.stringify({ message: "Failed to retrieve item" }));
      } else {
        res.statusCode = 200;
        res.setHeader("Content-Type", "application/json");
        res.end(JSON.stringify(data.Item || { message: "Item not found" }));
      }
    });
  } else {
    res.statusCode = 404;
    res.setHeader("Content-Type", "text/plain");
    res.end("Not Found");
  }
});
server.listen(port, () => {
  console.log(\`Server running at http://localhost:\${port}/\`);
});
EOL
# Install project dependencies (none for this example but include npm init if needed)
npm init -y
# Install necessary packages
npm install
# Start the application
nohup node app.js > output.log 2>&1 &