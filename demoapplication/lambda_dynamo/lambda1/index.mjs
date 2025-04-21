import { DynamoDBClient, PutItemCommand, GetItemCommand } from '@aws-sdk/client-dynamodb';


const dynamoClient = new DynamoDBClient({ region: 'us-east-1' });


const TABLE_NAME = "TestTable";


export const handler = async (event,context) => {
    console.log('Received event:', JSON.stringify(event));

    try {
        const httpMethod = event.httpMethod;

        if (httpMethod === 'POST' && event.path === '/put') {
            return await handlePut(event);
        } else if (httpMethod === 'GET' && event.path === '/retrieve') {
            return await handleGet(event);
        } else {

            return {
                statusCode: 404,
                body: JSON.stringify({ message: 'Invalid route or method.',route : event.path }),
            };
        }
    } catch (error) {
        console.error('Error handling request:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({ message: 'Internal Server Error', error }),
        };
    }
};


const handlePut = async (event) => {
    try {
        
        const body = JSON.parse(event.body); 
        const { message } = body;

        if (!message) {
            return {
                statusCode: 400,
                body: JSON.stringify({ status: 'error', message: 'Message is required in the request body.' }),
            };
        }

     
        const params = {
            TableName: TABLE_NAME,
            Item: {
                pk: { S: '1' }, 
                sk: {S : '1'},
                message: { S: message }, 
            },
        };

        // Put item into DynamoDB
        const command = new PutItemCommand(params);
        await dynamoClient.send(command);

        console.log('Successfully inserted item into DynamoDB.');
        return {
            statusCode: 200,
            body: JSON.stringify({ status: 'success', message: 'Data inserted into DynamoDB.', data: { id: '1', message } }),
        };
    } catch (error) {
        console.error('Failed to insert item into DynamoDB:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({ status: 'error', message: 'Failed to insert into DynamoDB.' }),
        };
    }
};

// GET Route: Retrieve "Hello, World!" or other message from DynamoDB
const handleGet = async () => {
    try {
        const params = {
            TableName: TABLE_NAME,
            Key: {
                pk: { S: '1' }, 
                sk: { S: '1' },// Static primary key value "1"
            },
        };

        // Get item from DynamoDB
        const command = new GetItemCommand(params);
        const result = await dynamoClient.send(command);

        if (!result.Item) {
            console.log('No item found with id = 1');
            return {
                statusCode: 404,
                body: JSON.stringify({ status: 'error', message: 'Item not found in DynamoDB.' }),
            };
        }

        // Retrieve the message from the item
        const message = result.Item.message.S;
        console.log('Successfully retrieved item from DynamoDB:', message);

        return {
            statusCode: 200,
            body: JSON.stringify({ status: 'success', data: { id: '1', message } }),
        };
    } catch (error) {
        console.error('Failed to retrieve item from DynamoDB:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({ status: 'error', message: 'Failed to retrieve data from DynamoDB.' }),
        };
    }
};