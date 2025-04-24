#!/bin/bash
# Update system packages and install necessary dependencies
echo "Updating system packages and installing dependencies..."
sudo yum update -y
sudo yum install -y gcc-c++ make
sudo curl -sL https://rpm.nodesource.com/setup_16.x | sudo bash -
sudo yum install -y nodejs
# Create a directory for the application
echo "Creating application directory..."
mkdir -p /home/ec2-user/my-node-app
cd /home/ec2-user/my-node-app
# Create the Node.js application file
echo "Creating Node.js application code..."
cat <<EOL > app.js
const http = require("http");
const AWS = require("aws-sdk");
// Set AWS Region
AWS.config.update({ region: "ap-south-1" }); // Adjust the region as needed
// Initialize DynamoDB Document Client
const dynamoDb = new AWS.DynamoDB.DocumentClient();
// Specify the DynamoDB table name
const TABLE_NAME = "TestTable";
const port = 8080;
const server = http.createServer(async (req, res) => {
  // Health Check Route
  if (req.url === "/check" && req.method === "GET") {
    res.statusCode = 200;
    res.setHeader("Content-Type", "application/json");
    res.end(JSON.stringify({ status: "up", message: "Server is running and healthy!" }));
    return;
  }
  // POST Route: Insert or update an item in DynamoDB
  if (req.url === "/put" && req.method === "POST") {
    let body = "";
    req.on("data", (chunk) => {
      body += chunk;
    });
    req.on("end", async () => {
      try {
        const item = JSON.parse(body); // Parse the JSON body from the request
        const { message } = item;
        // Validate request body
        if (!message) {
          res.statusCode = 400;
          res.end(JSON.stringify({ status: "error", message: "Message is required in the request body." }));
          return;
        }
        const dynamoParams = {
          TableName: TABLE_NAME,
          Item: {
            pk: "1", // Static primary key value
            sk: "1", // Static sort key value
            message, // Message attribute
          },
        };
        await dynamoDb.put(dynamoParams).promise();
        res.statusCode = 200;
        res.setHeader("Content-Type", "application/json");
        res.end(
          JSON.stringify({
            status: "success",
            message: "Data inserted into DynamoDB.",
            data: { id: "1", message },
          })
        );
      } catch (error) {
        res.statusCode = 500;
        res.setHeader("Content-Type", "application/json");
        res.end(JSON.stringify({ status: "error", message: "Failed to insert into DynamoDB.", error: error.message }));
      }
    });
    return;
  }
  // GET Route: Retrieve an item from DynamoDB
  if (req.url === "/retrieve" && req.method === "GET") {
    const dynamoParams = {
      TableName: TABLE_NAME,
      Key: {
        pk: "1", // Static primary key value
        sk: "1", // Static sort key value
      },
    };
    try {
      const data = await dynamoDb.get(dynamoParams).promise();
      if (data.Item) {
        res.statusCode = 200;
        res.setHeader("Content-Type", "application/json");
        res.end(
          JSON.stringify({
            status: "success",
            data: { id: "1", message: data.Item.message },
          })
        );
      } else {
        res.statusCode = 404;
        res.setHeader("Content-Type", "application/json");
        res.end(
          JSON.stringify({
            status: "error",
            message: "Item not found in DynamoDB.",
          })
        );
      }
    } catch (error) {
      res.statusCode = 500;
      res.setHeader("Content-Type", "application/json");
      res.end(JSON.stringify({ status: "error", message: "Failed to retrieve data from DynamoDB.", error: error.message }));
    }
    return;
  }
  // Catch-all for invalid routes
  res.statusCode = 404;
  res.setHeader("Content-Type", "application/json");
  res.end(JSON.stringify({ message: "Invalid route or method.", route: req.url }));
});
server.listen(port, () => {
  console.log(\`Server running at http://localhost:\${port}/\`);
});
EOL
# Initialize a new Node.js project and install dependencies
echo "Initializing Node.js project and installing required packages..."
npm init -y
npm install aws-sdk
# Start the application
echo "Starting Node.js application..."
nohup node app.js > output.log 2>&1 &
echo "Setup complete. Node.js application is running on port 8080."