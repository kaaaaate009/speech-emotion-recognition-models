import os
from django.shortcuts import render, redirect
from django.contrib.staticfiles.storage import staticfiles_storage
from datetime import datetime

from django.template.context_processors import static

from .models import Feedbacks, PriorityList
from .forms import FeedbackForm, PriorityForm

import librosa
import numpy as np
import matplotlib.style as ms
import pickle
import pandas as pd
import librosa.display
ms.use('seaborn-muted')
# %matplotlib inline

# Create your views here.


def uploadform(request):
    return render(request, 'uploadform.html')


def mainfunction(filepath, c):
    file_path = filepath
    y, sr = librosa.load(file_path, sr=44100)
    hop_length = 512
    columns = ['sig_mean', 'sig_std', 'rmse_mean', 'rmse_std', 'silence', 'harmonic', 'auto_corr_max', 'auto_corr_std', 'mfcc1', 'mfcc2', 'mfcc3', 'mfcc4', 'mfcc5', 'mfcc6', 'mfcc7', 'mfcc8', 'mfcc9', 'mfcc10', 'mfcc11', 'mfcc12', 'mfcc13']
    df_features = pd.DataFrame(columns=columns)
    feature_list = []

    sig_mean = np.mean(abs(y))
    feature_list.append(sig_mean)  # sig_mean
    feature_list.append(np.std(y))  # sig_std

    rmse = librosa.feature.rms(y + 0.0001)[0]
    feature_list.append(np.mean(rmse))  # rmse_mean
    feature_list.append(np.std(rmse))  # rmse_std

    silence = 0
    for e in rmse:
        if e <= 0.4 * np.mean(rmse):
            silence += 1
    silence /= float(len(rmse))
    feature_list.append(silence)  # silence

    y_harmonic = librosa.effects.hpss(y)[0]
    feature_list.append(np.mean(y_harmonic) * 1000)  # harmonic (scaled by 1000)

    cl = 0.45 * sig_mean
    center_clipped = []
    for s in y:
        if s >= cl:
            center_clipped.append(s - cl)
        elif s <= -cl:
            center_clipped.append(s + cl)
        elif np.abs(s) < cl:
            center_clipped.append(0)
    auto_corrs = librosa.core.autocorrelate(np.array(center_clipped))
    feature_list.append(1000 * np.max(auto_corrs)/len(auto_corrs))  # auto_corr_max (scaled by 1000)
    feature_list.append(np.std(auto_corrs))  # auto_corr_std

    # mfcc
    mfccs=np.mean(librosa.feature.mfcc(y=y, sr=sr, hop_length=hop_length, n_mfcc=13).T, axis=0)

    for i in range(0,13):
        feature_list.append(mfccs[i])  # mfcc

    df_features = df_features.append(pd.DataFrame(feature_list, index=columns).transpose(), ignore_index=True)

    #print(feature_list)
    #print(df_features)
    urlpath = staticfiles_storage.path('mlmodel/xgb_classifier2.pkl')

    with open(urlpath, 'rb') as file:
        Pickled_Model = pickle.load(file)

    ypred = Pickled_Model.predict_proba(df_features)
    print(ypred)

    temp = np.max(ypred)
    print(temp)
    index_max = np.argmax(ypred)
    print(index_max)
    emotion_dict = {0: 'ang',
                    1: 'hap',
                    2: 'sad',
                    3: 'fea',
                    4: 'sur',
                    5: 'neu'}
    print(emotion_dict.get(index_max))

    pl = PriorityList()
    pl.contact2 = c
    pl.emotion = emotion_dict.get(index_max)
    if index_max == 0:
        pl.priority = 1
    elif index_max == 2:
        pl.priority = 2
    elif index_max == 1:
        pl.priority = 4
    else:
        pl.priority = 3
    pl.save()

    return 0



def uploadaction(request):
    if request.method == 'POST':
        contact = request.POST['contact']
        afile = request.FILES['audiofile']
        recordtime = datetime.now()
        print(contact)
        tempform = FeedbackForm(request.POST, request.FILES)
        print(tempform)
        print('check 1')
        if tempform.is_valid():
            print('In inner loop')
            x = Feedbacks()
            x.contact = tempform.cleaned_data['contact']
            x.audiofile = tempform.cleaned_data['audiofile']
            x.recordtime = datetime.now()
            x.save()
            print('Done')
            print(x.audiofile)
            mainfunction(x.audiofile, x.contact)
        else:
            print('Invalid form')
    # return render(request, 'uploadform.html')
    return redirect('/')


def ListView(request):
    feedlist=PriorityList.objects.all()
    return render(request, 'ListView.html', {'feedlist': feedlist})
