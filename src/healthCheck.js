const http = require('http');

// Criar servidor HTTP simples para health check
const server = http.createServer((req, res) => {
    if (req.url === '/' || req.url === '/health') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            status: 'ok',
            message: 'Auge Bot is running',
            timestamp: new Date().toISOString()
        }));
    } else {
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Not found' }));
    }
});

// Porta do Render ou 3000 como fallback
const PORT = process.env.PORT || 3000;

module.exports = {
    startHealthCheck: () => {
        server.listen(PORT, () => {
            console.log(`🏥 Health check server rodando na porta ${PORT}`);
        });
    }
};