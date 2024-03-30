from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, BlacklistedSender, WhitelistedSender
from .forms import EmailCheckForm
from .naive_bayes import NaiveBayesClassifier
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout
import json

import nltk
from nltk.corpus import stopwords
import csv

# Create your views here.

#Default view - The one that loads when you open the website
def index(request):
    if request.user.is_authenticated:
        #Get the current user
        user_profile = UserProfile.objects.get(user=request.user)
        #Count no. of spam emails checked
        spam_count = user_profile.blacklisted_senders.count()
        #Count no. of ham emails checked
        not_spam_count = user_profile.whitelisted_senders.count()
        total = spam_count + not_spam_count
        context = {
            'spam_count': spam_count,
            'not_spam_count': not_spam_count,
            'total_mail': total,
        }
        return render(request, 'spam_detection/dashboard.html', context)
    else:
        return redirect('spam_detection:login')
    
#View to show evaluation metrics like accuracy, precision and recall
def evaluation_metrics(request):
    return render(request, 'spam_detection/metrics.html')
    

#View to register a new user
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('spam_detection:login')
    else:
        form = UserCreationForm()
    return render(request, 'spam_detection/register.html', {'form': form})

#View to login a user
def user_login(request):
    #Handle Post Requests
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('spam_detection:dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'spam_detection/login.html', {'form': form})

#View to logout a user
def user_logout(request):
    logout(request)
    return redirect('spam_detection:login')


#View to render a dashboard
@login_required
def dashboard(request):
    username = request.user.username

    user_profile = UserProfile.objects.get(user=request.user)

    spam_count = user_profile.blacklisted_senders.count()
    not_spam_count = user_profile.whitelisted_senders.count()
    total = spam_count + not_spam_count
    context = {
        'username': username,
        'spam_count': spam_count,
        'not_spam_count': not_spam_count,
        'total_mail': total
    }
    return render(request, 'spam_detection/dashboard.html', context)



english_stopwords = stopwords.words('english')

emails = []
labels = []

def read_csv(file_path):
    emails = []
    labels = []
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            labels.append(1 if row['Category'] == 'spam' else 0)
            emails.append(row['Message'])
    return emails, labels

emails, labels = read_csv('./phisingmail.csv')

classifier = NaiveBayesClassifier()
classifier.train(emails, labels)

@login_required
def check_spam(request):
    if request.method == 'POST':
        form = EmailCheckForm(request.POST)
        if form.is_valid():
            sender_email = form.cleaned_data['sender_email']
            email_text = form.cleaned_data['email_text']
            user_profile = UserProfile.objects.get(user=request.user)

            #Check if sender is blacklisted
            blacklisted = user_profile.blacklisted_senders.filter(email=sender_email)
            if blacklisted.exists():
                warning = "This email address is already blacklisted."
                form = EmailCheckForm()
                context = {
                    'warning': warning,
                    'form': form,
                }
                return render(request, 'spam_detection/check_spam.html', context)
            is_spam, log_prob_diff, confidence, features, matching_words  = classifier.predict(email_text)
            print(is_spam)
            
            
            if is_spam is True:
                blacklisted_sender, _ = BlacklistedSender.objects.get_or_create(email=sender_email)
                user_profile.blacklisted_senders.add(blacklisted_sender)
                context = {
                    'is_spam': is_spam,
                    'sender_email': sender_email,
                    'log_prob_diff': log_prob_diff,
                    'confidence': confidence,
                    'features': features,
                    'matching_words': matching_words,
                }
                return render(request, 'spam_detection/spam_result.html', context)
            if is_spam is False:
                whitelisted_sender, _ = WhitelistedSender.objects.get_or_create(email=sender_email)
                user_profile.whitelisted_senders.add(whitelisted_sender)
                context = {
                    'is_spam': is_spam,
                    'sender_email': sender_email,
                    'log_prob_diff': log_prob_diff,
                    'confidence': confidence,
                    'features': features,
                    'matching_words': matching_words,
                }
                return render(request, 'spam_detection/not_spam_result.html', context)
    else:
        form = EmailCheckForm()
    return render(request, 'spam_detection/check_spam.html', {'form': form})

@login_required
def blacklist(request):
    if request.user.is_authenticated:

        user_profile = UserProfile.objects.get(user=request.user)

        blacklisted_users = user_profile.blacklisted_senders.all()
        username = request.user.username
        context = {
            'username': username,
            'blacklist': blacklisted_users,
        }
        return render(request, 'spam_detection/blacklist.html', context)
    
@login_required
def whitelist(request):
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
        whitelisted_users = user_profile.whitelisted_senders.all()
        username = request.user.username
        context = {
            'username': username,
            'whitelist': whitelisted_users,
        }
        return render(request, 'spam_detection/whitelist.html', context)

