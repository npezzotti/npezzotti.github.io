Title: Curl Cheatsheet
Date: 2022-11-13
Author: Nathan Pezzotti
Category: networking
Tags: linux, networking
Image: curl-logo.svg

This is a cheatsheet for useful options for the `curl` utility when using HTTP. These examples use `httpbin.org`, which provides a highly useful HTTP API for testing.

**Specify request method with `--request`(`-X`)**

This option is generally not neeeded as `curl` is able to infer the method. See [here](https://everything.curl.dev/http#http-methods) for more information

"GET is default, using -d or -F makes it a POST, -I generates a HEAD and -T sends a PUT."

`GET` request:
```
$ curl "http://httpbin.org/get"                 
{
  "args": {}, 
  "headers": {
    "Accept": "*/*", 
    "Host": "httpbin.org", 
    "User-Agent": "curl/7.79.1", 
    "X-Amzn-Trace-Id": "Root=1-637197f3-3112ff28701cd7ee7e151ba2"
  }, 
  "origin": "141.155.142.134", 
  "url": "http://httpbin.org/get"
}
```
To attach body data to the request (i.e make it a `POST` request), use the `--data`(`-d`) or `--form`(`-F`) flags
```
$ curl "https://httpbin.org/post" -H "accept: application/json" -d "key1=value1&key2=value2"
{
  "args": {}, 
  "data": "", 
  "files": {}, 
  "form": {
    "key1": "value1", 
    "key2": "value2"
  }, 
  "headers": {
    "Accept": "application/json", 
    "Content-Length": "23", 
    "Content-Type": "application/x-www-form-urlencoded", 
    "Host": "httpbin.org", 
    "User-Agent": "curl/7.79.1", 
    "X-Amzn-Trace-Id": "Root=1-63719b5a-287c58eb116f3ed37e306811"
  }, 
  "json": null, 
  "origin": "141.155.142.134", 
  "url": "https://httpbin.org/post"
}
```
You can also load data from a file using the `@` symbol:
```
$ echo "key1=value1&key2=value2" > data.txt  
$ curl "https://httpbin.org/post" -H "accept: application/json" -d @data.txt                
{
  "args": {}, 
  "data": "", 
  "files": {}, 
  "form": {
    "key1": "value1", 
    "key2": "value2"
  }, 
  "headers": {
    "Accept": "application/json", 
    "Content-Length": "23", 
    "Content-Type": "application/x-www-form-urlencoded", 
    "Host": "httpbin.org", 
    "User-Agent": "curl/7.79.1", 
    "X-Amzn-Trace-Id": "Root=1-63719ba5-2abdd96f3c59f87218e9ac2e"
  }, 
  "json": null, 
  "origin": "141.155.142.134", 
  "url": "https://httpbin.org/post"
}
```
```
$ curl "https://httpbin.org/post" -H "accept: application/json" -F "key1=value1" -F "key2=value2"                  
{
  "args": {}, 
  "data": "", 
  "files": {}, 
  "form": {
    "key1": "value1", 
    "key2": "value2"
  }, 
  "headers": {
    "Accept": "application/json", 
    "Content-Length": "244", 
    "Content-Type": "multipart/form-data; boundary=------------------------b8fbb17b63cb9115", 
    "Host": "httpbin.org", 
    "User-Agent": "curl/7.79.1", 
    "X-Amzn-Trace-Id": "Root=1-63719cb9-405721fd18b9b9f42563c813"
  }, 
  "json": null, 
  "origin": "141.155.142.134", 
  "url": "https://httpbin.org/post"
}
```
By default, the `-d` option sends a `Content-Type: application/x-www-form-urlencoded` header. When you need to send JSON, use either `-d` with JSON data (ie. `'{"test": "json"}'`) and the `Content-Type: application/json` header, or the shortcut `--json`.
```
$ curl "https://httpbin.org/post" -H "accept: application/json" -H "Content-Type: application/json" -d '{"key": "value"}'
{
  "args": {}, 
  "data": "{\"key\": \"value\"}", 
  "files": {}, 
  "form": {}, 
  "headers": {
    "Accept": "application/json", 
    "Content-Length": "16", 
    "Content-Type": "application/json", 
    "Host": "httpbin.org", 
    "User-Agent": "curl/7.79.1", 
    "X-Amzn-Trace-Id": "Root=1-63719c16-616bf12d7fcc50480c65b420"
  }, 
  "json": {
    "key": "value"
  }, 
  "origin": "141.155.142.134", 
  "url": "https://httpbin.org/post"
}
```
**Retrieve only the headers with `--head` (`-I`)**

This send an HTTP `HEAD` request.
```
$ curl -I "https://httpbin.org/get"
HTTP/2 200 
date: Sun, 13 Nov 2022 23:23:44 GMT
content-type: application/json
content-length: 257
server: gunicorn/19.9.0
access-control-allow-origin: *
access-control-allow-credentials: true
```
**View verbose output with `--verbose`(`-v`)**

This is useful for inspecting connetion and TLS details.
```
$ curl -v "https://httpbin.org/get"
*   Trying 35.168.106.184:443...
* Connected to httpbin.org (35.168.106.184) port 443 (#0)
* ALPN, offering h2
* ALPN, offering http/1.1
* successfully set certificate verify locations:
*  CAfile: /etc/ssl/cert.pem
*  CApath: none
* (304) (OUT), TLS handshake, Client hello (1):
* (304) (IN), TLS handshake, Server hello (2):
* TLSv1.2 (IN), TLS handshake, Certificate (11):
* TLSv1.2 (IN), TLS handshake, Server key exchange (12):
* TLSv1.2 (IN), TLS handshake, Server finished (14):
* TLSv1.2 (OUT), TLS handshake, Client key exchange (16):
* TLSv1.2 (OUT), TLS change cipher, Change cipher spec (1):
* TLSv1.2 (OUT), TLS handshake, Finished (20):
* TLSv1.2 (IN), TLS change cipher, Change cipher spec (1):
* TLSv1.2 (IN), TLS handshake, Finished (20):
* SSL connection using TLSv1.2 / ECDHE-RSA-AES128-GCM-SHA256
* ALPN, server accepted to use h2
* Server certificate:
*  subject: CN=httpbin.org
*  start date: Oct 21 00:00:00 2022 GMT
*  expire date: Nov 19 23:59:59 2023 GMT
*  subjectAltName: host "httpbin.org" matched cert's "httpbin.org"
*  issuer: C=US; O=Amazon; OU=Server CA 1B; CN=Amazon
*  SSL certificate verify ok.
* Using HTTP2, server supports multiplexing
* Connection state changed (HTTP/2 confirmed)
* Copying HTTP/2 data in stream buffer to connection buffer after upgrade: len=0
* Using Stream ID: 1 (easy handle 0x151812c00)
> GET /get HTTP/2
> Host: httpbin.org
> user-agent: curl/7.79.1
> accept: */*
> 
* Connection state changed (MAX_CONCURRENT_STREAMS == 128)!
< HTTP/2 200 
< date: Sun, 13 Nov 2022 23:28:32 GMT
< content-type: application/json
< content-length: 257
< server: gunicorn/19.9.0
< access-control-allow-origin: *
< access-control-allow-credentials: true
< 
{
  "args": {}, 
  "headers": {
    "Accept": "*/*", 
    "Host": "httpbin.org", 
    "User-Agent": "curl/7.79.1", 
    "X-Amzn-Trace-Id": "Root=1-63717da0-6ce7a88c2dbfe7f61534fcb0"
  }, 
  "origin": "141.155.142.134", 
  "url": "https://httpbin.org/get"
}
* Connection #0 to host httpbin.org left intact
```

**HTTP basic authentication with `--user` (`-u`)**

The username and password are specified in `<USERNAME>:<PASSWORD>` format.
```
$ curl -I --user test-user:password "https://httpbin.org/basic-auth/test-user/password" -H "accept: application/json"
HTTP/2 200 
date: Sun, 13 Nov 2022 23:54:09 GMT
content-type: application/json
content-length: 49
server: gunicorn/19.9.0
access-control-allow-origin: *
access-control-allow-credentials: true
```

**Follow redirects with the `-L` flag**
```
$ curl -L -I https://httpbin.org/absolute-redirect/1
HTTP/2 302 
date: Sun, 13 Nov 2022 23:42:33 GMT
content-type: text/html; charset=utf-8
content-length: 251
location: http://httpbin.org/get
server: gunicorn/19.9.0
access-control-allow-origin: *
access-control-allow-credentials: true

HTTP/1.1 200 OK
Date: Sun, 13 Nov 2022 23:42:33 GMT
Content-Type: application/json
Content-Length: 256
Connection: keep-alive
Server: gunicorn/19.9.0
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

**Add an HTTP header with `--header` (`-H`)**

```
curl -I "https://httpbin.org/bearer" -H "accept: application/json" -H "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c" 
HTTP/2 401 
date: Mon, 14 Nov 2022 00:10:22 GMT
content-type: text/html; charset=utf-8
content-length: 0
server: gunicorn/19.9.0
www-authenticate: Bearer
access-control-allow-origin: *
access-control-allow-credentials: true
```

**Write response content to a file with `-output`(`-o`)**

You can also use `--remote-name`(`-O`) to write to a local file named like the remote file.
```
$ curl "https://httpbin.org/json" -H "accept: application/json" -o output.txt
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   429  100   429    0     0   4930      0 --:--:-- --:--:-- --:--:--  5362
$ cat output.txt 
{
  "slideshow": {
    "author": "Yours Truly", 
    "date": "date of publication", 
    "slides": [
      {
        "title": "Wake up to WonderWidgets!", 
        "type": "all"
      }, 
      {
        "items": [
          "Why <em>WonderWidgets</em> are great", 
          "Who <em>buys</em> WonderWidgets"
        ], 
        "title": "Overview", 
        "type": "all"
      }
    ], 
    "title": "Sample Slide Show"
  }
}
```
**Mute progress bar with `--silent` (`-s`) flag**

This is for preventing the progress bar from appearing in the terminal/file output, as seen in the example above.
```
$ curl -s "https://httpbin.org/json" -H "accept: application/json" -o output.txt
$
```

**Connect through a proxy with `--proxy`(`-x`)**
```
curl -vI -x "http://127.0.0.1:3128" "http://httpbin.org/get"
*   Trying 127.0.0.1:3128...
* Connected to 127.0.0.1 (127.0.0.1) port 3128 (#0)
> HEAD http://httpbin.org/get HTTP/1.1
> Host: httpbin.org
> User-Agent: curl/7.79.1
> Accept: */*
> Proxy-Connection: Keep-Alive
> 
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
HTTP/1.1 200 OK
< Date: Mon, 14 Nov 2022 01:03:32 GMT
Date: Mon, 14 Nov 2022 01:03:32 GMT
< Content-Type: application/json
Content-Type: application/json
< Content-Length: 308
Content-Length: 308
< Server: gunicorn/19.9.0
Server: gunicorn/19.9.0
< Access-Control-Allow-Origin: *
Access-Control-Allow-Origin: *
< Access-Control-Allow-Credentials: true
Access-Control-Allow-Credentials: true
< X-Cache: MISS from 82fe2e923e70
X-Cache: MISS from 82fe2e923e70
< X-Cache-Lookup: MISS from 82fe2e923e70:3128
X-Cache-Lookup: MISS from 82fe2e923e70:3128
< Via: 1.1 82fe2e923e70 (squid/5.2)
Via: 1.1 82fe2e923e70 (squid/5.2)
< Connection: keep-alive
Connection: keep-alive

< 
* Connection #0 to host 127.0.0.1 left intact
```
**Ignore certificate errors and allow insecure connection with `--insecure` (`-k`)**
```
$ curl -I -k https://self-signed.badssl.com/
HTTP/1.1 200 OK
Server: nginx/1.10.3 (Ubuntu)
Date: Mon, 14 Nov 2022 00:47:01 GMT
Content-Type: text/html
Content-Length: 502
Last-Modified: Thu, 27 Oct 2022 19:09:20 GMT
Connection: keep-alive
ETag: "635ad760-1f6"
Cache-Control: no-store
Accept-Ranges: bytes
```
**Customize output with `--write-out`(`-w`)**

This is useful for writing some output and statistics about the request once complete in a custom format. There are many variables which can be viewed by viewing the `curl` man page. Variables are specified as`%{variable_name}`.
```
$ curl -w "Response content: %{content_type}, Number of headers: %{num_headers}.\n" "http://httpbin.org/get"   
{
  "args": {}, 
  "headers": {
    "Accept": "*/*", 
    "Host": "httpbin.org", 
    "User-Agent": "curl/7.79.1", 
    "X-Amzn-Trace-Id": "Root=1-6371958f-37e6cc1d206f89c023cf99dd"
  }, 
  "origin": "141.155.142.134", 
  "url": "http://httpbin.org/get"
}
Response content: application/json, Number of headers: 7.
```