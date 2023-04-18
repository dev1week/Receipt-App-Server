from django.shortcuts import render

# Create your views here.
from rest_framework import status 
from rest_framework.views import APIView 
from rest_framework.response import Response 
from django.http import Http404


from .serializers import ReceiptSerializer
from .models import Receipt

class ReceiptList(APIView):
    def get(self, request):
        receipts = Receipt.objects.all()

        serializer = ReceiptSerializer(receipts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ReceiptSerializer(data = request.data)
        if(serializer.is_valid()):
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
        

class ReceiptsDetail(APIView):
    def get_object(self, pk):
        try: 
            return Receipt.objects.get(pk=pk)
        except Receipt.DoesNotExist:
            raise Http404
    
    def get(self, request, pk, format=None):
        reciept = self.get_object(pk)
        serializer = ReceiptSerializer(reciept)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        reciept = self.get_object(pk)
        serializer = ReceiptSerializer(reciept, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQEUST)
    
    def delete(self, request, pk, format=None):
        reciept = self.get_object(pk)
        reciept.delete()
        return Response(status= status.Http_204_NO_CONTENT)