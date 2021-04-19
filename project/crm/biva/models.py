from django.db import models

# Create your models here.

class Cards:
    type:str
    now:int
    previous:int
    percentage:int

    def assign(self,type,now,previous,percentage):
        self.type = type
        self.now = now
        self.previous = previous
        self.percentage = percentage