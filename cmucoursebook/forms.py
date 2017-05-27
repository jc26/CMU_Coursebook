from django import forms
from django.contrib.auth.forms import AuthenticationForm
from cmucoursebook.models import *
from django.core.validators import validate_email

MAX_UPLOAD_SIZE = 3000000


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label='username', widget=forms.TextInput(attrs={'placeholder': 'Username...', 'class':"form-control", 'class':"form-username"}))
    password = forms.CharField(label='password', widget=forms.PasswordInput(attrs={'placeholder': 'Password...', 'class':"form-control", 'class':"form-password"}))


class RegistrationForm(forms.Form):
    firstname = forms.CharField(max_length=20, label='First name', widget=forms.TextInput(attrs={'placeholder': 'First Name', 'class':"form-control"}))
    lastname = forms.CharField(max_length=20, label='Last name', widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'class':"form-control"}))
    email = forms.CharField(max_length=50, label='Email', widget=forms.TextInput(attrs={'placeholder': 'Email', 'class':"form-control", 'class':"form-email"}))
    username = forms.CharField(max_length=20, label='Username', widget=forms.TextInput(attrs={'placeholder': 'Username', 'class':"form-control"}))
    password1 = forms.CharField(max_length=200, label='Password', widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class':"form-control"}))
    password2 = forms.CharField(max_length=200, label='Confirm Password', widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class':"form-control"}))

    def clean(self):
        # Call superclass's validation
        cleaned_data = super(RegistrationForm, self).clean()

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
             raise forms.ValidationError("Passwords did not match.")
        return cleaned_data

    def clean_username(self):
        # Confirms that the username is not already present in the
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")
        return username

    def clean_email(self):
        # Confirms that the email is an Andrew email(XXX@xxx.cmu.edu)
        email = self.cleaned_data.get('email')
        print(email)
        validate_email(email)
        if len(email) < 7:
            raise forms.ValidationError("Email is invalid.")
        suffix = email[-7:]
        if suffix != 'cmu.edu':
            raise forms.ValidationError("Not a CMU email.")
        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('from_city', 'from_country', 'major',  'year', 'age', 'bio')

    def clean_from_city(self):
        from_city = self.cleaned_data['from_city']
        if len(from_city) > 50:
            raise forms.ValidationError('from_city is too long!')
        return from_city

    def clean_from_country(self):
        from_country = self.cleaned_data['from_country']
        if len(from_country) > 50:
            raise forms.ValidationError('from_country is too long!')
        return from_country

    def clean_major(self):
        major = self.cleaned_data['major']
        if len(major) > 50:
            raise forms.ValidationError('major is too long!')
        return major

    def clean_year(self):
        choice = ['FR', 'SO', 'JR', 'SR', 'GR']
        year = self.cleaned_data.get('year')
        if year not in choice:
            raise forms.ValidationError('invalid year!')
        return year

    def clean_age(self):
        try:
            cleaned_age = int(self.cleaned_data.get('age'))
        except:
            cleaned_age = None
        if cleaned_age and (cleaned_age < 0 or cleaned_age > 200):
            raise forms.ValidationError("age is not a reasonable positive integer.")
        return cleaned_age

    def clean_bio(self):
        bio = self.cleaned_data['bio']
        if len(bio) > 430:
            raise forms.ValidationError('bio is too long!')
        return bio


class ImageForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('img',)
        widgets = {
                    'img': forms.FileInput(),
                   }

    def clean_img(self):
        img = self.cleaned_data['img']
        if not img:
            raise forms.ValidationError('You must upload a image')
        if not img.content_type or not img.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if img.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return img


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')
        widgets = {
                    'first_name': forms.TextInput(),
                    'last_name': forms.TextInput(),
                   }


class FileForm(forms.ModelForm):
    datatype = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        choices=((True, 'Course'),(False, 'History')),
        widget=forms.RadioSelect
    )

    class Meta:
        model = DataFile
        fields = ('csvfile',)

    def clean_csvfile(self):
        csvfile = self.cleaned_data['csvfile']
        if not csvfile:
            raise forms.ValidationError('You must upload a csv file')
        return csvfile


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('difficulty', 'comment', 'skills')

    def clean_difficulty(self):
        difficulty = self.cleaned_data['difficulty']
        if not difficulty:
            raise forms.ValidationError('Invalid difficulty input')
        try:
            int_difficulty = int(difficulty)
        except:
            raise forms.ValidationError('Invalid difficulty input')
        if int_difficulty > 3 or int_difficulty < 1:
            raise forms.ValidationError('Invalid difficulty input')
        return difficulty

    def clean_comment(self):
        comment = self.cleaned_data['comment']
        if not comment:
            raise forms.ValidationError('You must make some comment!')
        if len(comment) > 800:
            raise forms.ValidationError('comments is too long!')
        return comment

    def clean_skills(self):
        skills = self.cleaned_data['skills']
        if not skills:
            raise forms.ValidationError('You must make some skills!')
        if len(skills) > 100:
            raise forms.ValidationError('skills is too long!')
        return skills