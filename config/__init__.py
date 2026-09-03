import pymysql

# Django's mysql backend expects the MySQLdb module; PyMySQL provides a compatible shim.
pymysql.install_as_MySQLdb()
# PyMySQL reports itself as version 1.4.6 for compatibility; Django's mysql
# backend requires mysqlclient>=2.2.1, so override the reported version.
pymysql.version_info = (2, 2, 4, "final", 0)
