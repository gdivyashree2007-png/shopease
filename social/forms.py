from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Profile


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username or email",
        widget=forms.TextInput(attrs={
            "autofocus": True,
            "autocomplete": "username",
            "autocapitalize": "none",
            "spellcheck": "false",
            "placeholder": "Username or registered email",
        }),
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "autocomplete": "current-password",
            "placeholder": "Your password",
        }),
    )
    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "Invalid username/email or password.",
    }

    def clean(self):
        identifier = (self.cleaned_data.get("username") or "").strip()
        if identifier:
            matches = User.objects.filter(username__iexact=identifier)
            if matches.count() == 1:
                self.cleaned_data["username"] = matches.get().get_username()
            elif not matches.exists() and "@" in identifier:
                email_matches = User.objects.filter(email__iexact=identifier)
                if email_matches.count() == 1:
                    self.cleaned_data["username"] = email_matches.get().get_username()
        return super().clean()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("bio", "picture")
        widgets = {"bio": forms.Textarea(attrs={"rows": 4, "maxlength": 280, "placeholder": "A little about you…"})}


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("content", "image")
        widgets = {"content": forms.Textarea(attrs={"rows": 4, "maxlength": 2000, "placeholder": "What’s on your mind?"})}
