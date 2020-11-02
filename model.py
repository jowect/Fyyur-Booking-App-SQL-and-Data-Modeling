from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

db=SQLAlchemy()

def db_setup(app):
    app.config.from_object('config')
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)
    return db

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    show_ids = db.relationship('Show', backref='venue', lazy=True)
    website = db.Column(db.String(), nullable=True)
    seeking_talent = db.Column(db.Boolean(), nullable=True, default=True)
    seeking_description = db.Column(db.String(), nullable=True)
    

    def __repr__(self):
        return f'<Venue ID: {self.id}, Name: {self.name}, City: {self.city}, State: {self.state}, Address: {self.address}, Phone: {self.phone}, Genres: {self.genres}, Image_link: {self.image_link}, Facebook_link: {self.facebook_link}, Show_ids: {self.show_ids}, Website: {self.website}, Seeking Talent: {self.seeking_talent}, Seeking Description: {self.seeking_description}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    show_ids = db.relationship('Show', backref='artist', lazy=True)
    website = db.Column(db.String(), nullable=True)
    seeking_venue = db.Column(db.Boolean(), nullable=True)
    seeking_description = db.Column(db.String(), nullable=True)
    
    def __repr__(self):
        return f'<Artist ID: {self.id}, Name: {self.name}, City: {self.city}, State: {self.state}, Phone: {self.phone}, Image_link: {self.image_link}, Facebook_link: {self.facebook_link}, Show_ids: {self.show_ids}, Website: {self.website}, Seeking Talent: {self.seeking_talent}, Seeking Description: {self.seeking_description}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)


    def __repr__(self):
        return f'<Show ID: {self.id}, Name: {self.name}, Date: {self.start_time}, Venue: {self.venue_id}, Artist: {self.artist_id}>'
