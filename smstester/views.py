# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.accountmanagement.models import OrganizationSettings
from datawinners.main.utils import get_database_manager, get_db_manager_for
from datawinners.smstester.forms import SMSTesterForm
from mangrove.datastore.database import get_db_manager
from mangrove.errors.MangroveException import MangroveException
from mangrove.transport.submissions import SubmissionHandler, Request



def index(request):
    message = ""
    if request.method == 'POST':
        form = SMSTesterForm(request.POST)
        if form.is_valid():
            _message = form.cleaned_data["message"]
            _from = form.cleaned_data["from_number"]
            _to = form.cleaned_data["to_number"]
            manager = get_db_manager_for(_to)
            try:
                s = SubmissionHandler(dbm=manager)
                response = s.accept(Request(transport="sms", message=_message, source=_from, destination=_to))
                message = response.message
            except MangroveException as exception:
                message = exception.message
    else:
        form = SMSTesterForm()

    return render_to_response('smstester/index.html',
                              {'form': form, 'message': message}, context_instance=RequestContext(request))
