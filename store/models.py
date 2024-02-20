from django.db import models
from category.models import  Category
from django.urls import reverse
from accounts.models import Account

# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=200 , unique=True)
    slug = models.CharField(max_length=200 , unique=True)
    description = models.TextField(max_length=500 , blank=True) 
    price = models.IntegerField()
    images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    
    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug ])
    def __str__(self):
        return self.product_name
    


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_manager='color', is_active=True)
    
    def colorsCel(self):
        return super(VariationManager, self).filter(variation_manager='colorCel', is_active=True)
    
    def aditions(self):
        return super(VariationManager, self).filter(variation_manager='adition', is_active=True)
    
    def signed(self):
        return super(VariationManager, self).filter(variation_manager='signed', is_active=True)
    
    def cpus(self):
        return super(VariationManager, self).filter(variation_manager='cpu', is_active=True)
    
variation_category_choice = (
    ('color','color'),
    ('color Cel','color cel'),
    ('adiciones', 'adiciones'),
    ('firmado', 'firmado'),
    ('cpu', 'cpu'),
)
class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_category + ':' + self.variation_value

    
class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.CharField(max_length=500, blank=True)
    rating = models.FloatField()
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject





