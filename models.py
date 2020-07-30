#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Association Object
class Show(db.Model):
    __tablename__ = 'show'

    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), primary_key=True)
    start_time = db.Column(db.DateTime , default=datetime.utcnow) 

    artist = db.relationship("Artist", back_populates="venues")
    venue = db.relationship("Venue", back_populates="artists")

   
class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String() , nullable=False) 
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120) , nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean , nullable=False , default=False)
    seeking_description = db.Column(db.String(240))

    artists = db.relationship("Show", back_populates="venue")
    genres = db.relationship('venues_genres' , backref='genres' , lazy=True) 


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String() , nullable=False)
    city = db.Column(db.String(120) , nullable=False)
    state = db.Column(db.String(120) , nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean , nullable=False , default=False)
    seeking_description = db.Column(db.String(240))

    venues = db.relationship("Show", back_populates="artist")
    genres = db.relationship('artists_genres' , backref='genres' , lazy=True) 

class artists_genres(db.Model):
    __tablename__ = 'artists_genres'
    artist_id = db.Column(db.Integer , db.ForeignKey('artist.id') , primary_key=True)
    genre = db.Column(db.String(120) , primary_key=True )

class venues_genres(db.Model):
    __tablename__ = 'venues_genres'
    venue_id = db.Column(db.Integer , db.ForeignKey('venue.id') , primary_key=True)
    genre = db.Column(db.String(120) , primary_key=True)
