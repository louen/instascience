#!/usr/bin/python3

import os
import glob

#import numpy as np
#import matplotlib.pyplot as plt

from instaloader import Instaloader, Profile
from instaloader.exceptions import *
L = Instaloader()

# Credentials to login (otherwise insta limits us to about 10 posts)
username="chapeaubelon"
password=""
# Profile to sweep
target_profile = "chapeaubelon"

# Cache directory for downloaded pictures
cache_dir = "instacache"

# Read pwd from file
with open("instapwd.txt") as f:
    password=f.read()
try:
    if password == "":
        L.interactive_login(username)
    else:
        L.login(username,password)
except BadCredentialsException:
    print(f"Cannot login with user {username}")
    exit(1)

print(f"Logged in with {username}")

# Read posts from profile
try:
    profile = Profile.from_username(L.context, username)
except ProfileNotExistsException:
    print(f"User {username} does not exists")
    exit(1)

print(f"Connected to user {username}")

posts = profile.get_posts()

# Create a temp folder to cache the posts
os.makedirs(cache_dir, exist_ok=True)


# use this to limit the dl times while we dev
max_posts = 10
counter = 0
for post in posts:
    counter = counter + 1 
    if counter > max_posts:
        break

    print(f"Post {post.shortcode} - {post.likes} likes")
    target = cache_dir 
    
    # ignore videos
    if post.is_video:
        continue
    # download image
    #if os.path.exists(target):
    #    print("(Cached)")
    #else:
    L.download_post(post, target)


# Now we have the GRAMS ! Let's do some data visualization
grams = glob.glob(os.path.join(target, "*.jpg"))
print(len(grams))


