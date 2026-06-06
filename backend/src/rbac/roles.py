from .permissions import Permissions

ROLES = {
    "admin": {
        Permissions.ADMIN_PANEL,
        Permissions.ADMIN_USERS,
        Permissions.ADMIN_SETTINGS,
        Permissions.SECURE_READ,
        Permissions.SECURE_WRITE,
        Permissions.TASKS_READ,
        Permissions.TASKS_WRITE,
        Permissions.DASHBOARD_VIEW,
    },
    "user": {
        Permissions.DASHBOARD_VIEW,
        Permissions.SECURE_READ,
    },
    "guest": {
        Permissions.DASHBOARD_VIEW,
    }
}
