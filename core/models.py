from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.db.models.expressions import RawSQL


# Create your models here.
class States(models.Model):
    id = models.AutoField(primary_key=True)
    status_title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.status_title}"


class Hashtag(models.Model):
    id = models.AutoField(primary_key=True)
    hashtag_title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.hashtag_title


class BaseModel(models.Model):
    state = models.ForeignKey(States, null=True, blank=True, on_delete=models.PROTECT)
    hashtags = models.ManyToManyField(Hashtag, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("users.CustomerUser", null=True, blank=True, on_delete=models.PROTECT,
                                   related_name='%(class)ss_created_by')
    updated_by = models.ForeignKey("users.CustomerUser", null=True, blank=True, on_delete=models.PROTECT,
                                   related_name="%(class)ss_updated_by")

    class Meta:
        abstract = True


class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=2, unique=True)
    name_code = models.CharField(max_length=50)
    population = models.PositiveIntegerField()
    capital = models.CharField(max_length=100)
    location = models.PointField(null=True, blank=True)
    phone_code = models.CharField(max_length=20, null=True, blank=True)
    emoji = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name


class State(models.Model):
    name = models.CharField(max_length=100)
    name_code = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=10, unique=False)
    capital = models.CharField(max_length=100, null=True, blank=True)
    location = models.PointField(null=True, blank=True)

    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}, {self.country}"


class CityManager(models.Manager):
    def find_nearest_city(self, location_point: Point):
        return self.annotate(distance=RawSQL(
            f'ST_Distance("core_city"."location", ST_GeomFromEWKB(%s::bytea))', (location_point.ewkb,),
            output_field=models.FloatField())).order_by('distance').first()


class City(models.Model):
    name = models.CharField(max_length=100)
    name_code = models.CharField(max_length=50)
    population = models.PositiveIntegerField(null=True, blank=True)
    location = models.PointField(null=True, blank=True)

    state = models.ForeignKey(State, on_delete=models.CASCADE)

    objects = CityManager()

    def __str__(self):
        return f"{self.name}, {self.state}"
