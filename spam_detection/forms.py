from django import forms


class EmailCheckForm(forms.Form):
    sender_email = forms.EmailField(label='Sender Email')
    email_text = forms.CharField(label='Email Text', widget=forms.Textarea)