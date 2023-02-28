from django import forms
from django.shortcuts import render

from emo_app.models import User

# coding:utf-8


from django import forms


class UserInfo(forms.Form):
    username = forms.CharField(max_length=16)
    #password = forms.CharField(max_length=4)

