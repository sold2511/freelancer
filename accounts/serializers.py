from rest_framework import serializers
from .models import *
from jobs.models import *
from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError
from django.utils.encoding import smart_str,force_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from .utils import Util
from django.contrib.auth.tokens import PasswordResetTokenGenerator 

class UserLoginSerializers(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=120)
    class Meta:
        model = CustomUser
        fields = ['email','password']
        
        
class UserRegisterSerializers(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})
    email = serializers.EmailField(required=True)
    class Meta:
        model=CustomUser
        fields = ['username','email','first_name','last_name','role','bio','profile_pic','website','tagline','phone','password','password2']
        
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        phone = attrs.get('phone')
        print(len(phone))
        print(password,password2)
        if len(phone) != 10:
            raise serializers.ValidationError("Phone must be 10 digit")
        if password != password2:
            raise serializers.ValidationError("Password doesnot match")
        return super().validate(attrs)
    
    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.is_active = False  # Ensure the user is active
        user.save()
        # password = validated_data.pop('password')
        return user

class SendEmailVerificationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    
    class Meta:
        model = CustomUser 
        fields = ['email']
    
    def validate(self, attrs):
        email = attrs.get('email')
        if CustomUser.objects.filter(email=email).exists():
            user1  = CustomUser.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user1.id))
            token = PasswordResetTokenGenerator().make_token(user1)
            link = "http://localhost:8000/api/v1/verify-email/"+uid+'/'+token+'/'
            
            data = {
                'subject':'Verify Your Email',
                # 'body':link,
                'body':render_to_string('accounts/verify.html', {
                'link': link,
            }),
                'to_email':user1.email
            }
            Util.send_email(data)
            print(link)
            return attrs
        else:
            raise ValidationError('You are not a Registered user')
    
class SendPasswordEmailSerializeres(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = CustomUser 
        fields = ['email']
    
    def validate(self, attrs):
        email = attrs.get('email')
        if CustomUser.objects.filter(email=email).exists():
            user  = CustomUser.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            link = "http://localhost:8000/api/v1/reset-password/"+uid+'/'+token+'/'
            
            data = {
                'subject':'Reset Your Password',
                # 'body':link,
                'body':render_to_string('accounts/verify.html', {
                'link': link,
            }),
                'to_email':user.email
            }
            Util.send_email(data)
            print(link)
            return attrs
        else:
            raise ValidationError('You are not a Registered user')
        
class UserPasswordResetSerializers(serializers.ModelSerializer):
    password = serializers.CharField(max_length=120,style={'input_type':'password'},write_only=True)
    password2 = serializers.CharField(max_length=120,style={'input_type':'password'},write_only=True)
    class Meta:
        model = CustomUser
        
        fields = ['password','password2']
    
    def validate(self, attrs):
        try:
            uid = self.context.get('uid')
            token = self.context.get('token')
            password = attrs.get('password')
            password2 = attrs.get('password2')
            if password != password2:
                raise serializers.ValidationError("Password doesnot match")
            ide = smart_str(urlsafe_base64_decode(uid))
            user = CustomUser.objects.get(id=ide)
            if not PasswordResetTokenGenerator().check_token(user,token):
                raise ValidationError('Token is expired or not valid ')
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier :
            PasswordResetTokenGenerator().check_token(user,token)
            raise ValidationError('Token is expired or not valid')
  
class UserProfileSerializers(serializers.ModelSerializer):
    # email = serializers.EmailField(max_length=120)
    class Meta:
        model = CustomUser
        fields = ['id','email','first_name']
        
        
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']
        
class JobSerializer(serializers.ModelSerializer):
    client = UserRegisterSerializers(read_only=True)  # nested read-only user info
    skills = SkillSerializer(many=True, read_only=True)
    skill_ids = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(), write_only=True, many=True, source='skills'
    )

    class Meta:
        model = Jobs
        fields = [
            'id',
            'title',
            'description',
            'budget',
            'deadline',
            'created_at',
            'updated_at',
            'status',
            'client',
            'category',
            'attachments',
            'skills',       # read-only
            'skill_ids',    # write-only
        ]