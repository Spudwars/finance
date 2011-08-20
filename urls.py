from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template


urlpatterns = patterns("finance.views",
    url(r"^test-view/$", 'test_views', name="test_views"),
)