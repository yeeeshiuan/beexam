from rest_framework import serializers
from member.models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']


class FormUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, allow_blank=True)
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(
        min_length=8,
        error_messages={
            'min_length': "Password must be longer than 7 characters"
        }
    )
    password_check = serializers.CharField()

    def validate(self, data):
        if not data['password']:
            raise serializers.ValidationError("lack of the parameters(password)")
        elif not data['password_check']:
            raise serializers.ValidationError("lack of the parameters(password)")
        elif data['password'] != data['password_check']:
            raise serializers.ValidationError("The two password fields did not match.")

        if data['email']:
            raise serializers.ValidationError("lack of the parameters(email)")

        return data
