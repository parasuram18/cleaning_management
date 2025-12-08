import time
from django.http import JsonResponse
from rest_framework.decorators import permission_classes, APIView
from rest_framework.permissions import AllowAny
from django.shortcuts import render
import sentry_sdk

from members.models import BlockMaster, CustomUser, RoleMapping

# Create your views here.




def sentry_page(request):
    return render(request, 'sentry.html')


@permission_classes([AllowAny])
class sentry_operations(APIView):
    def capture_exc(self, type):
        if type=='1':
            user_obj = CustomUser.objects.filter(iu_id='1', is_active=True)
            return 1/0
        else:
            data =''
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
        
# @login_required("login/")
def dashboard(request):
    data = {}
    member = RoleMapping.objects.filter(role__role='ward_member', is_active=True)
    users = [{'id':role.user.id,
            'name':role.user.get_user_name().title()} for role in member]
    data['users'] = users
    data['blocks'] = BlockMaster.objects.filter(is_active=True)
    data['room_name'] = 'overall_task_dashboard'
    return render(request, 'dashboard.html', context=data)

def task_details_dashboard(request):
    return render(request, 'taskpage.html')



from django.apps import apps
from collections import defaultdict
import pandas as pd

def get_all_models():
    models_by_app = {}
    overall_models = apps.get_models()
    # for model in overall_models:
    #     try:
    #         models_by_app[model._meta.app_label].append(model.__name__)
    #     except:
    #         models_by_app[model._meta.app_label] = [model.__name__]

    overall_models = {
        model._meta.app_label : [m.__name__ for m in overall_models if m._meta.app_label == model._meta.app_label]
        for model in overall_models
        }

    return overall_models

def file_upload_view(request):
    models = get_all_models()

    context = {"models_by_app":models}
    if request.method == 'POST':
        data = request.POST
        file = request.FILES['file']
        model_data = data['model']

        app_label, model_name = model_data.split('.')

        target_model = apps.get_model(app_label, model_name)
        field_names = [field.name for field in target_model._meta.fields if field.name != 'id']

        print(file)
        data_frame = pd.read_excel(file)
        file_columns = [column.lower() for column in data_frame.columns]

        if set(field_names) != set(file_columns):
            context['message'] = f'"{model_name}" Fields and "{file}" Columns are Not matched'

        else:
            context['message'] = 'data uploaded successfully'

    return render(request, 'file_form.html', context)