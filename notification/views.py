from django.http import HttpResponse
from django.contrib.auth.decorators import login_required as login
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import requests
import json
import os
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from .models import DeviceToken
# Create your views here.


@login
@csrf_exempt
def index(request):
    return render(request, 'index.html')


@login
def send(request):
    tokens = DeviceToken.objects.values_list('token', flat=True)
    if not tokens:
        return HttpResponse("No tokens available.")
    send_notification_fcm_v1(
        tokens, 'Code Keen added a new video', 'Check out the latest video on Code Keen!')
    return HttpResponse("Notification sent")


TOKENS = []


@csrf_exempt
@login
def save_token(request):

    if request.method == 'POST':
        body = json.loads(request.body)
        token = body.get("token")
        if token:
            user = request.user
            obj, created = DeviceToken.objects.get_or_create(
                token=token, defaults={'user': user})
            if created:
                return JsonResponse({'status': 'Token saved'})
            else:
                return JsonResponse({'status': 'Token already exists'})

    return JsonResponse({'error': 'Invalid request'}, status=400)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVICE_ACCOUNT_FILE = os.path.join(
    BASE_DIR, "secrets", "freelancer-45e71-d484fa4020ab.json")
PROJECT_ID = "freelancer-45e71"


def get_access_token():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/firebase.messaging"],
    )
    credentials.refresh(Request())
    return credentials.token


def send_notification_fcm_v1(token_list, title, body):
    access_token = get_access_token()

    url = f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; UTF-8",
    }

    for token in token_list:
        if not token or token.strip() == "":
            print("⚠️ Skipping empty or invalid token.")
            continue
        print("Sending to token:", token)
        message = {
            "message": {
                "token": token,
                "notification": {
                    "title": title,
                    "body": body,
                },
                "android": {
                    "priority": "high",
                },
                "apns": {
                    "payload": {
                        "aps": {
                            "sound": "default"
                        }
                    }
                }
            }
        }

        response = requests.post(url, headers=headers, json=message)
        print("Status:", response.status_code)
        print("Response:", response.text)



def main_view(request):
    context={}
    return render(request, 'notification/main1.html', context=context)