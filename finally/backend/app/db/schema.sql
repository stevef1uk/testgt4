-- FinAlly SQLite schema. Idempotent: safe to execute on every startup.

CREATE TABLE IF NOT EXISTS users_profile (
    id TEXT PRIMARY KEY NOT NULL DEFAULT 'default',
    cash_balance REAL NOT NULL DEFAULT 10000.0,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE TABLE IF NOT EXISTS watchlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default',
    ticker TEXT NOT NULL,
    added_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UNIQUE (user_id, ticker),
    FOREIGN KEY (user_id) REFERENCES users_profile (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_watchlist_user ON watchlist (user_id);

CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default',
    ticker TEXT NOT NULL,
    quantity REAL NOT NULL DEFAULT 0.0,
    avg_cost REAL NOT NULL DEFAULT 0.0,
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UNIQUE (user_id, ticker),
    FOREIGN KEY (user_id) REFERENCES users_profile (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_positions_user ON positions (user_id);

CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default',
    ticker TEXT NOT NULL,
    side TEXT NOT NULL CHECK (side IN ('buy', 'sell')),
    quantity REAL NOT NULL CHECK (quantity > 0),
    price REAL NOT NULL CHECK (price > 0),
    executed_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    FOREIGN KEY (user_id) REFERENCES users_profile (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_trades_user_executed ON trades (user_id, executed_at);

CREATE TABLE IF NOT EXISTS portfolio_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default',
    total_value REAL NOT NULL,
    recorded_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    FOREIGN KEY (user_id) REFERENCES users_profile (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_snapshots_user_recorded ON portfolio_snapshots (user_id, recorded_at);

CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default',
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    actions TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    FOREIGN KEY (user_id) REFERENCES users_profile (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chat_user_created ON chat_messages (user_id, created_at);