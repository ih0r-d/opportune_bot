#  coding: utf-8


# COMMON STRINGS

common_welcome_text = """ Hello! If you want to set a new reminder, user /new_event command \n
                          Please note, maximum of 5 reminders at once is supported for now """

common_guide_timezone = """ Enter your timezone like +x or -x (only integers supported \n
                            Warning! Timezone should be set related to GMT+0 \n"""

common_guide_time = """Enter reminder time. For example: \n\n
                       1. 20:00 - Send reminder today at 20:00\n
                       2. 15:57 20.12.2016 - Send reminder at 15:57 20.12.2016 \n
                       Currently supported dates before 31.12.2016 inclusive """

common_is_time_correct = """I recognized date and time as {0!s} \n
                            If that's correct, enter note text.\n
                            It you think that I'm mistaken, please, enter /cancel and try again"""

common_timezone_set = 'Timezone set, thank you!'
common_cancel = 'Ok. Let\'s start again'
common_note_added = 'Note added. You\'ll receive reminder {0!s}'

# ERRORS && EXCEPTIONS

error_note_too_long = 'Note must be under 1000 characters.\nPlease, shorten your note and try again'
error_date_in_past = 'You can\'t set date in the past!'
error_timezone_not_recognized = 'I can\'t recognize entered timezone, please try again'
error_time_not_recognized = 'I can\'t recognize time. Please, try again.'
error_timezone_not_set = 'You haven\'t set up timezone. Please, set it with /set_offset command and try again'

error_maximum_number_of_notes = """ You already have 5 reminders. To prevent flooding, you can\'t set more than 5 
                                    reminders at once. \n A list of set reminders is updated every 24 hours. """

error_could_not_save_note = 'Failed to save note in database. Please, try again'
error_after_2022 = 'Could not set date after 01.01.2022'
error_incorrect_input = 'Date/time set incorrectly. Please, try again'
error_incorrect_date = 'No such date'
