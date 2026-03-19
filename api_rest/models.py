from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# CRIAÇÃO DO MODELO DE USUÁRIO

class User(models.Model):

    user_nickname = models.CharField(max_length=100, primary_key=True, default='')
    user_name = models.CharField(max_length=150, default='')
    user_email = models.EmailField(default='') 
    user_age = models.IntegerField(default=0)
    password = models.CharField(max_length=128, default='')

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)    

    def __str__(self):
        return f'Nickname: {self.user_nickname} - Name: {self.user_name} - Email: {self.user_email} - Age: {self.user_age}'