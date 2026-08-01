from dataclasses import dataclass
from decimal import Decimal

from app.modules.companies.domain.entities import BranchType, CompanyRole
from app.modules.products.domain.entities import ProductType, UnitOfMeasure

DEMO_PASSWORD = "senha123"
PLATFORM_SLUG = "rigaud-platform"
RESTAURANT_SLUG = "sabor-da-serra"
RETAIL_SLUG = "moda-center"
RESETTABLE_TENANT_SLUGS = (RESTAURANT_SLUG, RETAIL_SLUG)


def valid_cnpj(seed: int) -> str:
    base = f"{seed:08d}0001"[-12:]

    def digit(value: str, weights: list[int]) -> str:
        total = sum(int(item) * weight for item, weight in zip(value, weights, strict=True))
        remainder = total % 11
        return str(0 if remainder < 2 else 11 - remainder)

    first = digit(base, [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    second = digit(base + first, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    return base + first + second


@dataclass(frozen=True)
class DemoCompany:
    legal_name: str
    trade_name: str
    document: str
    email: str
    phone: str
    slug: str
    code: str


@dataclass(frozen=True)
class DemoBranch:
    code: str
    name: str
    branch_type: BranchType
    is_headquarters: bool
    email: str
    phone: str
    address: str


@dataclass(frozen=True)
class DemoUser:
    email: str
    first_name: str
    last_name: str
    display_name: str
    phone: str
    company_role: CompanyRole
    is_superuser: bool = False


@dataclass(frozen=True)
class DemoCategory:
    internal_code: str
    name: str
    slug: str
    description: str
    icon: str
    color: str
    display_order: int


@dataclass(frozen=True)
class DemoProduct:
    internal_code: str
    name: str
    description: str
    product_type: ProductType
    unit_of_measure: UnitOfMeasure
    sale_price: Decimal
    cost_price: Decimal


PLATFORM_COMPANY = DemoCompany(
    legal_name="Rigaud Tech Platform Ltda",
    trade_name="Rigaud Tech Platform",
    document=valid_cnpj(9001),
    email="platform@rigaudtech.com",
    phone="75982165869",
    slug=PLATFORM_SLUG,
    code="RIGAUD",
)

PLATFORM_USERS = (
    DemoUser(
        email="platform@rigaudtech.com",
        first_name="Administrador",
        last_name="Plataforma",
        display_name="Administrador Plataforma",
        phone="75982165860",
        company_role=CompanyRole.COMPANY_ADMIN,
        is_superuser=True,
    ),
    DemoUser(
        email="suporte@rigaudtech.com",
        first_name="Suporte",
        last_name="Rigaud",
        display_name="Suporte Rigaud",
        phone="75982165861",
        company_role=CompanyRole.MEMBER,
    ),
    DemoUser(
        email="financeiro@rigaudtech.com",
        first_name="Financeiro",
        last_name="Rigaud",
        display_name="Financeiro Rigaud",
        phone="75982165862",
        company_role=CompanyRole.MEMBER,
    ),
    DemoUser(
        email="comercial@rigaudtech.com",
        first_name="Comercial",
        last_name="Rigaud",
        display_name="Comercial Rigaud",
        phone="75982165863",
        company_role=CompanyRole.MEMBER,
    ),
)

RESTAURANT_COMPANY = DemoCompany(
    legal_name="Restaurante Sabor da Serra Ltda",
    trade_name="Restaurante Sabor da Serra",
    document=valid_cnpj(9002),
    email="contato@sabordaserra.demo",
    phone="75982165870",
    slug=RESTAURANT_SLUG,
    code="SABOR",
)

RESTAURANT_BRANCHES = (
    DemoBranch(
        code="MATRIZ",
        name="Matriz",
        branch_type=BranchType.HEADQUARTERS,
        is_headquarters=True,
        email="matriz@sabordaserra.demo",
        phone="75982165871",
        address="Rua das Palmeiras, 100 - Centro",
    ),
    DemoBranch(
        code="DELIVERY",
        name="Delivery",
        branch_type=BranchType.STORE,
        is_headquarters=False,
        email="delivery@sabordaserra.demo",
        phone="75982165872",
        address="Rua das Palmeiras, 120 - Centro",
    ),
    DemoBranch(
        code="FOODTRUCK",
        name="Food Truck",
        branch_type=BranchType.STORE,
        is_headquarters=False,
        email="foodtruck@sabordaserra.demo",
        phone="75982165873",
        address="Eventos externos",
    ),
)

RESTAURANT_USERS = (
    DemoUser(
        "admin@demo.local", "Admin", "Demo", "Admin Demo", "75982165900", CompanyRole.COMPANY_ADMIN
    ),
    DemoUser(
        "gerente@demo.local",
        "Gerente",
        "Sabor",
        "Gerente Sabor",
        "75982165901",
        CompanyRole.COMPANY_ADMIN,
    ),
    DemoUser(
        "caixa@demo.local", "Caixa", "Sabor", "Caixa Sabor", "75982165902", CompanyRole.MEMBER
    ),
    DemoUser(
        "garcom1@demo.local", "Joao", "Garcom", "Garcom Joao", "75982165903", CompanyRole.MEMBER
    ),
    DemoUser(
        "garcom2@demo.local", "Carlos", "Garcom", "Garcom Carlos", "75982165904", CompanyRole.MEMBER
    ),
    DemoUser(
        "garcom3@demo.local", "Pedro", "Garcom", "Garcom Pedro", "75982165905", CompanyRole.MEMBER
    ),
    DemoUser(
        "cozinha@demo.local", "Ana", "Cozinha", "Cozinha Ana", "75982165906", CompanyRole.MEMBER
    ),
    DemoUser(
        "estoque@demo.local",
        "Marcos",
        "Estoque",
        "Estoque Marcos",
        "75982165907",
        CompanyRole.MEMBER,
    ),
    DemoUser(
        "financeiro@demo.local",
        "Fernanda",
        "Financeiro",
        "Financeiro Fernanda",
        "75982165908",
        CompanyRole.MEMBER,
    ),
)

RESTAURANT_CATEGORIES = (
    DemoCategory(
        "REST-CAT-001", "Bebidas", "bebidas", "Bebidas frias e quentes.", "local_bar", "#0088AA", 1
    ),
    DemoCategory(
        "REST-CAT-002",
        "Entradas",
        "entradas",
        "Porcoes e itens para compartilhar.",
        "tapas",
        "#AA6C39",
        2,
    ),
    DemoCategory(
        "REST-CAT-003", "Pratos", "pratos", "Pratos principais.", "restaurant", "#2F855A", 3
    ),
    DemoCategory(
        "REST-CAT-004", "Sobremesas", "sobremesas", "Doces e sobremesas.", "icecream", "#B83280", 4
    ),
    DemoCategory(
        "REST-CAT-005", "Promocoes", "promocoes", "Combos e promocoes.", "campaign", "#D69E2E", 5
    ),
)

RETAIL_COMPANY = DemoCompany(
    legal_name="Moda Center Comercio de Roupas Ltda",
    trade_name="Moda Center",
    document=valid_cnpj(9003),
    email="contato@modacenter.demo",
    phone="75982165880",
    slug=RETAIL_SLUG,
    code="MODA",
)

RETAIL_BRANCHES = (
    DemoBranch(
        code="SHOPPING",
        name="Shopping",
        branch_type=BranchType.HEADQUARTERS,
        is_headquarters=True,
        email="shopping@modacenter.demo",
        phone="75982165881",
        address="Shopping Principal, Loja 210",
    ),
    DemoBranch(
        code="CENTRO",
        name="Centro",
        branch_type=BranchType.STORE,
        is_headquarters=False,
        email="centro@modacenter.demo",
        phone="75982165882",
        address="Avenida Comercial, 55 - Centro",
    ),
)

RETAIL_USERS = (
    DemoUser(
        "admin@modacenter.demo",
        "Admin",
        "Moda",
        "Admin Moda",
        "75982165920",
        CompanyRole.COMPANY_ADMIN,
    ),
    DemoUser(
        "gerente@modacenter.demo",
        "Gerente",
        "Moda",
        "Gerente Moda",
        "75982165921",
        CompanyRole.COMPANY_ADMIN,
    ),
    DemoUser(
        "vendedor@demo.local",
        "Vendedor",
        "Moda",
        "Vendedor Moda",
        "75982165922",
        CompanyRole.MEMBER,
    ),
    DemoUser(
        "caixa@modacenter.demo", "Caixa", "Moda", "Caixa Moda", "75982165923", CompanyRole.MEMBER
    ),
    DemoUser(
        "estoque@modacenter.demo",
        "Estoque",
        "Moda",
        "Estoque Moda",
        "75982165924",
        CompanyRole.MEMBER,
    ),
)

RETAIL_CATEGORIES = (
    DemoCategory(
        "RETAIL-CAT-001",
        "Calcados",
        "calcados",
        "Calcados masculinos e femininos.",
        "steps",
        "#2B6CB0",
        1,
    ),
    DemoCategory(
        "RETAIL-CAT-002", "Roupas", "roupas", "Pecas de vestuario.", "checkroom", "#553C9A", 2
    ),
    DemoCategory(
        "RETAIL-CAT-003", "Bolsas", "bolsas", "Bolsas e mochilas.", "shopping_bag", "#975A16", 3
    ),
    DemoCategory(
        "RETAIL-CAT-004", "Acessorios", "acessorios", "Acessorios de moda.", "watch", "#2C7A7B", 4
    ),
)


def restaurant_products() -> tuple[DemoProduct, ...]:
    names = [
        "Hamburguer Artesanal",
        "Pizza Marguerita",
        "Pizza Calabresa",
        "Refrigerante Cola",
        "Refrigerante Guarana",
        "Suco de Laranja",
        "Suco de Uva",
        "Batata Frita",
        "Aneis de Cebola",
        "Salada Caesar",
        "Frango Grelhado",
        "Bife Acebolado",
        "Feijoada",
        "Moqueca",
        "Lasanha",
        "Risoto de Cogumelos",
        "Petit Gateau",
        "Pudim",
        "Mousse de Maracuja",
        "Cafe Espresso",
        "Agua Mineral",
        "Cerveja Pilsen",
        "Cerveja IPA",
        "Combo Familia",
        "Combo Executivo",
    ]
    products: list[DemoProduct] = []
    for index in range(50):
        name = names[index % len(names)]
        suffix = (index // len(names)) + 1
        display_name = name if suffix == 1 else f"{name} {suffix}"
        sale_price = Decimal("8.90") + Decimal(index) * Decimal("1.35")
        cost_price = sale_price * Decimal("0.42")
        products.append(
            DemoProduct(
                internal_code=f"REST-PRD-{index + 1:03d}",
                name=display_name,
                description="Produto demo para validacao de cardapio e vendas futuras.",
                product_type=ProductType.PREPARED_ITEM,
                unit_of_measure=UnitOfMeasure.UNIT,
                sale_price=sale_price.quantize(Decimal("0.01")),
                cost_price=cost_price.quantize(Decimal("0.01")),
            )
        )
    return tuple(products)


def retail_products() -> tuple[DemoProduct, ...]:
    names = [
        "Camisa Social",
        "Camiseta Basica",
        "Calca Jeans",
        "Vestido Midi",
        "Blazer",
        "Jaqueta Jeans",
        "Tenis Casual",
        "Sandalia",
        "Bota Cano Curto",
        "Bolsa Tote",
        "Mochila Urbana",
        "Cinto Couro",
        "Oculos de Sol",
        "Relogio Casual",
        "Saia Plissada",
        "Shorts Sarja",
    ]
    products: list[DemoProduct] = []
    for index in range(80):
        name = names[index % len(names)]
        suffix = (index // len(names)) + 1
        display_name = f"{name} Demo {suffix}"
        sale_price = Decimal("39.90") + Decimal(index) * Decimal("2.15")
        cost_price = sale_price * Decimal("0.48")
        products.append(
            DemoProduct(
                internal_code=f"RETAIL-PRD-{index + 1:03d}",
                name=display_name,
                description="Produto demo para validacao futura do fluxo de loja.",
                product_type=ProductType.SIMPLE,
                unit_of_measure=UnitOfMeasure.UNIT,
                sale_price=sale_price.quantize(Decimal("0.01")),
                cost_price=cost_price.quantize(Decimal("0.01")),
            )
        )
    return tuple(products)
