from django.conf.urls import url

from djkatha.dashboard import views

urlpatterns = [
    url(
        r'^$',
        views.home, name='home'
    ),
]
