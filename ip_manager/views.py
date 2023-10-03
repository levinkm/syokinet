import random
from django.shortcuts import render
from .models import IPTable, AllocatedIP
from rest_framework import status, viewsets, request, response, pagination
from .serializers import (
    AllocatedIPSerializerDetails,
    IPTableSerializerCreate,
    IPTableSerializerGet,
    IPTableSerializerUpdate,
    AllocatedIPSerializerCreate,
    AlllocatedIPSerializerGet,
    AllocatedIPSerializerUpdate,
)
from django.views.decorators.cache import cache_page
from syoki.permisions import IsAdminUserOrIsAuthenticatedReadOnly
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
)
from django.utils.decorators import method_decorator
from accounts.models import User
from django.core.exceptions import ValidationError
from .filters import filter_ip_range
from django.db.models import Q

# Create your views here.


class LargePagination(pagination.PageNumberPagination):
    """Class for custom Pagination"""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class IPTableViewSet(viewsets.ModelViewSet):
    queryset = IPTable.objects.all()
    # serializer_class = IPTableSerializerCreate
    permission_classes = [IsAdminUserOrIsAuthenticatedReadOnly]
    pagination_class = LargePagination

    def get_serializer_class(self):
        if (
            self.action == "list"
            or self.action == "retrieve"
            or self.action == "list_available"
        ):
            return IPTableSerializerGet
        elif self.action == "create":
            return IPTableSerializerCreate
        elif self.action == "release" or self.action == "update":
            return IPTableSerializerUpdate
        else:
            return IPTableSerializerCreate

    def list_available(self, request, *args, **kwargs):
        """Lists all IPs with status of  "available". Takes no parameter or request body"""
        ip = IPTable.objects.filter(status="available")
        serializer = IPTableSerializerGet(ip, many=True)

        return response.Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @method_decorator(cache_page(60 * 15, key_prefix="IP_LISTS"))
    def list(self, request, *args, **kwargs):
        """Lists all IPs in the system"""
        start_ip = kwargs.get("start_ip")
        end_ip = kwargs.get("end_ip")
        print(start_ip, end_ip)
        if start_ip and end_ip:
            all = IPTable.objects.filter(ip__gte=start_ip).filter(ip__lte=end_ip)
            print(all)

            return response.Response(IPTableSerializerGet(all, many=True).data)
        serializer = IPTableSerializerGet(self.queryset, many=True)
        return response.Response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        """Used to retrieve details of an IP using its ID"""
        instance = self.get_object()
        serializer = IPTableSerializerGet(instance)
        return response.Response(serializer.data)

    def release(self, request, ip_address=None, *args, **kwargs):
        """Used to release Id allocated to a given customer. Takes the IP as a path parameter and returns a string as a message"""
        instance = IPTable.objects.get(ip=ip_address)

        try:
            if instance.status == "available":
                raise ValueError("IP is already released")
            resp = instance.release

            return response.Response(resp, status=status.HTTP_200_OK)

        except IPTable.DoesNotExist:
            return response.Response(
                "IP does not exist", status=status.HTTP_404_NOT_FOUND
            )

        except ValueError as e:
            return response.Response(e.args[0], status=status.HTTP_404_NOT_FOUND)

        except Exception:
            return response.Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk=None, *args, **kwargs):
        """Used to delete an IP from the system. Only users with Admin Previlages can delete"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class AllocatedIPViewSet(viewsets.ModelViewSet):
    queryset = AllocatedIP.objects.all()
    serializer_class = AllocatedIPSerializerCreate
    permission_classes = [IsAdminUserOrIsAuthenticatedReadOnly]

    def create(self, request, *args, **kwargs):
        """Used to allocate IP to a Customer. Takes a customername and an email. Returns IP details allocated to the user"""
        serializer = self.serializer_class(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            customer = User.objects.get(email=request.data["email"])

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
            random_ip.status = "allocated"
            random_ip.save()

            return response.Response(
                IPTableSerializerCreate(random_ip).data, status=status.HTTP_201_CREATED
            )

        except ValidationError as e:
            return response.Response(e, status=status.HTTP_400_BAD_REQUEST)

        except ValueError as e:
            return response.Response(
                e.args[0], status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except User.DoesNotExist:
            return response.Response(
                "Customer does not exist", status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return response.Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        """Used to list all allocated IPs in the system. This route also does range fltering of allocated IPs. one has to pass `start_ap` and end `end_aip` as their parameters

        ###Example
        `http://000000000:8000/api/v1/allocated_ips?start_ip=00000000000&end_ip=00000000000`



        """
        start_ip = self.request.query_params.get("start_ip")
        end_ip = self.request.query_params.get("end_ip")
        params = kwargs.get("params")
        print(start_ip, end_ip)
        if start_ip and end_ip:
            all = AllocatedIP.objects.filter(ip__ip__gte=start_ip).filter(
                ip__ip__lte=end_ip
            )

            return response.Response(AllocatedIPSerializerDetails(all, many=True).data)

        serializer = AllocatedIPSerializerDetails(self.queryset, many=True)
        return response.Response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        """Used to retrieve a Details of a single IP using their ID"""
        instance = self.get_object()
        serializer = AlllocatedIPSerializerGet(instance)
        return response.Response(serializer.data)

    def update(self, request, pk=None, *args, **kwargs):
        """Used to update an allocated IP"""
        partial = True
        instance = self.get_object()
        serializer = AllocatedIPSerializerUpdate(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return response.Response(serializer.data)

    def destroy(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return response.Response(status=status.HTTP_204_NO_CONTENT)
