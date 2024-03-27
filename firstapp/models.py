from django.db import models

class users(models.Model):
    uid = models.CharField(max_length=50,null=False)
    datatest = models.CharField(max_length=50,null=False,default='0')
    created_time = models.DateTimeField(auto_now=True)
    experience = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    reward_claimed = models.BooleanField(default=False)
    nickname = models.CharField(max_length=255)
    image_url = models.URLField(blank=True, null=True)

    def _str_(self):
        return self.uid

#紀錄輸入的任務
class Task(models.Model):
    tid = models.CharField(max_length=50, default='0', null=False)
    task_name = models.CharField(max_length=255)
    time = models.TimeField(max_length=50,null=True, blank=True)
    date = models.DateField(max_length=50,null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    completed = models.BooleanField(default=False)  # 新增字段表示任务是否完成

    def __str__(self):
        return self.tid

#放隨機禮物
class Gift(models.Model):
    giftname = models.CharField(max_length=100)
    image_url = models.URLField()
    description = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.giftname

#紀錄拿到的禮物
class UserGift(models.Model):
    user = models.CharField(max_length=255)  # 假设您的用户ID是一个字符串类型
    gift = models.ForeignKey(Gift, on_delete=models.CASCADE)  # 关联到您的 Gift 模型
    image_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)  # 自动记录创建时间
    description = models.CharField(max_length=100, default='')

#紀錄完成的任務id
class CompletedTask(models.Model):
    user_id = models.CharField(max_length=100)  # 用戶ID
    task_id = models.CharField(max_length=100)  # 任務ID

#紀錄等級對應的圖片
class UserLevel(models.Model):
    level = models.IntegerField(unique=True)
    image_url = models.URLField()

    def __str__(self):
        return f"Level {self.level}"