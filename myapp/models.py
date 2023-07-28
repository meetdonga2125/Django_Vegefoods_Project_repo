from django.db import models

# Create your models here.
class User(models.Model):
    fname=models.CharField(max_length=100)
    lname=models.CharField(max_length=100)
    email=models.EmailField()
    mobile=models.PositiveIntegerField()
    address=models.TextField(max_length=300)
    password=models.CharField(max_length=100)
    profile_pic=models.ImageField(upload_to="profile_pic/",default="")
    usertype=models.CharField(max_length=100,default='buyer')


    def __str__(self):
        return self.fname+" "+self.lname
    


class Fruitage(models.Model):
    seller=models.ForeignKey(User,on_delete=models.CASCADE)
    category=(
        ('leafy-green','leafy-green'),
        ('cruciferous','cruciferous'),
        ('root','root'),
        ('pome','pome'),
        ('berries','berries'),
    )
    fruitage_category=models.CharField(max_length=100,choices=category)
    types=(
      ('vegetables','vegetables'),
      ('fruits','fruits'),
    )
    fruitage_type=models.CharField(max_length=100,choices=types)
    fruitage_price=models.PositiveIntegerField()
    weight=(
        ('500gm','500gm'),
        ('1kg','1kg'),
        ('2kg','2kg'),
        ('3kg','3kg'),
        ('4kg','4kg'),
        ('5kg','5kg'),
    )
    fruitage_weight=models.CharField(max_length=100,choices=weight)
    fruitage_name=models.CharField(max_length=100)
    fruitage_pic=models.ImageField(upload_to='product_pic/')

    def __str__(self):
        return self.seller.fname + "-" + self.fruitage_name
    

class Wishlist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    fruitage=models.ForeignKey(Fruitage,on_delete=models.CASCADE)  

    def __str__(self):
        return self.user.fname+" - "+self.fruitage.fruitage_name  
    

class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    fruitage=models.ForeignKey(Fruitage,on_delete=models.CASCADE) 
    fruitage_price = models.PositiveIntegerField()
    fruitage_qty = models.PositiveIntegerField(default=1)
    total_price = models.PositiveIntegerField()
    payment_status = models.BooleanField(default=False)


    def __str__(self):
        return self.user.fname+" - "+self.fruitage.fruitage_name


    