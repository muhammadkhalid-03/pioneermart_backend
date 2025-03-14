from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ('name',) #order by name
        verbose_name_plural = 'categories'

    #To show the name of the categories
    def __str__(self):
        return self.name
    