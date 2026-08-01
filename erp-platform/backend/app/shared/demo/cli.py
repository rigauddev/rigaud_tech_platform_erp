import argparse
import asyncio
import json

from app.database.session import session_context
from app.shared.demo.data import DEMO_PASSWORD
from app.shared.demo.service import DemoSeeder


async def run(action: str, password: str) -> dict[str, int | str]:
    async with session_context() as session:
        seeder = DemoSeeder(session=session, password=password)
        if action == "all":
            return (await seeder.seed_all()).as_dict()
        if action == "platform":
            return (await seeder.seed_platform()).as_dict()
        if action == "restaurant":
            return (await seeder.seed_restaurant()).as_dict()
        if action == "retail":
            return (await seeder.seed_retail()).as_dict()
        if action == "reset":
            return (await seeder.reset()).as_dict()
        if action == "status":
            return await seeder.status()
        if action == "scenarios":
            return await seeder.scenarios()
    raise ValueError(f"Unsupported demo action: {action}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed Rigaud ERP demo environment.")
    parser.add_argument(
        "action",
        choices=("all", "platform", "restaurant", "retail", "reset", "status", "scenarios"),
        help="Demo dataset to apply.",
    )
    parser.add_argument(
        "--password",
        default=DEMO_PASSWORD,
        help="Password assigned to demo accounts.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = asyncio.run(run(args.action, args.password))
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
