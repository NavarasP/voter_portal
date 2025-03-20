from django import forms
from .models import *

class VoterForm(forms.ModelForm):
    class Meta:
        model = Voter
        fields = '__all__'

    # def clean_aadhaar_num(self):
    #     aadhaar_num = self.cleaned_data.get('aadhaar_num')
    #     if Voter.objects.filter(aadhaar_num=aadhaar_num).exists():
    #         raise forms.ValidationError("This Aadhaar number is already registered.")
    #     return aadhaar_num


class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = '__all__'

class ConstituencyForm(forms.ModelForm):
    class Meta:
        model = Constituency
        fields = '__all__'