import csv
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction as db_transaction

# ✅ Adjust these imports to your project
from financial_companion.models import Transaction, Account  # <-- change this


REQUIRED_HEADERS = {"title", "description", "amount", "send", "receive"}


class Command(BaseCommand):
    help = "Import Transaction rows from a CSV/TSV with columns: title, description, amount, send, receive"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="Path to CSV/TSV file")
        parser.add_argument(
            "--currency",
            default="GBP",
            help="Currency code to use for all imported rows (default: GBP).",
        )
        parser.add_argument(
            "--delimiter",
            default=None,
            help="Force delimiter (e.g. ',' or '\\t'). If omitted, auto-detects.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and validate, but do not write to DB.",
        )
        parser.add_argument(
            "--create-accounts",
            action="store_true",
            help="Create missing accounts by name instead of failing.",
        )
        parser.add_argument(
            "--skip-existing-pairs",
            action="store_true",
            help=(
                "If a Transaction with the same (sender_account, receiver_account) already exists, "
                "skip importing that row (useful if you kept unique_together on those fields)."
            ),
        )

    def _detect_delimiter(self, sample: str) -> str:
        # Prefer tab if it looks like TSV
        if "\t" in sample and sample.count("\t") >= sample.count(","):
            return "\t"
        try:
            return csv.Sniffer().sniff(sample, delimiters=[",", "\t", ";", "|"]).delimiter
        except Exception:
            return ","

    def handle(self, *args, **options):
        file_path = Path(options["file"])
        if not file_path.exists():
            raise CommandError(f"File not found: {file_path}")

        # Read a small sample to detect delimiter
        raw = file_path.read_text(encoding="utf-8-sig")
        sample = raw[:4096]

        delimiter = options["delimiter"]
        if delimiter is None:
            delimiter = self._detect_delimiter(sample)
        if delimiter == "\\t":
            delimiter = "\t"

        reader = csv.DictReader(raw.splitlines(), delimiter=delimiter)

        if not reader.fieldnames:
            raise CommandError("No headers found in file.")

        headers = {h.strip() for h in reader.fieldnames if h}
        missing = REQUIRED_HEADERS - headers
        if missing:
            raise CommandError(f"Missing required headers: {sorted(missing)}. Found: {sorted(headers)}")

        currency = (options["currency"] or "").strip().upper()
        dry_run = options["dry_run"]
        create_accounts = options["create_accounts"]
        skip_existing_pairs = options["skip_existing_pairs"]

        created = 0
        skipped = 0
        errors = 0

        def norm(s: str) -> str:
            return (s or "").strip()

        @db_transaction.atomic
        def run_import():
            nonlocal created, skipped, errors

            for idx, row in enumerate(reader, start=2):  # start=2 because header is line 1
                title = norm(row.get("title"))
                description = norm(row.get("description"))
                amount_raw = norm(row.get("amount"))
                send_name = norm(row.get("send"))
                receive_name = norm(row.get("receive"))

                # Basic validation
                if not title:
                    self.stderr.write(f"Line {idx}: missing title")
                    errors += 1
                    continue
                if not amount_raw:
                    self.stderr.write(f"Line {idx}: missing amount")
                    errors += 1
                    continue
                if not send_name or not receive_name:
                    self.stderr.write(f"Line {idx}: missing send/receive")
                    errors += 1
                    continue

                # Parse Decimal safely
                try:
                    # allow "1,234.56"
                    amount = Decimal(amount_raw.replace(",", ""))
                except Exception:
                    self.stderr.write(f"Line {idx}: invalid amount '{amount_raw}'")
                    errors += 1
                    continue

                # Fetch accounts by name
                sender = Account.objects.filter(name=send_name).first()
                receiver = Account.objects.filter(name=receive_name).first()

                if sender is None:
                    if create_accounts:
                        sender = Account.objects.create(name=send_name)
                    else:
                        self.stderr.write(f"Line {idx}: sender account not found: '{send_name}'")
                        errors += 1
                        continue

                if receiver is None:
                    if create_accounts:
                        receiver = Account.objects.create(name=receive_name)
                    else:
                        self.stderr.write(f"Line {idx}: receiver account not found: '{receive_name}'")
                        errors += 1
                        continue

                if skip_existing_pairs:
                    exists = Transaction.objects.filter(
                        sender_account=sender,
                        receiver_account=receiver,
                    ).exists()
                    if exists:
                        skipped += 1
                        continue

                if not dry_run:
                    Transaction.objects.create(
                        title=title,
                        description=description,
                        amount=amount,
                        currency=currency,
                        sender_account=sender,
                        receiver_account=receiver,
                    )
                created += 1

            if dry_run:
                # prevent accidental commits in dry run
                db_transaction.set_rollback(True)

        run_import()

        self.stdout.write(self.style.SUCCESS(
            f"Done. created={created}, skipped={skipped}, errors={errors}, dry_run={dry_run}, delimiter={repr(delimiter)}"
        ))
