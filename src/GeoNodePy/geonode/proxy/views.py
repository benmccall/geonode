from django.http import HttpResponse
from httplib import HTTPConnection
from urlparse import urlsplit, urlparse
import httplib2
from django.conf import settings
from geonode.maps.models import Layer
from django.shortcuts import get_object_or_404


def proxy(request):
    if 'url' not in request.GET:
        return HttpResponse(
                "The proxy service requires a URL-encoded URL as a parameter.",
                status=400,
                content_type="text/plain"
                )

    url = urlsplit(request.GET['url'])
    locator = url.path
    if url.query != "":
        locator += '?' + url.query
    if url.fragment != "":
        locator += '#' + url.fragment

    headers = {}
    if settings.SESSION_COOKIE_NAME in request.COOKIES:
        headers["Cookie"] = request.META["HTTP_COOKIE"]

    if request.method in ("POST", "PUT") and "CONTENT_TYPE" in request.META:
        headers["Content-Type"] = request.META["CONTENT_TYPE"]

    conn = HTTPConnection(url.hostname, url.port)
    conn.request(request.method, locator, request.raw_post_data, headers)
    result = conn.getresponse()
    response = HttpResponse(
            result.read(),
            status=result.status,
            content_type=result.getheader("Content-Type", "text/plain")
            )
    return response

def geoserver_rest_proxy(request, proxy_path, downstream_path):
    if not request.user.is_authenticated():
        return HttpResponse(
            "You must be logged in to access GeoServer",
            mimetype="text/plain",
            status=401)

    def strip_prefix(path, prefix):
        assert path.startswith(prefix)
        return path[len(prefix):]

    path = strip_prefix(request.get_full_path(), proxy_path)
    url = "".join([settings.GEOSERVER_BASE_URL, downstream_path, path])

    http = httplib2.Http()
    http.add_credentials(*settings.GEOSERVER_CREDENTIALS)
    headers = dict()

    if request.method in ("POST", "PUT") and "CONTENT_TYPE" in request.META:
        headers["Content-Type"] = request.META["CONTENT_TYPE"]

    response, content = http.request(
        url, request.method,
        body=request.raw_post_data or None,
        headers=headers)

    return HttpResponse(
        content=content,
        status=response.status,
        mimetype=response.get("content-type", "text/plain"))


def download(request, service):
    params = request.GET
    service=service.replace("_","/")
    url = settings.GEOSERVER_BASE_URL + service + "?" + params.urlencode()

    if service == "wfs":
        layername = params.get("typename")
    elif service == "wcs":
        layername = params.get("coverage")
    else: #wms and wms/kml
        layername = params.get("layers")

    layer = get_object_or_404(Layer, typename=layername)

    if layer.is_downloadable and request.user.has_perm('maps.view_layer', obj=layer):
        http = httplib2.Http()
        http.add_credentials(*settings.GEOSERVER_CREDENTIALS)
        headers = dict()

        download_response, content = http.request(
            url, request.method,
            body=None,
            headers=headers)

        content_disposition = None
        if 'content_disposition' in download_response:
            content_disposition = download_response['content-disposition']
        mimetype = download_response['content-type']
        response = HttpResponse(content, mimetype = mimetype)
        if content_disposition is not None:
            response['Content-Disposition'] = content_disposition
        return response
    else:
        return HttpResponse(status=403)