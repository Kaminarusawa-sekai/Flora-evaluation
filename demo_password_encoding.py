"""
演示密码编码效果
"""
from core.env_utils import get_database_url, build_database_url, encode_db_password

print("=" * 70)
print("数据库密码特殊字符编码演示")
print("=" * 70)

# 示例 1: 直接编码密码
password = "LDPP@MySQL82024!"
encoded = encode_db_password(password)
print(f"\n原始密码: {password}")
print(f"编码后密码: {encoded}")

# 示例 2: 构建完整的数据库 URL
print("\n" + "=" * 70)
print("构建数据库 URL")
print("=" * 70)

url = build_database_url(
    dialect='mysql',
    driver='pymysql',
    username='root',
    password='LDPP@MySQL82024!',
    host='192.168.1.33',
    port=8888,
    database='eqiai_erp'
)

print(f"\n构建的 URL: {url}")

# 示例 3: 从环境变量获取并自动编码
print("\n" + "=" * 70)
print("从 .env 文件自动处理")
print("=" * 70)

from dotenv import load_dotenv
load_dotenv()

encoded_url = get_database_url('DATABASE_URL')
print(f"\n原始 .env 配置:")
print(f"DATABASE_URL=mysql+pymysql://root:LDPP@MySQL82024!@192.168.1.33:8888/eqiai_erp")
print(f"\n自动编码后:")
print(f"{encoded_url}")

print("\n" + "=" * 70)
print("✅ 编码完成！现在可以安全地使用这个 URL 连接数据库了")
print("=" * 70)
