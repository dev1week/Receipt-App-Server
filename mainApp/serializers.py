from rest_framework import serializers
from .models import Receipt


#모델 인스턴스 ->  json, xml 등 
class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt # 모델 설정
        fields = ('id','title','amount', 'date') # 필드 설정