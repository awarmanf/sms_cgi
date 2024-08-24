
# SMS Web Application

The SMS Web is a web application to sent sms using Perl CGI. You must setup it on the same [SMS Gateway Server](https://github.com/awarmanf/sms_gateway_perl).

>This application is designed on Debian Linux (Wheezy).

## Requirement

Packages installation in Debian / Ubuntu.

```bash
apt-get install nginx
apt-get install php-pear
apt-get install php5-cgi
apt-get install php5-fpm
apt-get install php5-gd
apt-get install php5-imap php5-mysql
apt-get install php5
apt-get install fcgiwrap
apt-get install libdbd-mysql-perl
apt-get install libdbi-perl
apt-get install mysql-server mysql-client
```

## Check if php5-fm and fcgi are working

```
$ /etc/init.d/php5-fpm status
[ ok ] php5-fpm is running.

$ /etc/init.d/fcgiwrap status
[ ok ] Checking status of FastCGI wrapper: fcgiwrap running.
```

## Edit nginx default configuration

Edit `/etc/nginx/sites-available/default`

```nginx
server {

	root /usr/share/nginx/www;
        index index.php index.html index.htm;

	# Make site accessible from http://localhost/
	server_name localhost;

	location / {
		# First attempt to serve request as file, then
		# as directory, then fall back to displaying a 404.
		try_files $uri $uri/ /index.html;
		# Uncomment to enable naxsi on this location
		# include /etc/nginx/naxsi.rules
	}

	location /doc/ {
		alias /usr/share/doc/;
		autoindex on;
		allow 127.0.0.1;
		allow ::1;
		deny all;
	}

	error_page 404 /404.html;

	# redirect server error pages to the static page /50x.html
	#
	error_page 500 502 503 504 /50x.html;
	location = /50x.html {
		root /usr/share/nginx/www;
	}

    # pass the PHP scripts to FastCGI server listening on /var/run/php5-fpm.sock
    location ~ \.php$ {
        try_files $uri =404;
        fastcgi_pass unix:/var/run/php5-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ \.pl|cgi$ {
        gzip off;
        include /etc/nginx/fastcgi_params;
        fastcgi_pass unix:/var/run/fcgiwrap.socket;
        fastcgi_index index.pl;
        fastcgi_param SCRIPT_FILENAME /usr/share/nginx/www/cgi$fastcgi_script_name;
    }
}
```

Start nginx

```
/etc/init.d/nginx start
```

## Create database smscgi

Login to mysql as user root

```sql
CREATE DATABASE smscgi;
CREATE USER 'user1'@'localhost' IDENTIFIED BY 'password1';
GRANT ALL PRIVILEGES ON `smscgi` . * TO 'user1'@'localhost';
QUIT;
```

Then execute sql statements on file `smscgi.db`

```
mysql -u user1 -p smscgi < smscgi.db
```

## Test if CGI is working

Create directory cgi

```
mkdir /usr/share/nginx/www/cgi
```

Then put files `test.cgi` and `sms.cgi` in that directory.

Make executable

```
chmod 755 /usr/share/nginx/www/cgi/test.cgi
chmod 755 /usr/share/nginx/www/cgi/sms.cgi
```

Test if cgi is working by using curl

    curl http://localhost/cgi/test.cgi

The output

```html
<html><head><title>Perl Environment Variables</title></head>
<body>
<h1>Perl Environment Variables</h1>
COLUMNS = 170<br>
CONSOLE = /dev/console<br>
CONTENT_LENGTH = <br>
CONTENT_TYPE = <br>
DOCUMENT_ROOT = /usr/share/nginx/www<br>
DOCUMENT_URI = /cgi/test.cgi<br>
FCGI_ROLE = RESPONDER<br>
GATEWAY_INTERFACE = CGI/1.1<br>
HOME = /<br>
HTTPS = <br>
HTTP_ACCEPT = */*<br>
HTTP_HOST = localhost<br>
HTTP_USER_AGENT = curl/7.26.0<br>
INIT_VERSION = sysvinit-2.88<br>
LINES = 48<br>
PATH = /usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin<br>
PREVLEVEL = N<br>
PWD = /<br>
QUERY_STRING = <br>
REDIRECT_STATUS = 200<br>
REMOTE_ADDR = 127.0.0.1<br>
REMOTE_PORT = 43133<br>
REQUEST_METHOD = GET<br>
REQUEST_URI = /cgi/test.cgi<br>
RUNLEVEL = 2<br>
SCRIPT_FILENAME = /usr/share/nginx/www/cgi/test.cgi<br>
SCRIPT_NAME = /cgi/test.cgi<br>
SERVER_ADDR = 127.0.0.1<br>
SERVER_NAME = localhost<br>
SERVER_PORT = 80<br>
SERVER_PROTOCOL = HTTP/1.1<br>
SERVER_SOFTWARE = nginx/1.2.1<br>
SHELL = /bin/sh<br>
TERM = linux<br>
init = /sbin/init<br>
previous = N<br>
rootmnt = /root<br>
runlevel = 2<br>
</body></html>
```

## Make user nginx (www-data) can write to /var/tmp/sms

```
chgrp www-data /var/tmp/sms
chmod 775 /var/tmp/sms
```

## Test send sms

### Using browser

Just input this line into the browser

```
http://localhost/cgi/sms.cgi?user=user1&pass=password1&to=085236006001&txt=Tes%20kirim%20sms
```

>When using the browser to send sms the space character must be encoded to `%20`.

### Using curl

Test send sms to single number

```
curl -o output -s "http://localhost/cgi/sms.cgi?user=user1&pass=password1&to=085236006000&txt=tes sms"
```

If success the output will be

```html
<!DOCTYPE html
	PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
	 "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en-US" xml:lang="en-US">
<head>
<title>SMS sent</title>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
</head>
<body>
<h1>SMS sent</h1>
</body>
</html>
```

Test send sms to multi numbers

```
curl -o output -s "http://localhost/cgi/sms.cgi?user=user1&pass=password1&to=085236006000,085236006001,085236006002&txt=tes sms"
```

The sms file `/var/tmp/sms/sms.1724415565` will contain

```
085236006000 tes sms
085236006001 tes sms
085236006002 tes sms
```

