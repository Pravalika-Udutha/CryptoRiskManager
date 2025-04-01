from django.db import models
from django.db.models import CASCADE

class ClientRegister_Model(models.Model):
    username = models.CharField(max_length = 30)
    email = models.EmailField(max_length = 30)
    password = models.CharField(max_length = 10)
    phoneno = models.CharField(max_length = 10)
    country = models.CharField(max_length = 30)
    state = models.CharField(max_length = 30)
    city = models.CharField(max_length = 30)
    address = models.CharField(max_length = 3000,default='Unknown')
    gender = models.CharField(max_length = 30,default='Gender')

class financial_risk_type(models.Model):
    idn = models.CharField(max_length = 3000)
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    rank = models.IntegerField()
    market_cap_usd = models.FloatField()
    price_usd = models.FloatField()
    price_btc = models.FloatField()
    volume_usd_24h = models.FloatField()
    available_supply = models.FloatField()
    total_supply = models.FloatField()
    max_supply = models.FloatField(null=True, blank=True)
    percent_change_1h = models.FloatField()
    percent_change_24h = models.FloatField()
    percent_change_7d = models.FloatField()
    last_updated = models.DateTimeField()
    prediction = models.IntegerField()
    

class detection_accuracy(models.Model):
    names = models.CharField(max_length = 300)
    ratio = models.CharField(max_length = 300)

class detection_ratio(models.Model):
    names = models.CharField(max_length = 300)
    ratio = models.CharField(max_length = 300)