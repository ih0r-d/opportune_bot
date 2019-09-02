from lang import ua

token = '943043936:AAGLo303W4kGyJbDAZ0ii0wLSKPH-yqrRG8'  # Set here your key

log_name = 'opportune_bot'  # Log file name
log_level: str = 'debug'  # debug, info, warning, error

# Server offset from GMT (f.ex Ukraine is 2)
server_offset = 2

database_offsets_file = 'users_offsets'
database_states_file = 'state_storage'
database_temp_time_storage = 'temp_time_storage'
database_schedules_file = 'schedules.db'

# Language of bot. Look into "lang" folder for more
lang = ua

# Allows to temporally discard all messages except yours
# Looks at app.py (cmd_closed_mode function)
is_closed = False
