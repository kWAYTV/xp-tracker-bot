import pytz
from datetime import datetime, timedelta

class DateTime:
    def __init__(self):
        self.timezone = pytz.timezone('Europe/Madrid')

    def get_current_timestamp(self):
        # Set the timezone to Central European Time (Spain)
        # Get the current time in the specified timezone
        current_time = datetime.now(self.timezone)
        return current_time

    def time_until_next_wednesday(self):
        # Get the current remaining time till next Wednesday 3 AM CET
        current_time = datetime.now(self.timezone)

        # If today is Wednesday but before 3 AM
        if current_time.weekday() == 2 and current_time.hour < 3:
            next_wednesday = current_time.replace(hour=3, minute=0, second=0, microsecond=0)
        else:
            # Days until next Wednesday
            days_until_wednesday = (2 - current_time.weekday() + 7) % 7
            if days_until_wednesday == 0:
                days_until_wednesday = 7
            next_wednesday = (current_time + timedelta(days=days_until_wednesday)).replace(hour=3, minute=0, second=0, microsecond=0)

        # Get the time remaining
        time_remaining = next_wednesday - current_time

        # Get the time remaining in days, hours, minutes and seconds
        days, seconds = time_remaining.days, time_remaining.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        # Construct the output string
        output_list = []
        if days:
            output_list.append(f"{days} Days")
        if hours:
            output_list.append(f"{hours} Hours")
        if minutes:
            output_list.append(f"{minutes} Minutes")
        if seconds:
            output_list.append(f"{seconds} Seconds")
        
        return ' '.join(output_list)
