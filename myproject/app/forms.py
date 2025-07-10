from django import forms
from django.contrib.auth.models import User
from .models import Job, Profile


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'category', 'budget']


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES)
    skills = forms.CharField(widget=forms.Textarea, required=False)
    experience = forms.CharField(required=False)  # Use CharField for flexibility
    github = forms.URLField(required=False)
    resume = forms.FileField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'skills', 'experience', 'github', 'resume']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()
            profile, created = Profile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data['role']
            profile.skills = self.cleaned_data.get('skills', '')
            profile.experience = self.cleaned_data.get('experience', '')
            profile.github = self.cleaned_data.get('github', '')
            if self.cleaned_data.get('resume'):
                profile.resume = self.cleaned_data['resume']
            profile.save()
        return user
