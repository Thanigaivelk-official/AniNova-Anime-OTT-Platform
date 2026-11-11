import pymysql
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.mysql.features import DatabaseFeatures

# Enable PyMySQL as MySQLdb drop-in replacement
pymysql.install_as_MySQLdb()

# Compatibility patches for MariaDB 10.4 running on Django 5.1
BaseDatabaseWrapper.check_database_version_supported = lambda self: None
DatabaseFeatures.can_return_columns_from_insert = property(lambda self: False)
