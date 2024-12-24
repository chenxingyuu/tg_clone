from typing import Union, List, Set

from app.system.models import Permission
from cores.log import LOG

scopes = {}


async def init_scopes():
    global scopes

    scopes = {
        permission.name: permission.description
        for permission in await Permission.get_queryset().all()
    }
    LOG.info(f"初始化权限范围 {scopes = }")


def filter_scopes(scope_list: Union[List[str], Set[str]]) -> List[str]:
    """
    过滤范围
    >>> filter_scopes(["a:b:c", "a:b:d", "a:b", "d", "e:f"])
    ['d', 'a:b', 'e:f']
    """
    # 按层级排序
    sorted_scopes = sorted(scope_list, key=lambda x: x.count(":"))

    result = []
    # 使用一个集合来跟踪已处理的权限
    covered_scopes = set()

    for scope in sorted_scopes:
        # 检查当前权限是否被其他权限覆盖
        if not any(scope.startswith(covered_scope + ":") for covered_scope in covered_scopes):
            result.append(scope)
            covered_scopes.add(scope)

    return result
