export function useScrollToTop() {
  const isScrollable = (el: HTMLElement): boolean => {
    const style = getComputedStyle(el);

    const overflowY = style.overflowY;
    const isOverflowScrollable =
      overflowY === 'auto' ||
      overflowY === 'scroll' ||
      overflowY === 'overlay';

    const hasScrollableContent = el.scrollHeight > el.clientHeight;

    return isOverflowScrollable && hasScrollableContent;
  };

  const scrollToTop = (el: HTMLElement | null) => {
    let current: HTMLElement | null = el;

    while (current) {
      if (isScrollable(current)) {
        current.scrollTo({ top: 0, behavior: 'smooth' });
        return;
      }
      current = current.parentElement;
    }

    // fallback: page scroll
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return { scrollToTop };
}
