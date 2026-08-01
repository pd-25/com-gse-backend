from pydantic import BaseModel, ConfigDict


class FooterSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    brand_name: str
    brand_highlight: str | None
    popular_categories_heading: str
    customer_services_heading: str
    contact_heading: str
    whatsapp_label: str
    whatsapp_number: str
    phone_label: str
    phone_number: str
    email: str | None
    connect_label: str
    connect_url: str
    store_label: str
    store_url: str
    app_heading: str
    app_store_url: str | None
    app_store_badge: str | None
    play_store_url: str | None
    play_store_badge: str | None
    copyright_text: str


class FooterLinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    label: str
    slug: str | None
    url: str
    sort_order: int


class FooterResponse(BaseModel):
    settings: FooterSettingsResponse
    popular_categories_heading: str
    customer_services_heading: str
    popular_categories: list[FooterLinkResponse]
    customer_services: list[FooterLinkResponse]


class FooterPageResponse(BaseModel):
    title: str
    slug: str
    content: str
