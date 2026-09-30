from django.db import models

class Medicine(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='medicines/')
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
    