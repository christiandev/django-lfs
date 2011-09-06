# django importsad
from django.core.management.base import BaseCommand
from django.db import models

# lfs imports
from lfs.voucher.models import Voucher
import lfs.core.settings as lfs_settings

# south imports
from south.db import db


class Command(BaseCommand):
    args = ''
    help = 'Migrations for LFS'

    def handle(self, *args, **options):
        """
        """
        # 0.5 -> trunk
        db.add_column("voucher_voucher", "used_amount", models.PositiveSmallIntegerField(default=0))
        db.add_column("voucher_voucher", "last_used_date", models.DateTimeField(blank=True, null=True))
        db.add_column("voucher_voucher", "limit", models.PositiveSmallIntegerField(default=1))

        for voucher in Voucher.objects.all():
            voucher.limit = 1
            voucher.save()

        # This mus be done with execute because the old fields are not there
        # anymore (and therefore can't be accessed via attribute) after the user
        # has upgraded to the latest version.
        db.execute("update voucher_voucher set used_amount = 1 where used = 1")
        db.execute("update voucher_voucher set used_amount = 0 where used = 0")
        db.execute("update voucher_voucher set last_used_date = used_date")

        db.delete_column('voucher_voucher', 'used')
        db.delete_column('voucher_voucher', 'used_date')

        # price calculator
        db.add_column("catalog_product", "price_calculator", models.CharField(
            null=True, blank=True, choices=lfs_settings.LFS_PRICE_CALCULATOR_DICTIONARY.items(), max_length=255))

        db.add_column("core_shop", "price_calculator",
            models.CharField(choices=lfs_settings.LFS_PRICE_CALCULATOR_DICTIONARY.items(), default=lfs_settings.LFS_DEFAULT_PRICE_CALCULATOR, max_length=255))

        # Currencies now set in lfs.core.settings.LFS_LOCALE
        print 'Warning, you must set the variable LFS_LOCALE to a value that supports your default currency in lfs/core/settings.py e.g. LFS_LOCALE="en_US.utf8"'
        db.delete_column('core_shop', 'default_currency')
