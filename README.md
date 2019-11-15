Selectel DNS Authenticator plugin for Certbot
==============================================
A certbot dns plugin to obtain certificates using Selectel DNS.

## Obtain DNS API key

https://my.selectel.ru/profile/apikeys

## Install

pip install certbot-dns-selectel

##Credentials File

```
certbot_dns_selectel:dns_selectel_api_key = XXXXXXXXXXXXXXXXXXXXXXXXX_XXXXXX
```

```bash
chmod 600 /path/to/credentials.ini
```

## Obtain Certificates

```bash
certbot certonly -a certbot-dns-selectel:dns-selectel \
  --certbot-dns-selectel:dns-selectel-credentials /path/to/credentials.ini \
  --certbot-dns-selectel:dns-selectel-propagation-seconds 30 \
  -d example.com \
  -d "*.example.com" \
  -m admin@example.com \
  --agree-tos -n
```
