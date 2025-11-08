from config import CHANNEL_ID
class Analytics:
    def __init__(self, telegram_client):
        self.client = telegram_client
        self.current_subscribers = 1000
    
    async def update_subscribers(self):
            self.current_subscribers = 1400

    def calculate_effectiveness(self, post_data):
        views = post_data['views']
        reactions = post_data['reactions']
        
        if views == 0:
            return 0
        
        if views > self.current_subscribers:
            score = self.repost_formula(views)
        else:
            score = self.default_formula(views, reactions)
        
        return round(score * 100, 2)
    
    def repost_formula(self, views):
        multiplier = self.get_repost_multiplier(views)
        effectiveness = 1 - (multiplier * self.current_subscribers / views)
        return max(effectiveness, 0)
    
    def get_repost_multiplier(self, views):
        if views > 3 * self.current_subscribers:
            return 4
        elif views > 2 * self.current_subscribers:
            return 3
        else:
            return 2
        
    def default_formula(self, views, reactions):
        return reactions / views
    
    def calculate_salary_distribution(self, db_manager):
        conn = db_manager.get_connection()
        
        total_score = conn.execute('SELECT SUM(monthly_score) FROM meme_models').fetchone()[0] or 1
        models = conn.execute('SELECT username, monthly_score FROM meme_models').fetchall()
        
        distribution = {}
        for username, score in models:
            percentage = (score / total_score) * 100
            distribution[username] = {'score': score, 'percentage': round(percentage, 2)}
        
        conn.close()
        return distribution
    
    def get_post_analysis(self, post_data):
        views = post_data['views']
        effectiveness = self.calculate_effectiveness(post_data)
        
        analysis = {
            'post_id': post_data['post_id'],
            'author': post_data['author'],
            'views': views,
            'subscribers': self.current_subscribers,
            'effectiveness': effectiveness,
            'post_type': 'repost' if views > self.current_subscribers else 'regular',
            'views_to_subs_ratio': round(views / self.current_subscribers, 2)
        }
        
        if views > self.current_subscribers:
            multiplier = self.get_repost_multiplier(views)
            analysis.update({
                'repost_multiplier': multiplier,
                'calculated_formula': f"1 - ({multiplier} * {self.current_subscribers} / {views})"
            })
        
        return analysis