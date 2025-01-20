# /etc/varnish/default.vcl
#
# This is a Varnish configuration file optimized for aggressively caching
# the output of a SunPower PVS device.
#
# See the VCL chapters in the Users Guide for a comprehensive documentation
# at https://www.varnish-cache.org/docs/.

# Marker to tell the VCL compiler that this VCL has been written with the
# 4.0 or 4.1 syntax.
vcl 4.1;

# Default backend definition. Set this to point to your content server.
backend default {
    .host = "172.27.153.1";
    .port = "80";
}

sub vcl_recv {
    # Happens before we check if we have this in cache already.
    #
    # Typically you clean up the request here, removing cookies you don't need,
    # rewriting the request, etc.
    if (req.method == "HEAD") {
        return (synth(405));
    }
    if (req.method == "GET") {
        return (hash);
    }
}

sub vcl_backend_response {
    # Happens after we have read the response headers from the backend.
    #
    # Here you clean the response headers, removing silly Set-Cookie headers
    # and other mistakes your backend does.
    set beresp.uncacheable = false;
    set beresp.ttl = 600s;
    unset beresp.http.pragma;
    unset beresp.http.cache-control;
    return (deliver);
}

sub vcl_deliver {
    # Happens when we have all the pieces we need, and are about to send the
    # response to the client.
    #
    # You can do accounting or modifying the final object here.
}
