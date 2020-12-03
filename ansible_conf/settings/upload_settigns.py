import environ 

env = environ.Env()

ABSOLUTE_PATH_UPLOAD_CONFIGS = env.str('ABSOLUTE_PATH_UPLOAD_CONFIGS', default='/configs')
