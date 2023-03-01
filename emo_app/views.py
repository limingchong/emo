import json
from datetime import datetime, timedelta
from time import sleep

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import ListView
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from emo_app.forms import UserInfo
from emo_app.models import User, Sentence, Room
import quicktranslate
from django.template import Context, Template


# Create your views here.


def say(request):
    sleep(0.3)

    def check_contain_chinese(check_str):
        for ch in check_str.encode('utf-8').decode('utf-8'):
            if u'\u4e00' <= ch <= u'\u9fff':
                return True
        return False

    if request.POST['sentence'] != '':
        sentence = request.POST['sentence']
        analyzer = SentimentIntensityAnalyzer()

        origin_sentence = ""
        translation = ""
        if check_contain_chinese(sentence):
            translation = quicktranslate.get_translate_youdao(sentence)
            origin_sentence = sentence
        else:
            translation = sentence
            origin_sentence = sentence

        vs = analyzer.polarity_scores(translation)

        roomname = request.COOKIES['roomname']

        data = {
            'username': request.COOKIES['username'],
            'sentence': origin_sentence,
            'time': datetime.now(),
            'img': round(vs['compound'] / 2, 1) * 10,
            'pos': vs['pos'],
            'neg': vs['neg'],
            'neu': vs['neu'],
            'com': vs['compound'],
            'roomname': roomname
        }
        Sentence.objects.create(**data)

        total_com = 0
        count = 0
        for s in Sentence.objects.filter(roomname=roomname):
            if check_contain_chinese(s.sentence):
                total_com += analyzer.polarity_scores(quicktranslate.get_translate_youdao(s.sentence))['compound']
            else:
                total_com += analyzer.polarity_scores(s.sentence)['compound']
            count += 1

        avg_com = total_com / count
        Room.objects.filter(roomname=roomname).update(com=avg_com, img=(round(avg_com / 2, 1) * 10))

    return HttpResponseRedirect("/")


class roomlist(ListView):
    model = Room
    template_name = 'roomlist.html'

    def post(self, request, *args, **kwargs):
        response = HttpResponseRedirect("/")
        if request.POST['roomname'] != '':
            data = {
                'roomname': request.POST['roomname'],
                'username': request.COOKIES['username'],
                'time': datetime.now(),
                'com': 0,
                'img': "0.0"
            }
            Room.objects.create(**data)
            response.set_cookie('roomname', data['roomname'], expires=datetime.now() + timedelta(days=999))
        return response


def change(request, *args, **kwargs):
    response = HttpResponseRedirect("/room")
    response.set_cookie('roomname', kwargs["roomname"], expires=datetime.now() + timedelta(days=999))
    return response


def get_detail(request, *args, **kwargs):

    coms = []
    for s in Sentence.objects.filter(username=kwargs['name']):
        coms.append(s.com)

    return render(request, template_name="detail.html", context={
        'name': kwargs['name'],
        'average': 0.5,
        'datas': coms
    })


class chatroom(ListView):
    model = Sentence
    template_name = 'room.html'
    context_object_name = 'user_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.request.COOKIES['username']
        context['roomname'] = self.request.COOKIES['roomname']
        if (Sentence.objects.filter(roomname=self.request.COOKIES['roomname'])):
            context['last_sentence'] = Sentence.objects.filter(roomname=self.request.COOKIES['roomname']).count()
        else:
            context['last_sentence'] = 0

        return context

    def post(self, request, *args, **kwargs):
        return say(request)


def test_num(request, *args, **kwargs):
    analyzer = SentimentIntensityAnalyzer()
    vs = analyzer.polarity_scores(kwargs['num1'])
    return HttpResponse("hi " + "{:-<65} {}".format(kwargs['num1'], str(vs)))


def help(request, *args, **kwargs):
    return render(request, template_name="help.html", context={
        'from': kwargs['from']
    })


def register(request):
    if request.method == 'GET':
        if 'username' in request.COOKIES:
            if not User.objects.filter(username=request.COOKIES['username']):
                data = {'username': request.COOKIES['username']}
                User.objects.create(**data)

            if 'roomname' in request.COOKIES:
                if not Room.objects.filter(roomname=request.COOKIES['roomname']):
                    data = {
                        'roomname': request.COOKIES['roomname'],
                        'username': request.COOKIES['username'],
                        'time': datetime.now(),
                        'com': 0,
                        'img': "0.0"
                    }
                    Room.objects.create(**data)

                return HttpResponseRedirect('room')
            else:
                return HttpResponseRedirect('list')
        else:
            return render(request, 'login.html')

    else:
        reg_form_obj = UserInfo(data=request.POST)
        if reg_form_obj.is_valid():
            data = reg_form_obj.cleaned_data
            if User.objects.filter(username=data['username']):
                return HttpResponseRedirect("/")

            User.objects.create(**data)
            response = HttpResponseRedirect('list')
            response.set_cookie('username', data['username'], expires=datetime.now() + timedelta(days=999))
            return response
        else:
            print('ERROR')
            print(reg_form_obj.errors)
            return render(request, 'login.html')
