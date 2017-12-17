from django.forms.widgets import Input


class DateInput(Input):
    input_type = 'date'
    template_name = 'django/forms/widgets/date.html'


class AdminDateInputWidget(DateInput):
    def __init__(self, attrs=None):
        final_attrs = {'class': 'vDateField'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminDateInputWidget, self).__init__(attrs=final_attrs)