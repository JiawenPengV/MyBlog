# MyBlog - A place to share your life
## Synopsis
MyBlog is a full stack web application powered by Django. It provides a platform to let people communicate with each other and share their daily life. Registered users can post the event on the main page and they can also view followed users' posts. Users can view other users' profile and choose to follow or unfollow them. What's more, the interaction between different users is fulfilled by synchronized comments.

## Technical Stack
* Django/python
* Google App Engine
* Google Storage

## Functions
* 1.User registration and authorization.
* 2.Editing user profile and viewing other users' profile. The user can upload new image as profile image and add personal information.
* 3.Posting new event with the local timestamp.
* 4.Adding new comments to existed events.
* 5.Events management. The user can delete existed posts.
* 6.Auto-refreshing using AJAX.


## Requirements
* Django 1.11
* python 2/3

## Installation
Clone the GitHub repository and then import source code under /src into your PyCharm.

```
git clone https://github.com/Jiawenjiang/MyBlog
python manage.py makemigrations
python manage.py migrate
python runserver
```



## Usage/Quick Start
* Register account(you need to confirm in your email)
* Post new posts on the main page
* Click username to view his profile
* Click follow/unfollow button to follow/unfollow other users
* Leave comments under existed posts
* Manage your own posts on your profile page
* enjoy!:+1:

## Screenshots
login page
![](https://github.com/Jiawenjiang/MyBlog/raw/master/demoPics/login.png)
register page
![](https://github.com/Jiawenjiang/MyBlog/raw/master/demoPics/register.png)
main page
![](https://github.com/Jiawenjiang/MyBlog/raw/master/demoPics/mainpage.png)
profile page
![](https://github.com/Jiawenjiang/MyBlog/raw/master/demoPics/profile.png)
edit profile page
![](https://github.com/Jiawenjiang/MyBlog/raw/master/demoPics/edit_profile.png)
folloe/unfollow page
![](https://github.com/Jiawenjiang/MyBlog/raw/master/demoPics/follow_unfollow.png)




## Licenses
NAN


## Deployment
My Deployment URL:
https://grumblr-jiawenpeng.appspot.com/
(Please contact me at jiawenp1@andrew.cmu.edu if this instance is not running)

## Notes:
I’m sending real Emails for registration and resetting.
Make sure you use a real email address and confirm the link in the email sent to you.
In settings.py, I changed my password in to password for submission.




