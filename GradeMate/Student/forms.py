from django import forms
from .models import StudentAnswer, StudentAssignment
from Teacher.models import Question, Assignment

class StudentAnswerForm(forms.ModelForm):
    question = forms.ModelChoiceField(
        queryset=Question.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent'
        }),
        label='Select Question',
        empty_label='Choose a question...'
    )
    
    class Meta:
        model = StudentAnswer
        fields = ['question', 'answer_text']
        widgets = {
            'answer_text': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'rows': 10,
                'placeholder': 'Type your answer here...'
            }),
        }
        labels = {
            'answer_text': 'Your Answer',
        }


class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = StudentAssignment
        fields = ['file', 'answer_text']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'accept': '.pdf,.doc,.docx,.txt,.png,.jpg,.jpeg,.webp'
            }),
            'answer_text': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'rows': 10,
                'placeholder': 'Type your answer here or upload a file...'
            }),
        }
        labels = {
            'file': 'Upload Answer File (PDF, DOC, Images)',
            'answer_text': 'Answer Text (Optional - can be extracted from file)',
        }
