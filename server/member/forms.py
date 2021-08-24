from django import forms
from django.contrib import messages

LOGIN_SYSTEM_CHOICES = (
    (1, '後台系統'),
    (2, '代理後台系統'),
    (3, '玩家後台系統')
)

class LoginForm(forms.Form):
    user_id  = forms.CharField(label="帳號",max_length=20)
    user_pwd = forms.CharField(label="密碼",widget=forms.PasswordInput())
    login_system = forms.ChoiceField(
        widget=forms.RadioSelect, choices=LOGIN_SYSTEM_CHOICES)

class AccountForm(forms.Form):
    user_id  = forms.CharField(label="帳號",max_length=20)
    user_pwd = forms.CharField(label="密碼",widget=forms.PasswordInput())
    login_system = forms.ChoiceField(
        widget=forms.RadioSelect, choices=LOGIN_SYSTEM_CHOICES)

class PasswordChangeForm(forms.Form):
    error_messages = {
        'password_mismatch': "新舊密碼不一致。",
        'password_incorrect': "舊密碼不正確，請重新輸入。",
    }
    old_password = forms.CharField(
        label="舊密碼",
        strip=False,
        max_length=20, 
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'autofocus': True, 'class': 'form-control', 'placeholder': "請輸入舊密碼"}),
    )

    new_password1 = forms.CharField(
        label="新密碼",
        strip=False,
        max_length=20, 
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control', 'placeholder': "請輸入新密碼"}),
    )
    new_password2 = forms.CharField(
        label="新密碼確認",
        strip=False,
        max_length=20, 
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control', 'placeholder': "請再次輸入新密碼"}),
    )

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2

# 玩家後台系統專用 start --------------------------------------------------
class LoginForm1(forms.Form):
    user_id  = forms.IntegerField(label="帳號")
    login_system = forms.ChoiceField(
        widget=forms.RadioSelect, choices=LOGIN_SYSTEM_CHOICES)
#   密碼版
class LoginForm2(forms.Form):
    user_id  = forms.CharField(label="帳號",max_length=20)
    user_pwd = forms.CharField(label="密碼",widget=forms.PasswordInput())
    login_system = forms.ChoiceField(
        widget=forms.RadioSelect, choices=LOGIN_SYSTEM_CHOICES)

# 玩家後台系統專用 end ------------------------------------------------------

