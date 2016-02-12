from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.test.utils import override_settings

from nose.tools import eq_

from csp.decorators import csp, csp_replace, csp_update, csp_exempt
from csp.middleware import CSPMiddleware

REQUEST = RequestFactory().get('/')
mw = CSPMiddleware()

class DecoratorTests(TestCase):
    def test_csp_exempt(self):
        @csp_exempt
        def view(request):
            return HttpResponse()
        response = view(REQUEST)
        assert response._csp_exempt

    @override_settings(CSP_IMG_SRC=['foo.com'])
    def test_csp_update(self):
        @csp_update(IMG_SRC='bar.com')
        def view(request):
            return HttpResponse()
        response = view(REQUEST)
        eq_(response._csp_update, {'img-src': 'bar.com'})

    @override_settings(CSP_IMG_SRC=['foo.com'])
    def test_csp_replace(self):
        @csp_replace(IMG_SRC='bar.com')
        def view(request):
            return HttpResponse()
        response = view(REQUEST)
        eq_(response._csp_replace, {'img-src': 'bar.com'})

    def test_csp(self):
        @csp(IMG_SRC=['foo.com'], FONT_SRC=['bar.com'])
        def view(request):
            return HttpResponse()
        response = view(REQUEST)
        eq_(response._csp_config,
            {'img-src': ['foo.com'], 'font-src': ['bar.com']})
        mw.process_response(REQUEST, response)
        eq_(policy_list, ["font-src bar.com", "img-src foo.com"])

    def test_csp_string_values(self):
        # Test backwards compatibility where values were strings
        @csp(IMG_SRC='foo.com', FONT_SRC='bar.com')
        def view(request):
            return HttpResponse()
        response = view(REQUEST)
        eq_(response._csp_config,
            {'img-src': ['foo.com'], 'font-src': ['bar.com']})
        mw.process_response(REQUEST, response)
        policy_list = sorted(response['Content-Security-Policy'].split("; "))
        eq_(policy_list, ["font-src bar.com", "img-src foo.com"])
