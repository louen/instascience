#!/usr/bin/python3

import os
import glob
import matplotlib

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors

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

for gram in grams[0:1]:
    img = Image.open(gram)
    rgb_array = np.array(img)

    height, width, channels = rgb_array.shape
    img_type = rgb_array.dtype

    rgb_squash_v = np.average(rgb_array, axis=0)
    rgb_squash_h = np.average(rgb_array, axis=1)
    rgb_avg = np.average(rgb_array, axis=(0, 1))

    # resize display image so they're not 1px wide
    pix = 100
    img_squash_v = Image.fromarray(np.expand_dims(rgb_squash_v, axis = 0).astype(img_type)).resize((width,pix), Image.NEAREST)
    img_squash_h = Image.fromarray(np.expand_dims(rgb_squash_h, axis = 1).astype(img_type)).resize((pix,height), Image.NEAREST)
    img_avg = Image.fromarray(np.resize(rgb_avg, (pix,pix,channels)).astype(img_type))

    hsv_array = colors.rgb_to_hsv(rgb_array)
    hsv_squash_v = np.expand_dims(np.average(hsv_array, axis = 0), axis = 0)
    hsv_squash_h = np.expand_dims(np.average(hsv_array, axis = 1), axis = 1)
    hsv_avg = np.average(hsv_array, axis = (0,1))

    img_squash_v2 = Image.fromarray(colors.hsv_to_rgb(hsv_squash_v).astype(img_type)).resize((width, pix), Image.NEAREST)
    img_squash_h2 = Image.fromarray(colors.hsv_to_rgb(hsv_squash_h).astype(img_type)).resize((pix, height), Image.NEAREST)
    img_avg2= Image.fromarray(colors.hsv_to_rgb(hsv_avg).astype(img_type)).resize((pix,pix), Image.NEAREST)



    fig  = plt.figure(constrained_layout = True)
    spec = fig.add_gridspec(3,3, width_ratios = [width, pix, pix], height_ratios = [height, pix, pix])

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


    ax = fig.add_subplot(spec[0,2])
    ax.axis('off')
    ax.imshow(img_squash_h2, interpolation='nearest')
   
    ax = fig.add_subplot(spec[2,0])
    ax.axis('off')
    ax.imshow(img_squash_v2, interpolation='nearest')

    ax = fig.add_subplot(spec[2,2])
    ax.axis('off')
    ax.imshow(img_avg, interpolation='nearest')

    plt.show()


