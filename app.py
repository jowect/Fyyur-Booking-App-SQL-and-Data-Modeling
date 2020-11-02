#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from datetime import datetime
from flask import (
Flask,
render_template,
request,
Response,
flash,
redirect,
url_for,
jsonify
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from model import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
db = db_setup(app)

app.config.from_object('config')


#TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
    # TODO: replace with real venues data,
    # num_shows should be aggregated based on number of upcoming shows per venue.
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    venue_query = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
    city_and_state = ''
    data = []
    for venue in venue_query:
        #upcoming_shows = venue.shows.filter(Show.start_time > current_time).all()
        upcoming_shows = Show.query.filter(Show.start_time > current_time).all()
        if city_and_state == venue.city + venue.state:
            data[len(data) - 1]["venues"].append({
              "id": venue.id,
              "name": venue.name,
              "num_upcoming_shows": len(upcoming_shows)
            })
        else:
            city_and_state = venue.city + venue.state
            data.append({
              "city": venue.city,
              "state": venue.state,
              "venues": [{
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(upcoming_shows)
              }]
            })
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  venues = db.session.query(Venue).filter(Venue.name.ilike('%' + search_term + '%')).all()
  data = []
  for venue in venues:
      num_upcoming_shows = 0
      shows = db.session.query(Show).filter(Show.venue_id == venue.id)
  for show in shows:
    if (show.start_time > datetime.now()): num_upcoming_shows += 1
    data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows
      })
  response={
        "count": len(venues),
        "data": data
    }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = db.session.query(Venue).filter(Venue.id == venue_id).one()
  list_shows=db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).all()
  #list_shows = db.session.query(Show).filter(Show.venue_id == venue_id)
  past_shows = []
  upcoming_shows = []
  for show in list_shows:
    artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show.artist_id).one()
    show_add = {
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(show.start_time)
        }
    if (show.start_time < datetime.now()):
        #print(past_shows, file=sys.stderr)
        past_shows.append(show_add)
    else:
        upcoming_shows.append(show_add)
  data = {
      "id": venue.id,
      "name": venue.name,
      "genres": [venue.genres],
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
  }

  data = list(filter(lambda d: d['id'] == venue_id, [data]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    body = {}
    try:
        venue = Venue(
        name = request.form.get('name'),
        city = request.form.get('city'),
        state = request.form.get('state'),
        address = request.form.get('address'),
        phone = request.form.get('phone'),
        genres = request.form.get('genres'),
        facebook_link = request.form.get('facebook_link'),
        image_link=request.form.get('image_link'),
        website=request.form.get('image_link'),
        seeking_talent=request.form.get('seeking_talent'),
        seeking_description=request.form.get('seeking_description')
        )
        if 'seeking_talent' not in request.form:
          venue.seeking_talent = True
        db.create_all()
        db.session.add(venue)
        db.session.commit()
        body['id'] = venue.id
        body['name'] = venue.name
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except():
        db.session.rollback()
        error = True
        print(sys.exc_info())
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
      return render_template('pages/home.html')

  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    error = False
    try:
        Venue.query.filter_by(venue=venue_id).delete()
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except():
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify({'success': True})

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
    artist_query = Artist.query.group_by(Artist.id, Artist.name).all()
    data = []
    for artist in artist_query:
            data.append({
              "id": artist.id,
              "name": artist.name,
            })
        
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  artists = db.session.query(Artist).filter(Artist.name.ilike('%' + search_term + '%')).all()
  data = []
  for artist in artists:
      num_upcoming_shows = 0
      shows = db.session.query(Show).filter(Show.artist_id == Artist.id)
  for show in shows:
    if (show.start_time > datetime.now()): num_upcoming_shows += 1
    data.append({
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": num_upcoming_shows
      })
  response={
        "count": len(artists),
        "data": data
    }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
   # shows the artist page with the given artist_id
  # TODO: replace with real venue data from the artist table, using artist_id
  artist = db.session.query(Artist).filter(Artist.id == artist_id).one()
  list_shows=db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).all()
  #list_shows = db.session.query(Show).filter(Show.artist_id == artist_id)
  upcoming_shows = []
  past_shows = []
  for show in list_shows:
    venue = db.session.query(Venue.name, Venue.image_link).filter(Venue.id == show.venue_id).one()
    show_add = {
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "artist_image_link": venue.image_link,
        "start_time": str(show.start_time)
        }
    if (show.start_time < datetime.now()):
        past_shows.append(show_add)
    else:
        upcoming_shows.append(show_add)

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": [artist.genres],
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  
  data = list(filter(lambda d: d['id'] == artist_id, [data]))[0]
  return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  artist = Artist.query.filter_by(id=artist_id).first_or_404()
  form = ArtistForm(obj=artist)

  return render_template('forms/edit_artist.html', form=form, artist=artist)
  

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  edit_artist = Artist.query.get(artist_id)
  error = False
  body = {}
  try:
        edit_artist.name = request.form.get('name'),
        edit_artist.city = request.form.get('city'),
        edit_artist.state = request.form.get('state'),
        edit_artist.phone = request.form.get('phone'),
        edit_artist.genres = request.form.get('genres'),
        edit_artist.facebook_link = request.form.get('facebook_link'),
        edit_artist.image_link=request.form.get('image_link'),
        edit_artist.website=request.form.get('image_link'),
        edit_artist.seeking_venue=request.form.get('seeking_venue'),
        edit_artist.seeking_description=request.form.get('seeking_description')
        if 'seeking_venue' not in request.form:
          artist.seeking_venue = True
        db.session.commit()
        body['id'] = edit_artist.id
        body['name'] = edit_artist.name
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except():
        db.session.rollback()
        error = True
        print(sys.exc_info())
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
  finally:
        db.session.close()
  if error:
        abort(500)
  else:
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET']) 
# TODO: populate form with values from venue with ID <venue_id>
def edit_venue(venue_id):

  venue = Venue.query.filter_by(id=venue_id).first_or_404()
  form = VenueForm(obj=venue)
 
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

    edit_venue = Venue.query.get(venue_id)
    error = False
    body = {}
    try:
        edit_venue.name = request.form.get('name'),
        edit_venue.city = request.form.get('city'),
        edit_venue.state = request.form.get('state'),
        edit_venue.address = request.form.get('address'),
        edit_venue.phone = request.form.get('phone'),
        edit_venue.genres = request.form.get('genres'),
        edit_venue.facebook_link = request.form.get('facebook_link'),
        edit_venue.image_link=request.form.get('image_link'),
        edit_venue.website=request.form.get('image_link'),
        edit_venue.seeking_talent=request.form.get('seeking_talent'),
        edit_venue.seeking_description=request.form.get('seeking_description')
        if 'seeking_talent' not in request.form:
          edit_venue.seeking_talent = True
        db.session.commit()
        body['id'] = edit_venue.id
        body['name'] = edit_venue.name
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except():
        db.session.rollback()
        error = True
        print(sys.exc_info())
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
      return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    body = {}
    try:
        artist = Artist(
        name = request.form.get('name'),
        city = request.form.get('city'),
        state = request.form.get('state'),
        phone = request.form.get('phone'),
        genres = request.form.get('genres'),
        facebook_link = request.form.get('facebook_link'),
        image_link=request.form.get('image_link'),
        website=request.form.get('image_link'),
        seeking_venue=request.form.get('seeking_venue'),
        seeking_description=request.form.get('seeking_description')
        )
        if 'seeking_venue' not in request.form:
          artist.seeking_venue = True
        db.create_all()
        db.session.add(artist)
        db.session.commit()
        body['id'] = artist.id
        body['name'] = artist.name
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except():
        db.session.rollback()
        error = True
        print(sys.exc_info())
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
      return render_template('pages/home.html')

  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Artist record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  # return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    data = []
    shows = Show.query.order_by(Show.start_time.desc()).all()
    for show in shows:
        venue = Venue.query.filter_by(id=show.venue_id).first_or_404()
        artist = Artist.query.filter_by(id=show.artist_id).first_or_404()
        data.extend([{
            "venue_id": venue.id,
            "venue_name": venue.name,
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        }])
    return render_template('pages/shows.html', shows=data)
    

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

    error = False
    date_format = '%Y-%m-%d %H:%M:%S'
    body = {}
    try:
        show = Show(
        name = request.form.get('name'),
        artist_id = request.form.get('artist_id'),
        venue_id = request.form.get('venue_id'),
        start_time = request.form.get('start_time')    
        )
        db.create_all()
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except():
        db.session.rollback()
        error = True
        print(sys.exc_info())
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
      return render_template('pages/home.html')

@app.errorhandler(401)
def unauthorized_error(error):
    return render_template('errors/401.html'), 401

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(405)
def invalid_method_error(error):
    return render_template('errors/405.html'), 405

@app.errorhandler(409)
def duplicate_resource_error(error):
    return render_template('errors/409.html'), 409

@app.errorhandler(422)
def not_processable_error(error):
    return render_template('errors/422.html'), 422

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
