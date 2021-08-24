from django.conf.urls import url
from django.urls import include, path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    url(r'admin/', admin.site.urls),
    # Login/logout view for browsable API
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'gamecore/', include('gamecore.urls')),
    url(r'member/', include('member.urls')),
    path('accounts/login/', auth_views.LoginView.as_view()),


    #
    #url(r'^admin/', admin.site.urls),
    #url(r'', include('blog.urls',namespace='blog')),

]

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)