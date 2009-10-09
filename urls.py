from django.conf.urls.defaults import *

urlpatterns = patterns('dtinyurl.views',
    (r'(?P<tiny_id>[^/]+)/(.*)$', 'handle_tiny_url'),
)

