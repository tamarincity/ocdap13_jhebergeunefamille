from django import forms


class UploadFileForm(forms.Form):
    file_picture_front_of_house = forms.ImageField(required=False)
    file_picture_of_bedroom = forms.ImageField(required=False)
    file_other_picture = forms.ImageField(required=False)
