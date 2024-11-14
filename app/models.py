from app import db

class FastestLap(db.Model):
    __tablename__ = 'fastest_laps'
    
    id = db.Column(db.Integer, primary_key=True)
    season = db.Column(db.Integer, nullable=False)
    race = db.Column(db.String(100), nullable=False)
    driver = db.Column(db.String(100), nullable=False)
    team = db.Column(db.String(100), nullable=False)
    lap_time = db.Column(db.String(20), nullable=False)
    lap_number = db.Column(db.Integer)
    
    def __repr__(self):
        return f"<FastestLap {self.race} - {self.season}>" 

class RaceWinner(db.Model):
    __tablename__ = 'race_winners'
    
    id = db.Column(db.Integer, primary_key=True)
    season = db.Column(db.Integer, nullable=False)
    race = db.Column(db.String(100), nullable=False)
    driver = db.Column(db.String(100), nullable=False)
    team = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f"<RaceWinner {self.race} - {self.season}>" 