from TikTokApi import TikTokApi

# Function to remove reposts
def remove_reposts(username, password):
    api = TikTokApi.get_instance()
    try:
        api.login(username=username, password=password)
        user = api.get_user(username)
        videos = user.videos()
        repost_videos = [video for video in videos if video.is_repost()]
        
        for repost_video in repost_videos:
            api.delete_video(repost_video.id)
            print(f"Repost video {repost_video.id} removed")

        print("All reposts have been removed.")
    except Exception as e:
        print(f"Error removing reposts: {e}")

# Function to remove likes
def remove_likes(username, password):
    api = TikTokApi.get_instance()
    try:
        api.login(username=username, password=password)
        user = api.get_user(username)
        liked_videos = user.liked_videos()

        for liked_video in liked_videos:
            api.remove_like(liked_video.id)
            print(f"Like removed from video {liked_video.id}")

        print("All likes have been removed.")
    except Exception as e:
        print(f"Error removing likes: {e}")

# Function to remove favorites
def remove_favorites(username, password):
    api = TikTokApi.get_instance()
    try:
        api.login(username=username, password=password)
        user = api.get_user(username)
        favorites = user.favorites()

        for favorite in favorites:
            api.remove_favorite(favorite.id)
            print(f"Favorite removed from video {favorite.id}")

        print("All favorites have been removed.")
    except Exception as e:
        print(f"Error removing favorites: {e}")

# Main function to show the menu
def show_menu():
    print("Welcome! Please choose an action:")
    print("1. Remove Reposts")
    print("2. Remove Likes")
    print("3. Remove Favorites")
    print("4. Exit")

    choice = input("Enter your choice (1/2/3/4): ")

    if choice in ['1', '2', '3']:
        username = input("Enter your TikTok username: ")
        password = input("Enter your TikTok password: ")
        
        if choice == '1':
            remove_reposts(username, password)
        elif choice == '2':
            remove_likes(username, password)
        elif choice == '3':
            remove_favorites(username, password)
    elif choice == '4':
        print("Exiting...")
        exit()
    else:
        print("Invalid choice, please try again!")
        show_menu()

# Start the menu
if __name__ == "__main__":
    show_menu()
