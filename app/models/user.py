from app import db

class User(db.Model):
    id 	 = db.Column(db.Integer, primary_key=True)

    def roles(self):
        return []
