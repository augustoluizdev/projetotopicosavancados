from django.db import models

# CRIAÇÃO DO MODELO DE USUÁRIO

class User(models.Model):

    user_nickname = models.CharField(max_length=100, primary_key=True, default='')
    user_name = models.CharField(max_length=150, default='')
    user_email = models.EmailField(default='') 
    user_age = models.IntegerField(default=0)

    def __str__(self):
        return f'Nickname: {self.user_nickname} - Name: {self.user_name} - Email: {self.user_email} - Age: {self.user_age}'