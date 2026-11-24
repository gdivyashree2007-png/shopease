(() => {
  const csrfToken = () => document.querySelector('meta[name="csrf-token"]')?.content || "";
  const send = async (url, body = null) => {
    const headers = { "X-CSRFToken": csrfToken(), "X-Requested-With": "XMLHttpRequest" };
    if (body) headers["Content-Type"] = "application/x-www-form-urlencoded;charset=UTF-8";
    const response = await fetch(url, { method: "POST", headers, body, credentials: "same-origin" });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || "That didn’t work. Please try again.");
    return data;
  };

  document.addEventListener("click", async (event) => {
    const like = event.target.closest("[data-like-url]");
    if (like) {
      event.preventDefault();
      if (like.disabled) return;
      like.disabled = true;
      try {
        const result = await send(like.dataset.likeUrl);
        like.classList.toggle("is-liked", result.liked);
        like.setAttribute("aria-pressed", String(result.liked));
        like.setAttribute("aria-label", `${result.liked ? "Unlike" : "Like"} post`);
        like.querySelector(".heart").textContent = result.liked ? "♥" : "♡";
        like.querySelector("[data-like-count]").textContent = result.count;
      } catch (error) {
        const card = like.closest(".post-card");
        const status = card?.querySelector(".inline-status");
        if (status) status.textContent = error.message;
      } finally { like.disabled = false; }
      return;
    }

    const follow = event.target.closest("[data-follow-url]");
    if (follow) {
      event.preventDefault();
      if (follow.disabled) return;
      follow.disabled = true;
      const status = document.querySelector(".follow-status");
      try {
        const result = await send(follow.dataset.followUrl);
        follow.classList.toggle("is-following", result.following);
        follow.setAttribute("aria-pressed", String(result.following));
        follow.textContent = result.following ? "Following" : "＋ Follow";
        const count = document.querySelector("#follower-count");
        if (count) count.textContent = result.count;
        if (status) status.textContent = result.following ? "You’re connected." : "You unfollowed this person.";
      } catch (error) { if (status) status.textContent = error.message; }
      finally { follow.disabled = false; }
      return;
    }

    const removeComment = event.target.closest("[data-comment-delete-url]");
    if (removeComment) {
      event.preventDefault();
      if (!window.confirm("Delete your comment?")) return;
      removeComment.disabled = true;
      const card = removeComment.closest(".post-card");
      try {
        const result = await send(removeComment.dataset.commentDeleteUrl);
        document.getElementById(`comment-${result.deleted}`)?.remove();
        updateCommentCount(card, result.count);
        if (result.count === 0) {
          const list = card?.querySelector("[data-comment-list]");
          if (list) list.innerHTML = '<p class="empty-comments" data-empty-comments>Be the first to reply.</p>';
        }
      } catch (error) {
        const status = card?.querySelector(".inline-status");
        if (status) status.textContent = error.message;
      } finally { removeComment.disabled = false; }
    }
  });

  const updateCommentCount = (card, count) => {
    card?.querySelectorAll("[data-comment-count]").forEach((node) => { node.textContent = count; });
  };

  document.addEventListener("submit", async (event) => {
    const form = event.target.closest("[data-comment-form]");
    if (form) {
      event.preventDefault();
      const input = form.querySelector('input[name="text"]');
      const status = form.parentElement.querySelector(".inline-status");
      const button = form.querySelector("button");
      if (!input.value.trim()) { input.focus(); return; }
      button.disabled = true;
      if (status) status.textContent = "";
      const card = form.closest(".post-card");
      try {
        const body = new URLSearchParams({ text: input.value.trim() });
        const result = await send(form.dataset.commentUrl, body);
        card.querySelector("[data-empty-comments]")?.remove();
        card.querySelector("[data-comment-list]")?.insertAdjacentHTML("beforeend", result.html);
        updateCommentCount(card, result.count);
        input.value = "";
      } catch (error) { if (status) status.textContent = error.message; }
      finally { button.disabled = false; }
      return;
    }

    const confirmForm = event.target.closest("form[data-confirm]");
    if (confirmForm && !window.confirm(confirmForm.dataset.confirm)) event.preventDefault();
  });
})();
