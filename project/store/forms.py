from django import forms
from django.forms.models import BaseInlineFormSet
from .models import Comment, Contact

email_errors = {
    'required': 'هذا الحقل مطلوب.',
    'invalid': 'أدخل بريد الكتروني صالح.',
}

errors_required = {
    'required': 'هذا الحقل مطلوب.',
}

class RequiredInlineFormSet(BaseInlineFormSet):
    """
    Generates an inline formset that is required
    """

    def _construct_form(self, i, **kwargs):
        """
        Override the method to change the form attribute empty_permitted
        """
        form = super(RequiredInlineFormSet, self)._construct_form(i, **kwargs)
        form.empty_permitted = False
        return form

class NewComment(forms.ModelForm):
    name = forms.CharField(error_messages=errors_required)
    email = forms.EmailField(error_messages=email_errors)
    description = forms.Textarea()
    class Meta:
        model = Comment
        fields = ['name', 'email', 'description']

class ContactForm(forms.ModelForm):
    email = forms.EmailField(error_messages=email_errors)
    description = forms.Textarea()
    class Meta:
        model = Contact
        fields = ['email', 'description']