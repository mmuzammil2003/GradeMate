from django import forms
from .models import Question

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'model_answer']
        widgets = {
            'question_text': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Enter the question text...'
            }),
            'model_answer': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'rows': 6,
                'placeholder': 'Enter the model/expected answer...'
            }),
        }
        labels = {
            'question_text': 'Question Text',
            'model_answer': 'Model Answer',
        }
