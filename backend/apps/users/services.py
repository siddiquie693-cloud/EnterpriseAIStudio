from django.contrib.auth import get_user_model

User = get_user_model()


def create_user(validated_data):
    password = validated_data.pop("password")

    user = User(**validated_data)
    user.set_password(password)
    user.save()

    return user
