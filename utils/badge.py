def status_badge(status):

    badges = {

        "Pending": "warning",

        "Preparing": "primary",

        "Ready": "success",

        "Completed": "dark",

        "Cancelled": "danger"

    }

    return badges.get(status, "secondary")