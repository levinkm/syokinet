from django.urls import path
from views import IPTableViewSet,AllocatedIPViewSet

urlpatterns = [
    path('ip/', IPTableViewSet.as_view({'get': 'list'})),
    path('ip/create', IPTableViewSet.as_view({'post': 'create'})),
    path('ip/release/{ip_address}', IPTableViewSet.as_view({'put': 'update'})),
    path('ip/avilable/', IPTableViewSet.as_view({'get': 'list_available'})),
    path('ip/delete/{ip_address}', IPTableViewSet.as_view({'delete': 'destroy'})),
    path('ip/allocated/', AllocatedIPViewSet.as_view({'get': 'list'})),
    path('ip/allocate', AllocatedIPViewSet.as_view({'post': 'create'})),
    # path('ip/release/{ip_address}', AllocatedIPViewSet.as_view({'post': 'destroy'})),
]