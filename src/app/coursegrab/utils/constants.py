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
COURSEGRAB_TO_EMAIL = "coursegrabappstore@gmail.com"

# Max recipients addressed per email send. Each recipient receives an individual
# email (their own To:), not a shared BCC — a transactional pattern that scores far
# better with strict inbox providers (e.g. Microsoft/Outlook). For SendGrid this is
# the number of personalizations batched into one API request (provider limit 1000);
# for SES we loop one send per recipient, so it just bounds the batch we iterate.
MAX_RECIPIENTS_PER_SEND = 1000
