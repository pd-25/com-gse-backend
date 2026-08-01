from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.rich_text import sanitize_rich_text


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class AdminCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    is_subadmin: bool = True


class AdminUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)
    is_subadmin: bool | None = None


class CategoryAdminRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    slug: str = Field(min_length=2, max_length=255)
    description: str | None = None
    quality_standards: str | None = None
    buying_guide: str | None = None
    image: str | None = None
    thumbnail_image: str | None = None
    showcase_image: str | None = None
    showcase_tag: str | None = Field(default=None, max_length=100)
    showcase_description: str | None = Field(default=None, max_length=255)
    showcase_button_text: str | None = Field(default=None, max_length=100)
    showcase_button_url: str | None = Field(default=None, max_length=500)
    is_showcase: bool = False
    display_order: int = 0
    parent_id: int | None = None
    is_active: bool = True

    @field_validator("description", "quality_standards", "buying_guide")
    @classmethod
    def sanitize_long_form_content(cls, value: str | None) -> str | None:
        return sanitize_rich_text(value)


class ProductImageAdminRequest(BaseModel):
    image: str = Field(min_length=1)
    file_type: str = "image"
    is_preview: bool = False

    @field_validator("file_type")
    @classmethod
    def valid_file_type(cls, value: str) -> str:
        if value not in {"image", "video", "motion", "gif"}:
            raise ValueError("Unsupported file type")
        return value


class ProductAdminRequest(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    slug: str = Field(min_length=2, max_length=255)
    brand: str | None = Field(default=None, max_length=150)
    description: str | None = None
    short_desc: str | None = None
    currency: str = Field(default="USD", min_length=3, max_length=10)
    price: Decimal = Field(ge=0)
    old_price: Decimal | None = Field(default=None, ge=0)
    rating: Decimal | None = Field(default=None, ge=0, le=5)
    sold_count: int = Field(default=0, ge=0)
    badge: str | None = Field(default=None, max_length=100)
    is_flash_sale: bool = False
    display_order: int = 0
    price_per_measurement: str | None = Field(default=None, max_length=50)
    min_order: int | None = Field(default=None, ge=1)
    category_id: int | None = None
    subcategory_id: int | None = None
    id_recomended: bool = False
    images: list[ProductImageAdminRequest] = Field(default_factory=list)

    @field_validator("description")
    @classmethod
    def sanitize_long_form_content(cls, value: str | None) -> str | None:
        return sanitize_rich_text(value)


class HeroBannerAdminRequest(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    subtitle: str | None = Field(default=None, max_length=255)
    price: Decimal | None = Field(default=None, ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    image: str = Field(min_length=1)
    button_text: str = Field(default="Explore Shop", min_length=1, max_length=100)
    button_url: str = Field(default="/products", min_length=1, max_length=500)
    display_order: int = 0
    is_active: bool = True


class PromotionalCardAdminRequest(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    price: Decimal = Field(ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    image: str = Field(min_length=1)
    button_text: str = Field(default="Shop Now", min_length=1, max_length=100)
    button_url: str = Field(default="/products", min_length=1, max_length=500)
    display_order: int = 0
    is_active: bool = True


class HomepageSectionAdminRequest(BaseModel):
    section_key: str = Field(min_length=2, max_length=100)
    title: str = Field(min_length=2, max_length=255)
    subtitle: str | None = None
    display_order: int = 0
    is_active: bool = True


class FooterSettingAdminRequest(BaseModel):
    brand_name: str = Field(min_length=2, max_length=255)
    brand_highlight: str | None = Field(default=None, max_length=255)
    popular_categories_heading: str = Field(max_length=100)
    customer_services_heading: str = Field(max_length=100)
    contact_heading: str = Field(max_length=100)
    whatsapp_label: str = Field(max_length=100)
    whatsapp_number: str = Field(max_length=40)
    phone_label: str = Field(max_length=100)
    phone_number: str = Field(max_length=40)
    email: EmailStr | None = None
    connect_label: str = Field(max_length=100)
    connect_url: str = Field(max_length=500)
    store_label: str = Field(max_length=100)
    store_url: str = Field(max_length=500)
    app_heading: str = Field(max_length=100)
    app_store_url: str | None = Field(default=None, max_length=500)
    app_store_badge: str | None = Field(default=None, max_length=500)
    play_store_url: str | None = Field(default=None, max_length=500)
    play_store_badge: str | None = Field(default=None, max_length=500)
    copyright_text: str = Field(max_length=500)
    is_active: bool = True


class FooterLinkAdminRequest(BaseModel):
    section: str = Field(min_length=2, max_length=50)
    label: str = Field(min_length=2, max_length=255)
    slug: str | None = Field(default=None, max_length=255)
    url: str = Field(min_length=1, max_length=500)
    content: str | None = None
    sort_order: int = 0
    is_active: bool = True

    @field_validator("section")
    @classmethod
    def valid_footer_section(cls, value: str) -> str:
        if value not in {"popular_category", "customer_service"}:
            raise ValueError("Unsupported footer section")
        return value


class UserAdminUpdateRequest(BaseModel):
    is_active: bool | None = None
    is_verified: bool | None = None


class OrderAdminUpdateRequest(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def valid_status(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"pending", "paid", "processing", "completed", "cancelled", "refunded"}:
            raise ValueError("Unsupported order status")
        return normalized
