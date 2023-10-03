import random
from django.shortcuts import render
from .models import IPTable, AllocatedIP
from rest_framework import status, viewsets, request, response, pagination
from .serializers import (
    IPTableSerializerCreate,
    IPTableSerializerGet,
    IPTableSerializerUpdate,
    AllocatedIPSerializerCreate,
    AllocatedIPSerializerGet,
    AllocatedIPSerializerUpdate
)
from django.views.decorators.cache import cache_page
from syoki.permisions import IsAdminUserOrIsAuthenticatedReadOnly
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, IsAuthenticatedOrReadOnly, IsAdmin
from django.utils.decorators import method_decorator
from accounts.models import User
# Create your views here.


class LargePagination(pagination.PageNumberPagination):
    """Class for custom Pagination"""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class IPTableViewSet(viewsets.ModelViewSet):
    queryset = IPTable.objects.all()
    serializer_class = IPTableSerializerCreate
    permission_classes = [IsAdminUserOrIsAuthenticatedReadOnly]
    pagination_class = LargePagination

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @method_decorator(cache_page(60 * 15, key_prefix="IP_LISTS"))
    def list(self, request, *args, **kwargs):
        # TODO: filtering all allocated IPs by range
        serializer = IPTableSerializerGet(self.queryset, many=True)
        return response.Response(serializer.data)

    def retrieve(self, request, pk=None,  *args, **kwargs):
        instance = self.get_object()
        serializer = IPTableSerializerGet(instance)
        return response.Response(serializer.data)

    def update(self, request, ip_address=None, *args, **kwargs):

        instance = IPTable.objects.get(ip=ip_address)

        try:
            if instance.status == "allocated":
                raise ValueError("IP is already allocated")
            resp = instance.release

            return response.Response(resp, status=status.HTTP_200_OK)

        except IPTable.DoesNotExist:
            return response.Response("IP does not exist", status=status.HTTP_404_NOT_FOUND)

        except ValueError as e:
            return response.Response(e, status=status.HTTP_404_NOT_FOUND)

        except Exception:
            return response.Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class AllocatedIPViewSet(viewsets.ModelViewSet):
    queryset = AllocatedIP.objects.all()
    serializer_class = AllocatedIPSerializerCreate
    permission_classes = [IsAdminUserOrIsAuthenticatedReadOnly]

    def list_available(self, request, *args, **kwargs):
        ip = IPTable.objects.filter(status="available")
        serializer = IPTableSerializerGet(ip, many=True)

        return response.Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            customer = User.objects.get(email=request.data['email'])

            # get a random IP
            ip = IPTable.objects.filter(status="available")

            if ip.count() == 0:
                raise ValueError("No available IPs")
            random_ip = random.choice(ip)

            # check if the customer has an allocated IP
            if AllocatedIP.objects.filter(customer=customer).exists():
                raise ValueError("Customer already has an allocated IP")

            # create an instance of AllocatedIP
            inst = AllocatedIP.objects.create(customer=customer, ip=random_ip)

            # update the status of the IP
            ip.status = "allocated"
            ip.save()

            return response.Response(AllocatedIPSerializerGet(inst).data, status=status.HTTP_201_CREATED)

        except serializer.ValidationError as e:
            return response.Response(e, status=status.HTTP_400_BAD_REQUEST)

        except ValueError as e:
            return response.Response(e, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except User.DoesNotExist:
            return response.Response("Customer does not exist", status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:

            return response.Response(status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):

        serializer = AllocatedIPSerializerGet(self.queryset, many=True)
        return response.Response(serializer.data)

    def retrieve(self, request, pk=None,  *args, **kwargs):
        instance = self.get_object()
        serializer = AllocatedIPSerializerGet(instance)
        return response.Response(serializer.data)

    def update(self, request, pk=None, *args, **kwargs):
        partial = True
        instance = self.get_object()
        serializer = AllocatedIPSerializerUpdate(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return response.Response(serializer.data)

    def destroy(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return response.Response(status=status.HTTP_204_NO_CONTENT)
