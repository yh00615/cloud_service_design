const express = require('express');
const app = express();
const port = 3000;

app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>CI/CD Demo</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          max-width: 800px;
          margin: 50px auto;
          padding: 20px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
          background: white;
          padding: 40px;
          border-radius: 10px;
          box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        h1 {
          color: #667eea;
          margin: 0 0 20px 0;
        }
        .version {
          color: #764ba2;
          font-size: 24px;
          font-weight: bold;
        }
        .info {
          margin-top: 20px;
          padding: 15px;
          background: #f5f5f5;
          border-radius: 5px;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>🚀 CI/CD Pipeline Demo</h1>
        <p class="version">Version 1.0</p>
        <div class="info">
          <p><strong>Status:</strong> Running</p>
          <p><strong>Timestamp:</strong> ${new Date().toISOString()}</p>
        </div>
      </div>
    </body>
    </html>
  `);
});

app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    version: '1.0',
    timestamp: new Date().toISOString()
  });
});

app.listen(port, '0.0.0.0', () => {
  console.log(`App listening on port ${port}`);
});
