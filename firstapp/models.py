from django.db import models

class users(models.Model):
    uid = models.CharField(max_length=50,null=False)
    datatest = models.CharField(max_length=50,null=False,default='0')
    created_time = models.DateTimeField(auto_now=True)
    
    def _str_(self):
        return self.uid
    
class booking(models.Model):
    bid = models.CharField(max_length=50, default='0', null=False)
    datatest = models.CharField(max_length=50,null=False,default='0')
    exhibittype = models.CharField(max_length=20,null=False)
    exhibitamount = models.CharField(max_length=5,null=False)
    money = models.CharField(max_length=50, default='0', null=False)
    #created_time = models.DateTimeField(auto_now=True)
    which_date =  models.DateField(auto_now=True)
    which_time =  models.TimeField(auto_now=True)
    
    def _str_(self):
        return self.bid

class Task(models.Model):
    task_name = models.CharField(max_length=255)
    time = models.TimeField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.task_name