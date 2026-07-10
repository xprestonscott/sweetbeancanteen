/* ================================================================
   SWEET BEAN CANTEEN — v3
   Hero: cup spin-drops from above as you scroll; when it lands,
   steam rises and "SWEET BEAN CANTEEN" stamps onto the sleeve.
   Everything is driven by scroll position, so scrolling back up
   plays the whole thing in reverse automatically.
   ================================================================ */
(function () {
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Fade the scroll hint out as the user scrolls past the hero.
  const hint = document.getElementById("scrollHint");
  if (hint) {
    const onScroll = () => {
      const p = Math.min(window.scrollY / (window.innerHeight * 0.5), 1);
      hint.style.opacity = String(1 - p);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  // Section reveals on scroll.
  const revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && !reduced) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("is-in");
            io.unobserve(e.target);
          }
        });
      },
      { threshold: 0.15 }
    );
    revealEls.forEach((el) => io.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add("is-in"));
  }
})();
