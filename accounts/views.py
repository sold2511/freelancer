from django.shortcuts import render,redirect , HttpResponse
from rest_framework.response import Response
from django.contrib.auth import logout
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .renderer import UserRenderer
from .serializers import *
from django.contrib.auth import login
from rest_framework.permissions import IsAuthenticated

def get_tokens_for_user(user):
    if not user.is_active:
      raise AuthenticationFailed("User is not active")

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    

class UserRegisterView(APIView):
    renderer_classes = [UserRenderer]
    def get(self, request):
        return render(request, 'accounts/register.html')
    def post(self,request,format=True):
        serializer = UserRegisterSerializers(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if not  user.is_active:
                serializer1 = SendEmailVerificationSerializer(data={'email': user.email})
                if serializer1.is_valid(raise_exception=True):
                    return render(
                        request,
                        "accounts/_base.html",  # or a separate error template like "error.html"
                        {
                            "success_message": "Email verification link sent successfully. Please check your email."
                        },
                        status=status.HTTP_200_OK
                    )
                    
            token = get_tokens_for_user(user)
            
            # Optionally login the user
            user.backend = 'django.contrib.auth.backends.ModelBackend'  # or your custom backend
            login(request, user)
            
            # Store in session
            request.session['token'] = token['access']
            request.session['refresh_token'] = token['refresh']
            request.session['username'] = user.username
            request.session['role'] = user.role 

            # return Response({"msg":"User Registered Successfully"},status=status.HTTP_201_CREATED)
            return redirect('job-list')
        return render(request, 'accounts/register.html', {'errors': serializer.errors})
    
# Create your views here

class UserLoginView(APIView):
    renderer_classes = [UserRenderer]
    def get(self, request):
        return render(request, 'accounts/login.html')
    def post(self,request,format=True):
        serializer = UserLoginSerializers(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            user = CustomUser.objects.filter(email=email).first()
            if not user.is_active:
                return  render(
            request,
            "accounts/_base.html",  # or a separate error template like "error.html"
            {
                "error_message": "User is not active. Please contact the admin or verify your email."
            },
            status=403
        )   
            print(f"Trying to authenticate {email} with password +{password}+")
            user = authenticate(email=email, password=password)
            print(f"User authenticated: {user}")
            
            
            if user is not None:
                token = get_tokens_for_user(user)
                user_data = serializer.data
                login(request,user)
                request.session['token'] = token['access']
                print("Token stored in session:", request.session.get('token'))
                request.session['username'] = user.username
                request.session['role'] = user.role
                return redirect('job-list')
            else:
                return render(request, 'accounts/login.html', {
    'errors': {'non_field_errors': 'Email or password is not valid'}
}, status=status.HTTP_401_UNAUTHORIZED)
        #         return Response({'errors':{'non_field_errors':'Email or password is not valid'}},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        

class SendPasswordEmailView(APIView):        
    renderer_classes=[UserRenderer]
    # permission_classes = [IsAuthenticated]
    
    def post(self,req,format=None):
        serializer = SendPasswordEmailSerializeres(data=req.data)
        if serializer.is_valid(raise_exception=True):
            return Response({'msg':'Password change link send  Successfully'},status=status.HTTP_200_OK)
        return Response({'Errors':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
    


class VerifiedUser(APIView):
    renderer_classes = [UserRenderer]
    def get(self,req,uid,token,format=None):
        try:
            uid = urlsafe_base64_decode(uid).decode()
            user = CustomUser.objects.get(id=uid)
            if PasswordResetTokenGenerator().check_token(user, token):
                user.is_active = True
                user.save()
                return render(req,'accounts/_base.html',{'success_message':'Email verified successfully'},status=status.HTTP_200_OK)
            else:
                return render(req,'accounts/_base.html',{'error_message':'Invalid Token'},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return render(req,'accounts/_base.html',{'error_message':str(e)},status=status.HTTP_400_BAD_REQUEST)
class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]
    def post(self,req,uid,token,format=None):
        serializer= UserPasswordResetSerializers(data=req.data,context={'uid':uid,'token':token})
        if serializer.is_valid(raise_exception=True):
            return Response({'msg':'Password changed Successfully'},status=status.HTTP_200_OK)
        return Response({'error_message':serializer.errors},status=status.HTTP_400_BAD_REQUEST)



def logout_view(req):
    logout(req)
    req.session.flush()
    return redirect('login')