# Hướng dẫn cài Keycloak

Sử dụng Podman để cài đặt Keycloak phục vụ cho test tính năng validate token.

Tạo network nếu chưa có:

```bash
podman network create dns
```

Tạo volumn để lưu dữ liệu:

```bash
podman volume create kcdata
```
Run keycloak:

```bash
podman run -d
  --name keycloak
  --network dns
  -p 8080:8080
  -e KEYCLOAK_ADMIN=admin
  -e KEYCLOAK_ADMIN_PASSWORD=admin
  -v kcdata:/opt/keycloak/data
  quay.io/keycloak/keycloak:latest
  start-dev
```

Đăng nhập vào địa chỉ sau để tạo client và user:

```
http://localhost:8080 
```

Ví dụ lấy JWT token:

```bash
curl -X POST \
  http://localhost:8080/realms/master/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=fastapi-client" \
  -d "username=testuser" \
  -d "password=123456" \
  -d "grant_type=password"
```

JWKS endpoint: 

```
http://localhost:8080/realms/master/protocol/openid-connect/certs
```

Issuer endpoint:

```
http://localhost:8080/realms/master
```

JWT example:

```
eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJTTHJrSUFoMVItSDZYYURIanJYSU1EVEdxTXlsZmNRaERQb1dkNU5GSlBvIn0.eyJleHAiOjE3NzUzMDM5MDcsImlhdCI6MTc3NTMwMzg0NywianRpIjoib25ydHJvOmM3ODQ5ODcyLWM4MjctMDg4Mi0yZmU2LWYwMzUyZGJmNzk1NiIsImlzcyI6Imh0dHA6Ly9sb2NhbGhvc3Q6ODA4MC9yZWFsbXMvbWFzdGVyIiwiYXVkIjpbIm1hc3Rlci1yZWFsbSIsImFjY291bnQiXSwic3ViIjoiYmMwODYxOTYtNzBlOC00YWViLTlhNjktNzA5MGRjYjI4MGU0IiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiZGVtbyIsInNpZCI6ImRZUUdpajhBWXl1VnJZQWVFVFUwTkRLcSIsImFjciI6IjEiLCJhbGxvd2VkLW9yaWdpbnMiOlsiLyoiXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbImNyZWF0ZS1yZWFsbSIsImRlZmF1bHQtcm9sZXMtbWFzdGVyIiwib2ZmbGluZV9hY2Nlc3MiLCJhZG1pbiIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsibWFzdGVyLXJlYWxtIjp7InJvbGVzIjpbInZpZXctaWRlbnRpdHktcHJvdmlkZXJzIiwidmlldy1yZWFsbSIsIm1hbmFnZS1pZGVudGl0eS1wcm92aWRlcnMiLCJpbXBlcnNvbmF0aW9uIiwiY3JlYXRlLWNsaWVudCIsIm1hbmFnZS11c2VycyIsInF1ZXJ5LXJlYWxtcyIsInZpZXctYXV0aG9yaXphdGlvbiIsInF1ZXJ5LWNsaWVudHMiLCJxdWVyeS11c2VycyIsIm1hbmFnZS1ldmVudHMiLCJtYW5hZ2UtcmVhbG0iLCJ2aWV3LWV2ZW50cyIsInZpZXctdXNlcnMiLCJ2aWV3LWNsaWVudHMiLCJtYW5hZ2UtYXV0aG9yaXphdGlvbiIsIm1hbmFnZS1jbGllbnRzIiwicXVlcnktZ3JvdXBzIl19LCJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6InByb2ZpbGUgZW1haWwiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsInByZWZlcnJlZF91c2VybmFtZSI6ImFkbWluIn0.qmUjNX81xZ3xdij7TTY2dgh_aeTvmbN0qVyRt-UVkUVpN4pKhDEFGoocuSBpj08w2pfczQ1AtGXimq7lANXYpRV-9fxxzuRj_tSM_PGOIw16WNMCfzrD5gQjZvn54XKlk3_j0mw3Ce2VZ06opEE2lxvg-dnMEfp-PPXnNurLPdlWjSP-fIrMAkIagL02ikK_83lqgQWKTjLODrdg2zuVyGvkkBNyMp_6nmCRCFD5qhh6CG1Rrwtj-XD6SWVLbrG-sRdnYCBR3hLZVoiNx3t0S0_v2D1166MXcWmjPojkRrj4lgnlLzJRFj4mAZwM1brtUeypSB6UzaPmbwSKjC38Lw
```

