from django import forms
from django_recaptcha.fields import ReCaptchaField


class FastaUploadForm(forms.Form):
    fasta_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "rows": 12,
            "cols": 80,
            "placeholder": "Paste FASTA sequence here..."
        })
    )

    fasta_file = forms.FileField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get("fasta_text")
        file = cleaned_data.get("fasta_file")

        if not text and not file:
            raise forms.ValidationError("Provide either FASTA text or a file.")

        if text and file:
            raise forms.ValidationError("Use only one input method.")

        return cleaned_data
    

class ContactForm(forms.Form):
    subject = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    message = forms.CharField(widget=forms.Textarea(attrs={
        "rows":10,
        "cols":40,
        "placeholder":"Type your message here",}),
        required=True)