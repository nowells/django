from django.conf.urls.defaults import *
from views import resolver_404_view, backtracking_view

urlpatterns = patterns('',
    url(r'', resolver_404_view, name='resolver_404_view'),
    url(r'^backtrack/$', backtracking_view, name='backtracking_view'),
)