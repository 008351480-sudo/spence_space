
import re
from pathlib import Path

from docx import Document
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Recipe


class Command(BaseCommand):
    help = "Import recipes from Recipe List.docx"

    def handle(self, *args, **options):
        file_path = Path(settings.BASE_DIR) / "Recipe List.docx"

        if not file_path.exists():
            raise CommandError(f"File not found: {file_path}")

        document = Document(file_path)

        created = 0
        updated = 0
        skipped = 0

        pattern = re.compile(
            r"^\s*\d+\s*:\s*(.+?)\s*:\s*(https?://\S+)\s*$"
        )


        for paragraph in document.paragraphs:
            for line in paragraph.text.splitlines():
                line = line.strip()

                if not line:
                    continue

                match = pattern.match(line)

                if not match:
                    self.stdout.write(
                        self.style.WARNING(f"Skipped: {line}")
                    )
                    skipped += 1
                    continue

                name = match.group(1).strip()
                source_url = match.group(2).strip()

                recipe, was_created = Recipe.objects.update_or_create(
                    name=name,
                    defaults={"source_url": source_url},
                )

                if was_created:
                    created += 1
                else:
                    updated += 1


        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete! "
                f"Created: {created}, "
                f"Updated: {updated}, "
                f"Skipped: {skipped}"
            )
        )
