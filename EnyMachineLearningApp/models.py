from django.db import models

# Create your models here.
class UserPanel(models.Model):
    UserId = models.CharField(max_length=50, primary_key=True)
    Password = models.CharField(max_length=50)
    Email = models.CharField(max_length=100)
    IsActive = models.IntegerField()
    FirstName = models.CharField(max_length=200)
    LastName = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'UserPanel'