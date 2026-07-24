"""cc_* 노트북 공통 목(mock) 파일시스템.

가상 프로젝트: orderhub — 사내 주문 관리 백엔드 (FastAPI + SQLAlchemy).
40개 파일, path -> content 평면 딕셔너리.

사용법:
    from cc_mock_fs import FS            # 그대로 쓰기 (read/grep/glob/edit/write 목 도구)

    # mtime 구조가 필요한 노트북(cc_tool_sequence_hard_rules / soft_rules):
    for p, c in FS.items():
        _seed(p, c)

기존 노트북 시나리오 앵커 (경로만 새 구조로 이동):
    - DEBUG/TIMEOUT/RETRY_LIMIT/ALLOWED_HOSTS  → /project/src/app/config.py
    - clamp + TODO                             → /project/src/app/utils/common.py
    - authenticate/_hash_password              → /project/src/app/services/auth_service.py
    - fetch_with_retry                         → /project/src/app/utils/http_client.py
    - timeout=30/retry=3/host=…                → /project/configs/app.ini
    - [warn] timeout exceeded 로그             → /project/logs/app.log
    - 할 일 메모                                → /project/docs/todo.md

grep 실습용으로 심어둔 것: TODO 6곳, FIXME 2곳, deprecated 1곳,
주문 총액 계산 버그(ORDER-482), 쿠폰 중복 적용 버그(ORDER-517).
"""

FS = {
    # ── 루트 ──────────────────────────────────────────────
    "/project/README.md": '''# orderhub

사내 주문 관리 백엔드. FastAPI + SQLAlchemy + PostgreSQL.

## 실행

```bash
make install   # 의존성 설치
make migrate   # DB 마이그레이션
make run       # 개발 서버 (기본 8000 포트)
make test      # 전체 테스트
```

## 구조

- `src/app/routers/` — HTTP 엔드포인트 (auth / users / products / orders)
- `src/app/services/` — 비즈니스 로직
- `src/app/repositories/` — DB 접근 계층
- `src/app/models/` — SQLAlchemy 모델
- `src/app/schemas/` — Pydantic 요청/응답 스키마
- `migrations/` — SQL 마이그레이션 (수동 관리)

## 알려진 이슈

- ORDER-482: 쿠폰 할인이 배송비에도 적용되는 버그 (order_service 참고)
- ORDER-517: 쿠폰 중복 적용 가능 (진행 중)
''',

    "/project/pyproject.toml": '''[project]
name = "orderhub"
version = "0.4.2"
description = "사내 주문 관리 백엔드"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "sqlalchemy>=2.0",
    "psycopg[binary]>=3.2",
    "pydantic>=2.8",
    "pydantic-settings>=2.4",
    "python-jose[cryptography]>=3.3",
    "redis>=5.0",
]

[dependency-groups]
dev = [
    "pytest>=8.3",
    "pytest-asyncio>=0.24",
    "httpx>=0.27",
    "ruff>=0.6",
]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
''',

    "/project/.env.example": '''# 로컬 개발용 예시 — 실제 값은 .env 에 두고 커밋 금지
DATABASE_URL=postgresql+psycopg://orderhub:change-me@localhost:5432/orderhub
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=change-me-in-production
JWT_EXPIRE_MINUTES=60
PAYMENT_GATEWAY_URL=https://pay.example.com/v2
PAYMENT_API_KEY=change-me
LOG_LEVEL=INFO
''',

    "/project/Makefile": '''.PHONY: install run test lint migrate seed

install:
\tuv sync

run:
\tuv run uvicorn app.main:app --reload --app-dir src

test:
\tuv run pytest -q

lint:
\tuv run ruff check src tests

migrate:
\tuv run python scripts/run_migrations.py

seed:
\tuv run python scripts/seed_db.py
''',


    "/project/configs/app.ini": '''[server]
host=api.example.com
port=8000
timeout=30
retry=3

[database]
pool_size=10
pool_timeout=5
echo=false

[cache]
ttl_seconds=300
prefix=orderhub
''',


    # ── src/app 코어 ──────────────────────────────────────
    "/project/src/app/main.py": '''from fastapi import FastAPI

from app.config import settings
from app.routers import auth_router, orders_router, products_router, users_router

app = FastAPI(title="orderhub", version="0.4.2", debug=settings.DEBUG)

app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(users_router.router, prefix="/users", tags=["users"])
app.include_router(products_router.router, prefix="/products", tags=["products"])
app.include_router(orders_router.router, prefix="/orders", tags=["orders"])


@app.get("/health")
def health():
    # 로드밸런서 헬스체크 전용 — 인증 없음
    return {"status": "ok", "version": app.version}
''',

    "/project/src/app/config.py": '''import os

DEBUG = True
TIMEOUT = 30
RETRY_LIMIT = 3
ALLOWED_HOSTS = ["localhost", "api.example.com"]


class Settings:
    # TODO: pydantic-settings 로 이전하고 이 수동 클래스는 제거
    DEBUG = DEBUG
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://localhost/orderhub")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
    PAYMENT_GATEWAY_URL = os.getenv("PAYMENT_GATEWAY_URL", "https://pay.example.com/v2")


settings = Settings()
''',

    "/project/src/app/database.py": '''from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(settings.DATABASE_URL, pool_size=10, pool_timeout=5)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_session():
    # FastAPI Depends 용 세션 팩토리 — 요청 종료 시 반드시 close
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''',

    "/project/src/app/dependencies.py": '''from fastapi import Depends, Header, HTTPException

from app.database import get_session
from app.services.auth_service import decode_token
from app.repositories.user_repo import UserRepo


def get_current_user(authorization: str = Header(None), db=Depends(get_session)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="인증 토큰이 없습니다")
    payload = decode_token(authorization.removeprefix("Bearer "))
    user = UserRepo(db).get_by_id(payload["sub"])
    if user is None:
        raise HTTPException(status_code=401, detail="존재하지 않는 사용자입니다")
    return user


def require_admin(user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다")
    return user
''',

    # ── 라우터 ────────────────────────────────────────────
    "/project/src/app/routers/auth_router.py": '''from fastapi import APIRouter, Depends, HTTPException

from app.database import get_session
from app.schemas.user_schema import LoginRequest, TokenResponse
from app.services.auth_service import authenticate, issue_token

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db=Depends(get_session)):
    user = authenticate(body.username, body.password, db)
    if user is None:
        # 계정 존재 여부를 노출하지 않기 위해 메시지를 통일한다
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다")
    return TokenResponse(access_token=issue_token(user), token_type="bearer")
''',

    "/project/src/app/routers/orders_router.py": '''from fastapi import APIRouter, Depends, HTTPException

from app.database import get_session
from app.dependencies import get_current_user
from app.schemas.order_schema import OrderCreate, OrderOut
from app.services.order_service import OrderService

router = APIRouter()


@router.post("", response_model=OrderOut, status_code=201)
def create_order(body: OrderCreate, user=Depends(get_current_user), db=Depends(get_session)):
    return OrderService(db).create(user_id=user.id, items=body.items, coupon_code=body.coupon_code)


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, user=Depends(get_current_user), db=Depends(get_session)):
    order = OrderService(db).get(order_id)
    if order is None or order.user_id != user.id:
        # 남의 주문은 404 로 위장한다 (존재 여부 노출 방지)
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
    return order


@router.post("/{order_id}/cancel", response_model=OrderOut)
def cancel_order(order_id: int, user=Depends(get_current_user), db=Depends(get_session)):
    return OrderService(db).cancel(order_id, requested_by=user.id)
''',

    "/project/src/app/routers/products_router.py": '''from fastapi import APIRouter, Depends

from app.database import get_session
from app.dependencies import require_admin
from app.services.product_service import ProductService
from app.utils.pagination import paginate

router = APIRouter()


@router.get("")
def list_products(page: int = 1, size: int = 20, keyword: str = "", db=Depends(get_session)):
    items = ProductService(db).search(keyword)
    return paginate(items, page=page, size=size)


@router.post("", status_code=201)
def create_product(name: str, price: int, stock: int, _=Depends(require_admin), db=Depends(get_session)):
    return ProductService(db).create(name=name, price=price, stock=stock)
''',

    "/project/src/app/routers/users_router.py": '''from fastapi import APIRouter, Depends

from app.database import get_session
from app.dependencies import get_current_user, require_admin
from app.repositories.user_repo import UserRepo

router = APIRouter()


@router.get("/me")
def get_me(user=Depends(get_current_user)):
    return {"id": user.id, "username": user.username, "role": user.role}


@router.get("")
def list_users(_=Depends(require_admin), db=Depends(get_session)):
    # TODO: 페이지네이션 적용 — 지금은 전체 사용자를 한 번에 돌려준다
    return UserRepo(db).list_all()
''',

    # ── 서비스 ────────────────────────────────────────────
    "/project/src/app/services/auth_service.py": '''import hashlib
import time

from jose import jwt

from app.config import settings
from app.repositories.user_repo import UserRepo


def _hash_password(password: str, salt: str) -> str:
    # TODO: sha256 단순 해시는 취약 — bcrypt 로 교체 (AUTH-201)
    return hashlib.sha256((salt + password).encode()).hexdigest()


def authenticate(username: str, password: str, db):
    # user 를 찾아 salt+password 해시를 대조한다. 실패 사유는 구분하지 않는다.
    user = UserRepo(db).get_by_username(username)
    if user is None:
        return None
    if _hash_password(password, user.salt) != user.password_hash:
        return None
    return user


def issue_token(user) -> str:
    payload = {"sub": user.id, "role": user.role, "exp": int(time.time()) + settings.JWT_EXPIRE_MINUTES * 60}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
''',

    "/project/src/app/services/order_service.py": '''from app.repositories.order_repo import OrderRepo
from app.repositories.product_repo import ProductRepo
from app.services.payment_service import request_payment
from app.utils.common import clamp

FREE_SHIPPING_THRESHOLD = 50_000
SHIPPING_FEE = 3_000


class OrderService:
    def __init__(self, db):
        self.db = db
        self.orders = OrderRepo(db)
        self.products = ProductRepo(db)

    def calc_total(self, items, coupon=None):
        subtotal = 0
        for item in items:
            product = self.products.get_by_id(item["product_id"])
            subtotal += product.price * item["qty"]
        shipping = 0 if subtotal >= FREE_SHIPPING_THRESHOLD else SHIPPING_FEE
        total = subtotal + shipping
        if coupon:
            # FIXME(ORDER-482): 할인이 배송비 포함 총액에 걸린다.
            # 정책상 쿠폰은 상품 금액(subtotal)에만 적용해야 한다.
            total = clamp(total - coupon.amount, 0, total)
        return total

    def create(self, user_id, items, coupon_code=None):
        coupon = self.orders.find_coupon(coupon_code) if coupon_code else None
        # FIXME(ORDER-517): 이미 사용한 쿠폰인지 검사하지 않아 중복 적용이 가능하다
        total = self.calc_total(items, coupon)
        order = self.orders.insert(user_id=user_id, items=items, total=total)
        request_payment(order_id=order.id, amount=total)
        return order

    def get(self, order_id):
        return self.orders.get_by_id(order_id)

    def cancel(self, order_id, requested_by):
        order = self.orders.get_by_id(order_id)
        # 결제 완료 후 24시간 이내에만 취소 허용
        return self.orders.mark_cancelled(order, requested_by)
''',

    "/project/src/app/services/product_service.py": '''from app.repositories.product_repo import ProductRepo


class ProductService:
    def __init__(self, db):
        self.repo = ProductRepo(db)

    def search(self, keyword: str):
        if not keyword:
            return self.repo.list_active()
        return self.repo.search_by_name(keyword)

    def create(self, name: str, price: int, stock: int):
        if price <= 0:
            raise ValueError("가격은 0보다 커야 합니다")
        return self.repo.insert(name=name, price=price, stock=stock)

    def decrease_stock(self, product_id: int, qty: int):
        product = self.repo.get_by_id(product_id)
        if product.stock < qty:
            raise ValueError(f"재고 부족: {product.name} (남은 수량 {product.stock})")
        self.repo.update_stock(product_id, product.stock - qty)
''',

    "/project/src/app/services/payment_service.py": '''from app.config import settings
from app.utils.http_client import fetch_with_retry


def request_payment(order_id: int, amount: int) -> dict:
    # 결제 게이트웨이 v2 — 실패 시 fetch_with_retry 가 RETRY_LIMIT 만큼 재시도한다
    url = f"{settings.PAYMENT_GATEWAY_URL}/charge?order={order_id}&amount={amount}"
    response = fetch_with_retry(url)
    return {"order_id": order_id, "amount": amount, "raw": response}


def charge_legacy(order_id: int, amount: int) -> dict:
    # deprecated: v1 게이트웨이는 2026-03 폐기 예정. request_payment 를 쓸 것 (PAY-77)
    url = f"https://pay.example.com/v1/charge?order={order_id}&amount={amount}"
    return {"order_id": order_id, "amount": amount, "raw": fetch_with_retry(url)}


def refund(order_id: int, amount: int) -> dict:
    # TODO: 부분 환불 지원 — 지금은 전액 환불만 가능
    url = f"{settings.PAYMENT_GATEWAY_URL}/refund?order={order_id}&amount={amount}"
    return {"order_id": order_id, "refunded": amount, "raw": fetch_with_retry(url)}
''',

    # ── 모델 ──────────────────────────────────────────────
    "/project/src/app/models/user.py": '''from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(64))
    salt: Mapped[str] = mapped_column(String(32))
    role: Mapped[str] = mapped_column(String(20), default="member")  # member | admin
''',

    "/project/src/app/models/order.py": '''from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    total: Mapped[int] = mapped_column(Integer)  # 원 단위 정수 — float 금지
    status: Mapped[str] = mapped_column(String(20), default="pending")
    # 상태 전이: pending -> paid -> shipped -> done, 어느 단계든 -> cancelled
''',

    "/project/src/app/models/product.py": '''from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    price: Mapped[int] = mapped_column(Integer)  # 원 단위 정수
    stock: Mapped[int] = mapped_column(Integer, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
''',

    # ── 리포지토리 ────────────────────────────────────────
    "/project/src/app/repositories/user_repo.py": '''from sqlalchemy import select

from app.models.user import User


class UserRepo:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, user_id: int):
        return self.db.get(User, user_id)

    def get_by_username(self, username: str):
        return self.db.scalar(select(User).where(User.username == username))

    def list_all(self):
        return list(self.db.scalars(select(User).order_by(User.id)))
''',

    "/project/src/app/repositories/order_repo.py": '''from sqlalchemy import select

from app.models.order import Order


class OrderRepo:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, order_id: int):
        return self.db.get(Order, order_id)

    def insert(self, user_id: int, items: list, total: int):
        order = Order(user_id=user_id, total=total, status="pending")
        self.db.add(order)
        self.db.commit()
        return order

    def mark_cancelled(self, order, requested_by: int):
        order.status = "cancelled"
        self.db.commit()
        return order

    def find_coupon(self, code: str):
        # TODO: 쿠폰 테이블 분리 — 지금은 하드코딩된 프로모션 코드만 인식
        promotions = {"WELCOME5": 5_000, "VIP10": 10_000}
        if code not in promotions:
            return None
        return type("Coupon", (), {"code": code, "amount": promotions[code]})()
''',

    "/project/src/app/repositories/product_repo.py": '''from sqlalchemy import select

from app.models.product import Product


class ProductRepo:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, product_id: int):
        return self.db.get(Product, product_id)

    def list_active(self):
        return list(self.db.scalars(select(Product).where(Product.active)))

    def search_by_name(self, keyword: str):
        return list(self.db.scalars(select(Product).where(Product.name.contains(keyword))))

    def insert(self, name: str, price: int, stock: int):
        product = Product(name=name, price=price, stock=stock)
        self.db.add(product)
        self.db.commit()
        return product

    def update_stock(self, product_id: int, new_stock: int):
        self.get_by_id(product_id).stock = new_stock
        self.db.commit()
''',

    # ── 유틸 ──────────────────────────────────────────────
    "/project/src/app/utils/common.py": '''# TODO: 이 함수는 나중에 numpy 로 대체
def clamp(value, low, high):
    return max(low, min(high, value))


def chunked(seq, size):
    # 리스트를 size 단위로 잘라서 돌려준다. 마지막 조각은 짧을 수 있다.
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


def mask_secret(value: str, visible: int = 4) -> str:
    # 로그에 시크릿을 남길 때 끝 4자만 노출한다. 예: ****-me
    if len(value) <= visible:
        return "*" * len(value)
    return "*" * (len(value) - visible) + value[-visible:]
''',

    "/project/src/app/utils/http_client.py": '''import urllib.request

from app.config import RETRY_LIMIT, TIMEOUT


def fetch_with_retry(url: str, retries: int = RETRY_LIMIT):
    # 일시적 네트워크 오류만 재시도한다. 4xx 는 재시도해도 소용없으므로 즉시 올린다.
    last_error = None
    for _ in range(retries):
        try:
            return urllib.request.urlopen(url, timeout=TIMEOUT).read()
        except OSError as e:
            last_error = e
    raise RuntimeError(f"fetch failed after {retries} retries") from last_error
''',


    "/project/src/app/utils/pagination.py": '''def paginate(items, page: int = 1, size: int = 20):
    if page < 1 or size < 1:
        raise ValueError("page 와 size 는 1 이상이어야 합니다")
    start = (page - 1) * size
    return {
        "total": len(items),
        "page": page,
        "size": size,
        "items": items[start:start + size],
    }
''',

    # ── 스키마 ────────────────────────────────────────────
    "/project/src/app/schemas/order_schema.py": '''from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    product_id: int
    qty: int = Field(ge=1, le=99)


class OrderCreate(BaseModel):
    items: list[OrderItem] = Field(min_length=1)
    coupon_code: str | None = None


class OrderOut(BaseModel):
    id: int
    user_id: int
    total: int
    status: str

    model_config = {"from_attributes": True}
''',

    "/project/src/app/schemas/user_schema.py": '''from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
''',

    # ── 테스트 ────────────────────────────────────────────
    "/project/tests/conftest.py": '''import pytest

from app.database import Base, SessionLocal, engine


@pytest.fixture()
def db():
    # 테스트마다 스키마를 새로 만들고 끝나면 정리한다 (in-memory 아님 주의)
    Base.metadata.create_all(engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(engine)
''',

    "/project/tests/test_auth_service.py": '''from app.services.auth_service import _hash_password, authenticate


def test_hash_password_deterministic():
    assert _hash_password("pw1234!", "salt") == _hash_password("pw1234!", "salt")


def test_hash_password_salt_changes_hash():
    assert _hash_password("pw1234!", "saltA") != _hash_password("pw1234!", "saltB")


def test_authenticate_unknown_user_returns_none(db):
    assert authenticate("ghost", "whatever123", db) is None
''',

    "/project/tests/test_order_service.py": '''import pytest

from app.services.order_service import OrderService, SHIPPING_FEE


def test_total_includes_shipping_under_threshold(db, seed_products):
    service = OrderService(db)
    total = service.calc_total([{"product_id": 1, "qty": 1}])  # 12,000원 상품
    assert total == 12_000 + SHIPPING_FEE


def test_free_shipping_over_threshold(db, seed_products):
    service = OrderService(db)
    total = service.calc_total([{"product_id": 2, "qty": 2}])  # 32,000원 × 2
    assert total == 64_000


@pytest.mark.xfail(reason="ORDER-482: 쿠폰이 배송비에도 적용되는 버그 — 수정 전까지 실패가 정상")
def test_coupon_applies_to_subtotal_only(db, seed_products, welcome_coupon):
    service = OrderService(db)
    total = service.calc_total([{"product_id": 1, "qty": 1}], coupon=welcome_coupon)
    # 기대: (12,000 - 5,000) + 배송비 3,000 = 10,000
    assert total == 10_000
''',

    "/project/tests/test_utils.py": '''import pytest

from app.utils.common import chunked, clamp, mask_secret
from app.utils.pagination import paginate


def test_clamp_bounds():
    assert clamp(5, 0, 10) == 5
    assert clamp(-1, 0, 10) == 0
    assert clamp(99, 0, 10) == 10


def test_chunked_last_piece_short():
    assert list(chunked([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]


def test_mask_secret_keeps_tail():
    assert mask_secret("change-me") == "*****e-me"


def test_paginate_rejects_zero_page():
    with pytest.raises(ValueError):
        paginate([], page=0)
''',

    # ── 스크립트 / 마이그레이션 ───────────────────────────
    "/project/scripts/seed_db.py": '''# 로컬 개발용 시드 데이터 — 운영 DB 에 절대 실행 금지
from app.database import Base, SessionLocal, engine
from app.models.product import Product
from app.models.user import User
from app.services.auth_service import _hash_password

Base.metadata.create_all(engine)
db = SessionLocal()

db.add(User(username="admin", salt="s1", password_hash=_hash_password("admin1234!", "s1"), role="admin"))
db.add(User(username="hong", salt="s2", password_hash=_hash_password("hong1234!", "s2")))
db.add(Product(name="스탠딩 데스크", price=12_000, stock=30))
db.add(Product(name="기계식 키보드", price=32_000, stock=12))
db.add(Product(name="모니터암", price=45_000, stock=7))
db.commit()
print("시드 완료: 사용자 2명, 상품 3개")
''',

    "/project/scripts/run_migrations.py": '''# migrations/*.sql 을 파일명 순서대로 실행하는 단순 러너
import pathlib

from sqlalchemy import text

from app.database import engine

MIGRATIONS_DIR = pathlib.Path(__file__).parent.parent / "migrations"

with engine.begin() as conn:
    for sql_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
        print(f"적용: {sql_file.name}")
        conn.execute(text(sql_file.read_text()))
print("마이그레이션 완료")
''',

    "/project/migrations/0001_create_users.sql": '''CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(64) NOT NULL,
    salt          VARCHAR(32) NOT NULL,
    role          VARCHAR(20) NOT NULL DEFAULT 'member',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);
''',

    "/project/migrations/0002_create_orders.sql": '''CREATE TABLE IF NOT EXISTS orders (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users (id),
    total      INTEGER NOT NULL CHECK (total >= 0),
    status     VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders (user_id);
-- 상태 전이: pending -> paid -> shipped -> done, 어느 단계든 -> cancelled
''',

    "/project/migrations/0003_create_products.sql": '''CREATE TABLE IF NOT EXISTS products (
    id     SERIAL PRIMARY KEY,
    name   VARCHAR(100) NOT NULL,
    price  INTEGER NOT NULL CHECK (price > 0),
    stock  INTEGER NOT NULL DEFAULT 0,
    active BOOLEAN NOT NULL DEFAULT true
);

CREATE INDEX IF NOT EXISTS idx_products_name ON products (name);
''',

    # ── 문서 / 로그 ───────────────────────────────────────
    "/project/docs/architecture.md": '''# 아키텍처 개요

요청 흐름: Router → Service → Repository → DB

- Router: HTTP 입출력과 인증/권한 검사만. 비즈니스 로직 금지.
- Service: 비즈니스 규칙의 유일한 위치. 트랜잭션 경계도 여기서.
- Repository: SQLAlchemy 쿼리 전담. Service 밖에서 직접 호출 금지.

## 금액 처리 원칙

- 모든 금액은 **원 단위 정수**. float 사용 금지.
- 할인 적용 순서: 상품 금액 → 쿠폰 → 배송비 (ORDER-482 는 이 순서 위반 버그)

## 인증

- JWT (HS256), 만료 60분. 시크릿은 환경변수 JWT_SECRET.
- 비밀번호 해시는 sha256+salt — bcrypt 이전 예정 (AUTH-201).
''',

    "/project/docs/todo.md": '''# 팀 할 일 메모

- [ ] ORDER-482: 쿠폰 할인을 subtotal 에만 적용하도록 수정
- [ ] ORDER-517: 쿠폰 사용 이력 테이블 추가해서 중복 적용 차단
- [ ] AUTH-201: 비밀번호 해시 bcrypt 이전
- [ ] PAY-77: charge_legacy 호출부 제거 후 함수 삭제
- [x] 상품 검색 페이지네이션 적용
- [ ] users 목록 API 페이지네이션 적용
''',


    "/project/logs/app.log": '''[INFO] 2026-07-23 11:58:02 app — 서버 시작 (버전 0.4.2, DEBUG=True)
[INFO] 2026-07-23 12:00:11 app.orders — 주문 생성 user=2 total=15000
[warn] timeout exceeded at 12:01 — POST https://pay.example.com/v2/charge (30s)
[info] retry ok at 12:02 — 재시도 1회 만에 성공
[INFO] 2026-07-23 12:05:44 app.orders — 주문 생성 user=2 total=64000
[ERROR] 2026-07-23 12:07:19 app.payment — fetch failed after 3 retries (order=1042)
[INFO] 2026-07-23 12:07:19 app.orders — 주문 1042 상태 pending 유지, 수동 확인 필요
[warn] 2026-07-23 12:31:05 app.auth — 로그인 5회 연속 실패 username=hong
''',

}


if __name__ == "__main__":
    total_bytes = sum(len(c.encode()) for c in FS.values())
    print(f"파일 {len(FS)}개, 총 {total_bytes:,} bytes")
    for path in sorted(FS):
        lines = FS[path].count("\n")
        print(f"  {path}  ({lines}줄)")
