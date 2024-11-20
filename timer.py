import uasyncio as asyncio
import time

class Timer:
    def __init__(self, hour=0, minute=0, days_of_week=None, date=None, repeat=True):
        """
        Initialize the Timer with customizable configurations.
        
        :param hour: Hour in 24-hour format (0-23)
        :param minute: Minute (0-59)
        :param days_of_week: List of integers representing days of the week (0=Monday, 6=Sunday)
        :param date: Dictionary with 'month' and 'day' for specific dates, e.g., {'month': 12, 'day': 25} for Dec 25
        :param repeat: Whether the timer should repeat
        """
        self.hour = hour
        self.minute = minute
        self.days_of_week = days_of_week if days_of_week is not None else list(range(7))  # Default to all days
        self.date = date  # Optional specific date configuration
        self.repeat = repeat
        self.active = True  # Timer status
    
    def set_time(self, hour, minute):
        self.hour = hour
        self.minute = minute

    def set_days_of_week(self, days_of_week):
        self.days_of_week = days_of_week

    def set_date(self, month, day):
        self.date = {'month': month, 'day': day}

    def set_repeat(self, repeat):
        self.repeat = repeat

    def check_time(self):
        if not self.active:
            return False
        
        current_time = time.localtime()
        current_hour, current_minute = current_time[3], current_time[4]
        current_day = current_time[6]  # Day of the week (0=Monday, 6=Sunday)
        current_month, current_day_of_month = current_time[1], current_time[2]

        # Check hour and minute
        if self.hour == current_hour and self.minute == current_minute:
            # Check day of the week
            if current_day in self.days_of_week:
                # Check specific date if provided
                if self.date is None or (self.date['month'] == current_month and self.date['day'] == current_day_of_month):
                    return True
        return False
    
    async def start(self, action_callback, *args):
        while self.active:
            if self.check_time():
                await action_callback(*args)  # Pass arguments to the callback
                if not self.repeat:
                    self.active = False
                    break
            await asyncio.sleep(60)


    def stop(self):
        self.active = False

    async def reset(self, hour=None, minute=None, days_of_week=None, date=None, repeat=None):
        if hour is not None:
            self.hour = hour
        if minute is not None:
            self.minute = minute
        if days_of_week is not None:
            self.days_of_week = days_of_week
        if date is not None:
            self.date = date
        if repeat is not None:
            self.repeat = repeat
        self.active = True
