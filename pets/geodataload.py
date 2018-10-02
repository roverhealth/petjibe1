import django,os,sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "petjibe.settings")
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from django.core.wsgi import get_wsgi_application
os.environ['DJANGO_SETTINGS_MODULE'] = 'petjibe.settings'
application = get_wsgi_application()
from django.conf import settings
#settings.configure()
django.setup()
from pets.models import *
import requests
from itertools import *
import getopt, sys



#======================================================================================================#
'''
    @name: isBadLine
    @param: line
    @output: line
    @see: this method returns line starts with # 
'''
def isBadLine(line):
    if line.startswith(b'#'):
        return line

#======================================================================================================#
'''
    @name: insertCountry_meta
    @param: none
    @output: store data
    @see: this method store country meta data into database table 
'''
def insertCountry_meta():
    try:
        country_obj = Country.objects.all()
        country_obj.delete()
    except:
        pass
    try:
        country_data_dir = os.path.join(settings.BASE_DIR,"geodata")
        country_data_file=country_data_dir+"/geocurr.txt"
        with open(country_data_file, "rb") as fp:
            for line in dropwhile(isBadLine, fp):
                for wd in line.splitlines():
                    word = str(wd.strip(), 'utf-8').split("\t")
                    country_code_2ch = word[0]
                    country_code_3ch = word[1]
                    isd_code = word[12]
                    country_name = word[4]
                    currency_code = word[10]
                    currency_desc = word[11]
                    national_language_code = word[15]
                    try:
                        country_meta = Country(country_name = country_name,
                                                    country_code_2ch = country_code_2ch,
                                                    country_code_3ch = country_code_3ch,
                                                    isd_code = isd_code,
                                                    national_language_code = national_language_code,
                                                    currency_code = currency_code,
                                                    currency_desc = currency_desc,)
                        country_meta.save()
                    except:
                        print("could not insert data into country table")
            
        print("country details added in country table")
    except Exception as e:
        print(str(e))


#======================================================================================================#
'''
    @name: insertState_meta_all
    @param: none
    @output: store data
    @see: this method store state meta data into database table for all countries
'''
def insertState_meta_all():
    try:
        old_country_code=""
        country_meta_obj = Country_meta.objects.all()
        if country_meta_obj:
            for onerec in country_meta_obj:
                countrycode = onerec.country_code_3ch
               
                if len(countrycode)<4:
                    if countrycode == old_country_code:
                        break
                    else:
                        old_country_code = countrycode                       
                        ws = "http://services.groupkt.com/state/get/"
                        ws_url = ws + countrycode + "/all"
                        response = requests.get(ws_url)
                        rjson =  response.json()
                        ajson = rjson['RestResponse']
                        clistjson = ajson['result']
                        for clist in clistjson:
                            state_name = clist['name']
                            state_code = clist['abbr']
                            state_meta = State(country_id=country_meta,
                                        country_code_3ch = countryCode,
                                        state_name = state_name,
                                        state_code = state_code)
                            state_meta.save()
                        
    except Exception as e:
        print(str(e))
        



#======================================================================================================#
'''
    @name: insertState_meta
    @param: countryCode
    @output: store data
    @see: this method store state meta data into database table according to country code
'''
def insertState_meta(countryCode):
    try:
        name_map = {'id' : 'id','country_name': 'country_name', 'country_code_2ch': 'country_code_2ch','isd_code': 'isd_code','national_language_code': 'national_language_code', 'national_language_desc': 'national_language_desc', 'currency_code': 'currency_code', 'currency_desc': 'currency_desc',}
        query = "SELECT * FROM pets_country WHERE country_code_3ch = %s"
        country_meta_obj = Country.objects.raw(query,[countryCode] , translations=name_map)
        for data in country_meta_obj:
            country_meta = data.id
            country_obj = Country.objects.get(pk=country_meta)
        if country_obj:
            ws = "http://services.groupkt.com/state/get/"
            ws_url = ws + countryCode + "/all"
            response = requests.get(ws_url)
            rjson =  response.json()
            ajson = rjson['RestResponse']
            clistjson = ajson['result']
            for clist in clistjson:
                state_name = clist['name']
                state_code = clist['abbr']
                try:
                    state_meta = State(country=country_obj,
                                            country_code_3ch = countryCode,
                                            state_name = state_name,
                                            state_code = state_code)
                    state_meta.save()
                except:
                    print("could not insert data into state table")
        
        print("state details added in state table")
        
    except Exception as e:
        print(str(e))
        
#======================================================================================================#
'''
    @name: insertCity_meta
    @param: countryCode, stateCode
    @output: store data
    @see: this method store city meta data into database table 
''' 
def insertCity_meta(countryCode, stateCode):
    try:
        name_map = {'id' : 'id','country_code_2ch': 'country_code_2ch',}
        query = "SELECT * FROM pets_country WHERE country_code_3ch = %s"
        country_meta_obj = Country.objects.raw(query,[countryCode] , translations=name_map)
        for data in country_meta_obj:
            countryCode_2ch = data.country_code_2ch
        name_map = {'id' : 'id','state_name': 'state_name',}
        query = "SELECT * FROM pets_state WHERE state_code = %s"
        state_meta_obj = State.objects.raw(query,[stateCode] , translations=name_map)
        for data in state_meta_obj:
            state_meta = data.id
            state_obj = State.objects.get(pk=state_meta)
        if state_obj:
            state_data_dir = os.path.join(settings.BASE_DIR,"geodata")
            state_data_file=state_data_dir+"/US_cities.txt"
            with open(state_data_file, "rb") as fp:
                for line in fp.readlines():
                    ln = str(line.strip(), 'utf-8').split('\t')
                    print(ln)
                    if ln[0] == countryCode_2ch:
                        zip_code = ln[1]
                        city_name = ln[2]
                        lat = ln[9]
                        long = ln[10]
                        try:
                            city_meta = City(state=state_obj,
                                                  country_code_3ch = countryCode,
                                                  state_code = stateCode,
                                                  zip_code = zip_code,
                                                  city_name = city_name,
                                                  lat = lat,
                                                  long = long)
                            city_meta.save()
                        except:
                            print("could not insert data into city table")
    
    except Exception as e:
        print(str(e))        

#=========================================================================================================#        
'''
    @name: geodataload
    @param: argv
    @output: store data
    @see: this method main, stores country, state and city meta data according to command 
'''    

def main(argv):
    cn = None
    st = None
    try:
        opt, args = getopt.getopt(argv, "hdc:s:", ["help", "data", "country=", "state="])
    except getopt.GetoptError:
        print("python metadatastore.py -c <country name> -s <state name> | -h <help> | -d <data> ")
        sys.exit(0)
        
    for o,v in opt :
        if o == '-h' or o == '--help':
            print("python metadatastore.py -c <country name> -s <state name> | -h <help> | -d <data> ")
        elif o == '-d' or o == '--data':
            #======= insert all country data
            insertCountry_meta()
        elif o in ('-c', '--country'):
            cn = v
        elif o in ('-s', '--state'):
            st = v
        else:
            print("value error. Please enter correct command")
            
    try:
        if cn is not None:
            if st is not None:
                #call city_meta
                insertCity_meta(cn, st)
            else:
                #call state_meta
                insertState_meta(cn)
        else:
            #call country_meta
            #insertCountry_meta()
            pass
        
#         if st is not None:
#             #call city_meta
#             insertCity_meta(cn, st)
#         else:
#             pass
            
    except Exception as e:
        print ("error")
        print(e)
    
'''
    @see : call from command line
'''
if __name__ == "__main__":
    main(sys.argv[1:])
    
    