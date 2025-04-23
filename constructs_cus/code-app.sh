#!/bin/bash
# Update packages and install basic dependencies
sudo yum update -y
sudo yum install -y gcc-c++ make
sudo curl -sL https://rpm.nodesource.com/setup_16.x | sudo bash -
sudo yum install -y nodejs
# Create a directory for the application
mkdir -p /home/ec2-user/my-node-app
cd /home/ec2-user/my-node-app

# Create a Node.js application with DynamoDB interaction (adapted for pk/sk schema)
cat <<EOL > app.js
const http = require("http");
const AWS = require("aws-sdk");

// Set AWS Region
AWS.config.update({ region: "us-east-1" }); // Adjust the region if needed

// Initialize DynamoDB Document Client
const dynamoDb = new AWS.DynamoDB.DocumentClient();

const port = 8080;

const server = http.createServer(async (req, res) => {
  // Health check route
  if (req.url === "/check" && req.method === "GET") {
    res.statusCode = 200;
    res.setHeader("Content-Type", "application/json");
    res.end(JSON.stringify({ status: "up", message: "Server is running and healthy!" }));
    return;
  }

  // GET route to fetch an item from DynamoDB using pk and sk
  if (req.url.startsWith("/get") && req.method === "GET") {
    const queryParams = req.url.split("?")[1];
    const params = new URLSearchParams(queryParams);

    const pk = params.get("pk");
    const sk = params.get("sk");

    if (!pk || !sk) {
      res.statusCode = 400;
      res.end(JSON.stringify({ error: "Missing 'pk' or 'sk' query parameters" }));
      return;
    }

    const dynamoParams = {
      TableName: "TestTable", // Replace with your DynamoDB table name
      Key: { pk, sk }, // Key structure based on your schema
    };

    try {
      const data = await dynamoDb.get(dynamoParams).promise();
      if (data.Item) {
        res.statusCode = 200;
        res.setHeader("Content-Type", "application/json");
        res.end(JSON.stringify(data.Item));
      } else {
        res.statusCode = 404;
        res.end(JSON.stringify({ error: "Item not found" }));
      }
    } catch (error) {
      res.statusCode = 500;
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  // POST route to add/update an item in DynamoDB (using pk and sk)
  if (req.url.startsWith("/put") && req.method === "POST") {
    let body = "";
    req.on("data", (chunk) => {
      body += chunk;
    });

    req.on("end", async () => {
      try {
        const item = JSON.parse(body); // Parse the JSON body from the incoming request
        if (!item.pk || !item.sk) {
          res.statusCode = 400;
          res.end(JSON.stringify({ error: "Missing 'pk' or 'sk' in request payload" }));
          return;
        }

        const dynamoParams = {
          TableName: "TestTable", // Replace with your DynamoDB table name
          Item: item, // Item to be put in the table (include pk, sk, and other attributes)
        };

        await dynamoDb.put(dynamoParams).promise();
        res.statusCode = 200;
        res.setHeader("Content-Type", "application/json");
        res.end(JSON.stringify({ message: "Item added/updated successfully!" }));
      } catch (error) {
        res.statusCode = 500;
        res.end(JSON.stringify({ error: error.message }));
      }
    });
    return;
  }

  // Catch-all for undefined routes
  res.statusCode = 404;
  res.setHeader("Content-Type", "text/plain");
  res.end("Route not found");
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