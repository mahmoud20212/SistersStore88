from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

username_errors = {
    'required': 'هذا الحقل مطلوب.',
    'min_length': 'إسم المستخدم يجب أن لا يقل عن 4 عناصر.',
}
first_name_errors = {
    'required': 'هذا الحقل مطلوب.',
    'min_length': 'الإسم الأول يجب أن لا يقل عن 4 عناصر.',
}
last_name_errors = {
    'required': 'هذا الحقل مطلوب.',
    'min_length': 'الإسم الأخير يجب أن لا يقل عن 4 عناصر.',
}
password_errors = {
    'required': 'هذا الحقل مطلوب.',
    'min_length': 'كلمة المرور يجب  ألا تقل عن 8 عناصر.',
}
email_errors = {
    'required': 'هذا الحقل مطلوب.',
    'invalid': 'أدخل بريد الكتروني صالح.',
}
errors_required = {
    'required': 'هذا الحقل مطلوب.',
}

class UserCreationForm(forms.ModelForm):
    username = forms.CharField(min_length=4, error_messages=username_errors)
    first_name = forms.CharField(min_length=4, error_messages=first_name_errors)
    last_name = forms.CharField(min_length=4, error_messages=last_name_errors)
    email = forms.EmailField(error_messages=email_errors)
    password1 = forms.CharField(min_length=8, error_messages=password_errors)
    password2 = forms.CharField(min_length=8, error_messages=password_errors)
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name',
                  'last_name', 'password1', 'password2']
    
    # def __init__(self, *args, **kwargs):
    #     super(UserCreationForm, self).__init__(*args, **kwargs)
    #     # self.fields['username'].error_messages = {'required': 'msg'}

    #     for field in self.fields.values():
    #         field.error_messages = {'required':'هذا الحقل مطلوب.'}

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] != cd['password2']:
            raise forms.ValidationError('كلمة المرور غير مطابقة.')
        return cd['password2']

    def clean_username(self):
        cd = self.cleaned_data
        if User.objects.filter(username=cd['username']).exists():
            raise forms.ValidationError('يوجد إسم مستخدم مسجل بهذا الإسم.')
        return cd['username']

    def clean_email(self):
        cd = self.cleaned_data
        if User.objects.filter(email=cd['email']).exists():
            raise forms.ValidationError('هذا البريد الإلكتروني مسجل مسبقا.')
        return cd['email']

class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(min_length=4, error_messages=first_name_errors)
    last_name = forms.CharField(min_length=4, error_messages=last_name_errors)
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class UserChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput, error_messages=errors_required)
    new_password1 = forms.CharField(widget=forms.PasswordInput, min_length=8, error_messages=password_errors)
    new_password2 = forms.CharField(widget=forms.PasswordInput, min_length=8, error_messages=password_errors)

    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']

    def clean_new_password2(self):
        cd = self.cleaned_data
        if cd['new_password1'] != cd['new_password2']:
            raise forms.ValidationError('كلمة المرور غير مطابقة.')
        return cd['new_password2']


