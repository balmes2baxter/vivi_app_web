from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter
from core.views import ClienteViewSet

router = DefaultRouter()
router.register(r"clientes", ClienteViewSet, basename="cliente")

urlpatterns = [
    path("admin/", admin.site.urls),
    # 🔐 Rutas de autenticación con JWT
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include(router.urls)),
]
