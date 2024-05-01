# Python imports
import os
from urllib.parse import urlencode, urljoin

# Django imports
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpResponseRedirect
from django.middleware.csrf import get_token
from django.utils.encoding import (
    DjangoUnicodeDecodeError,
    smart_bytes,
    smart_str,
)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View

# Third party imports
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from zxcvbn import zxcvbn

## Module imports
from plane.app.serializers import (
    ChangePasswordSerializer,
    UserSerializer,
)
from plane.authentication.utils.login import user_login
from plane.bgtasks.forgot_password_task import forgot_password
from plane.db.models import User
from plane.license.models import Instance
from plane.license.utils.instance_value import get_configuration_value
from plane.authentication.utils.host import base_host


class CSRFTokenEndpoint(APIView):

    permission_classes = [
        AllowAny,
    ]

    def get(self, request):
        # Generate a CSRF token
        csrf_token = get_token(request)
        # Return the CSRF token in a JSON response
        return Response(
            {"csrf_token": str(csrf_token)}, status=status.HTTP_200_OK
        )


def generate_password_token(user):
    uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
    token = PasswordResetTokenGenerator().make_token(user)

    return uidb64, token


class ForgotPasswordEndpoint(APIView):
    permission_classes = [
        AllowAny,
    ]

    def post(self, request):
        email = request.data.get("email")

        # Check instance configuration
        instance = Instance.objects.first()
        if instance is None or not instance.is_setup_done:
            return Response(
                {
                    "error_code": "INSTANCE_NOT_CONFIGURED",
                    "error_message": "Instance is not configured",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        (EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD) = (
            get_configuration_value(
                [
                    {
                        "key": "EMAIL_HOST",
                        "default": os.environ.get("EMAIL_HOST"),
                    },
                    {
                        "key": "EMAIL_HOST_USER",
                        "default": os.environ.get("EMAIL_HOST_USER"),
                    },
                    {
                        "key": "EMAIL_HOST_PASSWORD",
                        "default": os.environ.get("EMAIL_HOST_PASSWORD"),
                    },
                ]
            )
        )

        if not (EMAIL_HOST and EMAIL_HOST_USER and EMAIL_HOST_PASSWORD):
            return Response(
                {
                    "error_code": "SMTP_NOT_CONFIGURED",
                    "error_message": "SMTP is not configured. Please contact your admin",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_email(email)
        except ValidationError:
            return Response(
                {
                    "error_code": "INVALID_EMAIL",
                    "error_message": "Please enter a valid email",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the user
        user = User.objects.filter(email=email).first()
        if user:
            # Get the reset token for user
            uidb64, token = generate_password_token(user=user)
            current_site = request.META.get("HTTP_ORIGIN")
            # send the forgot password email
            forgot_password.delay(
                user.first_name, user.email, uidb64, token, current_site
            )
            return Response(
                {"message": "Check your email to reset your password"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "error_code": "INVALID_EMAIL",
                "error_message": "Please check the email",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class ResetPasswordEndpoint(View):

    def post(self, request, uidb64, token):
        try:
            # Decode the id from the uidb64
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            # check if the token is valid for the user
            if not PasswordResetTokenGenerator().check_token(user, token):
                url = urljoin(
                    base_host(request=request),
                    "accounts/reset-password?"
                    + urlencode(
                        {
                            "error_code": "INVALID_TOKEN",
                            "error_message": "Token is invalid",
                        }
                    ),
                )
                return HttpResponseRedirect(url)

            password = request.POST.get("password", False)

            if not password:
                url = urljoin(
                    base_host(request=request),
                    "?" + urlencode({"error": "Password is required"}),
                )
                return HttpResponseRedirect(url)

            # Check the password complexity
            results = zxcvbn(password)
            if results["score"] < 3:
                url = urljoin(
                    base_host(request=request),
                    "accounts/reset-password?"
                    + urlencode(
                        {
                            "error_code": "INVALID_PASSWORD",
                            "error_message": "The password is not a valid password",
                        }
                    ),
                )
                return HttpResponseRedirect(url)

            # set_password also hashes the password that the user will get
            user.set_password(password)
            user.is_password_autoset = False
            user.save()

            url = urljoin(
                base_host(request=request),
                "accounts/sign-in?" + urlencode({"success", True}),
            )
            return HttpResponseRedirect(url)
        except DjangoUnicodeDecodeError:
            url = urljoin(
                base_host(request=request),
                "accounts/reset-password?"
                + urlencode(
                    {
                        "error_code": "INVALID_TOKEN",
                        "error_message": "The password token is not valid",
                    }
                ),
            )
            return HttpResponseRedirect(url)


class ChangePasswordEndpoint(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        user = User.objects.get(pk=request.user.id)
        if serializer.is_valid():
            if not user.check_password(serializer.data.get("old_password")):
                return Response(
                    {"error": "Old password is not correct"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # check the password score
            results = zxcvbn(serializer.data.get("new_password"))
            if results["score"] < 3:
                return Response(
                    {
                        "error_code": "INVALID_PASSWORD",
                        "error_message": "Invalid password.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # set_password also hashes the password that the user will get
            user.set_password(serializer.data.get("new_password"))
            user.is_password_autoset = False
            user.save()
            user_login(user=user, request=request)
            return Response(
                {"message": "Password updated successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "error_code": "INVALID_PASSWORD",
                "error_message": "Invalid passwords provided",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class SetUserPasswordEndpoint(APIView):
    def post(self, request):
        user = User.objects.get(pk=request.user.id)
        password = request.data.get("password", False)

        # If the user password is not autoset then return error
        if not user.is_password_autoset:
            return Response(
                {
                    "error": "Your password is already set please change your password from profile"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check password validation
        if not password and len(str(password)) < 8:
            return Response(
                {
                    "error_code": "INVALID_PASSWORD",
                    "error_message": "Invalid password.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = zxcvbn(password)
        if results["score"] < 3:
            return Response(
                {
                    "error_code": "INVALID_PASSWORD",
                    "error_message": "Invalid password.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Set the user password
        user.set_password(password)
        user.is_password_autoset = False
        user.save()
        # Login the user as the session is invalidated
        user_login(user=user, request=request)
        # Return the user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)