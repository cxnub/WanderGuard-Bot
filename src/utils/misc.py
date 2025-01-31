def time_difference_to_string(time_diff):
    seconds = time_diff.total_seconds()
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    if hours == 1:
        return "An hour ago"
    
    if hours > 1:
        return f"{int(hours)} hours ago"
    
    if minutes <= 1 and seconds > 1:
        return "A minute ago"
    
    if minutes > 1:
        return f"{int(minutes)} minutes ago"
    
    if seconds <= 1:
        return "A second ago"
    
    return f"{int(seconds)} seconds ago"

def status_symbol(status: str):
    if status.lower() == 'safe':
        return '🟢'
    if status.lower() == 'out of safe zone':
        return '🟡'
    if status.lower() == 'wandering':
        return '🔴'