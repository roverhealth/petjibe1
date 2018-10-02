#from django.contrib.gis.db import models
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
#from django_mysql.models import ListCharField
#=================================================================#
# Create your models here.

""" Country population """
class Country(models.Model):
    id = models.AutoField(primary_key=True)
    country_name = models.CharField(max_length=50)
    country_code_2ch = models.CharField(max_length=2)
    country_code_3ch = models.CharField(max_length=3)
    isd_code = models.CharField(null=True, blank = True,max_length=20)
    national_language_code = models.CharField(null=True, blank = True,max_length=100)
    national_language_desc = models.CharField(null=True, blank = True,max_length=15)
    currency_code = models.CharField(null=True, blank = True,max_length=6)
    currency_desc = models.CharField(null=True, blank = True, max_length=15)
    
""" State population """
class State(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.ForeignKey(Country,on_delete=models.CASCADE)
    country_code_3ch = models.CharField(max_length=3)
    state_name = models.CharField(max_length=50)
    state_code = models.CharField(max_length=20)
    
""" City population """    
class City(models.Model):
    id = models.AutoField(primary_key=True)
    state = models.ForeignKey(State,on_delete=models.CASCADE)
    country_code_3ch = models.CharField(max_length=3)
    state_code = models.CharField(max_length=20)
    zip_code = models.CharField(max_length=20)
    city_name = models.CharField(max_length=50)
    lat = models.FloatField(default=None,null = True, blank=True)
    long = models.FloatField(default=None,null = True, blank=True)

""" Pet_Owner_Interest model stores pet owner's interests """
class Pet_Owner_Interest(models.Model):
    Interest_Desc = models.CharField(max_length=60)
    add_date = models.DateTimeField('Date Pet Owner Interest added', auto_now_add = True)  
    
    def __str__(self):
        return self.Interest_Desc    

""" Petjibeuser model stores petjibe user information """
class Petjibeuser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    confirm_key = models.CharField(max_length=200, blank=True)
    first_name = models.CharField(max_length=80, blank=True)
    last_name = models.CharField(max_length=80, blank=True)
    addr1 = models.TextField(null=True,blank=True)
    addr2 = models.TextField(null=True,blank=True)
    country = models.CharField(max_length=5,null=True,blank=True)
    state = models.CharField(max_length=5,null=True,blank=True)
    city = models.CharField(max_length=50,null=True,blank=True)
    otherEmail=models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    comment = models.TextField(null=True,blank=True)
    ownpet=models.BooleanField(default=False)
    if_member = models.IntegerField(default=0)
    interest_ids=models.TextField(blank=True)
    otherstate = models.CharField(max_length=50,null=True,blank=True)
    #location = models.PointField(null=True)
    zipcode = models.CharField(max_length=10,null=True,blank=True)
    lat = models.FloatField(default=0.0)
    long = models.FloatField(default=0.0)
    updated_at= models.DateTimeField(null=True,blank=True,auto_now_add = True)
    profile_pic=models.CharField(null=True,max_length=100)
    def __str__(self):
        return self.user.username
    
    def save(self, *args, **kwargs):
        try:
            self.user.first_name=self.first_name
            self.user.last_name=self.last_name
            self.user.save()
        except:
            pass
        return super(Petjibeuser, self).save(*args, **kwargs)
    @property
    def get_profile_pic(self):
        pic = "default.jpg"
        if self.profile_pic:
            if len(self.profile_pic) > 1:
                pic = self.profile_pic
        return pic

""" FriendsConn model verifies one petjibeuser connected with how many users """
class FriendsConn(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    ownername = models.CharField(blank=True,null=True,max_length=100) # petjibe username
    connected = models.TextField(blank=True,null=True) # connected with petjibeusers
    invited = models.TextField(blank=True,null=True) # invitation sent to petjibeusers for connection 
    active = models.BooleanField(default=False) # active status indicates the user is online or not
    updated_at = models.DateTimeField(auto_now_add=True) 
    
    
""" EmailSubscription model verifies petjibeuser subscribe email id """
class EmailSubscription(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    semail = models.EmailField(blank=True)
    subscribe_key = models.CharField(max_length=200, blank=True)
    verified=models.BooleanField(default=False)
    
    

""" EmailVerification model verifies petjibeuser """
class EmailVerification(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    verified=models.BooleanField(default=False)
    otp=models.CharField(max_length=40)

""" Pet_Type model stores pets category """    
class Pet_Type (models.Model):
    pet_type = models.CharField(max_length=30)
    add_date = models.DateTimeField(auto_now_add = True)
    
    def __str__(self):
        return self.pet_type
    
""" Pet_Breed model stores data related to pet category and breed and breed description """
class Pet_Breed (models.Model):
    pet_type = models.ForeignKey(Pet_Type, on_delete=models.CASCADE)
    pet_breed = models.CharField(max_length=50)
    country = models.CharField(max_length=50, null=True,blank=True)
    origin  = models.CharField(max_length=50, null=True,blank=True) 
    body_type = models.CharField(max_length=50, null=True,blank=True)   
    add_date = models.DateTimeField('Date Pet Breed added', auto_now_add = True)
    
    def __str__(self):
        return self.pet_breed
 
    
""" Pet model stores pet user """
class Pet (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pet_id =  models.CharField(max_length=50, null=False,blank=False,unique=True)
    pet_name = models.CharField(max_length=50, null=True,blank=True)
    gender = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female')), default = 'Male')
    pet_type = models.ForeignKey(Pet_Type, on_delete=models.CASCADE)
    pet_breed =  models.ForeignKey(Pet_Breed, on_delete=models.CASCADE,  null=True,blank=True)
    age = models.CharField(max_length=5, null=True,blank=True)
    weight = models.CharField(max_length=5, null=True,blank=True)
    special_inst = models.CharField(max_length=255, null=True,blank=True)
    photo = models.ImageField(upload_to='profile_images', blank=True)
    add_date = models.DateTimeField('Date Pet added', auto_now_add = True) 
    
    def __str__(self):
        return self.pet_name 
    



""" Pet_Owner_Interest_Ref model stores data about pet owner's interests ref """    
class Pet_Owner_Interest_Ref(models.Model):
    interest_id = models.ManyToManyField(Pet_Owner_Interest,blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    add_date = models.DateTimeField('Date Pet added', auto_now_add = True)  
     
    def __str__(self):
        return self.user.username
    
""" Search model stores search information """       
class Search (models.Model):
    search_Date = models.DateTimeField('Search Date', auto_now_add = True)
    pet_type = models.ForeignKey(Pet_Type, on_delete=models.CASCADE,blank=True, null=True)
    pet_breed_type = models.ForeignKey(Pet_Breed, on_delete=models.CASCADE,blank=True, null=True)
    interest = models.TextField(blank=True)
    zip_code = models.CharField(max_length=15)     
    radius = models.CharField(max_length=15)     

""" Search model stores search results information """ 
class SearchResults (models.Model):  
    search=models.ForeignKey(Search, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pet_parent_nick_name = models.CharField(max_length=30, null=True,blank=True)
    dist_from_zip = models.CharField(max_length=20, null=True,blank=True)
    pet_count = models.CharField(max_length=5, null=True,blank=True)
    interest =  models.CharField(max_length=50, null=True,blank=True)
    add_date = models.DateTimeField('Date Pet added', auto_now_add = True)

""" Status model stores status data """ 
class Status (models.Model):     
    status = models.CharField(max_length=10)
    add_date = models.DateTimeField('Date Pet added', auto_now_add = True)
  
    def __str__(self):
        return self.status
 
""" ContentCategory model stores content category data """     
class ContentCategory (models.Model):               
    content_cat = models.CharField(max_length=60)
    add_date = models.DateTimeField('Date Content Category added', auto_now_add = True)
     
    def __str__(self):
        return self.content_cat 

""" ContentDetails model stores content category data """    
class ContentDetails (models.Model):    
    content_cat = models.ForeignKey(ContentCategory, on_delete=models.CASCADE)
    cont_link = models.CharField(max_length=250, null=True,blank=True)
    cont_stat =  models.ForeignKey(Status, on_delete=models.CASCADE) 
    cont_desc = models.TextField(blank=True,null=True)
    cont_heading = models.TextField(blank=True,null=True)
    cont_image = models.CharField(max_length=250, null=True,blank=True)
    img_flag = models.BooleanField(default=False)
    scrap_flag = models.BooleanField(default=False)
    add_date = models.DateTimeField('Date Content link was added', auto_now_add = True)
    
      
    def __str__(self):
        return self.cont_link      

""" Subscriber model stores email subscriber """
class Subscriber(models.Model):
    subscriber_email = models.EmailField(max_length=150)
    add_date = models.DateTimeField('Date Subscriber added', auto_now_add = True)

""" Contact model stores contact """
class Contact(models.Model):
    cont_name = models.CharField(max_length=100)
    cont_email = models.EmailField(max_length=150)
    cont_subj = models.CharField(max_length=150)
    cont_msg = models.TextField(max_length=250)
    cont_src = models.CharField(max_length=20) 
    add_date = models.DateTimeField('Contact Date', auto_now_add = True)    
    
""" UserPasswordKeys models stores keys when change password """
def get_default_my_date():
  return datetime.now() + timedelta(days=1)

class UserPasswordKeys(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    key=models.CharField(max_length=200)
    valid_till=models.DateTimeField(default=get_default_my_date)
    spent = models.BooleanField(default=False)
    mail_sent=models.BooleanField(default=False)
    
        
    
    
    
