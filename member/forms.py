from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import string

from member.models import User

def has_numbers(inputString):
    if not any(char.isdigit() for char in inputString):
        raise ValidationError(
            _('There is no number in the password'),
            params={'value': inputString},
        )

def has_upper_letters(inputString):
    res = True
    for ele in inputString:
        if ele.isupper():
            res = False
            break
    if res:
        raise ValidationError(
            _('There is no upper letter in the password')
        )

def has_lower_letters(inputString):
    res = True
    for ele in inputString:
        if ele.islower():
            res = False
            break
    if res:
        raise ValidationError(
            _('There is no lower letter in the password'),
            params={'value': inputString},
        )

def has_special_characters(inputString):
    res = True
    for ele in inputString:
        if ele in string.punctuation:
            res = False
            break
    if res:
        raise ValidationError(
            _('There is no special characters in the password'),
            params={'value': inputString},
        )


class UserForm(forms.Form):
    username = forms.CharField(max_length=150, strip=True, required=False)
    email = forms.EmailField(max_length=255, required=True)
    password = forms.CharField(
        min_length=8,
        required=True,
        error_messages={
            'min_length': "Password must be longer than 7 characters"
        },
        validators=[has_numbers,has_upper_letters,has_lower_letters,has_special_characters]
    )
    password_check = forms.CharField(
        min_length=8,
        required=True,
        error_messages={
            'min_length': "Password_check must be longer than 7 characters"
        }
    )

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get('password')
        password_check = cleaned_data.get('password_check')

        if not password or not password_check:
            return cleaned_data

        if password != password_check:
            raise ValidationError(
                _("The two passwords fields did not match."),
                code='invalid'
            )

        return cleaned_data


class UserResetUsernameForm(forms.Form):
    username = forms.CharField(max_length=150, strip=True, required=True)
