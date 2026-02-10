import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import logging

logger = logging.getLogger(__name__)

class Database:
    """SQLite Database handler for WhatsApp Bot"""
    
    def __init__(self, db_path='nutrition_bot.db'):
        """Initialize database connection"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create tables if they don't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # User profiles table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                phone_number TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                health_conditions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_interaction TIMESTAMP,
                total_interactions INTEGER DEFAULT 0
            )
            ''')
            
            # Interactions/messages table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                user_input TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                health_conditions TEXT,
                has_image BOOLEAN DEFAULT 0,
                calories REAL,
                protein REAL,
                carbs REAL,
                fats REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (phone_number) REFERENCES users(phone_number)
            )
            ''')
            
            # Daily intake tracking table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_intake (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                date DATE NOT NULL,
                total_calories REAL DEFAULT 0,
                total_protein REAL DEFAULT 0,
                total_carbs REAL DEFAULT 0,
                total_fats REAL DEFAULT 0,
                meal_count INTEGER DEFAULT 0,
                FOREIGN KEY (phone_number) REFERENCES users(phone_number),
                UNIQUE(phone_number, date)
            )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
        
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
            raise
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def create_user(self, phone_number: str, name: str) -> Dict:
        """Create a new user profile"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO users (phone_number, name)
            VALUES (?, ?)
            ''', (phone_number, name))
            
            conn.commit()
            conn.close()
            
            logger.info(f"User created: {phone_number}")
            return {"phone_number": phone_number, "name": name, "health_conditions": []}
        
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return {}
    
    def get_user(self, phone_number: str) -> Optional[Dict]:
        """Get user profile"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM users WHERE phone_number = ?
            ''', (phone_number,))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                health_conditions = json.loads(user['health_conditions']) if user['health_conditions'] else []
                return {
                    "phone_number": user['phone_number'],
                    "name": user['name'],
                    "health_conditions": health_conditions,
                    "created_at": user['created_at'],
                    "last_interaction": user['last_interaction'],
                    "total_interactions": user['total_interactions']
                }
            return None
        
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            return None
    
    def update_user_conditions(self, phone_number: str, health_conditions: List[str]):
        """Update user's health conditions"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get existing conditions
            cursor.execute('''
            SELECT health_conditions FROM users WHERE phone_number = ?
            ''', (phone_number,))
            
            result = cursor.fetchone()
            existing = json.loads(result['health_conditions']) if result and result['health_conditions'] else []
            
            # Merge new conditions
            all_conditions = list(set(existing + health_conditions))
            
            cursor.execute('''
            UPDATE users SET health_conditions = ? WHERE phone_number = ?
            ''', (json.dumps(all_conditions), phone_number))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Updated health conditions for {phone_number}")
        
        except Exception as e:
            logger.error(f"Error updating health conditions: {str(e)}")
    
    def store_interaction(self, phone_number: str, user_input: str, bot_response: str, 
                         health_conditions: List[str], has_image: bool, timestamp: datetime):
        """Store user interaction"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO interactions 
            (phone_number, user_input, bot_response, health_conditions, has_image, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                phone_number,
                user_input,
                bot_response,
                json.dumps(health_conditions),
                1 if has_image else 0,
                timestamp
            ))
            
            # Update user's last interaction and total count
            cursor.execute('''
            UPDATE users 
            SET last_interaction = ?, total_interactions = total_interactions + 1
            WHERE phone_number = ?
            ''', (timestamp, phone_number))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Interaction stored for {phone_number}")
        
        except Exception as e:
            logger.error(f"Error storing interaction: {str(e)}")
    
    def get_user_history(self, phone_number: str, limit: int = 10) -> List[Dict]:
        """Get user's interaction history"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM interactions 
            WHERE phone_number = ?
            ORDER BY timestamp DESC
            LIMIT ?
            ''', (phone_number, limit))
            
            interactions = cursor.fetchall()
            conn.close()
            
            history = []
            for interaction in interactions:
                history.append({
                    "id": interaction['id'],
                    "user_input": interaction['user_input'],
                    "bot_response": interaction['bot_response'],
                    "has_image": bool(interaction['has_image']),
                    "timestamp": interaction['timestamp'],
                    "health_conditions": json.loads(interaction['health_conditions']) if interaction['health_conditions'] else []
                })
            
            return history
        
        except Exception as e:
            logger.error(f"Error getting user history: {str(e)}")
            return []
    
    def get_statistics(self) -> Dict:
        """Get overall bot statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Total users
            cursor.execute('SELECT COUNT(*) as count FROM users')
            total_users = cursor.fetchone()['count']
            
            # Total interactions
            cursor.execute('SELECT COUNT(*) as count FROM interactions')
            total_interactions = cursor.fetchone()['count']
            
            # Active users (interactions in last 7 days)
            cursor.execute('''
            SELECT COUNT(DISTINCT phone_number) as count FROM interactions
            WHERE timestamp > datetime('now', '-7 days')
            ''')
            active_users = cursor.fetchone()['count']
            
            # Average interactions per user
            cursor.execute('''
            SELECT AVG(total_interactions) as avg FROM users
            ''')
            avg_interactions = cursor.fetchone()['avg'] or 0
            
            conn.close()
            
            return {
                "total_users": total_users,
                "total_interactions": total_interactions,
                "active_users_7d": active_users,
                "avg_interactions_per_user": round(avg_interactions, 2),
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {}
    
    def get_user_stats(self, phone_number: str, days: int = 7) -> Dict:
        """Get user's nutritional stats for the past N days"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT 
                AVG(calories) as avg_calories,
                SUM(calories) as total_calories,
                COUNT(*) as meal_count
            FROM interactions
            WHERE phone_number = ? AND timestamp > datetime('now', ? || ' days')
            ''', (phone_number, f'-{days}'))
            
            result = cursor.fetchone()
            conn.close()
            
            return {
                "avg_daily_calories": round(result['avg_calories']) if result['avg_calories'] else 0,
                "total_calories": round(result['total_calories']) if result['total_calories'] else 0,
                "meal_count": result['meal_count'] or 0,
                "period_days": days
            }
        
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            return {}
    
    def delete_old_interactions(self, days: int = 90):
        """Delete interactions older than N days (for privacy)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            DELETE FROM interactions
            WHERE timestamp < datetime('now', ? || ' days')
            ''', (f'-{days}',))
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Deleted {deleted} old interactions")
            return deleted
        
        except Exception as e:
            logger.error(f"Error deleting old interactions: {str(e)}")
            return 0
