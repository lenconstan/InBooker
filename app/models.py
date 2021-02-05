from app import rel_db
from datetime import datetime
from config import Config

class Updated(rel_db.Model):
    id = rel_db.Column(rel_db.Integer, primary_key=True)
    reference = rel_db.Column(rel_db.String(125), index=True)
    bumbal_id = rel_db.Column(rel_db.String(20), index=True)
    updated_by = rel_db.Column(rel_db.String(5), index=True)
    today = rel_db.Column(rel_db.DateTime, index=True, default=datetime.today().date())
    timestamp = rel_db.Column(rel_db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return str(self.today)


