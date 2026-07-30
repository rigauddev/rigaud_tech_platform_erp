from enum import StrEnum


class EntitlementType(StrEnum):
    MODULE = "module"
    FEATURE = "feature"
    LIMIT = "limit"


class EntitlementKey(StrEnum):
    FINANCE = "finance"
    PRODUCTS = "products"
    CLIENTS = "clients"
    DELIVERY = "delivery"
    KDS = "kds"
    NFC_E = "nfc_e"
    WEB = "web"
    ANDROID = "android"
    IOS = "ios"
    WINDOWS = "windows"
    MACOS = "macos"
    RESTAURANT = "restaurant"
    QR_MENU = "qr_menu"
    SELF_CHECKOUT = "self_checkout"
    PIX = "pix"
    DIGITAL_TABLE = "digital_table"
    ONLINE_RESERVATION = "online_reservation"
    DIGITAL_TAB = "digital_tab"
