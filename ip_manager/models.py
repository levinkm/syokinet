from django.db import models
import uuid

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class IPTable(BaseModel):

    STATUS_CHOICES = (
        ('allocated', 'allocated'),
        ('availble', 'Availble'),
        ('reserved', 'Reserved'),
    )

    ip = models.IPAddressField(unique=True, null=False, blank=False)
    status = models.CharField(max_length=20,choices = STATUS_CHOICES,default='availble')

    @property
    def allocate(self):
        return self.status == 'allocated'
    @property
    def release(self):
        try:
           if self.status == 'available':
               return "IP is not allocated"
           
           allocatedip = AllocatedIP.objects.get(ip=self)
           allocatedip.delete()
           self.status = 'available'
           self.save()

           return "IP has been released"
        except AllocatedIP.DoesNotExist:
            return AllocatedIP.DoesNotExist(f"IP {self} is not allocated")
        
        except Exception as e:
            return e

class AllocatedIP(BaseModel):
    ip = models.ForeignKey(IPTable, on_delete=models.CASCADE)
    customer = models.ForeignKey('User', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('ip', 'customer')
        verbose_name_plural = 'Allocated IP'


    def __str__(self):
        return self.ip.ip 


