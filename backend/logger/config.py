from backend.logger.handlers import CustomFileHandler

config = {
    'version': 1,

    'formatters': {
        'standard': {
            'format': '\n{asctime} - {name} - {levelname} - {filename} - {message}',
            'style': '{'
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'CRITICAL',
            'formatter': 'standard'
        },
        'api_file': {
            '()': CustomFileHandler,
            'filename': 'api_errors.log',
            'level': 'ERROR',
            'formatter': 'standard'
        },
        'database_file': {
            '()': CustomFileHandler,
            'filename': 'database_errors.log',
            'level': 'ERROR',
            'formatter': 'standard'
        }
    },

    'loggers': {
        'api_logger': {
            'level': 'INFO',
            'handlers': ['console', 'api_file']
        },
        'database_logger': {
            'level': 'ERROR',
            'handlers': ['database_file']
        }
    },
}