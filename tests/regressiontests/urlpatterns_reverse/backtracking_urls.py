from django.conf.urls.defaults import *
from views import continue_resolving_view, backtracking_view

urlpatterns = patterns('',
    url(r'', continue_resolving_view, name='continue_resolving_view'),
    url(r'^backtrack/$', backtracking_view, name='backtracking_view'),
)
