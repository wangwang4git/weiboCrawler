import urllib2

urllib2.install_opener(
    urllib2.build_opener(
        urllib2.ProxyHandler({'http': 'web-proxy.oa.com:8080'})
    )
)
print urllib2.urlopen('http://www.baidu.com').read()

