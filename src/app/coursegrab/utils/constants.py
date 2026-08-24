ROOT_URL = "https://classes.cornell.edu"

# Possible values for course status
OPEN = "OPEN"
CLOSED = "CLOSED"
WAITLISTED = "WAITLISTED"
ARCHIVED = "ARCHIVED"
INVALID = "INVALID"

# Possible values for notification
ANDROID = "ANDROID"
IOS = "IOS"
EMAIL = "EMAIL"
NONE = "NONE"

# Possible values for device type
WEB = "WEB"  # + ANDROID, IOS

# Push Notification
ALGORITHM = "ES256"

# Number of search results to return
NUM_SEARCH_RESULT = 50

# Coursegrab notifier email
COURSEGRAB_FROM_EMAIL = "noreply@coursegrab.me"
COURSEGRAB_TO_EMAIL = "coursegrabcornell@gmail.com"

# Max number of bcc emails per SES email notification.
# SES caps a single send at 50 total recipients (to + cc + bcc). One slot is
# used by COURSEGRAB_TO_EMAIL, leaving 49 for bcc.
MAX_BCC_SIZE = 49
