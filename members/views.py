from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import IuMaster, IuMasterProfile, CustomUser, UserPersonalProfile, RoleMaster, RoleMapping
from django.db import transaction

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


class company_detais(APIView):
    def get(self, request):
        try:
            company_id = request.query_params.get('id')
            if not company_id:
                return Response({'status':'Error', "message":"please enter id"}, status=status.HTTP_400_BAD_REQUEST)
            
            company = IuMaster.objects.get(id=company_id)
            data = {
                "company_name":company.company_name,
                "domain_name":company.domain_name
            }
            return Response({"message":"details fetched succesfully", "data":data}, status=status.HTTP_200_OK)
        
        except IuMaster.DoesNotExist :
            return Response({"status":"Error", "message":"company does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status':'Error', "message":"something went wrong", "error":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request):
        try:
            transaction.set_autocommit(False)
            
            data = request.data
            company_name = data.get('company_name')
            domain_name = data.get('domain_name')

            IuMaster.objects.create(company_name=company_name, domain_name=domain_name)

            transaction.commit()
            return Response({"status":"success", "message":"details added succesfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            transaction.rollback()
            return Response({'status':'Error', "message":"something went wrong", "error":str(e)}, status=status.HTTP_400_BAD_REQUEST)
class user_details(APIView):
    def post(self, request):
        try:
            raw_data = request.data


        except Exception as e:
            return Response({'status':'Error', "message":str(e)}, status=status.HTTP_400_BAD_REQUEST)
