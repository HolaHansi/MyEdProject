from django.conf import settings


# send the LABS_ONLY setting to all views
def labs_only_processor(request):
    return {'labsOnly': settings.LABS_ONLY}
