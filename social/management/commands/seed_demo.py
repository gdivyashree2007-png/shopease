from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from social.models import Comment, Follow, Like, Post


USERS = [
    ("maya", "maya@example.com", "Collecting small moments and good sentences."),
    ("noah", "noah@example.com", "Coffee first, curiosity always."),
    ("amara", "amara@example.com", "Making room for a slower kind of good."),
    ("leo", "leo@example.com", "Designing things that feel a little more human."),
    ("sana", "sana@example.com", "Here for the books, the blooms, the banter."),
    ("kai", "kai@example.com", "Usually outside, occasionally online."),
]
POSTS = [
    ("maya", "A tiny reminder for today: you don't have to turn every quiet moment into something productive."),
    ("noah", "Found a new walking route with absolutely no reason to hurry. Highly recommend."),
    ("amara", "Made the kind of lunch that takes ten minutes and tastes like you had a plan."),
    ("leo", "Working on a little project that is mostly an excuse to use a color I love."),
    ("sana", "Three pages into a book and already hoping it never ends."),
    ("kai", "The sky turned pink on my way home. I stopped for a minute. That was the whole plan."),
    ("maya", "What is one ordinary thing that made your day better this week?"),
    ("noah", "A good conversation is still my favourite kind of notification."),
]
COMMENTS = [
    ("noah", 0, "Needed this little reminder today."),
    ("sana", 0, "A permission slip for all of us."),
    ("maya", 1, "The no-hurry route is the best route."),
    ("leo", 2, "Ten-minute meals deserve a fan club."),
    ("amara", 4, "Tell us the title when you're ready!"),
    ("kai", 5, "Stopping was the plan. Perfect."),
]
FOLLOWS = [("maya", "noah"), ("maya", "amara"), ("noah", "maya"), ("noah", "leo"), ("amara", "sana"), ("leo", "kai"), ("sana", "maya"), ("kai", "amara")]
LIKES = [("noah", 0), ("amara", 0), ("leo", 0), ("maya", 1), ("sana", 1), ("kai", 2), ("maya", 3), ("noah", 4), ("amara", 5), ("leo", 5), ("sana", 6), ("kai", 7)]


class Command(BaseCommand):
    help = "Create six sample SocialHub users, posts, comments, likes and follows."

    def handle(self, *args, **options):
        users = {}
        for username, email, bio in USERS:
            user, created = User.objects.get_or_create(username=username, defaults={"email": email})
            if created:
                user.set_password("SocialHub123!")
                user.save()
            profile = user.profile
            profile.bio = bio
            profile.save()
            users[username] = user
        posts = []
        for username, content in POSTS:
            post, _ = Post.objects.get_or_create(author=users[username], content=content)
            posts.append(post)
        for username, index, text in COMMENTS:
            Comment.objects.get_or_create(post=posts[index], author=users[username], text=text)
        for username, index in LIKES:
            Like.objects.get_or_create(post=posts[index], user=users[username])
        for follower, following in FOLLOWS:
            Follow.objects.get_or_create(follower=users[follower], following=users[following])
        self.stdout.write(self.style.SUCCESS("Demo content is ready. Sample account password: SocialHub123!"))
