from django.db import models
from base1.models import BaseModel
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
class category(BaseModel):
    category_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True,null=True,blank=True)
    category_image = models.ImageField(upload_to="static/category")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        super(category,self).save(*args, **kwargs)

    def __str__(self):
     return self.category_name
    



   
   

    
   

class product(BaseModel):
    
    product_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True,null=True,blank=True)
    category=models.ForeignKey(category, on_delete=models.CASCADE,related_name="products")
    stock = models.IntegerField(null=True,blank=True,default=1)
    price=models.IntegerField()
    product_discription=models.TextField()
    
    # delivery_date = models.DateField(blank=True, null=True)  # New field

    # def save(self, *args, **kwargs):
    #     if not self.delivery_date:
    #         self.delivery_date = timezone.now().date() + timedelta(days=7)  # Example: 7 days from order date
    #     super().save(*args, **kwargs)

    

    def save(self, *args, **kwargs):
        self.slug = slugify(self.product_name)
        super(product,self).save(*args, **kwargs)

    def __str__(self):
     return self.product_name

  
       
class productsImage(BaseModel):
    product = models.ForeignKey(product, on_delete=models.CASCADE, related_name="products_images")
    image = models.ImageField(upload_to="static/product")


