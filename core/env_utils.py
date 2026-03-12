"""
环境变量工具函数
"""
import os
from urllib.parse import quote_plus, urlparse, urlunparse


def get_database_url(env_var: str = 'DATABASE_URL') -> str:
    """
    获取数据库 URL，自动处理密码中的特殊字符
    
    Args:
        env_var: 环境变量名称
        
    Returns:
        处理后的数据库 URL
    """
    url = os.getenv(env_var)
    if not url:
        return None
    
    # 如果 URL 中包含密码，需要对密码进行编码
    try:
        # 解析 URL
        parsed = urlparse(url)
        
        # 如果有用户名和密码
        if parsed.username and parsed.password:
            # 对密码进行 URL 编码
            encoded_password = quote_plus(parsed.password)
            
            # 重新构建 netloc
            if parsed.port:
                netloc = f"{parsed.username}:{encoded_password}@{parsed.hostname}:{parsed.port}"
            else:
                netloc = f"{parsed.username}:{encoded_password}@{parsed.hostname}"
            
            # 重新构建 URL
            encoded_url = urlunparse((
                parsed.scheme,
                netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment
            ))
            
            return encoded_url
        
        return url
        
    except Exception as e:
        # 如果解析失败，返回原始 URL
        return url


def encode_db_password(password: str) -> str:
    """
    对数据库密码进行 URL 编码
    
    Args:
        password: 原始密码
        
    Returns:
        编码后的密码
    """
    return quote_plus(password)


def build_database_url(
    dialect: str,
    driver: str,
    username: str,
    password: str,
    host: str,
    port: int,
    database: str
) -> str:
    """
    构建数据库 URL，自动处理密码编码
    
    Args:
        dialect: 数据库类型 (mysql, postgresql, etc.)
        driver: 驱动名称 (pymysql, psycopg2, etc.)
        username: 用户名
        password: 密码（原始密码，会自动编码）
        host: 主机地址
        port: 端口号
        database: 数据库名
        
    Returns:
        完整的数据库 URL
        
    Example:
        >>> build_database_url('mysql', 'pymysql', 'root', 'pass@word!', 'localhost', 3306, 'mydb')
        'mysql+pymysql://root:pass%40word%21@localhost:3306/mydb'
    """
    encoded_password = quote_plus(password)
    
    if driver:
        scheme = f"{dialect}+{driver}"
    else:
        scheme = dialect
    
    return f"{scheme}://{username}:{encoded_password}@{host}:{port}/{database}"
