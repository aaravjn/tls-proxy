# Use an in-memory SQLite table to store the data
# The schema of the table would be:
    # Source_IP: PART OF PRIMARY KEY
    # Source_port: PART OF PRIMARY KEY
    # Destination_IP
    # Destination_port
    # Proxy_port: SECONDARY INDEX
# Write functions to insert, delete, update and query the data

import sqlite3

class ConnectionDatabase:
    def __init__(self):
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE connections (source_ip TEXT, source_port INTEGER, destination_ip TEXT, destination_port INTEGER, proxy_port TEXT, PRIMARY KEY (source_ip, source_port))')
        self.cursor.execute('CREATE INDEX proxy_port_index ON connections (proxy_port)')
        self.conn.commit()

    def entry_exists(self, source_ip, source_port):
        self.cursor.execute('SELECT 1 FROM connections WHERE source_ip = ? AND source_port = ?', (source_ip, source_port))
        return self.cursor.fetchone() is not None

    def insert(self, source_ip, source_port, destination_ip, destination_port, proxy_port):
        if not self.entry_exists(source_ip, source_port):
            self.cursor.execute('INSERT INTO connections VALUES (?, ?, ?, ?, ?)', (source_ip, source_port, destination_ip, destination_port, proxy_port))
            self.conn.commit()
    
    def delete(self, source_ip, source_port):
        self.cursor.execute('DELETE FROM connections WHERE source_ip = ? AND source_port = ?', (source_ip, source_port))
        self.conn.commit()
    
    def reverse_lookup(self, proxy_port):
        self.cursor.execute('SELECT * FROM connections WHERE proxy_port = ? LIMIT 1', (proxy_port,))
        return self.cursor.fetchone()