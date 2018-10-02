"""petjibe URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() functisearchMsgon: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.views.generic.base import TemplateView
from pets.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    #url(r'^accounts/', include('allauth.urls')), # added for allauth
    #============ petjibe user login and registration
    path('join/',TemplateView.as_view(template_name="login.html"),name="join"),
    path('registration/',SignupView.as_view()),
    path('login/',LoginView.as_view()),
    path('logout/',logout,name="logout"),
    path('email_confirmation/<str:key>/',email_confirmation,name="email_confirmation"),
    path('fb_token/',FbConnectView.as_view(),name="fb_token"),
    #============ pet registration 
    path('petRegisterPage/',petRegisterPage,name="petRegisterPage"),
    path('pet-register/',PetRegisterView.as_view()),
    path('pet-breed/',GetPetBreed.as_view()),
    #=========== owner profile registration 
    path('ownerRegistration/',ownerRegistration,name="ownerRegistration"),
    path('getStates/',GetStates.as_view()),
    path('ownerRegistrationSubmit/',OwnerRegistrationSubmit.as_view()),
    #=========== owner profile edit
    path('ownerProfileEdit/',ownerProfileEdit,name="ownerProfileEdit"),
    #=========== owner profile without pet
    path('profileWithoutPetView/',profileWithoutPetView,name="profileWithoutPetView"),
    #=========== owner profile with pet
    path('ownerProfile/',profileWithPetView,name="ownerProfile"),
    #=========== pet delete 
    path('petDelete/',PetDelete.as_view(),name="petDelete"),
    #=========== pet edit
    path('petEditView/<str:pet_id>',petEditView,name="petEditView"), 
    #=========== email subscription
    path('email_subscription/',Email_subscriptions.as_view(),name="email_subscription"),
    path('email_subscribe_valid/<str:key>/',email_subscription_valid,name="email_subscribe_valid"),
    #=========== pet article
    #path('petArticle/',TemplateView.as_view(template_name="pet-articles.html"),name="index"),
    path('petArticle/<str:type>',petArticleView,name="petArticle"), 
    path('petArticleSingle/<str:art_id>',articleRedirectView,name="petArticleSingle"), 
    #=========== pet forget password and change password
    path('forgotpassword/',forgot_password,name="forgotpassword"), 
    path('resetpassword/<str:key>/',reset_password,name="resetpassword"), 
    path('changepassword/',change_password,name="changepassword"),
    #=========== find extended family api call / view search results
    path('searchresults/',searchResultApiView,name="searchresults"),
    path('searchresultsview/',searchresultsview,name="searchresultsview"),
    path('searchMsg/<str:uid>/',searchmsg,name="searchMsg"),
    #=========== contact us 
    path('contactus/',ContactusView.as_view(),name="contactus"),
    #=========== getting zipcode 
    path('getzip/',GetZipcode.as_view(),name="getzip"),
    #============ dashboard 
    #path('index/',TemplateView.as_view(template_name="index.html"),name="index"),
    #path('index/',indexView,name="index"),
    path('',indexView,name="index"),
    #============== messaging app 
    url(r"^messages/", include("pinax.messages.urls", namespace="pinax_messages")),
    path('msgpage/',UserMsgView.as_view(),name="msgpage"),
    path('newmsg/',newMessageView,name="newmsg"),
    path('createmsgthread/',UserCreateMsgView.as_view(),name="createmsgthread"),
    path('createmultimsgthread/',UserCreateMultiMsgView.as_view(),name="createmultimsgthread"),
    path('replymsgthread/',UserReplyMsgView.as_view(),name="replymsgthread"),
    path('allmsgs/',allMessageView,name="allmsgs"),
    path('chatbox/',TemplateView.as_view(template_name="chat-box.html"),name="chatbox"),
    path('set_multi_email/',set_multi_emails,name="set_multi_email"),
    path('upload_profile_pic/',user_upload_image,name="upload_profile_pic"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
