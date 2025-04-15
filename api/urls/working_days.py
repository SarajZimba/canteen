from django.urls import path

from api.views.working_days import WorkingDaysAPI

urlpatterns = [
    path('post-workingdays', WorkingDaysAPI.as_view(), name="post-workingdays" )
] 
