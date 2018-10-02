from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register(ContentCategory)
admin.site.register(ContentDetails)
admin.site.register(Status)
#========= other models
admin.site.register(Pet_Owner_Interest)
admin.site.register(Petjibeuser)
admin.site.register(Pet_Type)
admin.site.register(Pet_Breed)
admin.site.register(Pet)
admin.site.register(Pet_Owner_Interest_Ref)
admin.site.register(Search)
admin.site.register(SearchResults)
admin.site.register(Subscriber)
admin.site.register(Contact)

