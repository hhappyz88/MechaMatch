from .base import SaveModifier
from .group_by_parent import GroupByParent

SAVE_TYPES: dict[str, type[SaveModifier]] = {
    "default": SaveModifier,
    "group_by_parent": GroupByParent,
}
