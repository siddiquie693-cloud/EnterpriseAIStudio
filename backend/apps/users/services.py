from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()


def create_user(validated_data):
    password = validated_data.pop("password")

    user = User(**validated_data)
    user.set_password(password)
    user.save()

    uid, token = generate_email_verification_token(user)

    return user, uid, token


def generate_email_verification_token(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    return uid, token
