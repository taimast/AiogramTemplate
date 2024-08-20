from sqladmin import ModelView

from src.db.models import User


class BaseAdmin(ModelView):
    is_async = True

    column_list = "__all__"
    column_details_list = "__all__"

    column_searchable_list = ["id"]


class UserAdmin(BaseAdmin, model=User):
    column_searchable_list = ["id", "username"]
