const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

class Database {
    constructor() {
        this.dbPath = process.env.DB_PATH || './data/bot.db';
        this.ensureDataDirectory();
        this.db = new sqlite3.Database(this.dbPath);
        this.initializeTables();
    }
    
    ensureDataDirectory() {
        const dataDir = path.dirname(this.dbPath);
        if (!fs.existsSync(dataDir)) {
            fs.mkdirSync(dataDir, { recursive: true });
        }
    }
    
    initializeTables() {
        const createUsersTable = `
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                funnel_step INTEGER DEFAULT 0,
                last_funnel_message DATETIME,
                is_active BOOLEAN DEFAULT 1
            )
        `;
        
        const createClicksTable = `
            CREATE TABLE IF NOT EXISTS link_clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                link_type TEXT NOT NULL,
                clicked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        `;
        
        const createMessagesTable = `
            CREATE TABLE IF NOT EXISTS scheduled_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message_type TEXT NOT NULL,
                scheduled_for DATETIME NOT NULL,
                sent BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        `;
        
        this.db.serialize(() => {
            this.db.run(createUsersTable);
            this.db.run(createClicksTable);
            this.db.run(createMessagesTable);
        });
        
        console.log('✅ Banco de dados inicializado');
    }
    
    // Métodos para usuários
    addUser(userInfo) {
        return new Promise((resolve, reject) => {
            const { id, username, first_name, last_name } = userInfo;
            const query = `
                INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, joined_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            `;
            
            this.db.run(query, [id, username, first_name, last_name], function(err) {
                if (err) {
                    reject(err);
                } else {
                    resolve(this.lastID);
                }
            });
        });
    }
    
    getUser(userId) {
        return new Promise((resolve, reject) => {
            const query = 'SELECT * FROM users WHERE user_id = ?';
            this.db.get(query, [userId], (err, row) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(row);
                }
            });
        });
    }
    
    updateUserFunnelStep(userId, step) {
        return new Promise((resolve, reject) => {
            const query = `
                UPDATE users 
                SET funnel_step = ?, last_funnel_message = CURRENT_TIMESTAMP 
                WHERE user_id = ?
            `;
            
            this.db.run(query, [step, userId], function(err) {
                if (err) {
                    reject(err);
                } else {
                    resolve(this.changes);
                }
            });
        });
    }
    
    // Métodos para funil de conversão
    getUsersForFunnelStep(step, hoursAgo) {
        return new Promise((resolve, reject) => {
            const query = `
                SELECT * FROM users 
                WHERE funnel_step = ? 
                AND datetime(joined_at) <= datetime('now', '-${hoursAgo} hours')
                AND is_active = 1
            `;
            
            this.db.all(query, [step], (err, rows) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(rows);
                }
            });
        });
    }
    
    // Métodos para rastreamento de cliques
    recordLinkClick(userId, linkType) {
        return new Promise((resolve, reject) => {
            const query = `
                INSERT INTO link_clicks (user_id, link_type)
                VALUES (?, ?)
            `;
            
            this.db.run(query, [userId, linkType], function(err) {
                if (err) {
                    reject(err);
                } else {
                    resolve(this.lastID);
                }
            });
        });
    }
    
    getLinkClickStats(linkType = null, days = 30) {
        return new Promise((resolve, reject) => {
            let query = `
                SELECT 
                    link_type,
                    COUNT(*) as clicks,
                    COUNT(DISTINCT user_id) as unique_users
                FROM link_clicks 
                WHERE datetime(clicked_at) >= datetime('now', '-${days} days')
            `;
            
            const params = [];
            if (linkType) {
                query += ' AND link_type = ?';
                params.push(linkType);
            }
            
            query += ' GROUP BY link_type';
            
            this.db.all(query, params, (err, rows) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(rows);
                }
            });
        });
    }
    
    close() {
        this.db.close();
    }
}

module.exports = Database;