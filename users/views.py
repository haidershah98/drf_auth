from rest_framework.viewsets import GenericViewSet
from django.middleware import csrf
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from utils.reusable_functions import set_access_cookies, set_refresh_cookies, get_tokens_for_user, get_first_error_message_from_serializer
from .serializers import UserSerializer, LoginSerializer
from .models import BlacklistedToken


class LoginView(GenericViewSet):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def login(self, request):
        try:
            serializer = LoginSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                user = serializer.validated_data['user']
                response = Response()

                token = get_tokens_for_user(user)
                set_access_cookies(response, token['access'])
                set_refresh_cookies(response, token['refresh'])
                csrf.get_token(request)

                data = UserSerializer(user, context={'request': request}).data
                if user.current_token:
                    b_token = BlacklistedToken.objects.create(token=user.current_token)
                    b_token.save()
                user.current_token = token['access']
                user.login_attempts = 0
                user.save()
                response.status_code = status.HTTP_200_OK

                response.data = {"message": "Login successfully", "user": data}
                return response
            else:
                return Response({'message': get_first_error_message_from_serializer(serializer.errors)}, status=400)

        except Exception as e:
            return Response({'message': str(e)}, status=500)


