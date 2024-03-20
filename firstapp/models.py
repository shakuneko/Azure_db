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

#紀錄輸入的任務
class Task(models.Model):
    tid = models.CharField(max_length=50, default='0', null=False)
    task_name = models.CharField(max_length=255)
    time = models.TimeField(max_length=50,null=True, blank=True)
    date = models.DateField(max_length=50,null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.tid

#放隨機禮物
class Gift(models.Model):
    giftname = models.CharField(max_length=100)
    image_url = models.URLField()

    def __str__(self):
        return self.giftname

#紀錄拿到的禮物
class UserGift(models.Model):
    user = models.CharField(max_length=255)  # 假设您的用户ID是一个字符串类型
    gift = models.ForeignKey(Gift, on_delete=models.CASCADE)  # 关联到您的 Gift 模型
    created_at = models.DateTimeField(auto_now_add=True)  # 自动记录创建时间