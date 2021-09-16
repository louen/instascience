#!/usr/bin/python3

import os
import glob

import numpy as np
import matplotlib.pyplot as plt

from PIL import Image

from instaloader import Instaloader, Profile
from instaloader.exceptions import *

# Credentials to login (otherwise insta limits us to about 10 posts)
username = "chapeaubelon"
password = ""
# Profile to sweep
target_profile = "chapeaubelon"

# Cache directory for downloaded pictures
cache_dir = "instacache"

if False:

    L = Instaloader()
    # Read pwd from file
    with open("instapwd.txt") as f:
        password = f.read()
    try:
        if password == "":
            L.interactive_login(username)
        else:
            L.login(username, password)
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
    max_posts = 1
    counter = 0
    for post in posts:
        counter = counter + 1
        if counter > max_posts:
            break

        print(f"Post {post.shortcode} - {post.likes} likes")

        # ignore videos
        if post.is_video:
            continue
        L.download_post(post, cache_dir)


# Now we have the GRAMS ! Let's do some data visualization
grams = glob.glob(os.path.join(cache_dir, "*.jpg"))
print(f"processing {len(grams)} grams")

for gram in grams[0:10]:
    img = Image.open(gram)
    array = np.array(img)

    height, width, channels = array.shape

    rgb_squash_v = np.average(array, axis=0)
    rgb_squash_h = np.average(array, axis=1)
    rgb_avg = np.average(array, axis=(0, 1))

    pix = 100

    img_squash_v = Image.fromarray(np.expand_dims(rgb_squash_v, axis = 0).astype(array.dtype)).resize((width,pix), Image.NEAREST)
    img_squash_h = Image.fromarray(np.expand_dims(rgb_squash_h, axis = 1).astype(array.dtype)).resize((pix,height), Image.NEAREST)
    img_avg = Image.fromarray(np.resize(rgb_avg, (pix,pix,channels)).astype(array.dtype))


    fig  = plt.figure(constrained_layout = True)
    spec = fig.add_gridspec(2,2, width_ratios = [width, pix], height_ratios = [height, pix])

    ax = fig.add_subplot(spec[0,0])
    ax.axis('off')
    ax.imshow(img, interpolation='nearest')

    ax = fig.add_subplot(spec[0,1])
    ax.axis('off')
    ax.imshow(img_squash_h, interpolation='nearest')
    

    ax = fig.add_subplot(spec[1,0])
    ax.axis('off')
    ax.imshow(img_squash_v, interpolation='nearest')

    ax = fig.add_subplot(spec[1,1])
    ax.axis('off')
    ax.imshow(img_avg, interpolation='nearest')
    plt.show()


