import os
import json
import urllib.request
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from authlib.jose import jwt, JoseError

# Cấu hình từ OpenID Provider của bạn (Keycloak, Auth0, AWS Cognito, Google...)
ISSUER_URL = os.getenv("ISSUER_URL", "https://your-auth-server.com/realm/myrealm")
JWKS_URL = os.getenv("JWKS_URL", f"{ISSUER_URL}/protocol/openid-connect/certs")
AUDIENCE = os.getenv("API_AUDIENCE", "account") # Tùy chọn: Validate audience nếu cần

# Load JWKS (JSON Web Key Set) và lưu vào bộ nhớ (cache)
# Trong môi trường production, bạn có thể thiết lập cơ chế refresh khi JWKS thay đổi.
def get_jwks():
    try:
        with urllib.request.urlopen(JWKS_URL) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Lỗi khi lấy JWKS từ {JWKS_URL}: {e}")
        return {}

JWKS = get_jwks()

# HTTPBearer trích xuất token tự động
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency lấy token từ Header và giải mã dựa trên public key (JWKS) từ server chứng thực.
    """
    token = credentials.credentials
    
    # Reload lại key nếu cần thiết hoặc báo lỗi (có thể tinh chỉnh theo real use case)
    if not JWKS:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể tải Public Keys từ Auth Server"
        )

    try:
        # Trong hệ thống dùng JWKS, chuẩn mã hóa thường là RSA (RS256)
        # Truyền JWKS list vào tham số `key` để thư viện tự match chữ ký (kid)
        claims = jwt.decode(token, key=JWKS)
        
        # Hàm validate mặc định (nếu muốn check thêm các thông tin Issuer / Audience / Exp)
        # Ta tạo một dictionary claims option để bắt buộc check exp (hạn token), iss (nguồn gốc token) và aud (audience)
        claims_options = {
            "iss": {"essential": True, "value": ISSUER_URL},
            # "aud": {"essential": True, "value": AUDIENCE}, # Uncomment nếu muốn check audience
            "exp": {"essential": True}
        }
        claims.validate(claims_options)
        
        return claims
        
    except JoseError as e:
        # Bắt JWT error của authlib (lỗi chữ ký, hết hạn, hoặc các lỗi không khớp claim)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token không hợp lệ: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
