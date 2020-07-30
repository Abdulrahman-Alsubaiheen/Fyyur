#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, Response, redirect, url_for, flash
import json
import pprint # x
from datetime import datetime
import dateutil.parser 
import babel 
from sqlalchemy.sql import func
from sqlalchemy import or_
from flask_moment import Moment # x
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  #date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(value, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  return render_template('pages/venues.html', venues=Venue.query.all() , city_state=Venue.query.with_entities(Venue.city, Venue.state).distinct())

#  Create Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  try:
    name = request.form.get('name')
    City = request.form.get('city')
    State= request.form.get('state')
    address= request.form.get('address')
    phone= request.form.get('phone')
    image_link = request.form.get('image_link')
    facebook_link= request.form.get('facebook_link')
    website = request.form.get('website')
    seeking_talent = request.form.get('seeking_talent')
    seeking_description = request.form.get('seeking_description')

    venue = Venue(name=name , city= City , state=State , address=address , phone=phone , facebook_link=facebook_link , website=website , image_link=image_link , seeking_description=seeking_description )
    db.session.add(venue)

    db.session.flush()

    if seeking_talent == 'y' :
      ST = Venue.query.get(venue.id)
      ST.seeking_talent = True

    # now adding the genres into (venues_genres) table
    genres = request.form.getlist('genres')

    for x in genres :
      venue_genre = venues_genres(venue_id = venue.id , genre = x)
      db.session.add(venue_genre)

    db.session.commit()
    flash('Venue ' + request.form['name'] +' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')  
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Search Venues
#  ----------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
  tag = request.form.get('search_term', '')
  search = "%{}%".format(tag)
  results = Venue.query.filter(Venue.name.ilike(search)).all()

  count = Venue.query.filter(Venue.name.ilike(search)).count()

  return render_template('pages/search_venues.html', count=count , results=results, search_term=request.form.get('search_term', ''))

#  Show Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  venue = Venue.query.get(venue_id)
  venue_genre = venues_genres.query.filter_by(venue_id=venue_id).all()

  time_now = datetime.now()

  past_shows = db.session.query(Show).join(Venue).join(Artist).filter(Venue.id==venue_id).filter(Show.start_time < time_now).with_entities(Venue.id.label('venue_id') , Artist.id.label('artist_id') , Artist.name.label('artist_name') , Artist.image_link.label('artist_image_link') , Show.start_time.label('start_time'))
  past_shows_count = db.session.query(Show).join(Venue).join(Artist).filter(Venue.id==venue_id).filter(Show.start_time < time_now).count()

  upcoming_shows = db.session.query(Show).join(Venue).join(Artist).filter(Venue.id==venue_id).filter(Show.start_time >= time_now).with_entities(Venue.id.label('venue_id') , Artist.id.label('artist_id') , Artist.name.label('artist_name') , Artist.image_link.label('artist_image_link') , Show.start_time.label('start_time'))
  upcoming_shows_count = db.session.query(Show).join(Venue).join(Artist).filter(Venue.id==venue_id).filter(Show.start_time >= time_now).count()

  return render_template('pages/show_venue.html', venue=venue , venue_genre=venue_genre , past_shows=past_shows , upcoming_shows=upcoming_shows , past_shows_count=past_shows_count , upcoming_shows_count=upcoming_shows_count)

#  Delete Venues
#  ----------------------------------------------------------------
@app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):

  try:
    venues_genres.query.filter_by(venue_id=venue_id).delete()
    Show.query.filter_by(venue_id=venue_id).delete()
    Venue.query.filter_by(id = venue_id).delete()
    db.session.commit()
    flash('Venue was successfully Deleted!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue could not be Deleted.')  
  finally:
    db.session.close()

  return render_template('pages/home.html')

#  Edit Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])#<a href=".." > is send 'GET'</a>
def edit_venue(venue_id):
  form = VenueForm()
  return render_template('forms/edit_venue.html', form=form, venue=Venue.query.filter_by(id = venue_id).first())

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])#form with input type submit is send 'POST'
def edit_venue_submission(venue_id):
  
  try:
    venue=Venue.query.get(venue_id)
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    venue.image_link = request.form.get('image_link')
    venue.facebook_link = request.form.get('facebook_link')
    venue.website = request.form.get('website')
    venue.seeking_description = request.form.get('seeking_description')

    seeking_talent = request.form.get('seeking_talent')
    if seeking_talent == 'y' :
      venue.seeking_talent = True
    else :
      venue.seeking_talent = False


  # update the genres from venues_genres table
    venues_genres.query.filter_by(venue_id=venue_id).delete()
    genres = request.form.getlist('genres')

    for x in genres :
      venue_genre = venues_genres(venue_id = venue.id , genre = x)
      db.session.add(venue_genre)


    db.session.commit()
    flash('Venue ' + request.form['name'] +' was successfully Edited!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue could not be Edited.')  
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))



#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():  
  return render_template('pages/artists.html', artists=Artist.query.all())

#  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  try:
    name = request.form.get('name')
    City = request.form.get('city')
    State= request.form.get('state')
    phone= request.form.get('phone')
    image_link = request.form.get('image_link')
    facebook_link= request.form.get('facebook_link')
    website = request.form.get('website')
    seeking_talent = request.form.get('seeking_talent')
    seeking_description = request.form.get('seeking_description')

    artist = Artist(name=name , city= City , state=State , phone=phone , facebook_link=facebook_link , image_link=image_link , website=website , seeking_description=seeking_description)
    db.session.add(artist)

    db.session.flush()

    if seeking_talent == 'y' :
      ST = Artist.query.get(artist.id)
      ST.seeking_talent = True


    # now adding the genres into venues_genres table

    genres = request.form.getlist('genres')

    for x in genres :
      artist_genre = artists_genres(artist_id = artist.id , genre = x)
      db.session.add(artist_genre)

    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')  
  finally:
    db.session.close()

  return render_template('pages/home.html')

#  Search Artist
#  ----------------------------------------------------------------
@app.route('/artists/search', methods=['POST'])
def search_artists():

  tag = request.form.get('search_term', '')
  search = "%{}%".format(tag)
  results = Artist.query.filter(Artist.name.ilike(search)).all()

  count = Artist.query.filter(Artist.name.ilike(search)).count()

  return render_template('pages/search_artists.html', count=count , results=results, search_term=request.form.get('search_term', ''))

#  Show Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  
  artist = Artist.query.get(artist_id)
  artist_genre = artists_genres.query.filter_by(artist_id=artist_id).all()

  time_now = datetime.now()

  past_shows2 = db.session.query(Show).join(Venue).join(Artist).filter(Artist.id==artist_id).filter(Show.start_time < time_now).with_entities(Venue.id.label('venue_id') , Artist.id.label('artist_id') , Venue.name.label('venue_name') , Venue.image_link.label('venue_image_link') , Show.start_time.label('start_time'))
  past_shows_count2 = db.session.query(Show).join(Venue).join(Artist).filter(Artist.id==artist_id).filter(Show.start_time < time_now).count()

  upcoming_shows2 = db.session.query(Show).join(Venue).join(Artist).filter(Artist.id==artist_id).filter(Show.start_time >= time_now).with_entities(Venue.id.label('venue_id') , Artist.id.label('artist_id') , Venue.name.label('venue_name') , Venue.image_link.label('venue_image_link') , Show.start_time.label('start_time'))
  upcoming_shows_count2 = db.session.query(Show).join(Venue).join(Artist).filter(Artist.id==artist_id).filter(Show.start_time >= time_now).count()
# upcoming_shows_count2 = upcoming_shows2.count()

  return render_template('pages/show_artist.html', artist=artist , artist_genre=artist_genre , past_shows=past_shows2 , upcoming_shows=upcoming_shows2 , past_shows_count=past_shows_count2 , upcoming_shows_count=upcoming_shows_count2)


#  Edit Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  return render_template('forms/edit_artist.html', form=form, artist=Artist.query.filter_by(id = artist_id).first())

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  try:
    artist=Artist.query.get(artist_id)

    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.image_link = request.form.get('image_link')
    artist.facebook_link = request.form.get('facebook_link')
    artist.website = request.form.get('website')
    artist.seeking_description = request.form.get('seeking_description')

    seeking_talent = request.form.get('seeking_talent')
    if seeking_talent == 'y' :
      venue.seeking_talent = True
    else :
      venue.seeking_talent = False

  # update the genres from artists_genres table
    artists_genres.query.filter_by(artist_id=artist_id).delete()
    genres = request.form.getlist('genres')

    for x in genres :
      artist_genre = artists_genres(artist_id = artist.id , genre = x)
      db.session.add(artist_genre)


    db.session.commit()
    flash('Artist ' + request.form['name'] +' was successfully Edited!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist could not be Edited.')  
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

#  Delete Artist
#  ----------------------------------------------------------------
@app.route('/artists/<artist_id>/delete', methods=['POST'])
def delete_artists(artist_id):

  try:
    artists_genres.query.filter_by(artist_id=artist_id).delete()
    Show.query.filter_by(artist_id=artist_id).delete()
    Artist.query.filter_by(id = artist_id).delete()
    db.session.commit()
    flash('Artist was successfully Deleted!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist could not be Deleted.')  
  finally:
    db.session.close()

  return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():

  shows3 = db.session.query(Show).join(Venue).join(Artist).with_entities(Venue.id.label('venue_id') , Venue.name.label('venue_name') , Artist.id.label('artist_id') , Artist.name.label('artist_name') , Artist.image_link.label('artist_image_link') , Show.start_time.label('start_time'))

  return render_template('pages/shows.html', shows=shows3)

#  Create Show
#  ----------------------------------------------------------------
@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  try:
    artist_id = request.form.get('artist_id')
    venue_id = request.form.get('venue_id')
    start_time = request.form.get('start_time')

    a = Artist.query.get(artist_id) 
    v = Venue.query.get(venue_id) 
    s = Show(venue=v , artist=a , start_time = start_time)
  
    db.session.add(s) 

    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

#  Search Show
#  ----------------------------------------------------------------
@app.route('/shows/search', methods=['POST'])
def search_shows():

  tag = request.form.get('search_term', '')
  search = "%{}%".format(tag)
  results = db.session.query(Show).join(Venue).join(Artist).filter(or_( Artist.name.ilike(search),Venue.name.ilike(search))).with_entities(Venue.id.label('venue_id') , Venue.name.label('venue_name') , Artist.id.label('artist_id') , Artist.name.label('artist_name') , Artist.image_link.label('artist_image_link') , Show.start_time.label('start_time'))

  count = db.session.query(Show).join(Venue).join(Artist).filter(or_( Artist.name.ilike(search),Venue.name.ilike(search))).count()

  return render_template('pages/search_shows.html', count=count , results=results, search_term=request.form.get('search_term', ''))


#----------------------------------------------------------------------------#

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')


#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
