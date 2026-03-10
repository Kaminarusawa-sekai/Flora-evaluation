"""
简单的数据库连接测试
"""

import pymysql
from urllib.parse import quote_plus

# 测试不同的连接方式
def test_direct_connection():
    """直接使用pymysql测试连接"""
    print("=" * 60)
    print("测试直接连接")
    print("=" * 60)

    try:
        connection = pymysql.connect(
            host='192.168.1.33',
            port=8888,
            user='root',
            password='LDPP@MySQL82024!',
            database='eqiai_erp',
            charset='utf8mb4'
        )

        print("[OK] 连接成功！")

        # 测试查询
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"[OK] 找到 {len(tables)} 张表")
            print(f"[OK] 前5张表: {[t[0] for t in tables[:5]]}")

        connection.close()
        return True

    except Exception as e:
        print(f"[FAIL] 连接失败: {e}")
        return False


def test_sqlalchemy_connection():
    """使用SQLAlchemy测试连接"""
    print("\n" + "=" * 60)
    print("测试SQLAlchemy连接")
    print("=" * 60)

    try:
        from sqlalchemy import create_engine, text

        password = quote_plus('LDPP@MySQL82024!')
        db_url = f"mysql+pymysql://root:{password}@192.168.1.33:8888/eqiai_erp"

        print(f"连接字符串: mysql+pymysql://root:***@192.168.1.33:8888/eqiai_erp")

        engine = create_engine(db_url)

        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES"))
            tables = result.fetchall()
            print(f"[OK] 连接成功！")
            print(f"[OK] 找到 {len(tables)} 张表")
            print(f"[OK] 前5张表: {[t[0] for t in tables[:5]]}")

        return True

    except Exception as e:
        print(f"[FAIL] 连接失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("数据库连接测试\n")

    # 测试1: 直接连接
    result1 = test_direct_connection()

    # 测试2: SQLAlchemy连接
    result2 = test_sqlalchemy_connection()

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"{'[OK]' if result1 else '[FAIL]'} 直接连接: {'通过' if result1 else '失败'}")
    print(f"{'[OK]' if result2 else '[FAIL]'} SQLAlchemy连接: {'通过' if result2 else '失败'}")

    if not result1 and not result2:
        print("\n可能的问题：")
        print("1. 数据库密码不正确")
        print("2. 数据库不允许从当前IP连接")
        print("3. 数据库服务未启动或端口不正确")
        print("4. 防火墙阻止了连接")
