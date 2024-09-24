# """Helper method for make a repeating timer"""
# from threading import Timer


# class RepeatTimer(Timer):
#     """RepeatTimer timer with repeating events"""

#     def run(self):
#         while not self.finished.wait(self.interval):
#             new_interval = self.function(*self.args, **self.kwargs)
#             if isinstance(new_interval, (float, int)):
#                 self.interval = new_interval
