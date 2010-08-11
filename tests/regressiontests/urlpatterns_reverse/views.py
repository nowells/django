from django.core.urlresolvers import Resolver404

def empty_view(request, *args, **kwargs):
    pass

def kwargs_view(request, arg1=1, arg2=2):
    pass

def absolute_kwargs_view(request, arg1=1, arg2=2):
    pass

def resolver_404_view(request, *args, **kwargs):
    raise Resolver404

def backtracking_view(request, *args, **kwargs):
    pass

class ViewClass(object):
    def __call__(self, request, *args, **kwargs):
        pass

view_class_instance = ViewClass()
