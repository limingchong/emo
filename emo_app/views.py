from django.shortcuts import render
from django.http import HttpResponse
from django.template.response import TemplateResponse
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# Create your views here.


def index(request, *args, **kwargs):
    return TemplateResponse(request, 'index.html')


def test_num(request, *args, **kwargs):
    analyzer = SentimentIntensityAnalyzer()
    vs = analyzer.polarity_scores(kwargs['num1'])
    return HttpResponse("hi " + "{:-<65} {}".format(kwargs['num1'], str(vs)))
