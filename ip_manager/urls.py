from django.urls import path
from .views import IPTableViewSet, AllocatedIPViewSet

urlpatterns = [
    path(
        "",
        IPTableViewSet.as_view({"get": "list"}),
    ),
    path("create", IPTableViewSet.as_view({"post": "create"})),
    path(
        "release/<ip_address>",
        IPTableViewSet.as_view({"put": "release"}),
    ),
    path("avilable/", IPTableViewSet.as_view({"get": "list_available"})),
    path(
        "delete/<ip_address>",
        IPTableViewSet.as_view({"delete": "destroy"}),
    ),
    path(
        "allocated",
        AllocatedIPViewSet.as_view({"get": "list"}),
    ),
    path("allocate", AllocatedIPViewSet.as_view({"post": "create"})),
    # path('ip/release/{ip_address}', AllocatedIPViewSet.as_view({'post': 'destroy'})),
]
