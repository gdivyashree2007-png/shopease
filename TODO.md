# Social Media Platform — TODO

## User registration and login — complete
- Register, login, logout with validation and error messages.
- Passwords hashed (use Django auth).
- Use CSRF protection, login-required checks, and proper permission checks.

## User profiles — complete
- Profile page with profile picture, bio, username, join date.
- Show follower count, following count and the user's posts.
- Edit profile page (update bio and picture).

## Posts, feeds, and Explore — complete
- Create a post with text and an optional image.
- Edit and delete own posts only.
- Home feed showing posts from followed users and own posts, newest first.
- Explore page showing all posts.

## Comments — complete
- Add a comment on any post.
- Delete own comments.
- Show comment count and list of comments under each post.
- Use JavaScript (fetch/AJAX) for comment actions so the page does not reload.

## Likes — complete
- Like / unlike a post (one like per user per post).
- Show like count, and highlight the heart if the current user already liked it.
- Use JavaScript (fetch/AJAX) for like actions so the page does not reload.

## Follows and social lists — complete
- Follow / unfollow other users from their profile.
- Users cannot follow themselves.
- Followers and Following list pages.
- Use JavaScript (fetch/AJAX) for follow/unfollow actions so the page does not reload.

## Username search — complete
- Search users by username.

## Data, admin, and media — complete
- Database: SQLite (Django ORM).
- Database models: User (Django built-in); Profile (user, bio, profile picture); Post (author, content, image, created date); Comment (post, author, text, created date); Like (post, user, unique together); Follow (follower, following, unique together).
- Register all models in Django admin.
- Handle media uploads properly (MEDIA_ROOT and MEDIA_URL configured).
- Add sample data (5 to 6 users, some posts, comments, likes and follows) using a seed script or fixture.

## Project source and run instructions — complete
- Frontend: HTML, CSS, JavaScript (no frameworks, responsive and clean modern UI).
- Backend: Django (Python).
- Use Django templates with separate static folders for CSS and JS.
- Full project source code with a clear folder structure.
- requirements.txt.
- README.md with setup steps (virtual env, migrate, createsuperuser, loaddata, runserver).
- Run and test the app, then share the working link or a zip of the project.
