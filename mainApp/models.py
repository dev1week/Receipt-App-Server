from django.db import models

#db에 저장할 영수증 모델 생성 
class Receipt(models.Model):
    
    title = models.CharField(max_length=30)
    amount = models.IntegerField()
    date = models.DateField()


    def __str__(self):
        return self.title 