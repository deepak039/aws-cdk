#!/bin/bash
yum update -y
curl -sL https://rpm.nodesource.com/setup_16.x | bash -
yum install nodejs -y
echo 'const http = require("http"); const server = http.createServer((req, res) => { res.writeHead(200, {"Content-Type": "text/plain"}); res.end("Hello from Node.js"); }); server.listen(3000);' > /home/ec2-user/app.js
node /home/ec2-user/app.js &