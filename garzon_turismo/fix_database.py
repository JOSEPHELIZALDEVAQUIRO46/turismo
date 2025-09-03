# fix_database.py
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garzon_turismo.settings')
django.setup()

from django.db import connection

def fix_database():
    cursor = connection.cursor()
    
    print("=== VERIFICANDO ESTRUCTURA ACTUAL ===")
    
    # Verificar estructura de categorías
    cursor.execute("DESCRIBE turismo_categoriaactividadfisica")
    columns = cursor.fetchall()
    print("Estructura turismo_categoriaactividadfisica:")
    for col in columns:
        print(f"  {col[0]} - {col[1]}")
    
    print("\n" + "="*50 + "\n")
    
    cursor.execute("DESCRIBE turismo_categoriaartesania")
    columns = cursor.fetchall()
    print("Estructura turismo_categoriaartesania:")
    for col in columns:
        print(f"  {col[0]} - {col[1]}")
    
    print("\n=== AGREGANDO COLUMNAS ===")
    
    # Verificar si las columnas ya existen
    cursor.execute("SHOW COLUMNS FROM turismo_actividadfisica LIKE 'categoria_id'")
    if not cursor.fetchall():
        try:
            print("Agregando categoria_id a turismo_actividadfisica...")
            cursor.execute("ALTER TABLE turismo_actividadfisica ADD COLUMN categoria_id BIGINT NULL")
            print("✓ Columna categoria_id agregada a ActividadFisica")
        except Exception as e:
            print(f"✗ Error agregando categoria_id a ActividadFisica: {e}")
    else:
        print("✓ Columna categoria_id ya existe en ActividadFisica")
    
    cursor.execute("SHOW COLUMNS FROM turismo_artesania LIKE 'categoria_id'")
    if not cursor.fetchall():
        try:
            print("Agregando categoria_id a turismo_artesania...")
            cursor.execute("ALTER TABLE turismo_artesania ADD COLUMN categoria_id BIGINT NULL")
            print("✓ Columna categoria_id agregada a Artesania")
        except Exception as e:
            print(f"✗ Error agregando categoria_id a Artesania: {e}")
    else:
        print("✓ Columna categoria_id ya existe en Artesania")
    
    print("\n=== AGREGANDO ÍNDICES ===")
    
    # Agregar índices
    try:
        cursor.execute("ALTER TABLE turismo_actividadfisica ADD INDEX turismo_actividadfisica_categoria_id_idx (categoria_id)")
        print("✓ Índice agregado a ActividadFisica")
    except Exception as e:
        print(f"Índice ActividadFisica: {e}")
    
    try:
        cursor.execute("ALTER TABLE turismo_artesania ADD INDEX turismo_artesania_categoria_id_idx (categoria_id)")
        print("✓ Índice agregado a Artesania")
    except Exception as e:
        print(f"Índice Artesania: {e}")
    
    print("\n=== AGREGANDO FOREIGN KEYS ===")
    
    # Agregar foreign keys
    try:
        cursor.execute("ALTER TABLE turismo_actividadfisica ADD FOREIGN KEY (categoria_id) REFERENCES turismo_categoriaactividadfisica(id)")
        print("✓ FK agregado a ActividadFisica")
    except Exception as e:
        print(f"FK ActividadFisica: {e}")
    
    try:
        cursor.execute("ALTER TABLE turismo_artesania ADD FOREIGN KEY (categoria_id) REFERENCES turismo_categoriaartesania(id)")
        print("✓ FK agregado a Artesania")
    except Exception as e:
        print(f"FK Artesania: {e}")
    
    print("\n=== VERIFICACIÓN FINAL ===")
    
    # Verificar que las columnas se agregaron
    cursor.execute("SHOW COLUMNS FROM turismo_actividadfisica LIKE 'categoria_id'")
    result = cursor.fetchall()
    print(f"Columna categoria_id en actividadfisica: {'✓ Existe' if result else '✗ No existe'}")
    
    cursor.execute("SHOW COLUMNS FROM turismo_artesania LIKE 'categoria_id'")
    result = cursor.fetchall()
    print(f"Columna categoria_id en artesania: {'✓ Existe' if result else '✗ No existe'}")

if __name__ == "__main__":
    fix_database()
    print("\n=== PROCESO COMPLETADO ===")