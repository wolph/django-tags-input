/** Fit same-origin examples to their content, including after Python starts. */
for (const frame of document.querySelectorAll('iframe[src*="playground/"]')) {
  if (!(frame instanceof HTMLIFrameElement)) continue;
  const resize = () => {
    const content = frame.contentDocument?.querySelector('main');
    if (!content) return;
    const observer = new ResizeObserver(() => {
      frame.style.height = `${Math.ceil(content.getBoundingClientRect().height)}px`;
    });
    observer.observe(content);
    frame.style.height = `${Math.ceil(content.getBoundingClientRect().height)}px`;
  };
  frame.addEventListener('load', resize);
  if (frame.contentDocument?.readyState === 'complete') resize();
}
