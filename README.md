# Utilisation de l'API


## Authentification
```
curl -X 'POST' 'http://34.163.146.144:8000/gettoken' -d 'username=clementine&password=mandarine'
```

## Verification du statut de l'api
```
curl -X 'GET' 'http://34.163.146.144:8000/healthCheck'
```

## Verification d'une transaction

Il faut utiliser le token récupéré lors du premier appel pour s'identifier pendant la requete suivante
```
curl -X 'GET' \
  'http://34.163.146.144:8000/fraudCheck?purchase_value=23&age=45&signup_time=2022-11-21T22%3A20%3A04.267946&purchase_time=2022-11-21T22%3A21%3A04.267998&sex=Male&source=SEO&browser=Chrome'\
  -H 'Authorization: Bearer $TOKEN'