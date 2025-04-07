#!/bin/bash

# Update packages and install basic dependencies
sudo yum update -y
sudo yum install -y gcc-c++ make
sudo curl -sL https://rpm.nodesource.com/setup_16.x | sudo bash -
sudo yum install -y nodejs

# Create a directory for the application
mkdir -p /home/ec2-user/my-node-app
cd /home/ec2-user/my-node-app

# Create a basic Node.js application
cat <<EOL > app.js
const http = require("http");
const port = 8080;

const server = http.createServer((req, res) => {
  res.statusCode = 200;
  res.setHeader("Content-Type", "text/plain");
  res.end("Hello, World from Node.js!");
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