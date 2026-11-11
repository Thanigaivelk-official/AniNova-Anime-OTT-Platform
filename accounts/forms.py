from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
import os


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'Password (min 8 characters)'}),
        min_length=8
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'Confirm Password'}),
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'Choose Otaku Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'Email address'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'Last Name'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_confirm')
        if p1 and p2 and p1 != p2:
            self.add_error('password_confirm', "Passwords do not match.")
        return cleaned_data


class UserAccountUpdateForm(forms.ModelForm):
    """Allows user to update username, email, and real name."""
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary'}),
            'email': forms.EmailInput(attrs={'class': 'form-control bg-dark text-light border-secondary'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This username is already taken.")
        return username


class UserProfilePhotoForm(forms.ModelForm):
    """Specialized form for Avatar photo upload with format and file size validation."""
    class Meta:
        model = UserProfile
        fields = ['avatar']

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # 1. Format check: JPG, JPEG, PNG, WEBP
            ext = os.path.splitext(avatar.name)[1].lower()
            valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
            if ext not in valid_extensions:
                raise forms.ValidationError("Unsupported file format. Please upload JPG, JPEG, PNG, or WEBP.")

            # 2. File size limit: 5MB
            max_size_bytes = 5 * 1024 * 1024
            if avatar.size > max_size_bytes:
                raise forms.ValidationError("Image file size too large. Maximum allowed size is 5MB.")

        return avatar


class UserProfileInfoForm(forms.ModelForm):
    """Allows updating phone, bio, and favorite anime title."""
    class Meta:
        model = UserProfile
        fields = ['phone', 'favorite_anime', 'bio']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': '+91 9876543210'}),
            'favorite_anime': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': 'e.g. Demon Slayer, Attack on Titan'}),
            'bio': forms.Textarea(attrs={'class': 'form-control bg-dark text-light border-secondary', 'rows': 3, 'placeholder': 'Share your anime tastes, favorite waifus/husbandos...'}),
        }
