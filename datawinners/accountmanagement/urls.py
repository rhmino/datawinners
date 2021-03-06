# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.core.urlresolvers import reverse

from datawinners.accountmanagement.forms import FullRegistrationForm, LoginForm, PasswordSetForm
from datawinners.accountmanagement.forms import MinimalRegistrationForm, ProRegistrationForm, ProSMSRegistrationForm
from datawinners.accountmanagement.views import custom_reset_password, custom_password_reset_confirm, access_denied
from views import settings, new_user, edit_user, edit_user_profile, users, custom_login, registration_complete, trial_expired, upgrade, delete_users, registration_activation_complete
from datawinners.accountmanagement.registration_views import register_view

admin.autodiscover()
from django.contrib.auth import views as auth_views


urlpatterns = patterns('',
                       (r'^register/$', register_view,
                        {'form_class': FullRegistrationForm, 'template_name': 'registration/register.html',
                         'backend': 'datawinners.accountmanagement.registration_backend.RegistrationBackend'}),
                       (r'^en/register/$', register_view,
                        {'language': 'en', 'form_class': FullRegistrationForm, 'template_name': 'registration/register.html',
                         'backend': 'datawinners.accountmanagement.registration_backend.RegistrationBackend'}),
                       (r'^fr/register/$', register_view,
                        {'language': 'fr', 'form_class': FullRegistrationForm, 'template_name': 'registration/register.html',
                         'backend': 'datawinners.accountmanagement.registration_backend.RegistrationBackend'}),
                       (r'^register/pro/$', register_view,
                        {'form_class': ProRegistrationForm, 'template_name': 'registration/register.html',
                         'backend': 'datawinners.accountmanagement.registration_backend.RegistrationBackend'}),
                       (r'^en/register/pro/$', register_view,
                        {'language': 'en', 'form_class': ProRegistrationForm, 'template_name': 'registration/register.html',
                         'backend': 'datawinners.accountmanagement.registration_backend.RegistrationBackend'}),
                       (r'^fr/register/pro/$', register_view,
                        {'language': 'fr', 'form_class': ProRegistrationForm, 'template_name': 'registration/register.html',
                         'backend': 'datawinners.accountmanagement.registration_backend.RegistrationBackend'}),
                       (r'^register/prosms/$', register_view,
                        {'form_class': ProSMSRegistrationForm, 'template_name': 'registration/register.html',
                         'backend': 'datawinners.accountmanagement.registration_backend.RegistrationBackend'}),
                       (r'^en/register/prosms/$', register_view,
                        {'language': 'en', 'form_class': ProSMSRegistrationForm, 'template_name': 'registration/register.html',
                         'backend': 'datawinners.accountmanagement.registration_backend.RegistrationBackend'}),
                       (r'^fr/register/prosms/$', register_view,
                        {'language': 'fr', 'form_class': ProSMSRegistrationForm, 'template_name': 'registration/register.html',
                         'backend': 'datawinners.accountmanagement.registration_backend.RegistrationBackend'}),
                       (r'^register/trial/$', register_view,
                        {'form_class': MinimalRegistrationForm, 'template_name': 'registration/register_for_trial.html',
                         'backend': 'datawinners.accountmanagement.registration_backend.RegistrationBackend'}),
                       (r'^en/register/trial/$', register_view,
                        {'language': 'en', 'form_class': MinimalRegistrationForm, 'template_name': 'registration/register_for_trial.html',
                         'backend': 'datawinners.accountmanagement.registration_backend.RegistrationBackend'}),
                       (r'^fr/register/trial/$', register_view,
                        {'language': 'fr', 'form_class': MinimalRegistrationForm, 'template_name': 'registration/register_for_trial.html',
                         'backend': 'datawinners.accountmanagement.registration_backend.RegistrationBackend'}),
                       url(r'^login/$', custom_login,
                           {'template_name': 'registration/login.html', 'authentication_form': LoginForm},
                           name='auth_login'),
                       url(r'^en/login/$', custom_login,
                           {'language': 'en', 'template_name': 'registration/login.html', 'authentication_form': LoginForm},
                           name='auth_login'),
                       url(r'^fr/login/$', custom_login,
                           {'language': 'fr', 'template_name': 'registration/login.html', 'authentication_form': LoginForm},
                           name='auth_login'),
                       url(r'^en/login/$', custom_login,
                           {'language': 'en', 'template_name': 'registration/login.html', 'authentication_form': LoginForm},
                           name='auth_login'),
                       url(r'^fr/login/$', custom_login,
                           {'language': 'fr', 'template_name': 'registration/login.html', 'authentication_form': LoginForm},
                           name='auth_login'),
                       url(r'^activate/complete/$', registration_activation_complete),
                       url(r'^password/reset/$', custom_reset_password, name='auth_password_reset'),
                       url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>.+)/$',
                           custom_password_reset_confirm,
                           {'set_password_form': PasswordSetForm,
                            'template_name': 'registration/password_reset_confirm.html'
                           },
                           name='auth_password_reset_confirm'),
                       url(r'^datasender/activate/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>.+)/$',
                           custom_password_reset_confirm, {'set_password_form': PasswordSetForm},
                           name='activate_datasender_account'),
                       ('', include('registration.backends.default.urls')),
                       (r'^registration_complete$', registration_complete),
                       url(r'^admin/', include(admin.site.urls)),
                       (r'^account/$', settings),
                       (r'^accessdenied/$', access_denied),
                       (r'^account/user/new/$', new_user),
                       (r'^profile/$', edit_user),
                       (r'^account/users/(?P<user_id>[0-9]+)/edit', edit_user_profile),
                       (r'^account/users/$', users),
                       (r'^account/users/delete/$', delete_users),
                       (r'^trial/expired/$', trial_expired),
                       url(r'^upgrade/$', upgrade, name='default_upgrade'),
                       url(r'^fr/upgrade/$', upgrade, {'language': 'fr'}),
                       url(r'^en/upgrade/$', upgrade, {'language': 'en'}),
                       url(r'^upgrade/prosms/$', upgrade, {'account_type':'prosms'}, name='prosms_upgrade'),
                       (r'^en/upgrade/prosms/$', upgrade, {'language': 'en', 'account_type':'prosms'}),
                       (r'^fr/upgrade/prosms/$', upgrade, {'language': 'fr', 'account_type':'prosms'}),
                       url(r'^upgrade/(?P<token>\w+)/$', upgrade, name='upgrade_from_mail'),
)
