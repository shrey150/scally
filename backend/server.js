const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
const port = 8000; // Use port 8000 for the server

app.use(cors());
app.use(bodyParser.json());

// Existing route handler
app.post('/api/test-endpoint', (req, res) => {
    const { repoUrl } = req.body;
    console.log(`Received repoUrl: ${repoUrl}`);
    res.json({ message: `Received repoUrl: ${repoUrl}` });
});

// New route handler for /generate endpoint
app.post('/generate', (req, res) => {
    // Here, you can perform any additional processing or logic required
    // before sending the response
    res.json({ message: 'Processing link and generating output...' });
});

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
