from django.db import models


class Merch(models.Model):

    class Meta:
        verbose_name_plural = 'Merch'

    id = models.DecimalField(max_digits=6, primary_key=True, decimal_places=0)
    name = models.CharField(max_length=254)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField()

    def __str__(self):
        return self.name