from django import forms
from .models import Feedbacks
from .models import PriorityList

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedbacks
        fields = [
            'contact',
            'audiofile'
        ]


class PriorityForm(forms.ModelForm):
    class Meta:
        model = PriorityList
        fields = [
            'contact2',
            'emotion',
            'priority'
        ]