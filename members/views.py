from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
import sentry_sdk.logger
from members.models import IuMaster, IuMasterProfile, CustomUser, UserPersonalProfile, RoleMaster, RoleMapping, BlockMaster, RoomMaster, FloorMaster, WorkSchedules
from django.db import transaction
from django.conf import settings
from members.helpers import get_iu_obj, get_role_from_token
from .validators import validate_phone, is_strong_password
from django.contrib.auth import authenticate, login
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from members import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from members.jwt import custom_payload_handler, custom_jwt_encode_handler
import time
import sentry_sdk
import requests


@api_view(['POST'])
def add_data(request):
    roles = ['admin','manager','ward_member']
    blocks = ['Block-A','Block-B','Block-C']
    floore = ["ground-floor","first-floor","second-floore"]
    rooms = [1,2,3,4,5]
    sessions = ['morning','afternoon','evening','night']
    try:
        iu_id = get_iu_obj(request)
        role = get_role_from_token(request)
        if role !='manager':
            return Response({"status":"error", "message":"you are not allowed to perform this action"}, status=status.HTTP_401_UNAUTHORIZED)
        transaction.set_autocommit(False)

        # for data in blocks:
        #     BlockMaster.objects.create(block_name=data, iu_id=iu_id, created_by=request.user.id)

        # blk_obj = BlockMaster.objects.all()
        # for a in blk_obj:
        #     for flr in floore:
        #         FloorMaster.objects.create(floor_number=flr, iu_id=iu_id, block=a, created_by=request.user.id)

        # flr_obj = FloorMaster.objects.all()
        # for flr in flr_obj:
        #     for room in rooms:
        #         RoomMaster.objects.create(room_number=room, floor=flr, iu_id=iu_id, created_by=request.user.id)

        transaction.commit()
        return Response({'status':'success', "message":"data added successfully"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        transaction.rollback()
        return Response({'status':'Error', "message":str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = serializers.CustomTokenObtainPairSerializer

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

@permission_classes([AllowAny, ])
class RegisterApi(APIView):
    def post(self, request):
        try:
            user_role = get_role_from_token(request)

            iu_obj = get_iu_obj(request)
            if not iu_obj:
                return Response({"status":"error", "message":"Unauthorized domain"}, status=status.HTTP_401_UNAUTHORIZED)
            
            user_data = request.data
            first_name = user_data.get('first_name')
            last_name = user_data.get('last_name')
            phone = user_data.get('phonenumber')
            email = user_data.get('email')
            role = user_data.get('role', 'ward_member')
            password= user_data.get('password')
            age = user_data.get('age')
            gender = user_data.get('gender')
            is_married = user_data.get('is_married')
            address = user_data.get('address')

            if user_role in ('manager', 'ward_member', None) and role in ('manager', 'admin'):
                return Response({"status":"error", "message":"you are not allowed to perform this action"}, status=status.HTTP_401_UNAUTHORIZED)

            phonenumber = validate_phone(phone)
            if not phonenumber:
                return Response({"status":"warning", "message":"Enter a valid phone number"}, status=status.HTTP_200_OK)
            if CustomUser.objects.filter(phonenumber=phonenumber, is_active=True).exists():
                return Response({"status":"warning", "message":"Phone number already exists"}, status=status.HTTP_200_OK)

            password = is_strong_password(password)
            if not password:
                return Response({"status":"warning", "message": "Enter a valid password (e.g. A@strong123)"}, status=status.HTTP_200_OK)

            role_obj = RoleMaster.objects.get(role=role)
            
            transaction.set_autocommit(False)
            user_obj = CustomUser(first_name=first_name, last_name=last_name,
                                phonenumber=phonenumber, email=email, iu_id = iu_obj)
            user_obj.set_password(password)
            user_obj.save()

            map_role = RoleMapping.objects.create(user=user_obj, role=role_obj, iu_id = iu_obj)
            map_role.save()

            personal_obj = UserPersonalProfile(user=user_obj, age=age, gender=gender,
                                               is_married=is_married, address=address, created_by=request.user.id)
            personal_obj.save()
            
            transaction.commit()
            return Response({"status":"success", "message":"user created succesfully", "user_id":user_obj.id}, status=status.HTTP_201_CREATED)

        except RoleMaster.DoesNotExist:
            transaction.rollback()
            return Response({"status":"warning", "message":"Role does not exist"}, status=status.HTTP_200_OK)
        except Exception as e:
            transaction.rollback()
            return Response({'status':'Error', "message":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
@permission_classes([AllowAny, ])
class LoginApi(APIView):

    def post(self, request):
        try:
            data = request.data
            phonenumber = data.get('phonenumber')
            password = data.get('password')
            # check thirdparty api usage for sentry
            # geocodingapi = "https://geocoding-api.open-meteo.com/v1/search?name=tenkasi&count=1"
            # location = requests.get(geocodingapi,timeout=10).json()


            user_obj = CustomUser.objects.get(phonenumber=phonenumber)
            if not user_obj.is_active:
                return Response({'status':"warning", "message":"user not found...!"}, status=status.HTTP_400_BAD_REQUEST)

            is_valid = user_obj.check_password(password)
            
            if not is_valid:
                return Response({"status":"error", "message":"Incorret password"}, status=status.HTTP_400_BAD_REQUEST)
            payload = custom_payload_handler(user_obj)
            token = custom_jwt_encode_handler(payload)

            return Response({"status":"success", "message":"user login succesfully", "token":token}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"status":"error", "message":"Incorret phonenumber"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            transaction.rollback()
            sentry_sdk.capture_exception(e)
            return Response({"status":"error", "message":str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserDetailsApi(APIView):

    def get(self, request):
        try:
            iu_obj = get_iu_obj(request)
            if not iu_obj:
                return Response({"status":"error", "message":"Unauthorized domain"}, status=status.HTTP_401_UNAUTHORIZED)
            
            role = get_role_from_token(request)

            if role == 'ward_member':
                user_id = request.user.id
                user_obj = CustomUser.objects.get(id=user_id, iu_id=iu_obj, is_active=True)
                user_personal_obj = UserPersonalProfile.objects.get(user=user_obj)
                user_details = {
                    'first_name':user_obj.first_name,
                    'last_name':user_obj.last_name,
                    'Age':user_personal_obj.age,
                    'Gender':user_personal_obj.gender,
                    'Is_married':user_personal_obj.is_married,
                    'Address':user_personal_obj.address,
                    'Email':user_obj.email,
                    'Phone number':user_obj.phonenumber
                }
            else:
                user_id = request.query_params.get('id')

                if user_id:
                    user_obj = CustomUser.objects.get(id=user_id, iu_id=iu_obj, is_active=True)
                    user_personal_obj = UserPersonalProfile.objects.get(user=user_obj)
                    user_details = {
                        'first_name':user_obj.first_name,
                        'last_name':user_obj.last_name,
                        'Age':user_personal_obj.age,
                        'Gender':user_personal_obj.gender,
                        'Is_married':user_personal_obj.is_married,
                        'Address':user_personal_obj.address,
                        'Email':user_obj.email,
                        'Phone number':user_obj.phonenumber
                    }
                else:
                    user_details = []
                    user_list = CustomUser.objects.filter(is_active=True)
                    for user_obj in user_list:
                        user_personal_obj = UserPersonalProfile.objects.get(user=user_obj)
                        user_details.append({
                            'first_name':user_obj.first_name,
                            'last_name':user_obj.last_name,
                            'Age':user_personal_obj.age,
                            'Gender':user_personal_obj.gender,
                            'Is_married':user_personal_obj.is_married,
                            'Address':user_personal_obj.address,
                            'Email':user_obj.email,
                            'Phone number':user_obj.phonenumber
                        })
            return Response({"status":"success", "message":"user details fetched succesfully", "data":user_details}, status=status.HTTP_200_OK)
        
        except CustomUser.DoesNotExist:
            return Response({"status":"error", "message":"user profile not found/ enter the valid user id"}, status=status.HTTP_400_BAD_REQUEST)
        except UserPersonalProfile.DoesNotExist:
            return Response({"status":"error", "message":"user personal details not found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status":"error", "message":"something went wrong", "error":str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request):
        try:

            iu_obj = get_iu_obj(request)
            if not iu_obj:
                return Response({"status":"error", "message":"Unauthorized domain"}, status=status.HTTP_401_UNAUTHORIZED)
            
            user_data = request.data
            id = user_data.get('id')
            if not id:
                return Response({"status":"warning", "message":"enter user id"}, status=status.HTTP_200_OK)
            
            role = get_role_from_token(request)
            if role == 'ward_member' and id !=request.user.id:
                return Response({"status":"error", "message":"you are not allowed to perform this action"}, status=status.HTTP_401_UNAUTHORIZED)
            
            first_name = user_data.get('first_name')
            last_name = user_data.get('last_name')
            phone = user_data.get('phonenumber')
            email = user_data.get('email')
            password= user_data.get('password')
            age = user_data.get('age')
            gender = user_data.get('gender')
            is_married = user_data.get('is_married')
            address = user_data.get('address')

            user_obj = CustomUser.objects.get(id=id, iu_id=iu_obj, is_active=True)
            personal_obj = UserPersonalProfile.objects.get(user=user_obj)

            if not user_obj.is_active:
                return Response({"status":"error", "message":"user profile is inactive"}, status=status.HTTP_400_BAD_REQUEST)

            phonenumber = validate_phone(phone)
            if not phonenumber:
                return Response({"status":"warning", "message":"Enter a valid phone number"}, status=status.HTTP_200_OK)
            if CustomUser.objects.filter(phonenumber=phonenumber, is_active=True).exclude(id=user_obj.id).exists():
                return Response({"status":"warning", "message":"Phone number already exists"}, status=status.HTTP_200_OK)

            password = is_strong_password(password)
            if not password:
                return Response({"status":"warning", "message": "Enter a valid password (e.g. A@strong123)"}, status=status.HTTP_200_OK)

            transaction.set_autocommit(False)
            user_obj.first_name=first_name
            user_obj.last_name=last_name
            user_obj.phonenumber=phonenumber
            user_obj.email=email
            user_obj.iu_id = iu_obj
            user_obj.set_password(password)
            user_obj.modified_by=request.user.id
            user_obj.save()

            personal_obj.user=user_obj
            personal_obj.age=age
            personal_obj.gender=gender
            personal_obj.is_married=is_married
            personal_obj.address=address
            personal_obj.modified_by=request.user.id
            personal_obj.save()

            transaction.commit()
            return Response({"status":"success", "message":"user data modified succesfully"}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            transaction.rollback()
            return Response({"status":"error", "message":"user not found..!"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            transaction.rollback()
            return Response({"status":"error", "message":"something went wrong", "error":str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        try:
            iu_obj = get_iu_obj(request)
            if not iu_obj:
                return Response({"status":"error", "message":"Unauthorized domain"}, status=status.HTTP_401_UNAUTHORIZED)
            
            id = request.data.get('id')
            role = get_role_from_token(request)
            if role == 'ward_member' and id !=request.user.id:
                return Response({"status":"error", "message":"you are not allowed to perform this action"}, status=status.HTTP_401_UNAUTHORIZED)

            if not id:
                return Response({"status":"warning", "message":"enter user id"}, status=status.HTTP_200_OK)

            user_obj = CustomUser.objects.get(id=id, iu_id=iu_obj, is_active=True)
            
            personal_obj = UserPersonalProfile.objects.get(user=user_obj)

            transaction.set_autocommit(False)
            user_obj.is_active = False
            user_obj.modified_by = request.user.id
            user_obj.save()

            personal_obj.is_active = False
            personal_obj.modified_by = request.user.id
            personal_obj.save()

            RoleMapping.objects.filter(user=user_obj).update(is_active=False)

            transaction.commit()
            return Response({"status":"success", "message":"user deleted succesfully"}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            transaction.rollback()
            return Response({"status":"error", "message":"user not found..!"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            transaction.rollback()
            return Response({"status":"error", "message":"something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

class BlockDetailsApi(APIView):
    def get(self, request):
        try:
            iu_obj = get_iu_obj(request)
            if not iu_obj:
                return Response({"status":"error", "message":"Unauthorized domain"}, status=status.HTTP_401_UNAUTHORIZED)
            
            role = get_role_from_token(request)
            if role == 'ward_member':
                return Response({"status":"error", "message":"you are not allowed to perform this action"}, status=status.HTTP_401_UNAUTHORIZED)

            block_name = request.query_params.get('block')
            floor_number = request.query_params.get('floor')

            if block_name and floor_number:
                block_obj = BlockMaster.objects.get(block_name=block_name, is_active=True)
                floor_obj = FloorMaster.objects.get(floor_number=floor_number, block=block_obj, is_active=True)
                room_list = floor_obj.room.filter(is_active=True)
                room_details = []
                for room in room_list:
                    data = {
                        "room_id":room.id,
                        "room_number":room.room_number,
                        "floor_name":room.floor.floor_number,
                        "block_name":room.floor.block.block_name
                    }
                    room_details.append(data)
                # room_numbers = [room_obj.room_number for room_obj in room_list]
                return Response({"status":"success", "message":"data collected", "data":room_details}, status=status.HTTP_200_OK)
            elif block_name:
                block_obj = BlockMaster.objects.get(block_name=block_name, is_active=True)
                floor_list = block_obj.floor.filter(is_active=True)
                floor_details = []
                for floor in floor_list:
                    data = {
                        "company_name":floor.iu_id.company_name,
                        "floor_id":floor.id,
                        "block_name":floor.block.block_name,
                        "floor_name":floor.floor_number
                    }
                    floor_details.append(data)
                # floor_numbers = [floor_obj.floor_number for floor_obj in floor_list]
                return Response({"status":"success", "message":"data collected", "data":floor_details}, status=status.HTTP_200_OK)
            else:
                block_list = BlockMaster.objects.filter(is_active=True)
                block_details = []
                for block in block_list:
                    data = {
                        "company_name":block.iu_id.company_name,
                        "block_name":block.block_name,
                        "block_id":block.id
                    }
                    block_details.append(data)

                # block_names = [block_obj.block_name for block_obj in block_list]
                return Response({"status":"success", "message":"data collected", "data":block_details}, status=status.HTTP_200_OK)

        except BlockMaster.DoesNotExist:
            return Response({"status":"error", "message":"Block name not registered"}, status=status.HTTP_400_BAD_REQUEST)
        except FloorMaster.DoesNotExist:
            return Response({"status":"error", "message":"Floor number not registered"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status":"error", "message":"something went wrong", "error":str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TaskManagementApi(APIView):
    def get(self, request):
        try:
            iu_obj = get_iu_obj(request)
            if not iu_obj:
                return Response({"status":"error", "message":"Unauthorized domain"}, status=status.HTTP_401_UNAUTHORIZED)

            role = get_role_from_token(request)
            if role=='ward_member':
                user_id = request.user.id
                task_details = []
                user_obj = CustomUser.objects.get(id=user_id, iu_id=iu_obj, is_active=True)
                task_list = WorkSchedules.objects.filter(ward_member=user_obj, is_active=True)
                for task_obj in task_list:
                        task_details.append({
                            "task_id":task_obj.id,
                            "asigned_to":task_obj.ward_member.first_name,
                            "block_name":task_obj.room.floor.block.block_name,
                            "floor_name":task_obj.room.floor.floor_number,
                            "room_number":task_obj.room.room_number,
                            "date":task_obj.date,
                            "session":task_obj.session
                        })
            else:
                user_id = request.query_params.get("user_id")

                if user_id:
                    task_details = []
                    user_obj = CustomUser.objects.get(id=user_id, iu_id=iu_obj, is_active=True)
                    task_list = WorkSchedules.objects.filter(ward_member=user_obj, is_active=True)
                    for task_obj in task_list:
                            task_details.append({
                                "task_id":task_obj.id,
                                "asigned_to":task_obj.ward_member.first_name,
                                "block_name":task_obj.room.floor.block.block_name,
                                "floor_name":task_obj.room.floor.floor_number,
                                "room_number":task_obj.room.room_number,
                                "date":task_obj.date,
                                "session":task_obj.session
                            })                
                else:
                    task_list = WorkSchedules.objects.filter(is_active=True)
                    task_details = []
                    for task_obj in task_list:
                            task_details.append({
                                "task_id":task_obj.id,
                                "asigned_to":task_obj.ward_member.first_name,
                                "block_name":task_obj.room.floor.block.block_name,
                                "floor_name":task_obj.room.floor.floor_number,
                                "room_number":task_obj.room.room_number,
                                "date":task_obj.date,
                                "session":task_obj.session
                            })                

            return Response({"status":"success", "message":"task details fetched successfully", "task_details":task_details}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"status":"error", "message":"enter a valid user id / inactive user"}, status=status.HTTP_404_NOT_FOUND)
        except WorkSchedules.DoesNotExist:
            return Response({"status":"error", "message":"enter a valid task id / deleted task"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status":"error", "message":"something went wrong", "error":str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        try:
            iu_obj = get_iu_obj(request)
            if not iu_obj:
                return Response({"status":"error", "message":"Unauthorized domain"}, status=status.HTTP_401_UNAUTHORIZED)
            
            role = get_role_from_token(request)
            if role != 'manager':
                return Response({"status":"error", "message":"you are not allowed to perform this action"}, status=status.HTTP_401_UNAUTHORIZED)

            data = request.data
            user_id = data.get('user_id')
            block_name = data.get('block_name')
            floor_number = data.get('floor_number')
            room_number = data.get('room_number')
            date = data.get('date')
            session = data.get('session')
            user_obj = CustomUser.objects.get(id=user_id, iu_id=iu_obj, is_active=True)
            userrole = RoleMapping.objects.get(user=user_obj).role.role
            if userrole != 'ward_member':
                return Response({"status":"error", "message":"assign tasks to ward members only"}, status=status.HTTP_400_BAD_REQUEST)
            block_obj = BlockMaster.objects.get(block_name=block_name, is_active=True, iu_id=iu_obj)
            floor_obj = FloorMaster.objects.get(floor_number=floor_number, block=block_obj, is_active=True, iu_id=iu_obj)
            room_obj = RoomMaster.objects.get(room_number=room_number, floor=floor_obj, is_active=True, iu_id=iu_obj )
            # if task is already assigned
            is_assigned = WorkSchedules.objects.filter(session=session, date=date,room=room_obj, is_active=True).exists()
            if is_assigned:
                return Response({"status":"error", "message":"A worker has already been assigned to this session"})

            task = WorkSchedules.objects.create(ward_member=user_obj, room=room_obj, date=date,
                                                session=session, iu_id=iu_obj, created_by=request.user.id)
            return Response({"status":"success", "message":f"Task assigned to {user_obj.first_name}", "task_id":task.id})
        
        except CustomUser.DoesNotExist:
            return Response({"status":"error", "message":"user not found..!"}, status=status.HTTP_404_NOT_FOUND)
        except BlockMaster.DoesNotExist:
            return Response({"status":"error", "message":"Block not registered..!"}, status=status.HTTP_404_NOT_FOUND)
        except FloorMaster.DoesNotExist:
            return Response({"status":"error", "message":"Floor does not registered..!"}, status=status.HTTP_404_NOT_FOUND)
        except RoomMaster.DoesNotExist:
            return Response({"status":"error", "message":"Room not registered..!"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status":"error", "message":"something went wrong", "error":str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        try:
            iu_obj = get_iu_obj(request)
            if not iu_obj:
                return Response({"status":"error", "message":"Unauthorized domain"}, status=status.HTTP_401_UNAUTHORIZED)
            
            role = get_role_from_token(request)
            if role != 'manager':
                return Response({"status":"error", "message":"you are not allowed to perform this action"}, status=status.HTTP_401_UNAUTHORIZED)

            data = request.data
            task_id = data.get('task_id')
            user_id = data.get('user_id')
            block_name = data.get('block_name')
            floor_number = data.get('floor_number')
            room_number = data.get('room_number')
            date = data.get('date')
            session = data.get('session')
            task_obj = WorkSchedules.objects.get(id=task_id, is_active=True, iu_id=iu_obj)
            user_obj = CustomUser.objects.get(id=user_id, iu_id=iu_obj, is_active=True)
            userrole = RoleMapping.objects.get(user=user_obj).role.role
            if userrole != 'ward_member':
                return Response({"status":"error", "message":"assign tasks to ward members only"}, status=status.HTTP_400_BAD_REQUEST)
            block_obj = BlockMaster.objects.get(block_name=block_name, is_active=True, iu_id=iu_obj)
            floor_obj = FloorMaster.objects.get(floor_number=floor_number, block=block_obj, is_active=True, iu_id=iu_obj)
            room_obj = RoomMaster.objects.get(room_number=room_number, floor=floor_obj, is_active=True, iu_id=iu_obj )
            # try to assign a task that is already assigned to another user
            is_assigned = WorkSchedules.objects.filter(session=session, date=date,room=room_obj, is_active=True).exclude(id=task_obj.id).exists()
            if is_assigned:
                return Response({"status":"error", "message":"A worker has already been assigned to this session"})

            task_obj.ward_member = user_obj
            task_obj.room = room_obj
            task_obj.date = date
            task_obj.session = session
            task_obj.iu_id = iu_obj
            task_obj.modified_by = request.user.id
            task_obj.save()
            return Response({"status":"success", "message":"Task modified succesfully"})
        except WorkSchedules.DoesNotExist:
            return Response({"status":"error", "message":"enter a valid task id / task completed / deleted"}, status=status.HTTP_404_NOT_FOUND)
        except CustomUser.DoesNotExist:
            return Response({"status":"error", "message":"enter a valid user id"}, status=status.HTTP_404_NOT_FOUND)
        except BlockMaster.DoesNotExist:
            return Response({"status":"error", "message":"enter a valid block id"}, status=status.HTTP_404_NOT_FOUND)
        except FloorMaster.DoesNotExist:
            return Response({"status":"error", "message":"enter a valid floor id"}, status=status.HTTP_404_NOT_FOUND)
        except RoomMaster.DoesNotExist:
            return Response({"status":"error", "message":"enter a valid room id"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status":"error", "message":"something went wrong", "error":str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            iu_obj = get_iu_obj(request)
            if not iu_obj:
                return Response({"status":"error", "message":"Unauthorized domain"}, status=status.HTTP_401_UNAUTHORIZED)
            
            role = get_role_from_token(request)
            if role != 'manager':
                return Response({"status":"error", "message":"you are not allowed to perform this action"}, status=status.HTTP_401_UNAUTHORIZED)
        
            task_id = request.data.get('task_id')
            task_obj = WorkSchedules.objects.get(id=task_id, is_active=True, iu_id=iu_obj)

            task_obj.is_active = False
            task_obj.modified_by = request.user.id
            task_obj.save()
            return Response({"status":"success", "message":"task succesfully deleted"}, status=status.HTTP_200_OK)
        except WorkSchedules.DoesNotExist:
            return Response({"status":"error", "message":"invalid task id / task already deleted"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status":"error", "message":"something went wrong", "error":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

def index(request):
    return render(request, 'index.html')
@permission_classes([AllowAny])
class sentry_operations(APIView):
    def capture_exc(self, type):
        if type=='1':
            user_obj = CustomUser.objects.filter(iu_id='1', is_active=True)
            return 1/0
        else:
            return data
    
    def log(self):
        sentry_sdk.capture_message(message="entering logging function", level="info")
        return True
    def profiling(self):
        data = []
        for i in range(5):
            time.sleep(i)
            data.append(i)
        return data

    def get(self,request, type):
        try:
            # user = request.user.get('id', 'Parasu')
            sentry_sdk.add_breadcrumb(
                category='user-action',
                message='User clicked the test button',
                level='info',
                data={'requested_by':"parasu"}
            )
            if type=='log':
                res = self.log()
            elif type=='time':
                res = self.profiling()
            else:
                res = self.capture_exc(str(type))
            if CustomUser.objects.filter(phonenumber="+919345769198", is_active=True).exists():
                objs = CustomUser.objects.filter(is_active=True)
            return JsonResponse({"status":"success", "data":res})
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return JsonResponse({"status":"Error", "message":str(e)})
        