import requests
import time
import random

class DiscordGroupLeaver:
    def __init__(self, token):
        self.token = token
        self.headers = {
            'Authorization': token,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_user_groups(self):
        url = "https://discord.com/api/v9/users/@me/channels"
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                channels = response.json()
                group_channels = [ch for ch in channels if ch.get('type') == 3]
                return group_channels
            else:
                print(f"Error fetching groups: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error: {e}")
            return []

    def close_dm(self, channel_id):
        url = f"https://discord.com/api/v9/channels/{channel_id}"
        try:
            response = self.session.delete(url)
            
            if response.status_code == 200:
                return True, "Success"
            elif response.status_code == 429:
                retry_after = response.json().get('retry_after', 60)
                return False, f"Rate limit - Wait {retry_after}s"
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"Exception: {str(e)}"

    def leave_group_legacy(self, channel_id):
        url = f"https://discord.com/api/v9/channels/{channel_id}/recipients/@me"
        try:
            response = self.session.delete(url)
            
            if response.status_code in [204, 200]:
                return True, "Success"
            elif response.status_code == 429:
                retry_after = response.json().get('retry_after', 60)
                return False, f"Rate limit - Wait {retry_after}s"
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"Exception: {str(e)}"

    def run(self):
        print("Searching for groups...")
        groups = self.get_user_groups()
        
        if not groups:
            print("No groups found.")
            return
        
        print(f"Found {len(groups)} groups.")
        
        count = 0
        errors = 0
        rate_limits = 0
        
        random.shuffle(groups)
        
        print("Starting group leaving process...")
        
        for i, group in enumerate(groups):
            group_id = group['id']
            group_name = group.get('name', 'Unnamed') or 'Unnamed'
            
            delay = random.uniform(0.5, 2.0)
            print(f"[{i+1}/{len(groups)}] Next leave in {delay:.1f}s...")
            time.sleep(delay)
            
            success, message = self.close_dm(group_id)
            
            if not success and "400" in message:
                print(f"Trying legacy method for {group_name}...")
                success, message = self.leave_group_legacy(group_id)
            
            if success:
                count += 1
                print(f"Left: {group_name} ({group_id})")
            else:
                if "Rate limit" in message:
                    rate_limits += 1
                    print(f"Rate limit on {group_name}")
                    if "Wait" in message:
                        wait_time = float(message.split(' ')[-1].replace('s', ''))
                        time.sleep(wait_time + random.uniform(5.0, 10.0))
                    groups.insert(i + 1, group)
                else:
                    errors += 1
                    print(f"Error on {group_name}: {message}")
            
            if count > 0 and count % 10 == 0 and count < len(groups):
                pause = random.uniform(5.0, 10.0)
                print(f"Pause for {pause:.1f}s...")
                time.sleep(pause)
        
        print("\n" + "="*50)
        print("FINAL REPORT:")
        print(f"Groups left: {count}")
        print(f"Errors: {errors}")
        print(f"Rate limits: {rate_limits}")
        print("="*50)

def get_token_input():
    print("Discord Group Leaver")
    print("=" * 30)
    
    token = input("Enter your Discord token: ").strip()
    
    if not token:
        print("Error: No token provided")
        return None
        
    return token

if __name__ == "__main__":
    token = get_token_input()
    
    if not token:
        print("Exiting...")
        input("Press Enter to close")
        exit()
    
    print("\nStarting...")
    leaver = DiscordGroupLeaver(token)
    leaver.run()
    
    input("\nPress Enter to exit")