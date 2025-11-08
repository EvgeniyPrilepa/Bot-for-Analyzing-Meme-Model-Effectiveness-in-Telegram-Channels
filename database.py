import sqlite3
import pandas as pd
from datetime import datetime

class Database:
    def __init__(self, db_path='meme_analytics.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = self.get_connection()
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                post_id INTEGER PRIMARY KEY,
                author TEXT,
                post_type TEXT,
                publish_time TEXT,
                final_views INTEGER,
                final_reactions INTEGER,
                final_effectiveness REAL,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS meme_models (
                username TEXT PRIMARY KEY,
                total_score REAL DEFAULT 0,
                monthly_score REAL DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def save_post_data(self, post_data, effectiveness):
        conn = self.get_connection()
        try:
            conn.execute('''
                INSERT OR REPLACE INTO posts 
                (post_id, author, post_type, publish_time, final_views, final_reactions, final_effectiveness)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                post_data['post_id'],
                post_data['author'],
                post_data['post_type'],
                post_data['publish_time'].isoformat(),
                post_data['views'],
                post_data['reactions'],
                effectiveness
            ))

            conn.execute('''
                INSERT OR REPLACE INTO meme_models 
                (username, monthly_score, total_score)
                VALUES (?, 
                        COALESCE((SELECT monthly_score FROM meme_models WHERE username = ?), 0) + ?,
                        COALESCE((SELECT total_score FROM meme_models WHERE username = ?), 0) + ?)
            ''', (
                post_data['author'],
                post_data['author'],
                effectiveness,
                post_data['author'],
                effectiveness
            ))
            
            conn.commit()
            
        except Exception as e:
            print(f"Ошибка: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_active_posts(self):
        conn = self.get_connection()
        posts = conn.execute('SELECT * FROM posts WHERE is_active = 1').fetchall()
        conn.close()
        return posts
    
    def deactivate_old_posts(self, hours_old=48):
        conn = self.get_connection()
        time_limit = datetime.now()
        
        conn.execute('''
            UPDATE posts SET is_active = 0 
            WHERE datetime(publish_time) < datetime(?, '-{} hours')
        '''.format(hours_old), (time_limit.isoformat(),))
        
        conn.commit()
        conn.close()
    
    def get_meme_model_stats(self, username):
        conn = self.get_connection()
        
        stats = conn.execute('''
            SELECT * FROM meme_models WHERE username = ?
        ''', (username,)).fetchone()
        
        conn.close()
        return stats
    
    def reset_monthly_scores(self):
        conn = self.get_connection()
        conn.execute('UPDATE meme_models SET monthly_score = 0')
        conn.commit()
        conn.close()
    
    def export_to_excel(self):
        conn = self.get_connection()
        try:
            posts_df = pd.read_sql('''
                SELECT post_id, author, post_type, publish_time, 
                       final_views, final_reactions, final_effectiveness,
                       CASE WHEN is_active = 1 THEN 'Активен' ELSE 'Завершен' END as status
                FROM posts 
                ORDER BY publish_time DESC
            ''', conn)
            
            models_df = pd.read_sql('''
                SELECT username, monthly_score, total_score 
                FROM meme_models 
                ORDER BY monthly_score DESC
            ''', conn)
            
            with pd.ExcelWriter('meme_analytics.xlsx') as writer:
                posts_df.to_excel(writer, sheet_name='Посты', index=False)
                models_df.to_excel(writer, sheet_name='Мемоделы', index=False)
            return True
            
        except Exception as e:
            print(f"Ошибка: {e}")
            return False
        finally:
            conn.close()
    
    def get_salary_distribution_data(self):
        conn = self.get_connection()
        
        total_result = conn.execute('SELECT SUM(monthly_score) FROM meme_models').fetchone()
        total_score = total_result[0] if total_result[0] is not None else 1
        
        models = conn.execute('''
            SELECT username, monthly_score 
            FROM meme_models 
            WHERE monthly_score > 0
            ORDER BY monthly_score DESC
        ''').fetchall()
        
        conn.close()
        
        return {
            'total_score': total_score,
            'models': models
        }