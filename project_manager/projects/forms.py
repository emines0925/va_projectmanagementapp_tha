from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import Project

class UserSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. Please enter a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class UserLoginForm(AuthenticationForm):
    """
    A form for user authentication that customizes Django's standard AuthenticationForm.
    This form adds CSS classes and placeholder text to the HTML widgets to improve
    their appearance.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customize the widget for the username field
        self.fields['username'].widget.attrs.update({
            'class': 'form-control mb-2',  # Add CSS class (e.g., for Bootstrap)
            'placeholder': 'Username'      # Placeholder text for the input box
        })

        # Customize the widget for the password field
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',       # Add CSS class
            'placeholder': 'Password'      # Placeholder text for the input box
        })

class ProjectForm(forms.ModelForm):
    """
    A ModelForm for creating and updating Project instances.
    Django's ModelForm automatically builds a form from your model's fields,
    which saves a lot of time and boilerplate code.
    """
    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'end_date']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the project title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5, # Make the text area a bit taller
                'placeholder': 'Provide a detailed description of the project'
            }),
            'start_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'end_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
        }
        
        labels = {
            'name': 'Project Title',
            'description': 'Project Description',
        }

class AddUserToProjectForm(forms.Form):
    """
    A form to add a user to a project with a specific role.
    """
   
    ROLE_CHOICES = [
        ('Editor', 'Editor'),
        ('Reader', 'Reader'),
    ]

    username = forms.CharField(
        max_length=150,
        label="Enter Username",
        widget=forms.TextInput(attrs={'placeholder': 'e.g., jane.doe'})
    )

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label="Assign Role"
    )

    def clean_username(self):
        """
        Custom validation for the username field.
        This method ensures that the view doesn't crash if an invalid username is entered.
        """
        username = self.cleaned_data.get('username')
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with this username was not found.")
        return username