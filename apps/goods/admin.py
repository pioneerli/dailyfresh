from django.contrib import admin

# Register your models here.
from apps.goods.models import Goods,GoodsType, GoodsSKU, GoodsImage, IndexGoodsBanner, IndexTypeGoodsBanner, \
    IndexPromotionBanner

admin.site.register(Goods)
admin.site.register(GoodsSKU)
admin.site.register(GoodsType)
admin.site.register(GoodsImage)
admin.site.register(IndexGoodsBanner)
admin.site.register(IndexTypeGoodsBanner)
admin.site.register(IndexPromotionBanner)