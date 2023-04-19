from django.shortcuts import render

# Create your views here.
from rest_framework import status 
from rest_framework.views import APIView 
from rest_framework.response import Response 
from django.http import Http404

from .serializers import ReceiptSerializer
from .models import Receipt

from rest_framework.parsers import MultiPartParser, FormParser

import requests 

import uuid
import re

import json
import base64

import my_settings

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
        
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        reciept = self.get_object(pk)
        reciept.delete()
        return Response(status= status.Http_204_NO_CONTENT)


def craete_request_body(file_format, file_data, file_name):
        request_body=  {
            'version': 'V2',
            'requestId': uuid.uuid4().__str__(),
            'timestamp': 0,
            'lang': 'ko',
            'images': [{'format': file_format, 'data': file_data, 'name': file_name}]
        }
        return json.dumps(request_body).encode('UTF-8')

class AnalyzeImageView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    #OCR_API URL
    ep_path = my_settings.OCR_API_URL
    ## headers
    custom_headers = {
        'Content-Type': 'application/json;UTF-8',
        'X-OCR-SECRET': my_settings.X_OCR_SECRET
    }

    #. , "원" 등 가격에서의 불필요한 데이터 삭제 
    def get_clean_amount(self, response):
        amount = response.json()['images'][0]['receipt']['result']['totalPrice']['price']['text']
        cleaned_amount = re.sub(r'[.,원]', '', amount)
        return cleaned_amount

    ##영수증 상 년도가 2자리로 되어있을 경우 보정
    def get_clean_year(self, date):
        year = int (date[0])
        if(year<1000):
            date[0] = str (year+2000)
        
        return date[0]

    
    def create_reciept_data(self, title, cleaned_amount, year, month, day):
        return {
            'title': title,
            'amount': cleaned_amount,
            'date': year + "-" + month + "-" + day,
        }

    #OCR API 요청
    def analyze_image(self, encode_request_body):
        response = requests.post(headers=self.custom_headers, url=self.ep_path, data=encode_request_body)
        title = response.json()['images'][0]['receipt']['result']['storeInfo']['name']['text']
        date = response.json()['images'][0]['receipt']['result']['paymentInfo']['date']['text'].split('/')
        cleaned_amount = self.get_clean_amount(response)
        date[0] = self.get_clean_year(date)
        reciept_data = self.create_reciept_data(title, cleaned_amount, date[0], date[1], date[2])
        
        return reciept_data

    #분석한 영수증 데이터 DB에 저장 
    def save_reciept(self, serializer):
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        #Multipart에서 file로 있는 이미지를 base64로 인코딩한 후 메모리에 임시 저장한다.
        file = request.FILES.get('file')
        file_data = base64.b64encode(file.read()).decode('utf-8')
        
        #파일 이름과 확장자명을 parsing한다. 
        file_name = file.name.split(".")[0]
        file_format = file.name.split(".")[1]

        #네이버 클라우드 ocr에 요청할 request를 생성한다. 
        ocr_request = craete_request_body(file_format, file_data, file_name)
        
        #네이버 클라우드 ocr api에 분석 결과를 요청한다. 
        reciept_data = self.analyze_image(ocr_request)
        
        #분석한 결과를 파이썬 객체화한다. 
        serializer = ReceiptSerializer(data=reciept_data)

        #유효성 검사후 통과하면 db에 저장한다. 
        return self.save_reciept(serializer)
       
        
            

