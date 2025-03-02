from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def validate(self, attrs):
        id = self.context.get('id', None)
        email = attrs.get('email', None)
        username = attrs.get('username', None)

        if id:
            if User.objects.filter(username=username, deleted=False).exclude(id=id).exists():
                raise serializers.ValidationError('User with this username already exists')
            elif email and User.objects.filter(email=email, deleted=False).exclude(id=id).exists():
                raise serializers.ValidationError('User with this Email already exists')
        else:
            if User.objects.filter(username=username, deleted=False).exists():
                raise serializers.ValidationError('User with this username already exists')
            elif email and User.objects.filter(email=email, deleted=False).exists():
                raise serializers.ValidationError('User with this Email already exists')
        return attrs


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100, required=True)
    password = serializers.CharField(max_length=100, required=True)

    def validate(self, attrs):
        username = attrs.get('username', None)
        password = attrs.get("password", None)
        if username and password:
            user = authenticate(username=username, password=password, deleted=False)
            if not user:
                if User.objects.filter(username=username, deleted=False).exists():
                    user_obj = User.objects.get(username=username, deleted=False)
                    if user_obj.login_attempts <= 2:
                        user_obj.login_attempts += 1
                        user_obj.save()
                    else:
                        if user_obj.is_blocked:
                            raise serializers.ValidationError('Your account has been blocked. Please contact support')
                        user_obj.is_blocked = True
                        user_obj.save()
                        raise serializers.ValidationError('Your account has been blocked. Please contact support')
                raise serializers.ValidationError('Invalid credentials')
            if user.is_blocked:
                raise serializers.ValidationError('Your account has been blocked, Please contact support')
        else:
            raise serializers.ValidationError('Username or Password is missing')

        attrs['user'] = user
        return attrs

