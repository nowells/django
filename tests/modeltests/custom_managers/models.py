"""
23. Giving models a custom manager

You can use a custom ``Manager`` in a particular model by extending the base
``Manager`` class and instantiating your custom ``Manager`` in your model.

There are two reasons you might want to customize a ``Manager``: to add extra
``Manager`` methods, and/or to modify the initial ``QuerySet`` the ``Manager``
returns.
"""

from django.db import models
from django.db.models import query

# An example of a custom manager called "objects".

class PersonManager(models.Manager):
    def get_fun_people(self):
        return self.filter(fun=True)

class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    fun = models.BooleanField()
    objects = PersonManager()

    def __unicode__(self):
        return u"%s %s" % (self.first_name, self.last_name)

# An example of a custom manager that sets get_query_set().

class PublishedBookManager(models.Manager):
    def get_query_set(self):
        return super(PublishedBookManager, self).get_query_set().filter(is_published=True)

class Book(models.Model):
    title = models.CharField(max_length=50)
    author = models.CharField(max_length=30)
    is_published = models.BooleanField()
    published_objects = PublishedBookManager()
    authors = models.ManyToManyField(Person, related_name='books')

    def __unicode__(self):
        return self.title

# An example of providing multiple custom managers.

class FastCarManager(models.Manager):
    def get_query_set(self):
        return super(FastCarManager, self).get_query_set().filter(top_speed__gt=150)

class Car(models.Model):
    name = models.CharField(max_length=10)
    mileage = models.IntegerField()
    top_speed = models.IntegerField(help_text="In miles per hour.")
    cars = models.Manager()
    fast_cars = FastCarManager()

    def __unicode__(self):
        return self.name

class ArtistManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self, *args, **kwargs):
        # We need to hack this to expose the internal data to the doctest suite.
        class MockQuerySet(query.QuerySet):
            def get(slf, *args, **kwargs):
                result = super(MockQuerySet, slf).get(*args, **kwargs)
                result.exposed_manager_data_for_tests = {
                    'model_attname': self.model_attname,
                    'related_model_instance': self.related_model_instance,
                    'related_model_attname': self.related_model_attname,
                    }
                return result
        return MockQuerySet(self.model, using=self._db)

class Artist(models.Model):
    name = models.CharField(max_length=50)
    songs = models.ManyToManyField('Song', blank=True, related_name='artists')
    best_songs = models.ManyToManyField('Song', blank=True)

    _default_manager = ArtistManager()
    objects = models.Manager()

    def __unicode__(self):
        return self.name

class Album(models.Model):
    artist = models.ForeignKey(Artist, related_name='albums')
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class Song(models.Model):
    album = models.ForeignKey(Album)
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

__test__ = {'API_TESTS':"""
>>> p1 = Person(first_name='Bugs', last_name='Bunny', fun=True)
>>> p1.save()
>>> p2 = Person(first_name='Droopy', last_name='Dog', fun=False)
>>> p2.save()
>>> Person.objects.get_fun_people()
[<Person: Bugs Bunny>]

# The RelatedManager used on the 'books' descriptor extends the default manager
>>> from modeltests.custom_managers.models import PublishedBookManager
>>> isinstance(p2.books, PublishedBookManager)
True

>>> b1 = Book(title='How to program', author='Rodney Dangerfield', is_published=True)
>>> b1.save()
>>> b2 = Book(title='How to be smart', author='Albert Einstein', is_published=False)
>>> b2.save()

# The default manager, "objects", doesn't exist,
# because a custom one was provided.
>>> Book.objects
Traceback (most recent call last):
    ...
AttributeError: type object 'Book' has no attribute 'objects'

# The RelatedManager used on the 'authors' descriptor extends the default manager
>>> from modeltests.custom_managers.models import PersonManager
>>> isinstance(b2.authors, PersonManager)
True

>>> Book.published_objects.all()
[<Book: How to program>]

>>> c1 = Car(name='Corvette', mileage=21, top_speed=180)
>>> c1.save()
>>> c2 = Car(name='Neon', mileage=31, top_speed=100)
>>> c2.save()
>>> Car.cars.order_by('name')
[<Car: Corvette>, <Car: Neon>]
>>> Car.fast_cars.all()
[<Car: Corvette>]

# Each model class gets a "_default_manager" attribute, which is a reference
# to the first manager defined in the class. In this case, it's "cars".
>>> Car._default_manager.order_by('name')
[<Car: Corvette>, <Car: Neon>]

# Test that each manager descriptor sets the appropriate values for the model_attname, related_model_attname, related_model_instance
>>> artist1 = Artist.objects.create(name='Queen')
>>> album1 = Album.objects.create(artist=artist1, name='A Kind of Magic')
>>> song1 = Song.objects.create(album=album1, name='Princes of the Universe')
>>> artist1.songs.add(song1)
>>> artist1.best_songs.add(song1)

>>> artist1.songs.model_attname
'artists'
>>> artist1.songs.related_model_instance
<Artist: Queen>
>>> artist1.songs.related_model_attname
'songs'

>>> artist1.best_songs.model_attname
'artist_set'
>>> artist1.best_songs.related_model_instance
<Artist: Queen>
>>> artist1.best_songs.related_model_attname
'best_songs'

>>> artist1.albums.model_attname
'artist'
>>> artist1.albums.related_model_instance
<Artist: Queen>
>>> artist1.albums.related_model_attname
'albums'

>>> song1.artists.model_attname
'songs'
>>> song1.artists.related_model_instance
<Song: Princes of the Universe>
>>> song1.artists.related_model_attname
'artists'

>>> del album1._artist_cache
>>> album1.artist.exposed_manager_data_for_tests['model_attname']
'albums'
>>> album1.artist.exposed_manager_data_for_tests['related_model_instance']
<Album: A Kind of Magic>
>>> album1.artist.exposed_manager_data_for_tests['related_model_attname']
'artist'
"""}
