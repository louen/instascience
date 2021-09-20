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

def float_array_to_img(array):
    assert(len(array.shape) == 3)
    return Image.fromarray((255.0 *array).astype('uint8') )

for gram in grams[0:1]:
    img = Image.open(gram)

    # convert image to different colorspaces in floatspace
    rgb_array = np.array(img) / 255.0                   # RGB
    hsv_array = colors.rgb_to_hsv(rgb_array)            # HSV

    height, width, channels = rgb_array.shape
    img_type = 'uint8' 

    # Average along horizontal axis
    rgb_squash_h = np.expand_dims(np.average(rgb_array, axis=1), axis=1)
    hsv_squash_h = np.expand_dims(np.average(hsv_array, axis=1), axis=1)

    # resize display image so they're not 1px wide
    pix = 100
    
    img_squash_h_rgb = float_array_to_img(rgb_squash_h).resize((pix,height), Image.NEAREST)
    img_squash_h_hsv = float_array_to_img(colors.hsv_to_rgb(hsv_squash_h)).resize((pix, height), Image.NEAREST)

    fig  = plt.figure(constrained_layout = True)
    spec = fig.add_gridspec(1,3, width_ratios = [width, pix, pix], height_ratios = [height])

    ax = fig.add_subplot(spec[0,0])
    ax.axis('off')
    ax.imshow(img, interpolation='nearest')

    ax = fig.add_subplot(spec[0,1])
    ax.axis('off')
    ax.imshow(img_squash_h_rgb, interpolation='nearest')
    
    ax = fig.add_subplot(spec[0,2])
    ax.axis('off')
    ax.imshow(img_squash_h_hsv, interpolation='nearest')
   
    plt.show()


def draw_color_wheel(ax):
    x_color= np.arange(0, 2*np.pi, 0.01)
    y_color = np.ones_like(x_color)
    ax.scatter(x_color, y_color, c=x_color, s=300, cmap = plt.get_cmap('hsv'), norm = colors.Normalize(0.0, 2*np.pi))


def smooth_with_wrap(hist, kernel):
    #assuming kernel weights sum to 1
    assert(len(kernel) % 2 == 1)
    result = np.zeros_like(hist)

    #surely there's a numpy function for that
    for i, x in enumerate(hist):
        for j, y in enumerate(kernel):
            index = (i + j - len(kernel) // 2 + 1) % len(hist)
            result[index] += y * x
    
    return result

def box_filter(n):
    return (1.0 / n ) * np.ones(n)


def plot_hue_hist(ax, bins, hist):
    x_dist = 2 * np.pi * bins
    normalized_hist = (1.0 + hist / np.max(hist))
    y_dist = np.append(normalized_hist, normalized_hist[0])
    ax.plot(x_dist, y_dist)

def plot_color_circle_density(array):


    bins = np.arange(0,1,1.0/256)
    hist, _ = np.histogram(array, bins)

    ax = plt.subplot(1,3,1,polar=True)
    ax.set_aspect(1.0)
    ax.set_ylim([0,2])
    ax.axis('off')
    ax.set_title('unfiltered')

    draw_color_wheel(ax)
    plot_hue_hist(ax,bins,hist)

    ax = plt.subplot(1,3,2, polar=True)
    ax.set_aspect(1.0)
    ax.set_ylim([0,2])
    ax.axis('off')
    ax.set_title('box 11')
    draw_color_wheel(ax)
    plot_hue_hist(ax,bins, smooth_with_wrap(hist, box_filter(11)))
    
    ax = plt.subplot(1,3,3, polar=True)
    ax.set_aspect(1.0)
    ax.set_ylim([0,2])
    ax.axis('off')
    ax.set_title('box 25')
    draw_color_wheel(ax)
    plot_hue_hist(ax,bins, smooth_with_wrap(hist, box_filter(25)))
    


    plt.show()

plot_color_circle_density(hsv_array[:,:,0])
