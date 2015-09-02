from django.conf import settings


# send the LABS_ONLY setting to all views
def labs_only_processor(request):
    return {'labsOnly': settings.LABS_ONLY}


# send the root url to all views
def root_url_processor(request):
    return {'rootURL': '//'+request.get_host()+'/'}
