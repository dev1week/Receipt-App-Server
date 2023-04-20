from django.urls import path 
from rest_framework.urlpatterns import format_suffix_patterns
from .views import ReceiptList, ReceiptsDetail, AnalyzeImageView

urlpatterns = [
    path('receipts/', ReceiptList.as_view()),
    path('receipt/<int:pk>',  ReceiptsDetail.as_view()),
    path('analyze/', AnalyzeImageView.as_view())
    
]

urlpatterns = format_suffix_patterns(urlpatterns)
