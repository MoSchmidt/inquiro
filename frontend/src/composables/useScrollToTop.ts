export function useScrollToTop() {
  const scrollToTop = (el: HTMLElement | null) => {
    let current: HTMLElement | null = el;

    while (current) {
      const { overflowY } = getComputedStyle(current);
      if (overflowY === 'auto' || overflowY === 'scroll') {
        current.scrollTo({ top: 0, behavior: 'smooth' });
        return;
      }
      current = current.parentElement;
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return { scrollToTop };
}
