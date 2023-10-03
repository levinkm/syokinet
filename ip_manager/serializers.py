from rest_framework import serializers

from ip_manager.models import IPTable,AllocatedIP

#============================================IPTable Serializer========================================

class IPTableSerializerCreate(serializers.ModelSerializer):
    
    class Meta:
        model = IPTable
        fields = ('id','ip', 'status') 

class IPTableSerializerUpdate(serializers.ModelSerializer):
    
    class Meta:
        model = IPTable
        fields = ('status')

class IPTableSerializerGet(IPTableSerializerCreate):
    class Meta:
        model = IPTable
        fields = "__all__"

#=========================================AllocatedIP serializers=======================================
  
class AllocatedIPSerializerCreate(serializers.Serializer):

    customer_name = serializers.CharField(max_length=50, required=False)
    email = serializers.EmailField(required=False)
    
    class Meta:
        fields = ('email', 'customer_name')

class AllocatedIPSerializerDetails(serializers.ModelSerializer):
    ip = IPTableSerializerGet()
    class Meta:
        model = AllocatedIP
        fields = "__all__"

class AlllocatedIPSerializerGet(serializers.ModelSerializer):

    class Meta:
        model = AllocatedIP
        fields = "__all__"

class AllocatedIPSerializerUpdate(serializers.ModelSerializer):
    
    class Meta:
        model = AllocatedIP
        fields = ('ip', 'customer_name', 'email')
        
