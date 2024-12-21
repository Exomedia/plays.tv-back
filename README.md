# plays.tv-back
Python script to get available videos from plays.tv archive at archive.org

# Note
It could be more eloquent and handle errors better but that's the best I could do within the time I was willing to put

# USAGE
Check your profile at https://web.archive.org/web/20191210091719/https://plays.tv/u/{Nickname}

Install requirements
```cmd
pip install requests beautifulsoup4 tenacity
```

Start script, it'll asks for your nickname
```cmd
py .\webarchive.py
```

Let it do its job

If it returns an error 10054, download manually from link ending with 720.mp4
```log
Fetching: https://web.archive.org/web/20191210091703/https://plays.tv/video/58e17174924e56e78a/full-monkey-sassnoe
Downloading video from: https://web.archive.org/web/20191213041228im_/https://d0playscdntv-a.akamaihd.net/video/GqS6WpKGZFi/processed/720.mp4
Error downloading video: ('Connection aborted.', ConnectionResetError(10054, 'Une connexion existante a dû être fermée par l’hôte distant', None, 10054, None))
```
