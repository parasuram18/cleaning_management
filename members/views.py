from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import IuMaster, IuMasterProfile, CustomUser, UserPersonalProfile, RoleMaster, RoleMapping
from django.db import transaction
from django.conf import settings
from .validators import validate_phone, is_valid_password

@api_view(['POST'])
def add_data(request):
    roles = ['admin','manager','ward_member']
    blocks = ['A','B','C']
    floore = [1,2,3,4]
    rooms = [1,2,3,4,5,6,7,8,9,10]
    sessions = ['morning','afternoon','evening','night']
    try:
        transaction.set_autocommit(False)

        # for data in roles:
        #     role_master.objects.create(role=data)
        # print('done')
        # for data in blocks:
        #     block_master.objects.create(block_name=data)
        # for data in floore:
        #     floor_master.objects.create(floor_number=data)
        # for data in rooms:
        #     room_master.objects.create(room_number=data)
        # for data in sessions:
        #     session_master.objects.create(session=data)

        transaction.commit()
        return Response({'status':'success', "message":"data added successfully"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        transaction.rollback()
        return Response({'status':'Error', "message":str(e)}, status=status.HTTP_400_BAD_REQUEST)


class iu_detais(APIView):
    # to get registered company details
    def get(self, request):
        try:
            company_id = request.query_params.get('id')
            # if request is empty raise an exception
            if not company_id:
                return Response({'status':'warning', "message":"Please enter id"}, status=status.HTTP_200_OK)
            # get and return company details from IuMaster table
            company = IuMaster.objects.get(id=company_id)
            data = {
                "company_name":company.company_name,
                "domain_name":company.domain_name
            }
            return Response({"message":"details fetched succesfully", "data":data}, status=status.HTTP_200_OK)
        # if company id not exists in IuMaster raise an exception    
        except IuMaster.DoesNotExist :
            return Response({"status":"warning", "message":"company does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status':'Error', "message":"something went wrong", "error":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request):
        try:
            # get data from POST request body
            data = request.data
            company_name = data.get('company_name')
            domain_name = data.get('domain_name')
            address = data.get('address')
            phone = data.get('phone')
            gst_number = data.get('gst_number')
            registration_date = data.get('registration_date')
            # if request is empty raise an exception
            if not company_name or not domain_name:
                return Response({"status":"warning", "message":"Please enter all the details"}, status=status.HTTP_200_OK)
            # if company domain already exists raise an exception
            if IuMaster.objects.filter(domain_name=domain_name).exists():
                return Response({"status":"error", "message":"Domain name already exists"}, status=status.HTTP_200_OK)
            
            transaction.set_autocommit(False)
            # add company details in IuMaster and IuMasterProfile tables
            iu_obj = IuMaster.objects.create(company_name=company_name, domain_name=domain_name)
            IuMasterProfile.objects.create(address=address, phone=phone, gst_number=gst_number, registration_date=registration_date, iu_master=iu_obj)
            transaction.commit()
            return Response({"status":"success", "message":"details added succesfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            transaction.rollback()
            return Response({'status':'Error', "message":"something went wrong", "error":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request):
        try:
            # get data from PUT request body
            data = request.data
            company_id = data.get('id')
            if not company_id:
                return Response({"status":"warning", "message":"enter company id"}, status=status.HTTP_200_OK)
            company_name = data.get('company_name')
            domain_name = data.get('domain_name')
            address = data.get('address')
            phone = data.get('phone')
            gst_number = data.get('gst_number')
            registration_date = data.get('registration_date')

            transaction.set_autocommit(False)
            iu_obj = IuMaster.objects.get(id=company_id)
            iu_obj.company_name = company_name
            iu_obj.domain_name = domain_name
            iu_obj.save()

            iu_profile_obj = IuMasterProfile.objects.get(iu_master=iu_obj)
            iu_profile_obj.address = address,
            iu_profile_obj.phone = phone,
            iu_profile_obj.gst_number = gst_number,
            iu_profile_obj.registration_date = registration_date
            iu_profile_obj.save()
                
            transaction.commit()
            return Response({"status":"success", "message":"details modified succesfully"}, status=status.HTTP_200_OK)
        
        except IuMaster.DoesNotExist:
            transaction.rollback()
            return Response({"status":"warning", "message":"company does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            transaction.rollback()
            return Response({'status':'Error', "message":"something went wrong", "error":str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            id = request.data.get('id')
            if not id:
                return Response({"status":"warning", "message":"enter company id"}, status=status.HTTP_200_OK)
            transaction.set_autocommit(False)
            iu_obj = IuMaster.objects.get(id=id)
            iu_obj.is_active = False
            iu_obj.save()

            iu_prfile_obj = IuMasterProfile.objects.get(iu_master=iu_obj)
            iu_prfile_obj.is_active = False
            iu_prfile_obj.save()

            transaction.commit()
            return Response({"status":"success", "message":"data deleted succesfully"}, status=status.HTTP_200_OK)
        except IuMaster.DoesNotExist:
            transaction.rollback()
            return Response({"status":"warning", "message":"company does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            transaction.rollback()

            return Response({'status':'Error', "message":"something went wrong", "error":str(e)}, status=status.HTTP_400_BAD_REQUEST)

class user_details(APIView):
    def post(self, request):
        try:
            user_data = request.data
            first_name = user_data.get('first_name')
            last_name = user_data.get('last_name')
            username = user_data.get('username')
            phone = user_data.get('phonenumber')
            email = user_data.get('email')
            password= user_data.get('password')
            age = user_data.get('age')
            gender = user_data.get('gender')
            is_married = user_data.get('is_married')
            address = user_data.get('address')

            phonenumber = validate_phone(phone)
            if not phonenumber:
                return Response({"status":"warning", "message":"Enter a valid phone number"}, status=status.HTTP_200_OK)
            if CustomUser.objects.filter(phonenumber=phonenumber).exists():
                return Response({"status":"warning", "message":"Phone number already exists"}, status=status.HTTP_200_OK)

            password = is_valid_password(password)
            if not password:
                return Response({"status":"warning", "message": "Enter a valid password (e.g. A@strong123)"}, status=status.HTTP_200_OK)

            transaction.set_autocommit(False)
            user_obj = CustomUser(first_name=first_name, last_name=last_name, username=username,
                                           phonenumber=phonenumber, email=email)
            user_obj.set_password(password)
            user_obj.save()

            personal_obj = UserPersonalProfile(user=user_obj, age=age, gender=gender,
                                               is_married=is_married, address=address)
            personal_obj.save()
            
            transaction.commit()
            return Response({"status":"success", "message":"user created succesfully", "data":user_data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            transaction.rollback()
            return Response({'status':'Error', "message":str(e)}, status=status.HTTP_400_BAD_REQUEST)
