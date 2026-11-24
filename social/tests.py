from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from .models import Comment, Follow, Like, Post, Profile


class SocialPlatformTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", email="alice@example.com", password="StrongPass2026!")
        self.bob = User.objects.create_user("bob", email="bob@example.com", password="StrongPass2026!")
        self.cara = User.objects.create_user("cara", email="cara@example.com", password="StrongPass2026!")
        self.post = Post.objects.create(author=self.alice, content="A good little post.")

    def test_profile_is_created_and_registration_hashes_password(self):
        self.assertTrue(Profile.objects.filter(user=self.alice).exists())
        response = self.client.post(reverse("register"), {
            "username": "newfriend", "email": "new@example.com",
            "password1": "HarborLight2026!", "password2": "HarborLight2026!",
        })
        self.assertRedirects(response, reverse("home"))
        user = User.objects.get(username="newfriend")
        self.assertNotEqual(user.password, "HarborLight2026!")
        self.assertTrue(user.check_password("HarborLight2026!"))

    def test_home_feed_contains_only_own_and_followed_posts(self):
        followed_post = Post.objects.create(author=self.bob, content="From a followed friend.")
        hidden_post = Post.objects.create(author=self.cara, content="Not in Alice's feed.")
        Follow.objects.create(follower=self.alice, following=self.bob)
        self.client.force_login(self.alice)
        response = self.client.get(reverse("home"))
        self.assertContains(response, self.post.content)
        self.assertContains(response, followed_post.content)
        self.assertNotContains(response, hidden_post.content)

    def test_like_toggle_is_unique_and_reversible(self):
        self.client.force_login(self.bob)
        url = reverse("like_toggle", args=[self.post.pk])
        first = self.client.post(url)
        second = self.client.post(url)
        self.assertEqual(first.json(), {"liked": True, "count": 1})
        self.assertEqual(second.json(), {"liked": False, "count": 0})
        self.client.post(url)
        self.client.post(url)
        self.assertEqual(Like.objects.filter(post=self.post, user=self.bob).count(), 0)

    def test_comment_add_and_only_author_can_delete(self):
        self.client.force_login(self.bob)
        response = self.client.post(reverse("comment_create", args=[self.post.pk]), {"text": "Lovely thought."})
        self.assertEqual(response.status_code, 200)
        comment = Comment.objects.get()
        self.assertIn("Lovely thought.", response.json()["html"])
        self.client.force_login(self.cara)
        denied = self.client.post(reverse("comment_delete", args=[comment.pk]))
        self.assertEqual(denied.status_code, 403)
        self.client.force_login(self.bob)
        removed = self.client.post(reverse("comment_delete", args=[comment.pk]))
        self.assertEqual(removed.status_code, 200)
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())

    def test_follow_toggle_and_self_follow_protection(self):
        self.client.force_login(self.alice)
        own = self.client.post(reverse("follow_toggle", args=[self.alice.username]))
        self.assertEqual(own.status_code, 400)
        url = reverse("follow_toggle", args=[self.bob.username])
        self.assertEqual(self.client.post(url).json(), {"following": True, "count": 1})
        self.assertEqual(self.client.post(url).json(), {"following": False, "count": 0})
        self.assertFalse(Follow.objects.filter(follower=self.alice, following=self.bob).exists())

    def test_users_cannot_edit_or_delete_another_persons_post(self):
        self.client.force_login(self.bob)
        edit = self.client.post(reverse("post_edit", args=[self.post.pk]), {"content": "Hijacked."})
        self.assertRedirects(edit, self.post.get_absolute_url())
        self.post.refresh_from_db()
        self.assertEqual(self.post.content, "A good little post.")
        delete = self.client.post(reverse("post_delete", args=[self.post.pk]))
        self.assertEqual(delete.status_code, 403)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())

    def test_ajax_endpoints_require_login(self):
        response = self.client.post(reverse("like_toggle", args=[self.post.pk]))
        self.assertEqual(response.status_code, 302)

    def test_search_finds_usernames_case_insensitively(self):
        response = self.client.get(reverse("search"), {"q": "ALI"})
        self.assertContains(response, "alice")
        self.assertNotContains(response, "cara")

    def test_login_accepts_username_or_registered_email(self):
        for identifier in ("alice", "ALICE@EXAMPLE.COM"):
            with self.subTest(identifier=identifier):
                self.client.logout()
                response = self.client.post(reverse("login"), {
                    "username": identifier, "password": "StrongPass2026!",
                })
                self.assertRedirects(response, reverse("home"))
                self.assertEqual(self.client.session.get("_auth_user_id"), str(self.alice.pk))

    def test_invalid_login_shows_error_and_duplicate_email_is_rejected(self):
        response = self.client.post(reverse("login"), {
            "username": "alice@example.com", "password": "incorrect",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username/email or password.")
        duplicate = self.client.post(reverse("register"), {
            "username": "alicecopy", "email": "ALICE@EXAMPLE.COM",
            "password1": "HarborLight2026!", "password2": "HarborLight2026!",
        })
        self.assertEqual(duplicate.status_code, 200)
        self.assertContains(duplicate, "An account with this email already exists.")
        self.assertFalse(User.objects.filter(username="alicecopy").exists())

    def test_csrf_is_enforced_and_secure_session_cookie_is_configured(self):
        client = Client(enforce_csrf_checks=True)
        login_url = reverse("login")
        client.get(login_url, secure=True)
        token = client.cookies["csrftoken"].value
        referer = "https://testserver/login/"
        rejected = client.post(login_url, {"username": "alice", "password": "StrongPass2026!"},
                               secure=True, HTTP_REFERER=referer)
        self.assertEqual(rejected.status_code, 403)
        response = client.post(login_url, {
            "username": "alice", "password": "StrongPass2026!", "csrfmiddlewaretoken": token,
        }, secure=True, HTTP_X_CSRFTOKEN=token, HTTP_REFERER=referer)
        self.assertEqual(response.status_code, 302)
        cookie = client.cookies["socialhub_session"]
        self.assertTrue(cookie["secure"])
        self.assertEqual(cookie["samesite"], "None")
        fresh_token = client.cookies["csrftoken"].value
        response = client.post(reverse("like_toggle", args=[self.post.pk]), secure=True,
                               HTTP_X_CSRFTOKEN=fresh_token,
                               HTTP_REFERER=f"https://testserver/posts/{self.post.pk}/")
        self.assertEqual(response.status_code, 200)
