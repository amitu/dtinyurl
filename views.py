from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.urlresolvers import get_mod_func

from dtinyurl.models import TinyURL

def handle_tiny_url(request, tiny_id):
    tiny_url = get_object_or_404(TinyURL, tiny_id=tiny_id)
    if tiny_url.action == "r":
        return HttpResponseRedirect(tiny_url.data)
    elif tiny_url.action == "m":
        return tiny_url.content_object.render(request)
    elif tiny_url.action == "v":
        mod_name, view_name = get_mod_func(tiny_url.data)
        view = getattr(__import__(mod_name, {}, {}, ['']), view_name)
        return view(request, tiny_url.content_object)
    elif tiny_url.action == "i":
        return render_to_response(
            "dtinyurl/inline.html", { 'tiny_url': tiny_url },
            context_instance = RequestContext(request)
        )
    else:
        raise AssertionError("bad action: %s" % tiny_url.action)
