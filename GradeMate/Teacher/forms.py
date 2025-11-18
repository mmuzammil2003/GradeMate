from django import forms
from .models import Question, Assignment, Subject, Classroom
from Student.models import StudentAssignment

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


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'subject', 'classroom', 'key_answer_file', 'key_answer_text', 'due_date', 'max_score']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'placeholder': 'Enter assignment title...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'rows': 5,
                'placeholder': 'Enter assignment description/instructions...'
            }),
            'subject': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent'
            }),
            'classroom': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent'
            }),
            'key_answer_file': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'accept': '.pdf,.doc,.docx,.txt'
            }),
            'key_answer_text': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'rows': 6,
                'placeholder': 'Enter key answer text (optional, can be extracted from file)...'
            }),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'type': 'datetime-local'
            }),
            'max_score': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'step': '0.01',
                'min': '0'
            }),
        }
        labels = {
            'title': 'Assignment Title',
            'description': 'Description/Instructions',
            'subject': 'Subject',
            'classroom': 'Class/Classroom',
            'key_answer_file': 'Key Answer File',
            'key_answer_text': 'Key Answer Text (Optional)',
            'due_date': 'Due Date',
            'max_score': 'Maximum Score',
        }


class SubmissionGradingForm(forms.ModelForm):
    class Meta:
        model = StudentAssignment
        fields = ['score', 'feedback']
        widgets = {
            'score': forms.NumberInput(attrs={
                'class': 'w-full border border-gray-300 rounded-md px-3 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'step': '0.01',
                'min': '0',
                'placeholder': 'e.g., 85'
            }),
            'feedback': forms.Textarea(attrs={
                'class': 'w-full border border-gray-300 rounded-md px-3 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'rows': 8,
                'placeholder': 'Provide constructive feedback...'
            }),
        }
        labels = {
            'score': 'Score',
            'feedback': 'Feedback for Student',
        }
