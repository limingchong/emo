from datetime import datetime, timedelta

import requests
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from django.views.generic import View, ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from emo_app.models import User, Sentence
from emo_app.forms import UserInfo
import json


# Create your views here.


class chatroom(ListView):
    model = Sentence
    template_name = 'chatroom.html'
    context_object_name = 'user_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.request.COOKIES['username']
        return context

    def post(self, request, *args, **kwargs):
        def check_contain_chinese(check_str):
            for ch in check_str.encode('utf-8').decode('utf-8'):
                if u'\u4e00' <= ch <= u'\u9fff':
                    return True
            return False

        if request.POST['sentence'] != '':
            sentence = request.POST['sentence']
            analyzer = SentimentIntensityAnalyzer()

            origin_sentence = ""
            if check_contain_chinese(sentence):
                api_url = "http://mymemory.translated.net/api/get?q={}&langpair={}|{}".format(sentence, "zh-CN", "en")
                hdrs = {
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                    'Accept-Encoding': 'none',
                    'Accept-Language': 'en-US,en;q=0.8',
                    'Connection': 'keep-alive'}
                response = requests.get(api_url, headers=hdrs)
                response_json = json.loads(response.text)
                origin_sentence = sentence
                sentence = response_json["responseData"]["translatedText"]
                print(sentence)

            vs = analyzer.polarity_scores(sentence)

            if origin_sentence != "":
                sentence = origin_sentence

            data = {
                'username': request.COOKIES['username'],
                'sentence': sentence,
                'time': datetime.now(),
                'color': ('{:02X}' * 3).format(int(255 * vs['pos']), int(255 * vs['neg']), 0),
                'pos': vs['pos'],
                'neg': vs['neg'],
                'neu': vs['neu'],
                'com': vs['compound']
            }
            Sentence.objects.create(**data)
        return HttpResponseRedirect("/")


def test_num(request, *args, **kwargs):
    analyzer = SentimentIntensityAnalyzer()
    vs = analyzer.polarity_scores(kwargs['num1'])
    return HttpResponse("hi " + "{:-<65} {}".format(kwargs['num1'], str(vs)))


def register(request):
    if request.method == 'GET':
        print(request.COOKIES)
        if 'username' in request.COOKIES:
            return HttpResponseRedirect('chatroom')

        else:
            return render(request, 'login.html')

    else:
        reg_form_obj = UserInfo(data=request.POST)
        if reg_form_obj.is_valid():
            data = reg_form_obj.cleaned_data
            User.objects.create(**data)
            response = HttpResponseRedirect('chatroom')
            response.set_cookie('username', data['username'], expires=datetime.now() + timedelta(days=999))
            return response
        else:
            print('ERROR')
            print(reg_form_obj.errors)
            return render(request, 'login.html')
