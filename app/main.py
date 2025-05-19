from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import authorization, product, cart, user  # Добавляем импорт cart

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(authorization.router)
app.include_router(product.router)
app.include_router(cart.router)

app.include_router(user.router)# Регистрируем роутер корзины