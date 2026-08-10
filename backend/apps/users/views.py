from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
)

from .serializers import (
    ChangePasswordSerializer,
    EmailVerificationSerializer,
    UserLoginSerializer,
    UserLogoutSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
)
from .services import generate_email_verification_token


class UserRegistrationAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=UserRegistrationSerializer,
        responses={201: UserRegistrationSerializer},
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            uid, token = generate_email_verification_token(user)

            return Response(
                {
                    "message": "User registered successfully.",
                    "email": user.email,
                    "username": user.username,
                    "verification": {
                        "uid": uid,
                        "token": token,
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=EmailVerificationSerializer,
        responses={
            200: {"description": "Email verified successfully."},
            400: {"description": "Invalid or expired verification link."},
        },
    )
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            user.is_verified = True
            user.save(update_fields=["is_verified"])

            return Response(
                {"message": "Email verified successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserLoginAPIView(TokenObtainPairView):
    serializer_class = UserLoginSerializer


class UserRefreshTokenAPIView(TokenRefreshView):
    pass


class UserLogoutAPIView(TokenBlacklistView):
    serializer_class = UserLogoutSerializer


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        responses=UserProfileSerializer,
    )
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(request=UserProfileSerializer, responses=UserProfileSerializer)
    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                },
            },
        },
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )

        if serializer.is_valid():
            user = request.user

            user.set_password(serializer.validated_data["new_password"])
            user.save(update_fields=["password"])

            refresh_token = request.data.get("refresh_token")

            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)

                    if token["user_id"] != str(user.id):
                        return Response(
                            {
                                "refresh_token": (
                                    "Refresh token does not belong to this user."
                                )
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    token.blacklist()

                except Exception:
                    return Response(
                        {"refresh_token": "Invalid refresh token."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            return Response(
                {"message": "Password changed successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
