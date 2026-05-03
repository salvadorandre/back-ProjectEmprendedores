import pymysql

# Esto hace que Django use PyMySQL como si fuera el conector oficial de MySQL
pymysql.install_as_MySQLdb()
