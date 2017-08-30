from django.utils import timezone

from .models import LastSeen

class LastSeenMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated():
            ls = request.user.lastseen
            ls.when = timezone.now()
            ls.save(update_fields=['when'])
        return None