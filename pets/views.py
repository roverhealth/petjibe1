from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse,HttpResponseNotFound, HttpResponseForbidden, HttpResponseServerError
from django.http.response import JsonResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, BadHeaderError
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.serializers import serialize
from django.conf import settings
from django.template.loader import get_template, render_to_string
from django.template import Context
from django.urls import reverse_lazy
# django rest_framework 
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication,BasicAuthentication,TokenAuthentication
from requests import get
import requests,magic
import string, random,uuid,json, os, time
from .models import *
#==== geodjango
#from django.contrib.gis.geos import GEOSGeometry
#from django.contrib.gis.measure import D
#vincenty
from vincenty import vincenty
import urllib3
import certifi
import html
from bs4 import BeautifulSoup
from pinax.messages.views import InboxView,ThreadView,MessageCreateView
from pinax.messages.models import *
from django.contrib.auth.models import User
from rest_framework.authentication import SessionAuthentication,TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import uuid,os
from django.core.cache import cache
from pathlib import Path
#===============================================================================#
# Create your views here.
'''
    @name: SignupView
    @methods : post
    @description : This API view used to signup user and create an user record in database
'''
class SignupView(APIView):
    def post(self,request,format=None):
        try:
            if request.method == 'POST':
                username = request.POST.get('username',None)
                email = request.POST.get('email',None)
                password = request.POST.get('password',None)

                try:
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        return Response({"success":"False","message":"user is already exists"})
                    else:
                        if username is not None and email is not None and password is not None:
                            user = User.objects.create_user(username=username,
                                             email=email,
                                             password=password)
                            user.is_active=True
                            user.save()
                            key = str(uuid.uuid4())+str(uuid.uuid4())+str(uuid.uuid4())
                            Petjibeuser(user=user,confirm_key=key).save()
                            FriendsConn(user=user,ownername=username).save()

                            #====== email verification part
                            link=settings.SITE_URL+'/email_confirmation/'+key+'/'
                            to_email=email
                            from_email = settings.EMAIL_HOST_USER
                            email_content = "Thank you "+email+" for joining us. Please click in the below link to confirm your email. \n"+link
                            html_content = get_template('email-thankyou.html').render({'content': link,'email':to_email})
                            text_content="This is a confirmation email."
                            subject="confirmation email from petjibe"
                            msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
                            msg.attach_alternative(html_content, "text/html")
                            msg.send()

                        return Response({"success":True,"message":"Please verify your email. to access your account"})
                except Exception as e:
                    print(str(e))

            return Response({"msg":'success'},status=status.HTTP_200_OK)
        except Exception as e:
            print('sign up error : '+str(e))
            return Response({'msg':str(e)},status=status.HTTP_400_BAD_REQUEST)


#=====================================================================================================================#
'''
    @name: email_confirmation
    @param : request 
    @description : email_confirmation view
'''
def email_confirmation(request,key):
    try:
        valid=False
        message="sign up again"
        if key:
            user_obj = Petjibeuser.objects.get(confirm_key=key)
            if user_obj is not None:
                valid=True
                return  HttpResponseRedirect('/')

        return render(request,"login.html",{'valid':valid,"message":message})
    except Exception as e:
        print(str(e))
        return render(request,"login.html",{})

#=====================================================================================================================#
'''
    @name: LoginView
    @methods : post
    @description : This API view used to login user and generate token 
'''
class LoginView(APIView):
    def post(self,request,format=None):
        try:
            username=request.data["username"]
            password=request.data["password"]
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.last_login is None:
                    if user.is_active:
                        login(request, user)
                        token = Token.objects.get_or_create(user=user)
                    else:
                        return Response({"msg": 'error', "message":"Please activate your account with email link" })
                    return Response({"msg":'success_first',"Token":token[0].key})
                else:
                    if user.is_active:
                        login(request, user)
                        token = Token.objects.get_or_create(user=user)
                    else:
                        return Response({"msg": 'error', "message": "Please activate your account with email link"})
                    return Response({"msg":'success',"Token":token[0].key})
            else:
                return Response({"msg": 'error', "message": "username/password don't match"})
        except Exception as e:
            return Response({'msg':str(e)},status=status.HTTP_400_BAD_REQUEST)

#=====================================================================================================================#
'''
    @name: FbConnectView
    @methods : post
    @description : This API view used to signup user and create an user record in database
'''
class FbConnectView(APIView):
    def post(self,request,format=None):
        try:
            if request.method == 'POST':
                access_token = request.POST.get('access_token',None)

                response = requests.get("https://graph.facebook.com/v3.1/me?fields=id,name,email,first_name,last_name&access_token="+access_token)
                if response.status_code==200:
                    res_data = response.json()
                    email=res_data["email"]
                    first_name = res_data["first_name"]
                    last_name = res_data["last_name"]

                    user, new = User.objects.get_or_create(username=email,
                                             email=email,
                                             first_name=first_name,
                                             last_name=last_name)

                    if new:
                        user.is_active=True
                        user.save()
                        key = str(uuid.uuid4())+str(uuid.uuid4())+str(uuid.uuid4())
                        Petjibeuser(user=user,confirm_key=key,first_name=first_name,).save()
                        #====== email verification part
                        link=settings.SITE_URL+'/email_confirmation/'+key+'/'
                        to_email=email
                        from_email = settings.EMAIL_HOST_USER
                        email_content = "Thank you "+email+" for joining us. Please click in the below link to confirm your email. \n"+link
                        html_content = get_template('email-thankyou.html').render({'content': link,'email':to_email})
                        text_content="This is a confirmation email."
                        subject="confirmation email from petjibe"
                        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()

                        return Response({"success":True,"message":"Please verify your email. to access your account"})
                    else:
                        if user.is_active:
                            login(request, user)
                            token = Token.objects.get_or_create(user=user)
                            return Response({"msg":'success_first',"Token":token[0].key})
                        #return Response({"success":"True"},status=status.HTTP_200_OK)

                else:
                    return Response({"msg":'failed'},status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'msg':'error'},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print('sign up error : '+str(e))
            return Response({'msg':str(e)},status=status.HTTP_400_BAD_REQUEST)


#=====================================================================================================================#

'''
    @name: logout
    @param : request 
    @description : logout user view
'''
@login_required
def logout(request):
    request.session.flush()
    return redirect('/join/')

#=====================================================================================================================#
'''
    @name: petRegisterPage
    @param : request 
    @description : pet register page view with pet Bread and pet Type
'''
@login_required
def petRegisterPage(request):
    try:
        pet_type = []
        pet_breed=[]
        pet_type_obj = Pet_Type.objects.all()
        if pet_type_obj is not None:
            for data in pet_type_obj:
                type_list=[]
                type_list.append(data.id)
                type_list.append(data.pet_type)
                pet_type.append(type_list)

        pet_breed_obj = Pet_Breed.objects.filter(pet_type=Pet_Type.objects.get(id=1))
        if pet_breed_obj is not None:
            for data in pet_breed_obj:
                #======= getting pet bread
                breed_list=[]
                breed_list.append(data.id)
                breed_list.append(data.pet_breed)
                pet_breed.append(breed_list)

        context={
                "pet_type" : pet_type,
                "pet_breed" : pet_breed
            }
        return render(request,"Register-pet.html",context)
    except Exception as e:
        return render(request,"Register-pet.html",{})

#=====================================================================================================================#
'''
    @name: GetPetBreed
    @methods : post
    @description : This API view used to register pet
'''
class GetPetBreed(APIView):
    def post(self,request,format=None):
        try:
            pet_breed=[]
            pettype=request.data["pettype"]

            pet_breed_obj = Pet_Breed.objects.filter(pet_type=Pet_Type.objects.get(pet_type=pettype))
            if pet_breed_obj is not None:
                for data in pet_breed_obj:
                    #======= getting pet bread
                    breed_list=[]
                    breed_list.append(data.id)
                    breed_list.append(data.pet_breed)
                    pet_breed.append(breed_list)

                return Response({"msg":'success',"pet_breed":pet_breed},status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'msg':str(e)},status=status.HTTP_400_BAD_REQUEST)

#=====================================================================================================================#
'''
    @name: PetRegisterView
    @methods : post
    @description : This API view used to register pet
'''
class PetRegisterView(APIView):
    authentication_classes = (SessionAuthentication,TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self,request,format=None):
        try:
            petname=request.data.get("petname","")
            pettype=request.data["pettype"]
            breed=request.data["breed"]
            gender=request.data.get("gender","")
            age=request.data.get("age","")
            instruction=request.data.get("instruction","")
            pic=request.data.get("pic","")
            weight=request.data.get("weight","")
            pet_id=request.data.get("pet_id",None)

            if pic is not None and len(pic)>0:
                #====== file location and file name generation
                f_name=str(pic)
                local_path = settings.MEDIA_ROOT
                file_path = os.path.join(local_path, "petimageupload")
                if os.path.isdir(file_path) == False:
                    os.makedirs(file_path)
                name=os.path.join(file_path, f_name)
                path = default_storage.save(name, pic)
            else:
                f_name=""

            #========= gender determine
            if gender.upper() == "FEMALE" or gender.upper() == 'F':
                gender = 'F'
            else:
                gender = 'M'

            #========= pet record creation
            cur_time = time.time()
            try:
                pet_obj = Pet.objects.get(pet_id=pet_id)
                if pet_obj is not None:
                    pet_obj.pet_name = petname
                    pet_obj.gender = gender
                    pet_obj.pet_type = Pet_Type.objects.get(pet_type=pettype)
                    pet_obj.pet_breed = Pet_Breed.objects.get(pet_breed=breed)
                    pet_obj.age = age
                    pet_obj.special_inst = instruction
                    if len(f_name)>0 and f_name is not None:
                        pet_obj.photo = "petimageupload/"+f_name
                    pet_obj.weight = weight
                    pet_obj.save()

            except Exception as e:
                print(str(e))
                pet_obj = Pet(
                                user = request.user,
                                pet_id = str(request.user.id)+"_"+str(cur_time),
                                pet_name = petname,
                                gender = gender,
                                pet_type = Pet_Type.objects.get(pet_type=pettype),
                                pet_breed = Pet_Breed.objects.get(pet_breed=breed),
                                age = age,
                                special_inst = instruction,
                                photo = "petimageupload/"+f_name,
                                weight = weight
                            )
                pet_obj.save()


            return Response({"msg":'success'},status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'msg':str(e)},status=status.HTTP_400_BAD_REQUEST)

#=====================================================================================================================#
'''
    @name: ownerRegistration
    @param : request 
    @description : owner profile registration view
'''
@login_required
def ownerRegistration(request):
    try:
        user = request.user
        user_obj = Petjibeuser.objects.get(user=user)
        if user_obj is not None:
            state_code = user_obj.state
            if state_code is not None and len(state_code)>1:
                return HttpResponseRedirect("/ownerProfileEdit/")
            else:
                #========= initialization
                country_list=[]
                state_list=[]
                interest_list=[]
                #========= getting all country data
                country_obj = Country.objects.all()
                if country_obj:
                    for country in country_obj:
                        inner_list=[]
                        country_code_3ch = country.country_code_3ch
                        country_name =  country.country_name
                        inner_list.append(country_code_3ch)
                        inner_list.append(country_name)
                        country_list.append(inner_list)

                #========= getting information from state data
                state_obj = State.objects.filter(country_code_3ch="USA")
                if state_obj:
                    for state in state_obj:
                        inner_list=[]
                        inner_list.append(state.state_code)
                        inner_list.append(state.state_name)
                        state_list.append(inner_list)

                #======== getting owner interests
                interest_obj=Pet_Owner_Interest.objects.all()
                if interest_obj:
                    for data in interest_obj:
                        inner_list=[]
                        inner_list.append(data.id)
                        inner_list.append(data.Interest_Desc)
                        interest_list.append(inner_list)

                context={
                        "country_list" : country_list,
                        "state_list" : state_list,
                        "interest_list":interest_list
                    }
                return render(request,"register-owner.html",context)
    except Exception as e:
        return render(request,"register-owner.html",{})

#=====================================================================================================================#
'''
    @name: GetStates
    @methods : post
    @description : This API view used to get states of particular country
'''
class GetStates(APIView):
    authentication_classes = (SessionAuthentication,TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self,request,format=None):
        try:
            state_list=[]
            country_code=request.data["country_code"]

            state_obj = State.objects.filter(country_code_3ch=country_code)
            if state_obj:
                for state in state_obj:
                    inner_list=[]
                    inner_list.append(state.state_code)
                    inner_list.append(state.state_name)
                    state_list.append(inner_list)

            return Response({"msg":'success',"state_list":state_list},status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'msg':str(e)},status=status.HTTP_400_BAD_REQUEST)


#=====================================================================================================================#
'''
    @name: OwnerRegistrationSubmit
    @methods : post
    @description : This API view used to store user registration data
'''
class OwnerRegistrationSubmit(APIView):
    authentication_classes = (SessionAuthentication,TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self,request,format=None):
        try:
            interest_chk_list=request.data.get("interest_chk_list","")
            country_code=request.data.get("country_code","")
            state_code=request.data.get("state_code","")
            firstname=request.data.get("firstname","")
            lastname=request.data.get("lastname","")
            address1=request.data.get("address1","")
            address2=request.data.get("address2","")
            zipcode=request.data.get("zipcode","")
            city=request.data.get("city","")
            comment=request.data.get("comment","")
            email=request.data.get("email","")
            phone=request.data.get("phone","")
            own_pet=request.data.get("own_pet","off")
            otherstate=request.data.get("otherstate","")

            if interest_chk_list!="[""]":
                interest_chk_list_val=interest_chk_list
            else:
                interest_chk_list_val=None


            if own_pet=="on":
                own_pet=True
            else:
                own_pet=False

            try:
                locationsrch=address1+address2+city
                try:
                    state_obj= State.objects.get(state_code=state_code)
                    if state_obj:
                        statesrch=state_obj.state_name
                except:
                    statesrch = otherstate

                response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+locationsrch+',+'+statesrch+'&key='+settings.GOOGLE_SEARCH_LOCATION)
                response= response.json()
                print(response)
                if 'results' in response:
                    if len(response['results'])>0:
                        if 'geometry' in response['results'][0]:
                            if 'location' in response['results'][0]['geometry']:
                                latitude=response['results'][0]['geometry']['location']['lat']
                                longitude=response['results'][0]['geometry']['location']['lng']
                                #pnt=GEOSGeometry('POINT('+str(longitude)+" "+str(latitude)+')', srid=4326)
            except Exception as e:
                print(e)
                #errors.append({'row':snom,'source':'Google map','error':str(e)})
                pass

            try:
                petjibe_user_obj = Petjibeuser.objects.get(user=request.user)
                if petjibe_user_obj is not None:
                    petjibe_user_obj.first_name=firstname
                    petjibe_user_obj.last_name=lastname
                    petjibe_user_obj.addr1=address1
                    petjibe_user_obj.addr2=address2
                    petjibe_user_obj.country=country_code
                    petjibe_user_obj.state=state_code
                    petjibe_user_obj.city=city
                    petjibe_user_obj.otherEmail=email
                    petjibe_user_obj.phone=phone
                    petjibe_user_obj.comment=comment
                    if interest_chk_list_val is not None:
                        petjibe_user_obj.interest_ids=interest_chk_list_val
                    petjibe_user_obj.ownpet = own_pet
                    petjibe_user_obj.otherstate = otherstate
                    petjibe_user_obj.zipcode = zipcode
                    petjibe_user_obj.lat = latitude
                    petjibe_user_obj.long = longitude
                    petjibe_user_obj.save()

                else:
                    # user record creation
                    petjibe_user_obj = Petjibeuser(
                                    user=request.user,
                                    first_name=firstname,
                                    last_name=lastname,
                                    addr1=address1,
                                    addr2=address2,
                                    country=country_code,
                                    state=state_code,
                                    city=city,
                                    otherEmail=email,
                                    comment=comment,
                                    interest_ids=interest_chk_list_val,
                                    ownpet=own_pet,
                                    otherstate=otherstate,
                                    zipcode=zipcode,
                                    lat=latitude,
                                    long=longitude
                                )
                    petjibe_user_obj.save()
                return Response({"msg":'success'},status=status.HTTP_200_OK)

            except Exception as e:
                print(str(e))
                return Response({'msg':str(e)},status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'msg':str(e)},status=status.HTTP_400_BAD_REQUEST)
#=====================================================================================================================#


'''
    @name: ownerProfileEdit
    @param : request 
    @description : owner profile registration view
'''


@login_required
def ownerProfileEdit(request):
    try:
        user_data = request.user
        try:
            country_list=[]
            state_list=[]
            rest_interest_ids=[]
            interest_list=[]
            interest_ids_list = None
            # getting all country data
            country_obj = Country.objects.all()
            if country_obj:
                for country in country_obj:
                    inner_list=[]
                    country_code_3ch = country.country_code_3ch
                    country_name =  country.country_name
                    inner_list.append(country_code_3ch)
                    inner_list.append(country_name)
                    country_list.append(inner_list)

            # getting information from state data
            state_obj = State.objects.filter(country_code_3ch="USA")
            if state_obj:
                for state in state_obj:
                    inner_list=[]
                    inner_list.append(state.state_code)
                    inner_list.append(state.state_name)
                    state_list.append(inner_list)

            # getting pet user information
            petjibe_user_obj = Petjibeuser.objects.get(user=user_data)
            if petjibe_user_obj is not None:

                firstname=petjibe_user_obj.first_name
                lastname=petjibe_user_obj.last_name
                address1=petjibe_user_obj.addr1
                address2=petjibe_user_obj.addr2
                country_code=petjibe_user_obj.country
                state_code=petjibe_user_obj.state
                city=petjibe_user_obj.city
                otheremail=petjibe_user_obj.otherEmail
                phone=petjibe_user_obj.phone
                comment=petjibe_user_obj.comment
                interest_chk_list=petjibe_user_obj.interest_ids
                own_pet=petjibe_user_obj.ownpet
                otherstate=petjibe_user_obj.otherstate
                pic=petjibe_user_obj.get_profile_pic

                try:
                    if otherstate is None:
                        state_flag = True
                    else:
                        state_flag=False
                except:
                    if len(otherstate)==0:
                        state_flag=True
                    else:
                        state_flag=False

                if len(interest_chk_list) > 0:
                    if interest_chk_list.startswith('['):
                        interest_chk_list = interest_chk_list[1:-1].replace("'","")
                        interest_ids = interest_chk_list.split(",")
                        interest_ids_list=interest_ids
                        if interest_ids_list[0]!="":
                            for id in interest_ids:
                                interest_obj=Pet_Owner_Interest.objects.get(pk=int(id))
                                if interest_obj:
                                    inner_list = []
                                    inner_list.append(interest_obj.id)
                                    inner_list.append(interest_obj.Interest_Desc)
                                    interest_list.append(inner_list)
                        else:
                            pass

                        # rest of interests set
                        count = 0
                        interest_obj = Pet_Owner_Interest.objects.all()
                        if interest_obj:
                            for obj in interest_obj:
                                if str(obj.id) not in interest_ids_list:
                                    inner_list=[]
                                    inner_list.append(obj.id)
                                    inner_list.append(obj.Interest_Desc)
                                    rest_interest_ids.append(inner_list)

                context={

                         "country_list" : country_list,
                         "state_list" : state_list,
                         "interest_list":interest_list,
                         "country_code":country_code,
                         "state_code":state_code,
                         "otherstate":otherstate,
                         "city":city,
                         "otheremail":otheremail,
                         "firstname":firstname,
                         "lastname":lastname,
                         "address1":address1,
                         "address2":address2,
                         "phone":phone,
                         "comment":comment,
                         "own_pet":own_pet,
                         "rest_interest_ids":rest_interest_ids,
                         "state_flag":state_flag,
                        "pic":pic,

                        }
            return render(request,"owner-profile-edit.html",context)
        except Exception as e:
            print(str(e))
            return render(request,"owner-profile-edit.html",{})
    except Exception as e:
        print(str(e))
        return render(request,"owner-profile-edit.html",{})
#=====================================================================================================================#
'''
    @name: profileWithoutPetView
    @param : request 
    @description : profile without pet view render owners profile page without
'''
@login_required
def profileWithoutPetView(request):
    try:
        interest_list=[]
        petjibe_user_obj = Petjibeuser.objects.get(user=request.user)
        if petjibe_user_obj is not None:
            firstname=petjibe_user_obj.first_name
            lastname=petjibe_user_obj.last_name
            address1=petjibe_user_obj.addr1
            address2=petjibe_user_obj.addr2
            country_code=petjibe_user_obj.country
            state_code=petjibe_user_obj.state
            city=petjibe_user_obj.city
            otheremail=petjibe_user_obj.otherEmail
            phone=petjibe_user_obj.phone
            comment=petjibe_user_obj.comment
            interest_chk_list=petjibe_user_obj.interest_ids
            otherstate=petjibe_user_obj.otherstate
            email = petjibe_user_obj.user.email

            if len(interest_chk_list)>0:
                if interest_chk_list.startswith('['):
                    interest_chk_list = interest_chk_list[1:-1].replace("'","")
                    interest_ids = interest_chk_list.split(",")
                    interest_ids_list=interest_ids
                    if interest_ids_list[0]!="":
                        for id in interest_ids:
                            interest_obj=Pet_Owner_Interest.objects.get(pk=int(id))
                            if interest_obj:
                                inner_list=[]
                                inner_list.append(interest_obj.id)
                                inner_list.append(interest_obj.Interest_Desc)
                                interest_list.append(inner_list)
                    else:
                        pass
            else:
                pass

            state_obj = State.objects.filter(country_code_3ch=country_code).get(state_code=state_code)
            if state_obj:
                state_name=state_obj.state_name

            country_obj = Country.objects.get(country_code_3ch=country_code)
            if country_obj:
                country_name=country_obj.country_name

            context={
                    "firstname":firstname,
                     "lastname":lastname,
                     "address1":address1,
                     "address2":address2,
                     "country_name":country_name,
                     "state_name":state_name,
                     "city":city,
                     "otherstate":otherstate,
                     "email":email,
                     "otheremail":otheremail,
                     "phone":phone,
                     "comment":comment,
                     "interest_list":interest_list
                }
            return render(request,"Owner_profile_without_pet.html",context)
    except Exception as e:
        return render(request,"Owner_profile_without_pet.html",{})


#=====================================================================================================================#
'''
    @name: profileWithPetView
    @param : request 
    @description : profile with pet view render owners profile page with pet
'''
@login_required
def profileWithPetView(request):
    try:
        # ========== variable initialization
        interest_list=[]
        pet_status ="off"
        pet_list=[]
        # ========== getting petjibe user data
        petjibe_user_obj = Petjibeuser.objects.get(user=request.user)
        if petjibe_user_obj is not None:
            firstname=petjibe_user_obj.first_name
            lastname=petjibe_user_obj.last_name
            address1=petjibe_user_obj.addr1
            address2=petjibe_user_obj.addr2
            country_code=petjibe_user_obj.country
            state_code=petjibe_user_obj.state
            city=petjibe_user_obj.city
            otheremail=petjibe_user_obj.otherEmail
            phone=petjibe_user_obj.phone
            comment=petjibe_user_obj.comment
            interest_chk_list=petjibe_user_obj.interest_ids
            otherstate=petjibe_user_obj.otherstate
            email = petjibe_user_obj.user.email
            ownpet = petjibe_user_obj.ownpet

            pic =petjibe_user_obj.get_profile_pic

            if len(interest_chk_list)>0:
                if interest_chk_list.startswith('[')==True:
                    interest_chk_list = interest_chk_list[1:-1].replace("'","")
                    interest_ids = interest_chk_list.split(",")
                    interest_ids_list=interest_ids
                    for id in interest_ids:
                        try:
                            interest_obj=Pet_Owner_Interest.objects.get(pk=int(id))
                            if interest_obj:
                                inner_list=[]
                                inner_list.append(interest_obj.id)
                                inner_list.append(interest_obj.Interest_Desc)
                                interest_list.append(inner_list)
                        except:
                            pass
                else:
                    pass
            else:
                pass

            #========= getting state name
            try:
                state_obj = State.objects.filter(country_code_3ch=country_code).get(state_code=state_code)
                if state_obj:
                    state_name=state_obj.state_name
            except:
                if otherstate is not None and len(otherstate)>0:
                    state_name=otherstate
                else:
                    state_name=""

            #========= getting country name
            try:
                country_obj = Country.objects.get(country_code_3ch=country_code)
                if country_obj:
                    country_name=country_obj.country_name
            except:
                country_name=""

            #======== getting pet data (if any)
            pet_obj = Pet.objects.filter(user=request.user)
            if pet_obj is not None:
                for onepet in pet_obj:
                    inner_list=[]
                    inner_list.append(onepet.pet_id)
                    inner_list.append(onepet.pet_name)
                    if onepet.gender == 'F':
                        inner_list.append("Female")
                    else:
                        inner_list.append("Male")
                    inner_list.append(onepet.pet_type.pet_type)
                    inner_list.append(onepet.pet_breed.pet_breed)
                    inner_list.append(onepet.age)
                    inner_list.append(onepet.special_inst)
                    inner_list.append(onepet.photo)
                    inner_list.append(onepet.weight)
                    pet_list.append(inner_list)

                pet_status ="on"



            #========== context
            context={
                    "firstname":firstname,
                     "lastname":lastname,
                     "address1":address1,
                     "address2":address2,
                     "country_name":country_name,
                     "state_name":state_name,
                     "city":city,
                     "otherstate":otherstate,
                     "email":email,
                     "otheremail":otheremail,
                     "phone":phone,
                     "comment":comment,
                     "interest_list":interest_list,
                     "pet_list":pet_list,
                     "pet_status":pet_status,
                    "pic":pic
                }
            return render(request,"owner-profile.html",context)
    except Exception as e:
        return render(request,"owner-profile.html",{})


#=====================================================================================================================#
'''
    @name: PetDelete
    @methods : post
    @description : This API view used to delete pet from user profile
'''
class PetDelete(APIView):
    authentication_classes = (SessionAuthentication,TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self,request,format=None):
        try:
            pet_id=request.data["pet_id"]

            try:
                pet_obj = Pet.objects.get(pet_id=pet_id)
                if pet_obj:
                    pet_obj.delete()
            except Exception as e:
                print(str(e))

            return Response({"msg":'success'},status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'msg':str(e)},status=status.HTTP_400_BAD_REQUEST)


#=====================================================================================================================#
'''
    @name: petEditView
    @param : request 
    @description : profile with pet edit render pet edit page
'''
@login_required
def petEditView(request,pet_id):
    try:
        pet_obj = Pet.objects.get(pet_id=pet_id)
        if pet_obj:
            pet_name=pet_obj.pet_name
            gender=pet_obj.gender
            pet_type_sel=pet_obj.pet_type.pet_type
            pet_breed_sel=pet_obj.pet_breed.pet_breed
            age=pet_obj.age
            weight=pet_obj.weight
            special_inst=pet_obj.special_inst

            #======= getting pet type list
            pet_type = []
            pet_breed=[]
            pet_type_obj = Pet_Type.objects.all()
            if pet_type_obj is not None:
                for data in pet_type_obj:
                    type_list=[]
                    type_list.append(data.id)
                    type_list.append(data.pet_type)
                    pet_type.append(type_list)

            pet_breed_obj = Pet_Breed.objects.filter(pet_type=Pet_Type.objects.get(pet_type="cat"))
            if pet_breed_obj is not None:
                for data in pet_breed_obj:
                    #======= getting pet bread
                    breed_list=[]
                    breed_list.append(data.id)
                    breed_list.append(data.pet_breed)
                    pet_breed.append(breed_list)

            #======= context
            context={
                    "pet_name":pet_name,
                    "gender":gender,
                    "pet_type_sel":pet_type_sel,
                    "pet_breed_sel":pet_breed_sel,
                    "age":age,
                    "weight":weight,
                    "special_inst":special_inst,
                    "pet_type":pet_type,
                    "pet_breed":pet_breed,
                    "update":True,
                    "pet_id":pet_id
                }

            return render(request,"Register-pet.html",context)
    except Exception as e:
        return render(request,"Register-pet.html",{})



#=====================================================================================================================#
'''
    @name: Email_subscriptions
    @param : request 
    @description : email subscription 
'''
class Email_subscriptions(APIView):
#     authentication_classes = (SessionAuthentication,TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)

    def post(self,request,format=None):
        try:
            if request.method == 'POST':
                subject = 'Subscribe Email'
                subscribe_email = request.data.get('subscribe_email','')
                to_email = subscribe_email

                #====== random key generation
                key = str(uuid.uuid4())+str(uuid.uuid4())+str(uuid.uuid4())
                #====== Email subscription data entry
                try:
                    subscription_obj = EmailSubscription.objects.get(user=request.user)
                    if subscription_obj is not None:
                        subscription_obj.semail=to_email
                        subscription_obj.subscribe_key=key
                        subscription_obj.save()
                    else:
                        subscription_obj = EmailSubscription(
                                                        user=request.user,
                                                        semail=to_email,
                                                        subscribe_key=key,
                                                    )
                        subscription_obj.save()

                except Exception as e:
                    subscription_obj = EmailSubscription(
                                                        user=request.user,
                                                        semail=to_email,
                                                        subscribe_key=key,
                                                    )
                    subscription_obj.save()

                #====== email verification part
                link=settings.SITE_URL+'/email_subscribe_valid/'+key+'/'
                from_email = settings.EMAIL_HOST_USER
                email_content = "Thank you for subscribing us. Please click in the below link to confirm your subscription email. \n"+link
                html_content = get_template('email-subscribe.html').render({'content': link,'email':to_email})
                text_content="This is a confirmation email."
                subject="confirmation email from petjibe"
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                return Response({"success":True,"message":"Please verify your email to subscribe"},status=status.HTTP_200_OK)

            return Response({"msg":"success"},status=status.HTTP_200_OK)
        except Exception as e:
            print(str(e))
            return Response({"success":True,"message":"Please verify your email to subscribe"})


#=====================================================================================================================#
'''
    @name: email_subscription_valid
    @param : request 
    @description : email_subscription_valid view
'''
def email_subscription_valid(request,key):
    try:
        valid=False
        message="subscribe again"
        if key:
            subscribe_obj = EmailSubscription.objects.get(subscribe_key=key)
            if subscribe_obj is not None:
                subscribe_obj.verified=True
                subscribe_obj.save()

                valid=True
                return  HttpResponseRedirect('/index/')

        return render(request,"index.html",{'valid':valid,"message":message})
    except Exception as e:
        print(str(e))
        return render(request,"index.html",{})


#=====================================================================================================================#
'''
    @name: indexView
    @param : request 
    @description : index page view render index page
'''
def indexView(request):
    try:
        #====== data initializations
        pet_type_list=[]
        pet_breed_list=[]
        owner_interest_list=[]
        category_list1=[]
        category_list2=[]
        zipcode_list=[]

        #====== fetching category data from database
        category_obj = ContentCategory.objects.all()
        if category_obj is not None:
            for data in category_obj:
                inner_list=[]
                inner_list.append(data.id)
                inner_list.append(data.content_cat)
                if int(data.id) < 4:
                    category_list1.append(inner_list)
                else:
                    category_list2.append(inner_list)
        #====== fetching pet type data from database
        pet_type_list.append([100,'Any'])
        pet_type_obj=Pet_Type.objects.all()
        if pet_type_obj is not None:
            for data in pet_type_obj:
                inner_list=[]
                inner_list.append(data.id)
                inner_list.append(data.pet_type)
                pet_type_list.append(inner_list)

        #====== fetching pet breed data from database
        pet_breed_obj=Pet_Breed.objects.filter(pet_type=Pet_Type.objects.get(pk=1))
        if pet_breed_obj is not None:
            for data in pet_breed_obj:
                inner_list=[]
                inner_list.append(data.id)
                inner_list.append(data.pet_breed)
                pet_breed_list.append(inner_list)

        #====== fetching pet owner interest data from database
        pet_owner_interest_obj=Pet_Owner_Interest.objects.all()
        if pet_owner_interest_obj is not None:
            for data in pet_owner_interest_obj:
                inner_list=[]
                inner_list.append(data.id)
                inner_list.append(data.Interest_Desc)
                owner_interest_list.append(inner_list)

        #====== fetching zip code data from database
#         petjibe_obj=Petjibeuser.objects.get(user=request.user)
#         if petjibe_obj is not None:
#             if petjibe_obj.country is None:
#                 country_code="USA"
#             else:
#                 country_code = petjibe_obj.country
#
#             if petjibe_obj.state is None:
#                 state_code="CA"
#             else:
#                 state_code = petjibe_obj.state
#
#             city_obj=City.objects.filter(country_code_3ch=country_code).filter(state_code=state_code)
#             if city_obj is not None:
#                 for data in city_obj:
#                     inner_list=[]
#                     inner_list.append(data.zip_code)
#                     zipcode_list.append(inner_list)

        #======= getting context
        context={
                 'category_list1':category_list1,
                 'category_list2':category_list2,
                 "pet_type_list":pet_type_list,
                 "pet_breed_list":pet_breed_list,
                 "owner_interest_list":owner_interest_list,
                 #"zipcode_list":zipcode_list,
                 "google_search_location_key":settings.GOOGLE_SEARCH_LOCATION,
                 "geolocation_api_key":settings.GOOGLE_GEOLOCATION_KEY,
                 }

        return render(request,"index.html",context)
    except Exception as e:
        print(str(e))
        return render(request,"index.html",{})

#=====================================================================================================================#
'''
    @name: petArticleView
    @param : request 
    @description : render pet article page 
'''

def petArticleView(request,type):
    try:
        #========== variable initialization
        pagetitle=""
        art_img=""
        art_desc=""
        meta_desc=""
        meta_title=""
        og_img=""
        og_title=""
        og_desc=""
        share_img=""
        article_list=[]

        #========= fetching content details data
        contents_obj = ContentDetails.objects.filter(content_cat_id=int(type))

        if contents_obj is not None and len(contents_obj)>0 :
            for one_obj in contents_obj:
                art_desc=one_obj.cont_desc
                art_img = one_obj.cont_image
                if art_desc is None or art_img is None:
                    #=========== getting data from url
                    res = requests.get(one_obj.cont_link)
                    if res.status_code==200:
                        soup=BeautifulSoup(res.content,"html.parser")
                        for data in soup.find_all("meta"):
                            if data.get("name")== "DESCRIPTION" or data.get("name")== "description":
                                meta_desc = data.get("content")
                            elif data.get("http-equiv")=="TITLE" or data.get("http-equiv")=="title" :
                                meta_title = data.get("content")
                            elif data.get("property")=="og:image":
                                if og_img is not None or len(og_img)>0:
                                    og_img_link = data.get("content")
                                    path_elem = og_img.split(".")
                                    if "jpg" not in path_elem:
                                        og_img=""
                                    else:
                                        og_img=og_img_link
                                else:
                                    og_img_link = data.get("content")
                                    path_elem = og_img.split(".")
                                    if "jpg" not in path_elem:
                                        og_img=""
                                    else:
                                        og_img=og_img_link

                            elif data.get("property")=="og:title":
                                og_title=data.get("content")
                            elif data.get("property")=="og:description":
                                og_desc=data.get("content")
                            elif data.get("name")=="shareaholic:image":
                                share_img = data.get("content")
                            else:
                                pass

                        page_title = soup.find("title").get_text()

                        #=========== saving data to the database
                        one_obj.cont_desc=meta_desc+"\n"+og_desc
                        if len(meta_title)>0 and meta_title is not None:
                            one_obj.cont_heading=meta_title
                        else:
                            one_obj.cont_heading=page_title
                        if len(og_img)>0 and og_img is not None:
                            one_obj.cont_image=og_img
                            one_obj.img_flag=True
                        elif share_img is not None and len(share_img)>0:
                            one_obj.cont_image=share_img
                            one_obj.img_flag=True
                        else:
                            one_obj.cont_image=""

                        one_obj.save()

                    #========== generate list
                    inner_list=[]
                    inner_list.append(one_obj.id)
                    inner_list.append(one_obj.cont_heading)
                    inner_list.append(one_obj.cont_image)
                    inner_list.append(one_obj.cont_desc)
                    inner_list.append(one_obj.add_date)
                    #article_list.append(inner_list)
                    if one_obj.img_flag == True:
                        article_list.append(inner_list)
                    else:
                        pass


                else:
                    #========== generate list
                    inner_list=[]
                    inner_list.append(one_obj.id)
                    inner_list.append(one_obj.cont_heading)
                    inner_list.append(one_obj.cont_image)
                    inner_list.append(one_obj.cont_desc)
                    inner_list.append(one_obj.add_date)
                    #article_list.append(inner_list)
                    if one_obj.img_flag == True:
                        article_list.append(inner_list)
                    else:
                        pass

        contentcat_obj=ContentCategory.objects.get(pk=int(type))
        if contentcat_obj is not None:
            pagetitle = contentcat_obj.content_cat

        return render(request,"pet-articles.html",{'article_list':article_list,'pagetitle':pagetitle})
    except Exception as e:
        print(str(e))
        return render(request,"pet-articles.html",{})

#=====================================================================================================================#
'''
    @name: articleRedirectView
    @param : request 
    @description : render pet article redirection page 
'''
def articleRedirectView(request,art_id):
    try:
        if art_id is not None:
            content_obj = ContentDetails.objects.get(pk=int(art_id))
            if content_obj is not None:
                article_link = content_obj.cont_link

            return render(request,"article_redirection.html", {"url":article_link})
    except Exception as e:
        print(str(e))

#=====================================================================================================================#
'''
    @name : send_mail
    @param: request
    @description: sending mail method
'''
def send_mail(user):
    try:
        user=User.objects.get(id=user)
        key=UserPasswordKeys.objects.filter(user=user,valid_till__lt=datetime.now()+timedelta(days=1),spent=False)
        if key:
            key=key.first()
            link=settings.SITE_URL+'/resetpassword/'+key.key+'/'
            message="""Hi,
            Please click on below link to reset your password.This link is valid for 1 day and is for one time use only.
            
            
            """
            message=message+link

            user.email_user(subject="Password reset link",message=message,from_email=settings.DEFAULT_FROM_EMAIL , fail_silently=False)
            key.mail_sent=True
            key.save()
    except Exception as e:
        print(str(e))

'''
    @name : forgot_password
    @param: request
    @description: forget password view
'''
def forgot_password(request):
    try:
        message=""
        if request.method=='POST':
            email=request.POST["email"]
            try:
                user=User.objects.filter(email__iexact=email)
                if user:
                    user=user.first()
                    key=str(uuid.uuid4())+str(uuid.uuid4())+str(uuid.uuid4())+str(uuid.uuid4())
                    user_pass_keys = UserPasswordKeys(user=user,key=key)
                    user_pass_keys.save()
                    send_mail(user.id)
                    message="Instructions sent to your email. Please check email!"
            except Exception as e :
                print(str(e))
                user=Petjibeuser.objects.filter(otherEmail__iexact=email)
                if user:
                    user=user.first()
                    key=str(uuid.uuid4())+str(uuid.uuid4())+str(uuid.uuid4())+str(uuid.uuid4())+str(uuid.uuid4())
                    UserPasswordKeys(user=user,key=key).save()
                    send_mail.delay(user.id)
                    message="Instructions sent to your email. Please check email!"
            return HttpResponseRedirect('/join/')

        else:
            message="Enter your registered email"
            return render(request,'forgot_password.html',{"message":message})

    except Exception as e:
        print(str(e))


#=====================================================================================================================#
'''
    @name : reset_password
    @param: request
    @description: reset password view 
'''
def reset_password(request,key):
    try:
        key = UserPasswordKeys.objects.filter(key=key, valid_till__lt=datetime.now() + timedelta(days=1), spent=False)
        valid=False
        message="Change Password"
        if key:
            key=key.first()
            valid=True
            if request.method=="POST":
                if "pw" in request.POST and "cpw" in request.POST:
                    password=request.POST["pw"]
                    cpassword = request.POST["cpw"]
                    if password==cpassword:
                        user=key.user
                        user.set_password(cpassword)
                        user.save()
                        key.spent=True
                        key.save()
                        return  HttpResponseRedirect('/')
                    else:
                        message="Passwords dont match"
        return render(request,"reset_password.html",{'valid':valid,"message":message})
    except Exception as e:
        print(str(e))

#=====================================================================================================================#
'''
    @name : change_password
    @param: request
    @description: change password view
'''
@login_required
def change_password(request):
    try:
        if request.method=="POST":
            if "oldpw" in request.POST and "newpw" in request.POST:
                oldpw=request.POST["oldpw"]
                newpw = request.POST["newpw"]
                conf_newpw = request.POST["conf_newpw"]
                if newpw==conf_newpw:
                    user=request.user
                    user.set_password(conf_newpw)
                    user.save()
                    return  HttpResponseRedirect('/logout/')
                else:
                    message="Passwords dont match"

            return  HttpResponseRedirect('/logout/')
            #return render(request,"change_password.html",{"message":message})
        else:
            return render(request,"change_password.html",{})

    except Exception as e:
        print(str(e))
        return render(request,"change_password.html",{})
#=====================================================================================================================#

'''
    @name : searchResultApiView
    @param: request
    @description: search results api view
'''
def searchResultApiView(request):
    try:
        if request.method=="POST":
            pet_type=request.POST.get("pet_type","")
            pet_breed=request.POST.get("pet_breed","")
            owner_interest=request.POST.get("owner_intrs","")
            radius = request.POST.get("radius","10")
            zip = request.POST.get("zipcode","")
            clat = request.POST["clat"]
            clong = request.POST["clong"]

            if len(clat) == 0 or clat is None:
                response = requests.get('http://api.ipstack.com/check?access_key='+settings.IP_STACK_ACCESS_KEY) # 00035a3e9a9b638882127722275c8957
                json_data = response.json()

                if len(json_data) > 0:
                    clat = json_data["latitude"]
                    clong = json_data["longitude"]

                    request.session['clat'] = clat
                    request.session['clong'] = clong

            else:
                request.session['clat'] = clat
                request.session['clong'] = clong

            #======= saving search parameter in database
            if pet_type == '0':
                search_obj = Search(
                                        search_Date=datetime.now,
                                        interest=owner_interest,
                                        zip_code=zip,
                                        radius=radius
                                    )
                search_obj.save()
                search_id = search_obj.id
            else:
                search_obj = Search(
                                        search_Date=datetime.now,
                                        pet_type=Pet_Type.objects.get(pk=pet_type),
                                        pet_breed_type=Pet_Breed.objects.get(pk=pet_breed),
                                        interest=owner_interest,
                                        zip_code=zip,
                                        radius=radius
                                    )
                search_obj.save()
                search_id = search_obj.id

            #====== variable initialization
            neighbour_list=[]
            interest_list=[]
            pet_flag=False
            owner_interest_flag=False
            dist_param_flag=False
            pet_count=0

            #====== search query current location
            cur_loc = (float(clat),float(clong))
            #======== all parameters checking
            try:
                petjibe_obj = Petjibeuser.objects.filter(zipcode=zip)
                if len(petjibe_obj) == 0:
                    petjibe_obj = Petjibeuser.objects.all()
            except Exception as e:
                petjibe_obj = Petjibeuser.objects.all()

            if petjibe_obj is not None:
                for one_obj in petjibe_obj:
                    if one_obj.user != request.user:
                        lat = one_obj.lat
                        long = one_obj.long
                        next_loc=(lat,long)

                        #======== distance comparison
                        distance_cmp = vincenty(cur_loc, next_loc, miles=True)
                        if float(distance_cmp) < float(radius):
                            dist_param_flag=True
                            outer_list=[]
                            outer_list.append(one_obj.first_name +" "+one_obj.last_name)
                            outer_list.append(one_obj.addr1)
                            outer_list.append(one_obj.addr2)
                            outer_list.append(one_obj.user.email)
                            outer_list.append(one_obj.lat)
                            outer_list.append(one_obj.long)

                            interest_chk_list = one_obj.interest_ids
                            if len(interest_chk_list)>0:
                                if interest_chk_list.startswith('['):
                                    interest_chk_list = interest_chk_list[1:-1].replace("'","")
                                    interest_ids = interest_chk_list.split(",")
                                    interest_ids_list=interest_ids
                                    if interest_ids_list[0]!="":
                                        for id in interest_ids:
                                            interest_obj=Pet_Owner_Interest.objects.get(pk=int(id))
                                            if interest_obj:
                                                #======== owner interest comparison
                                                if owner_interest == interest_obj.Interest_Desc:
                                                    owner_interest_flag = True

                                                    inner_list=[]
                                                    inner_list.append(interest_obj.id)
                                                    inner_list.append(interest_obj.Interest_Desc)
                                                    interest_list.append(inner_list)
                                    else:
                                        pass
                            else:
                                pass

                            outer_list.append(interest_list)

                            #========== getting pet breed and type
                            if pet_type != '0':
                                cur_pet_type = Pet_Type.objects.get(pk=pet_type).pet_type
                                cur_pet_breed = Pet_Breed.objects.get(pk=pet_breed).pet_breed

                                try:
                                    pet_obj = Pet.objects.filter(user=one_obj.user)
                                    if pet_obj is not None:
                                        for one in pet_obj:
                                            u_pet_type = one.pet_type.pet_type
                                            u_pet_breed = one.pet_breed.pet_breed


                                            if cur_pet_type == u_pet_type and cur_pet_breed == u_pet_breed:
                                                pet_flag = True
                                                pet_count+=1
                                    else:
                                        pet_count=0
                                except:
                                    pet_count=0

                                outer_list.append(pet_count)
                            else:
                                pet_flag = True
                                outer_list.append(pet_count)

                            if pet_flag == True and dist_param_flag == True:
                                neighbour_list.append(outer_list)

                                #========= save search results in database
                                search_result_data = SearchResults(
                                                            search=search_obj,
                                                            user=one_obj.user,
                                                            pet_parent_nick_name=one_obj.first_name+" "+one_obj.last_name,
                                                            dist_from_zip=distance_cmp,
                                                            pet_count=pet_count,
                                                            interest=one_obj.interest_ids
                                                        )
                                search_result_data.save()

                        else:
                            pass


            request.session['neighbour_list']=neighbour_list

            return JsonResponse({'msg':'success'})
        else:
            return render(request,"search-results.html",{})

    except Exception as e:
        print(str(e))
        return render(request,"search-results.html",{"success":False,"message":"Petjibe community search failed. Try again later."})

#=====================================================================================================================#
'''
    @name : searchresultsview
    @param: request
    @description: search results view to rendering search results page
'''
def searchresultsview(request):
    try:
        if request.method == "POST":
            if request.session:
                neighbour_list = request.session['neighbour_list']
                clat = request.session['clat']
                clong = request.session['clong']
                list_len = len(neighbour_list)

                #========= context
                context={
                        "neighbour_list":neighbour_list,
                        #"neighbour_list": [['Test1','24/6 R.K Road','West Bengal, India','test1@petjibe.com','22.2342','87.5666','feed pets','2'],['Test2','24/6 R.K Road','West Bengal, India','test2@petjibe.com','22.23134','87.2333','watch pets','2'],['Test3','24/6 R.K Road','West Bengal, India','test3@petjibe.com','22.23734','87.2393','like pets','3'],['Test4','24/6 R.K Road','West Bengal, India','test4@petjibe.com','22.23134','88.2333','like pets','4'],['Test5','24/6 R.K Road','West Bengal, India','test5@petjibe.com','22.776','88.8856','feed pet twice a day','2'],['Test6','24/6 R.K Road','West Bengal, India','test6@petjibe.com','22.98','87.23887','pet training','5'],['Test7','24/6 R.K Road','West Bengal, India','test7@petjibe.com','22.23134','87.8763','pet watching','2'],['Test8','24/6 R.K Road','West Bengal, India','test8@petjibe.com','22.23884','87.9733','love pet grooming','1'],['Test9','24/6 R.K Road','West Bengal, India','test9@petjibe.com','22.28934','87.8533','pet training','2'],['Test10','24/6 R.K Road','West Bengal, India','test10@petjibe.com','22.23994','87.7773','pet health','1'],['Test11','24/6 R.K Road','West Bengal, India','test11@petjibe.com','22.34134','87.9633','pet health','4'],['Test12','24/6 R.K Road','West Bengal, India','test12@petjibe.com','22.1134','87.7653','pet grooming','1'],['Test13','24/6 R.K Road','West Bengal, India','test13@petjibe.com','22.10134','86.3388','pet health','3'],['Test14','24/6 R.K Road','West Bengal, India','test14@petjibe.com','22.34444','86.330043','pet health','2'],['Test15','24/6 R.K Road','West Bengal, India','test15@petjibe.com','22.97134','87.33','pet organic food','5'],['Test16','24/6 R.K Road','West Bengal, India','test16@petjibe.com','21.23134','88.23','pet organic food','4'],['Test17','24/6 R.K Road','West Bengal, India','test17@petjibe.com','21.534','88.2883','pet health','2'],['Test18','24/6 R.K Road','West Bengal, India','test18@petjibe.com','22.56','88.23543','pet health','2'],['Test19','24/6 R.K Road','West Bengal, India','test19@petjibe.com','23.23134','88.23','feed pet','2'],['Test20','24/6 R.K Road','West Bengal, India','test20@petjibe.com','22.3654','87.8943','pet health','4'],['Test21','24/6 R.K Road','West Bengal, India','test21@petjibe.com','24.34','88.2643','pet grooming','3'],['Test22','24/6 R.K Road','West Bengal, India','test22@petjibe.com','23.34','88.2643','pet health','2'],['Test23','24/6 R.K Road','West Bengal, India','test23@petjibe.com','22.23134','88.23','pet organic food','3'],['Test24','24/6 R.K Road','West Bengal, India','test24@petjibe.com','21.23134','87.23','pet grooming','6'],['Test25','24/6 R.K Road','West Bengal, India','test25@petjibe.com','21.23134','87.939','pet organic food','2'],['Test26','24/6 R.K Road','West Bengal, India','test26@petjibe.com','22.6754','87.739','pet food','5'],['Test27','24/6 R.K Road','West Bengal, India','test27@petjibe.com','22.6654','87.9923','pet health','3'],['Test28','24/6 R.K Road','West Bengal, India','test28@petjibe.com','21.23134','86.23','pet grooming','2'],['Test29','24/6 R.K Road','West Bengal, India','test29@petjibe.com','22.23134','86.23','pet health','6'],['Test30','24/6 R.K Road','West Bengal, India','test30@petjibe.com','22.23134','84.23','pet health','2'],['Test31','24/6 R.K Road','West Bengal, India','test31@petjibe.com','23.23134','86.23','pet training','6'],['Test32','24/6 R.K Road','West Bengal, India','test32@petjibe.com','21.77454','88.23','pet health','1'],['Test33','24/6 R.K Road','West Bengal, India','test33@petjibe.com','21.23134','86.9723','pet training','3'],['Test34','24/6 R.K Road','West Bengal, India','test34@petjibe.com','21.238888','87.22223','pet training','2'],['Test35','24/6 R.K Road','West Bengal, India','test35@petjibe.com','21.8888','88.23765','pet grooming','1'],['Test36','24/6 R.K Road','West Bengal, India','test36@petjibe.com','22.287874','88.23','pet organic food','2'],['Test37','24/6 R.K Road','West Bengal, India','test37@petjibe.com','22.283434','87.656523','pet training','4'],['Test38','24/6 R.K Road','West Bengal, India','test38@petjibe.com','23.2334','88.23','pet training','1'],['Test39','24/6 R.K Road','West Bengal, India','test39@petjibe.com','21.23134','88.56332','pet food','1'],['Test40','24/6 R.K Road','West Bengal, India','test40@petjibe.com','21.27774','86.23','pet health','1'],['Test41','24/6 R.K Road','West Bengal, India','test41@petjibe.com','22.76548','87.238787','pet training','1'],['Test42','24/6 R.K Road','West Bengal, India','test42@petjibe.com','22.23134','87.878723','pet training','2']],
                        "clat":clat,
                        "clong":clong,
                        #"data_len":42,
                        "data_len":list_len,
                    }

                return JsonResponse(context)
        else:
            clat = request.session['clat']
            clong = request.session['clong']
            return render(request,"search-results.html",{"clat":clat,"clong":clong})
    except Exception as e:
        print(e)
        return render(request,"search-results.html",{})

#======================================================================================================================#


'''
    @name : SendMessageView
    @param: request
    @description: sending mail in community members
'''
def sendMessageView(request):
    try:
        if request.method=="POST":
            if "name_list" in request.POST and "email_list" in request.POST:
                name_list=request.data.get("name_list",[])
                email_list=request.data.get("email_list",[])

                context={
                         "email_list":email_list,
                         }

                return render(request,"search-message.html",context)
            else:
                return render(request,"search-message.html",{"email_list":[]})
        else:
            return render(request,"search-message.html",{})

    except Exception as e:
        print(str(e))
        return render(request,"search-message.html",{"success":False,"message":"Petjibe email server is not working. Please try again later"})

#=====================================================================================================================#

'''
    @name : SendMessageInCommunity
    @param: request
    @description: sending mail in community members
'''
class SendMessageInCommunity(APIView):
    authentication_classes = (SessionAuthentication,TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self,request,format=None):
        try:
            name_list=request.data.get("name_list",[])
            email_list=request.data.get("email_list",[])
            msg_body = request.data.get("msg_body",[])
            subject = "petjibe community message "
            to = email_list
            from_email = settings.DEFAULT_FROM_EMAIL

            email_msg = EmailMessage(subject, msg_body, from_email, [to])
            #msg.content_subtype = "html"  # Main content is now text/html
            email_msg.send()

            return Response({"success":True,"message":"All message send through petjibe community email"})

        except Exception as e:
            print(str(e))
            return Response({"success":False,"message":"Petjibe email server is not working. Please try again later"})

#=====================================================================================================================#


'''
    @name : contactusView
    @param: request
    @description: contact us view to send email to petjibe contact from user
'''
class ContactusView(APIView):

    def post(self,request,format=None):
        try:
            #============ getting data from post method
            cname=request.POST.get("cname","")
            cemail=request.POST["cemail"]
            csubject=request.POST.get("csubject","")
            cmessage=request.POST["cmessage"]

            #======== sending email
            to_email=settings.CONTACT_EMAIL
            from_email = settings.EMAIL_HOST_USER
            email_content = "Sender's Data : \n\n\n\n\n\n\n\n1) NAME : "+cname+" \n\n\n\n 2) EMAIL : "+cemail+"   \n\n\n\n 3) SUBJECT : "+csubject+" 4) \n\n\n\nMESSAGE : "+cmessage
            html_content = get_template('email-contact.html').render({'content': email_content,'email':to_email})
            text_content="This message is from contact section."
            subject="email subject from sender : "+csubject
            try:
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            except Exception as e:
                print(e)

            #======== saving data into database
            contact_obj=Contact(
                                cont_name=cname,
                                cont_email=cemail,
                                cont_subj=csubject,
                                cont_msg=cmessage,
                                cont_src="website"
                            )
            contact_obj.save()

            context={
                     "msg":"message sent",
                    }

            return Response(context)

        except Exception as e:
            print(str(e))
            return Response({})



#=====================================================================================================================#

'''
    @name : GetZipcode
    @param: request
    @description: getting zipcode of petjibe user from lat and long data
'''
class GetZipcode(APIView):
    authentication_classes = (SessionAuthentication,TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self,request,format=None):
        try:
            zipcode_list=[]
            #============ getting data from post method
            clat=request.POST.get("clat","")
            clong=request.POST.get("clong","")

            #=========== getting zipcode
            cur_loc=(float(clat),float(clong))
            petjibeuser_obj = Petjibeuser.objects.all()
            if petjibeuser_obj is not None:
                for one_obj in petjibeuser_obj:
                    ulat = one_obj.lat
                    ulong = one_obj.long
                    next_loc=(ulat,ulong)

                    distance_cmp = vincenty(cur_loc, next_loc, miles=True)
                    if float(distance_cmp) < float(500.00):
                        zipcode_list.append(one_obj.zipcode)

            context={
                     "zipcode_list":zipcode_list,
                    }

            return Response(context)

        except Exception as e:
            print(str(e))
            return Response({})



#=====================================================================================================================#


'''
    @name : UserMsgView
    @param: request
    @description: getting user message thread messages for particular thread
'''

class UserMsgView(APIView):
    """
        view for thread messages of a thread id
    """
    authentication_classes = (SessionAuthentication,TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        try:
            thread_list = []
            thread_username = ""
            thread_user_email = ""
            sender_email = ""
            thread_id = request.data["thread_id"]
            request.session["thread_id"] = thread_id
            thread_obj = Thread.objects.get(pk=thread_id)
            if thread_obj is not None:
                for one_user in thread_obj.users.all():
                    if one_user.get_username() == request.user.get_username():
                        pass
                    else:
                        thread_username = one_user.get_username()
                        request.session["thread_user"]=one_user.id

                msg_obj=Message.objects.filter(thread=thread_obj)
                if msg_obj is not None:
                    for msg in msg_obj:
                        inner_list=[]
                        inner_list.append(msg.content)
                        sender=json.loads(serialize('json',[msg.sender]))[0]
                        inner_list.append(sender["fields"]['username'])
                        inner_list.append(sender["fields"]['first_name'])
                        inner_list.append(sender["fields"]['last_name'])
                        sender_email = sender["fields"]['email']
                        inner_list.append(sender_email)
                        if sender_email != request.user.email :
                            thread_user_email = sender_email
                        else:
                            pass
                        inner_list.append(str(msg.sent_at).split(".")[0])
                        thread_list.append(inner_list)


            return Response({"thread_list":thread_list,"thread_username":thread_username,"thread_id":thread_id,"thread_user_email":thread_user_email})
        except Exception as e:
            print(e)
            return Response({})

#=====================================================================================================================#
'''
    @name : UserCreateMsgView
    @param: request
    @description: create new messages for particular thread
'''

class UserReplyMsgView(APIView):
    """
        view for create message on thread
    """
    authentication_classes = (SessionAuthentication,TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        try:
            content = request.data["msg"]
            try:
                thread_user_id = request.session["thread_user"]
                thread_user = User.objects.get(pk=thread_user_id)
                thread_obj = Thread.objects.get(pk=request.session["thread_id"])
            except:
                sender_email=request.data["sender_email"]
                thread_user = User.objects.get(email=sender_email)
                thread_id = request.data["thread_id"]
                thread_obj = Thread.objects.get(pk=int(thread_id))


            Message.new_reply(thread=thread_obj, user=thread_user, content=content)

            return Response({"msg":"sent"})
        except Exception as e:
            print(e)


#=====================================================================================================================#

'''
    @name : UserCreateMsgView
    @param: request
    @description: create new messages for particular thread
'''

class UserCreateMsgView(APIView):
    """
        view for create message on thread
    """
    authentication_classes = (SessionAuthentication,TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        try:
            to_user = request.data["to_user"]
            new_user = User.objects.get(email=to_user)
            subject = request.data["subject"]
            content = request.data["content"]
            try:
                Message.new_message(from_user=request.user, to_users=[new_user], subject=subject, content=content)
            except Exception as e:
                print(e)
            return Response({"msg":"sent"})
        except Exception as e:
            print(e)
            return Response({"msg":"not sent"})


#=====================================================================================================================#

'''
    @name : allMessageView
    @param: request
    @description: getting all messages from database for a particular user
'''
@login_required
def allMessageView(request):
    try:
        inbox_msg_details = []
        cur_thread_details = []
        thread_id = None
        cur_from_user = ""
        sender_email = ""
        last_thread_id = None

        cur_user_name = request.user.get_username()
        allInboxData = Thread.objects.filter(users__in=[request.user])
        if allInboxData:
            for one_obj in allInboxData:
                inner_dict={}
                thread_id = one_obj.id
                inner_dict["thread_id"]=thread_id
                inner_dict["subject"]=one_obj.subject
                cur_user = one_obj.users.all()
                for one in cur_user:
                    username = one.get_username()
                    if cur_user_name != username:
                        from_user = username
                        inner_dict["from_user"] = from_user
                        try:
                            inner_dict["profile_pic"] = Petjibeuser.objects.get(user__username=username).get_profile_pic
                        except:
                            pass
                    else:
                        pass

                inbox_msg_details.append(inner_dict)

        last_thread_id = thread_id
        thread_list = []
        thread_username = ""
        request.session["thread_id"] = last_thread_id
        thread_obj = Thread.objects.filter(pk=thread_id)
        if thread_obj:
            thread_obj=thread_obj.first()
            for one_user in thread_obj.users.all():
                if one_user.get_username() == request.user.get_username():
                    pass
                else:
                    thread_username = one_user.get_username()
                    request.session["thread_user"]=one_user.id

            msg_obj=Message.objects.filter(thread=thread_obj)
            if msg_obj is not None:
                for msg in msg_obj:
                    inner_dict={}
                    inner_dict["msg_content"] = msg.content
                    sender=json.loads(serialize('json',[msg.sender]))[0]
                    inner_list.append(sender["fields"]['username'])
                    inner_dict["first_name"] = sender["fields"]['first_name']
                    inner_dict["last_name"] = sender["fields"]['last_name']
                    sender_email = sender["fields"]['email']
                    if sender_email != request.user.email :
                        cur_from_user =  sender_email
                        inner_dict["sender_email"] = sender_email
                    else:
                        inner_dict["sender_email"] = sender_email
                    inner_dict["sent_at"] = str(msg.sent_at).split(".")[0]
                    cur_thread_details.append(inner_dict)


        user_list = []
        #============== getting users of petjibe
        #==== getting data from FriendsConn
        friend_list = []
        invite_friend_list = []
        friends_conn_obj = FriendsConn.objects.filter(user=request.user)
        if friends_conn_obj:
            friends_conn_obj=friends_conn_obj.first()
            connected = friends_conn_obj.connected
            invited = friends_conn_obj.invited
            
            if connected is not None:
                if connected.startswith('['):
                    connected_list = connected[1:-1].replace("'", "")
                    connected_frnds = connected_list.split(",")
                    if connected_frnds[0] != "":
                        for conn in connected_frnds:
                            userobj = User.objects.get(pk=int(conn))
                            if userobj:
                                friend_list.append(userobj)
                            else:
                                pass
                    else:
                        pass
                else:
                    pass
            else:
                pass
            if invited is not None:
                if invited.startswith('['):
                    invited_list = invited[1:-1].replace("'", "")
                    invited_frnds = invited_list.split(",")
                    if invited_frnds[0] != "":
                        for conn in invited_frnds:
                            userobj = User.objects.get(pk=int(conn))
                            if userobj:
                                invite_friend_list.append(userobj)
                            else:
                                pass
                    else:
                        pass
                else:
                    pass
            else:
                pass

        # ===== list of users
        user_obj = User.objects.all()
        if user_obj:
            for one_user in user_obj:
                inner_dict = {}
                if request.user.email != one_user.email:
                    inner_dict["email"] = one_user.email
                    inner_dict["username"] = one_user.username
                    try:
                        inner_dict["profile_pic"] = Petjibeuser.objects.get(user=one_user).get_profile_pic
                    except:
                        pass
                    if one_user in friend_list:
                        inner_dict["connected"] = "connected"
                    elif one_user in invite_friend_list:
                        inner_dict["invited"] = "invited"
                    else:
                        inner_dict["notconnected"] = "notconnected"
                else:
                    pass
                user_list.append(inner_dict)
                ppic="default.jpg"
                try:
                    ppic=Petjibeuser.objects.get(user=request.user).get_profile_pic
                except:
                    pass
        return render(request, "chat-box-mod.html", {"ppic":ppic,"cur_thread_details": cur_thread_details, "inbox_msg_details": list(reversed(inbox_msg_details)), "cur_from_user": cur_from_user, "last_thread_id": last_thread_id, "user_list": user_list, "receiver": request.user.email})

    except Exception as e:
        return HttpResponseRedirect("/join")


# =====================================================================================================================#

'''
    @name : newMessageView
    @param: request
    @description: getting all messages from database for a particular user
'''


@login_required
def newMessageView(request):
    try:
        user_list = []
        # ============== getting users of petjibe
        # ===== list of users
        user_obj = User.objects.all()
        if user_obj is not None:
            for one_user in user_obj:
                inner_list = []
                if request.user.email != one_user.email:
                    inner_list.append(one_user.email)
                    inner_list.append(one_user.username)
                else:
                    pass
                user_list.append(inner_list)
        #return HttpResponseRedirect("/")
        return render(request,"msgcreate.html",{"user_list":user_list})
    except Exception as e:
        return render(request,"msgcreate.html",{})

#=====================================================================================================================#

def set_multi_emails(request):
    key=""
    if request.method=='POST' and request.is_ajax():
        if 'email_ids' in request.POST:
            key=str(uuid.uuid4())
            cache.set(key,request.POST['email_ids'],100000)
    return JsonResponse({"key":key})

#=====================================================================================================================#

def searchmsg(request,uid):
    emails=[]
    pusers=[]
    if uid in cache:
        emails=cache.get(uid)
        try:
            emails=json.loads(emails)
            print(emails)
            pusers=Petjibeuser.objects.filter(user__in=User.objects.filter(email__in=emails))
        except:
            pass
    return render(request,'search-message.html',{'emails':emails,'uid':uid,'petu':pusers})

#=====================================================================================================================#

class UserCreateMultiMsgView(APIView):
    """
        view for create message on thread
    """
    authentication_classes = (SessionAuthentication, TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def fetchusers(self,uid):
        pusers = []
        if uid in cache:
            emails = cache.get(uid)
            try:
                emails = json.loads(emails)
                print(emails)
                pusers=User.objects.filter(email__in=emails)

            except:
                pass
        return pusers
    def post(self, request):
        try:
            uid=request.data["uid"]
            touser=self.fetchusers(uid)
            subject = "Send All"
            content = request.data["content"]
            try:
                Message.new_message(from_user=request.user, to_users=touser, subject=subject, content=content)
            except Exception as e:
                print(e)
            return Response({"msg": "sent"})
        except Exception as e:
            print(e)
            return Response({"msg": "not sent"})

#=====================================================================================================================#

from pinax.messages.signals import message_sent
from django.dispatch import receiver
@receiver(message_sent)
def auto_msg_email(sender, **kwargs):
    fro1m=kwargs['message'].sender
    to=kwargs['thread'].users.all()
    subject=kwargs['thread'].subject
    for user in to:
        if user != fro1m:
            messge="""
            Hi """+user.get_full_name()+""",
            
            You have just recieved a new message from """+fro1m.username+"""
            
            Subject:"""+kwargs['thread'].subject+"""
            
            Message:"""+kwargs['message'].content+"""
            
            
            """
            user.email_user("New message on petjibe",messge)
    # if 'message' in kwargs:
    #     print(kwargs['message'].sender)
    # if 'thread' in kwargs:
    #     print(kwargs['thread'].users.all())

    print("sent")


@login_required
def user_upload_image(request):
    if request.method=="POST" and request.is_ajax():
        print(request.FILES)
        user = request.user
        if not user:
            return JsonResponse({'message':'error'})
        petju = Petjibeuser.objects.filter(user=user)
        if not petju:
            return JsonResponse({'message': 'error'})
        if 'file' in request.FILES:
            f=request.FILES['file']
            ftype=magic.from_buffer(f.read()).lower()
            if 'jpeg' not in ftype and 'png' not in ftype and 'jpg' not in ftype:
                return JsonResponse({'message': 'incorrect file type'})
            media_path=os.path.join(settings.MEDIA_ROOT,'profile_images')
            path = Path(media_path)
            path.mkdir(parents=True, exist_ok=True)
            fname=str(uuid.uuid4())[:20]+'.jpg'
            impath=os.path.join(media_path,fname)
            with open(impath,'wb+') as fn:
                for chunk in f.chunks():
                    fn.write(chunk)
            petju=petju.first()
            petju.profile_pic=fname
            petju.save()
    return JsonResponse({'message':'success'})



#=====================================================================================================================#

'''
    @name : inviteFriends
    @param: request
    @description: sent invitations to other petjibe users
'''







