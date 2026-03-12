-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);

-- Bugs table
CREATE TABLE IF NOT EXISTS bugs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    severity TEXT CHECK(severity IN ('low', 'medium', 'high', 'critical')),
    status TEXT DEFAULT 'open',
    reporter_id INTEGER,
    reward_amount REAL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reporter_id) REFERENCES users(id)
);

-- Leaderboard cache table
CREATE TABLE IF NOT EXISTS leaderboard (
    user_id INTEGER PRIMARY KEY,
    points INTEGER DEFAULT 0,
    bugs_verified INTEGER DEFAULT 0,
    rank INTEGER,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Stats table (for faster aggregations)
CREATE TABLE IF NOT EXISTS stats (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial stats
INSERT OR IGNORE INTO stats (key, value) VALUES ('bugs_reported', '15234');
INSERT OR IGNORE INTO stats (key, value) VALUES ('active_researchers', '3421');
INSERT OR IGNORE INTO stats (key, value) VALUES ('rewards_distributed', '$248,500');
INSERT OR IGNORE INTO stats (key, value) VALUES ('projects_protected', '892');
-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT,
    reward TEXT DEFAULT 'N/A',
    bugs INTEGER DEFAULT 0,
    status TEXT DEFAULT 'Active',
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample projects
INSERT OR IGNORE INTO projects (id, name, type, reward, bugs, status, description) VALUES
(1, 'Acme Corp', 'Web Application', '$500', 48, 'Active', 'Security testing for our main customer portal and API endpoints.'),
(2, 'ShopSafe', 'E-Commerce Platform', '$1,000', 73, 'Active', 'Focus on payment flows, authentication, and XSS vulnerabilities.'),
(3, 'MedVault', 'Healthcare SaaS', '$5,000', 21, 'Critical Only', 'Patient data security is paramount. Critical and high severity vulnerabilities rewarded.');
