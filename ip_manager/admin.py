from django.contrib import admin
from ip_manager.models import IPTable, AllocatedIP

# Register your models here.
admin.site.site_header = "SYOKINET"

admin.site.site_title = "SYOKINET"
admin.site.index_title = "SYOKINET"
admin.site.register(IPTable)
admin.site.register(AllocatedIP)
