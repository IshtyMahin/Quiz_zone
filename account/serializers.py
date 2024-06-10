from account.models import User
from rest_framework import serializers
from django.utils.encoding import smart_str,force_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models  import ContactMessage

class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'profile_img', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("Password and Confirm password doesn't match")
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            profile_img = validated_data['profile_img'],
            password=validated_data['password']
        )
    
class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255,min_length=3)
    
    class Meta:
        model = User
        fields = ['email','password']
        
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','first_name','last_name','email','profile_img']
        
        
class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
    class Meta:
        fields = ['password', 'password2']
        
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('user')
        if password!= password2:
            raise serializers.ValidationError("Password and Confirm password doesn't match")
        
        user.set_password(password)
        user.save()
        return attrs
        
        
class SendPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    
    class Meta:
        fields = ['email']
        
    def validate(self, attrs):
        email = attrs.get('email')
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("User with this email doesn't exist")
        
        user = User.objects.get(email=email)
        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        
        link = f'https://mindd-test.netlify.app/reset_pass_page.html?uid={uid}&token={token}'
        print("Password reset link:", link)
        email_subject = "Request for reset password"
        email_body = render_to_string("resetPassword.html", {"confirm_link": link})
        
        email = EmailMultiAlternatives(
            email_subject,
            email_body,
            to=[user.email]
        )
        email.attach_alternative(email_body, "text/html")
        email.send()
        return attrs
        

class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
    
    class Meta:
        fields = ['password', 'password2']
        
    def validate(self, attrs):
        try:
            password = attrs.get('password')
            password2 = attrs.get('password2')
            uid = self.context.get('uid')
            token = self.context.get('token')
            if password != password2:
                raise serializers.ValidationError("Password and Confirm Password doesn't match")
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError('Token is not Valid or Expired')
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
             PasswordResetTokenGenerator().check_token(user, token)
             raise serializers.ValidationError('Token is not Valid or Expired')
    
    

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']