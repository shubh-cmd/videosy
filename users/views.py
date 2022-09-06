from multiprocessing import AuthenticationError
import random

from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework import exceptions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .validators import CheckPermissions
from .models import User, PasswordReset
from .serializers import UserSerializer
import math, random
from rest_framework import status

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data['email']
        if User.objects.filter(email=email).exists():
            return Response(status=status.HTTP_200_OK,data={"message": "user exists"})
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        if request.data['is_verified']:
            return Response(status=status.HTTP_200_OK,data={"message": "User used google sign"})
            
        
        digits = "0123456789"
        OTP = ""
 
        for _ in range(6) :
            OTP += digits[math.floor(random.random() * 10)]


        if PasswordReset.objects.filter(email=email).exists():
            PasswordReset.objects.filter(email=email).delete()

        PasswordReset.objects.create(email=email, otp=OTP)
        send_mail(
            subject='OTP for Email Verification',
            message=
            f""" 
            Dear user,

            Your OTP is {OTP}.
            Kindly use this OTP to complete sign up.

            Thanks!
            Liiia Team
            """,
            from_email='shubham0af024@gmail.com',
            recipient_list=[email],
            fail_silently=False
        )

        return Response({
            'message': 'please check your email!'
        })


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        if not request.data['is_google_signin'] and password == 'google_signin':
            raise AuthenticationFailed('Incorrect Password')

        user = get_object_or_404(User, email=email)

        if request.data['is_google_signin'] and user.registered_with_OTP:
            pass
        else: 
            if not user.check_password(password):
             raise AuthenticationFailed('Incorrect Password')

        if not user.is_verified:
            raise AuthenticationError("User is not verified")

        token, created = Token.objects.get_or_create(user=user)

        
        data = {"token": token.key, "email": token.user.email}
        
        return Response(data=data, status=200)


class UserView(APIView):
    permission_classes = [IsAuthenticated | CheckPermissions]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self,request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors)




class LogoutView(APIView):
    permission_classes = [IsAuthenticated | CheckPermissions]

    def post(self, request):
        try:
            Token.objects.get(user=request.user).delete()
        except Token.DoesNotExist:
            pass

        Token.objects.create(user=request.user)

        return Response(status=200)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data['email']
    
        digits = "0123456789"
        OTP = ""
 
        for _ in range(6) :
            OTP += digits[math.floor(random.random() * 10)]

        if PasswordReset.objects.filter(email=email).exists():
            PasswordReset.objects.filter(email=email).delete()

        PasswordReset.objects.create(email=email, otp=OTP)

        send_mail(
            subject='OTP for Reset Password',
            message=
            f""" 
            Dear user,

            Your OTP is {OTP}.
            Kindly use this OTP to reset password.

            Thanks!
            Liiia Team
            """,
            from_email='shubham0af024@gmail.com',
            recipient_list=[email],
            fail_silently=False
        )

        return Response({
            'message': 'please check your email!'
        })


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data

        if data['password'] != request.data['password_confirm']:
            raise exceptions.APIException('Password do not match')

        passwordReset = get_object_or_404(PasswordReset, otp=data['otp'])

        user = get_object_or_404(User, email=passwordReset.email)

        user.set_password(data['password'])
        user.save()
        passwordReset.delete()

        return Response(status=200)


class VerifyEmail(APIView):

    def post(self,request):
         
        passwordReset = get_object_or_404(PasswordReset, otp=request.data['otp'])
        user = get_object_or_404(User, email=passwordReset.email)
        user.is_verified = True
        user.registered_with_OTP = True
        user.save()
        passwordReset.delete()

        return Response(status=200)
